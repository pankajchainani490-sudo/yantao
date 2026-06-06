from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from app.core.config import settings


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = Path(db_path or settings.db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_path: Optional[Path] = None) -> None:
    with get_connection(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_ip TEXT NOT NULL,
                destination_ip TEXT NOT NULL,
                source_port INTEGER NOT NULL,
                destination_port INTEGER NOT NULL,
                predicted_label TEXT NOT NULL,
                predicted_label_id INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                confidence REAL NOT NULL,
                model_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER NOT NULL,
                source_ip TEXT NOT NULL,
                source_port INTEGER NOT NULL,
                destination_ip TEXT NOT NULL,
                destination_port INTEGER NOT NULL,
                attack_type TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                confidence REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (prediction_id) REFERENCES predictions (id)
            );

            CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_ip TEXT NOT NULL,
                source_port INTEGER NOT NULL,
                attack_type TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                hit_count INTEGER NOT NULL,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                status TEXT NOT NULL,
                reason TEXT NOT NULL,
                created_by TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS replay_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                is_running INTEGER NOT NULL,
                current_stage INTEGER NOT NULL,
                current_label TEXT NOT NULL,
                progress REAL NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS site_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_host TEXT NOT NULL,
                scheme TEXT NOT NULL,
                port INTEGER NOT NULL,
                target_url TEXT NOT NULL,
                display_name TEXT NOT NULL,
                is_active INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(target_host, scheme, port)
            );

            CREATE TABLE IF NOT EXISTS traffic_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER,
                target_host TEXT NOT NULL,
                target_url TEXT NOT NULL,
                source_ip TEXT NOT NULL,
                source_port INTEGER NOT NULL,
                destination_port INTEGER NOT NULL,
                scenario TEXT NOT NULL,
                request_count INTEGER NOT NULL,
                packets_per_sec REAL NOT NULL,
                bytes_per_sec REAL NOT NULL,
                flow_duration REAL NOT NULL,
                predicted_label TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                confidence REAL NOT NULL,
                prediction_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (target_id) REFERENCES site_targets (id),
                FOREIGN KEY (prediction_id) REFERENCES predictions (id)
            );
            """
        )
        _migrate_monitor_tables(connection)
        _seed_demo_data(connection)
        _seed_monitor_target(connection)
        connection.commit()


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {str(row["name"]) for row in rows}


def _create_site_targets_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS site_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_host TEXT NOT NULL,
            scheme TEXT NOT NULL,
            port INTEGER NOT NULL,
            target_url TEXT NOT NULL,
            display_name TEXT NOT NULL,
            is_active INTEGER NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(target_host, scheme, port)
        )
        """
    )


def _build_target_url(host: str, scheme: str, port: int) -> str:
    url = f"{scheme}://{host}"
    if (scheme == "http" and port != 80) or (scheme == "https" and port != 443):
        url = f"{url}:{port}"
    return url


def _migrate_site_targets(connection: sqlite3.Connection) -> None:
    table_row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'site_targets'"
    ).fetchone()
    if not table_row:
        _create_site_targets_table(connection)
        return

    columns = _table_columns(connection, "site_targets")
    table_sql = str(table_row["sql"] or "")
    needs_rebuild = (
        "display_name" not in columns
        or "is_active" not in columns
        or "CHECK (id = 1)" in table_sql
        or "CHECK(id = 1)" in table_sql
    )
    if not needs_rebuild:
        return

    legacy_rows = [dict(row) for row in connection.execute("SELECT * FROM site_targets").fetchall()]
    connection.execute("DROP TABLE IF EXISTS site_targets_legacy")
    connection.execute("ALTER TABLE site_targets RENAME TO site_targets_legacy")
    _create_site_targets_table(connection)

    now = datetime.utcnow().isoformat()
    for row in legacy_rows:
        scheme = str(row.get("scheme") or "http")
        port = int(row.get("port") or (443 if scheme == "https" else 80))
        host = str(row.get("target_host") or "localhost")
        target_url = str(row.get("target_url") or _build_target_url(host, scheme, port))
        display_name = str(row.get("display_name") or f"{host}:{port}")
        updated_at = str(row.get("updated_at") or now)
        is_active = int(row.get("is_active", 1))
        connection.execute(
            """
            INSERT OR IGNORE INTO site_targets (
                id, target_host, scheme, port, target_url, display_name, is_active, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (row.get("id"), host, scheme, port, target_url, display_name, is_active, updated_at),
        )

    connection.execute("DROP TABLE IF EXISTS site_targets_legacy")


def _migrate_traffic_events(connection: sqlite3.Connection) -> None:
    columns = _table_columns(connection, "traffic_events")
    if "target_id" not in columns:
        connection.execute("ALTER TABLE traffic_events ADD COLUMN target_id INTEGER")

    now = datetime.utcnow().isoformat()
    connection.execute(
        """
        INSERT OR IGNORE INTO site_targets (
            target_host, scheme, port, target_url, display_name, is_active, updated_at
        )
        SELECT
            target_host,
            CASE WHEN lower(target_url) LIKE 'https://%' THEN 'https' ELSE 'http' END AS scheme,
            destination_port,
            target_url,
            target_host || ':' || destination_port,
            1,
            COALESCE(MAX(created_at), ?)
        FROM traffic_events
        WHERE target_id IS NULL
        GROUP BY target_host, target_url, destination_port
        """,
        (now,),
    )
    connection.execute(
        """
        UPDATE traffic_events
        SET target_id = (
            SELECT site_targets.id
            FROM site_targets
            WHERE site_targets.target_host = traffic_events.target_host
              AND site_targets.port = traffic_events.destination_port
              AND site_targets.scheme = CASE
                  WHEN lower(traffic_events.target_url) LIKE 'https://%' THEN 'https'
                  ELSE 'http'
              END
            ORDER BY site_targets.id DESC
            LIMIT 1
        )
        WHERE target_id IS NULL
        """
    )


def _migrate_monitor_tables(connection: sqlite3.Connection) -> None:
    _migrate_site_targets(connection)
    _migrate_traffic_events(connection)


def _seed_monitor_target(connection: sqlite3.Connection) -> None:
    existing_local_target = connection.execute(
        """
        SELECT COUNT(*)
        FROM site_targets
        WHERE scheme = 'http'
          AND port = 5173
          AND target_host IN ('localhost', '127.0.0.1')
        """
    ).fetchone()[0]
    if existing_local_target:
        return

    now = datetime.utcnow().isoformat()
    connection.execute(
        """
        INSERT OR IGNORE INTO site_targets (
            target_host, scheme, port, target_url, display_name, is_active, updated_at
        )
        VALUES ('localhost', 'http', 5173, 'http://localhost:5173', 'localhost:5173', 1, ?)
        """,
        (now,),
    )


def _seed_demo_data(connection: sqlite3.Connection) -> None:
    prediction_count = connection.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    if prediction_count:
        return

    now = datetime.utcnow()
    demo_predictions = [
        {
            "source_ip": "192.168.10.12",
            "destination_ip": "93.184.216.34",
            "source_port": 51514,
            "destination_port": 443,
            "predicted_label": "benign",
            "predicted_label_id": 0,
            "risk_level": "low",
            "confidence": 0.97,
            "model_name": "random_forest",
            "created_at": (now - timedelta(minutes=35)).isoformat(),
        },
        {
            "source_ip": "192.168.10.66",
            "destination_ip": "192.168.10.1",
            "source_port": 0,
            "destination_port": 0,
            "predicted_label": "arp_spoof",
            "predicted_label_id": 1,
            "risk_level": "high",
            "confidence": 0.96,
            "model_name": "random_forest",
            "created_at": (now - timedelta(minutes=28)).isoformat(),
        },
        {
            "source_ip": "10.10.0.45",
            "destination_ip": "172.16.0.10",
            "source_port": 42350,
            "destination_port": 80,
            "predicted_label": "ddos",
            "predicted_label_id": 2,
            "risk_level": "high",
            "confidence": 0.99,
            "model_name": "random_forest",
            "created_at": (now - timedelta(minutes=22)).isoformat(),
        },
        {
            "source_ip": "192.168.20.18",
            "destination_ip": "45.83.64.12",
            "source_port": 50362,
            "destination_port": 8080,
            "predicted_label": "trojan",
            "predicted_label_id": 3,
            "risk_level": "medium",
            "confidence": 0.88,
            "model_name": "decision_tree",
            "created_at": (now - timedelta(minutes=18)).isoformat(),
        },
        {
            "source_ip": "10.10.0.46",
            "destination_ip": "172.16.0.10",
            "source_port": 42368,
            "destination_port": 80,
            "predicted_label": "ddos",
            "predicted_label_id": 2,
            "risk_level": "high",
            "confidence": 0.98,
            "model_name": "random_forest",
            "created_at": (now - timedelta(minutes=12)).isoformat(),
        },
        {
            "source_ip": "192.168.10.22",
            "destination_ip": "13.107.42.14",
            "source_port": 52018,
            "destination_port": 443,
            "predicted_label": "benign",
            "predicted_label_id": 0,
            "risk_level": "low",
            "confidence": 0.95,
            "model_name": "random_forest",
            "created_at": (now - timedelta(minutes=6)).isoformat(),
        },
    ]

    malicious_prediction_ids: list[tuple[int, dict[str, object]]] = []
    for prediction in demo_predictions:
        cursor = connection.execute(
            """
            INSERT INTO predictions (
                source_ip, destination_ip, source_port, destination_port,
                predicted_label, predicted_label_id, risk_level, confidence,
                model_name, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                prediction["source_ip"],
                prediction["destination_ip"],
                prediction["source_port"],
                prediction["destination_port"],
                prediction["predicted_label"],
                prediction["predicted_label_id"],
                prediction["risk_level"],
                prediction["confidence"],
                prediction["model_name"],
                prediction["created_at"],
            ),
        )
        if prediction["predicted_label"] != "benign":
            malicious_prediction_ids.append((cursor.lastrowid, prediction))

    for prediction_id, prediction in malicious_prediction_ids:
        connection.execute(
            """
            INSERT INTO alerts (
                prediction_id, source_ip, source_port, destination_ip,
                destination_port, attack_type, risk_level, confidence, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                prediction_id,
                prediction["source_ip"],
                prediction["source_port"],
                prediction["destination_ip"],
                prediction["destination_port"],
                prediction["predicted_label"],
                prediction["risk_level"],
                prediction["confidence"],
                "open",
                prediction["created_at"],
            ),
        )

    blacklist_rows = [
        {
            "source_ip": "192.168.10.66",
            "source_port": 0,
            "attack_type": "arp_spoof",
            "risk_level": "high",
            "hit_count": 3,
            "first_seen_at": (now - timedelta(minutes=28)).isoformat(),
            "last_seen_at": (now - timedelta(minutes=20)).isoformat(),
            "status": "active",
            "reason": "Repeated ARP spoof alerts in demo seed data.",
            "created_by": "system",
        },
        {
            "source_ip": "10.10.0.45",
            "source_port": 42350,
            "attack_type": "ddos",
            "risk_level": "high",
            "hit_count": 2,
            "first_seen_at": (now - timedelta(minutes=22)).isoformat(),
            "last_seen_at": (now - timedelta(minutes=12)).isoformat(),
            "status": "active",
            "reason": "Repeated DDoS alerts in demo seed data.",
            "created_by": "system",
        },
    ]

    for row in blacklist_rows:
        connection.execute(
            """
            INSERT INTO blacklist (
                source_ip, source_port, attack_type, risk_level, hit_count,
                first_seen_at, last_seen_at, status, reason, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["source_ip"],
                row["source_port"],
                row["attack_type"],
                row["risk_level"],
                row["hit_count"],
                row["first_seen_at"],
                row["last_seen_at"],
                row["status"],
                row["reason"],
                row["created_by"],
            ),
        )

    replay_label = json.loads(settings.replay_manifest_path.read_text(encoding="utf-8"))["stages"][0]["label"]
    connection.execute(
        """
        INSERT INTO replay_state (id, is_running, current_stage, current_label, progress, updated_at)
        VALUES (1, 0, 0, ?, 0.0, ?)
        """,
        (replay_label, now.isoformat()),
    )
