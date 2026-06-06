from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from app.core.config import settings
from app.db.database import get_connection


def _utcnow() -> str:
    return datetime.utcnow().isoformat()


def create_prediction_event(payload: dict[str, Any], db_path: Optional[Path] = None) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO predictions (
                source_ip, destination_ip, source_port, destination_port,
                predicted_label, predicted_label_id, risk_level, confidence,
                model_name, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["source_ip"],
                payload["destination_ip"],
                payload["source_port"],
                payload["destination_port"],
                payload["predicted_label"],
                payload["predicted_label_id"],
                payload["risk_level"],
                payload["confidence"],
                payload["model_name"],
                payload.get("created_at", _utcnow()),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def create_alert(payload: dict[str, Any], db_path: Optional[Path] = None) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO alerts (
                prediction_id, source_ip, source_port, destination_ip,
                destination_port, attack_type, risk_level, confidence, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["prediction_id"],
                payload["source_ip"],
                payload["source_port"],
                payload["destination_ip"],
                payload["destination_port"],
                payload["attack_type"],
                payload["risk_level"],
                payload["confidence"],
                payload.get("status", "open"),
                payload.get("created_at", _utcnow()),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def count_alert_hits(source_ip: str, attack_type: str, db_path: Optional[Path] = None) -> int:
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS hit_count FROM alerts WHERE source_ip = ? AND attack_type = ?",
            (source_ip, attack_type),
        ).fetchone()
        return int(row["hit_count"])


def upsert_blacklist_entry(payload: dict[str, Any], db_path: Optional[Path] = None) -> dict[str, Any]:
    with get_connection(db_path) as connection:
        existing = connection.execute(
            "SELECT * FROM blacklist WHERE source_ip = ? AND attack_type = ? AND status = 'active'",
            (payload["source_ip"], payload["attack_type"]),
        ).fetchone()
        now = payload.get("last_seen_at", _utcnow())

        if existing:
            hit_count = max(int(existing["hit_count"]), int(payload.get("hit_count", existing["hit_count"])))
            connection.execute(
                """
                UPDATE blacklist
                SET source_port = ?, risk_level = ?, hit_count = ?, last_seen_at = ?, reason = ?, created_by = ?
                WHERE id = ?
                """,
                (
                    payload["source_port"],
                    payload["risk_level"],
                    hit_count,
                    now,
                    payload["reason"],
                    payload.get("created_by", "system"),
                    existing["id"],
                ),
            )
            connection.commit()
            row = connection.execute("SELECT * FROM blacklist WHERE id = ?", (existing["id"],)).fetchone()
        else:
            cursor = connection.execute(
                """
                INSERT INTO blacklist (
                    source_ip, source_port, attack_type, risk_level, hit_count,
                    first_seen_at, last_seen_at, status, reason, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["source_ip"],
                    payload["source_port"],
                    payload["attack_type"],
                    payload["risk_level"],
                    payload.get("hit_count", 1),
                    payload.get("first_seen_at", now),
                    now,
                    payload.get("status", "active"),
                    payload["reason"],
                    payload.get("created_by", "system"),
                ),
            )
            connection.commit()
            row = connection.execute("SELECT * FROM blacklist WHERE id = ?", (cursor.lastrowid,)).fetchone()

    return dict(row)


def list_blacklist(db_path: Optional[Path] = None) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT * FROM blacklist ORDER BY last_seen_at DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def delete_blacklist_entry(entry_id: int, db_path: Optional[Path] = None) -> bool:
    with get_connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM blacklist WHERE id = ?", (entry_id,))
        connection.commit()
        return cursor.rowcount > 0


def list_alerts(limit: int = 50, db_path: Optional[Path] = None) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT * FROM alerts ORDER BY created_at DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_dashboard_summary(db_path: Optional[Path] = None) -> dict[str, Any]:
    with get_connection(db_path) as connection:
        summary = {}
        summary["total_predictions"] = int(connection.execute("SELECT COUNT(*) FROM predictions").fetchone()[0])
        summary["malicious_predictions"] = int(
            connection.execute("SELECT COUNT(*) FROM predictions WHERE predicted_label != 'benign'").fetchone()[0]
        )
        summary["benign_predictions"] = int(
            connection.execute("SELECT COUNT(*) FROM predictions WHERE predicted_label = 'benign'").fetchone()[0]
        )
        summary["open_alerts"] = int(connection.execute("SELECT COUNT(*) FROM alerts WHERE status = 'open'").fetchone()[0])
        summary["blacklist_count"] = int(connection.execute("SELECT COUNT(*) FROM blacklist").fetchone()[0])
        replay_state = connection.execute("SELECT is_running FROM replay_state WHERE id = 1").fetchone()
        summary["replay_running"] = bool(replay_state["is_running"]) if replay_state else False
        return summary


def get_dashboard_trends(db_path: Optional[Path] = None) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT substr(created_at, 1, 13) AS bucket, predicted_label AS label, COUNT(*) AS count
            FROM predictions
            GROUP BY bucket, label
            ORDER BY bucket ASC, label ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def get_dashboard_top_sources(limit: int = 5, db_path: Optional[Path] = None) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT source_ip, predicted_label AS attack_type, COUNT(*) AS hit_count,
                   MAX(confidence) AS max_confidence
            FROM predictions
            WHERE predicted_label != 'benign'
            GROUP BY source_ip, predicted_label
            ORDER BY hit_count DESC, max_confidence DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def start_replay(stage_order: int = 1, db_path: Optional[Path] = None) -> dict[str, Any]:
    manifest = json.loads(settings.replay_manifest_path.read_text(encoding="utf-8"))
    stage = next((item for item in manifest["stages"] if item["order"] == stage_order), manifest["stages"][0])
    progress = round(stage["order"] / len(manifest["stages"]), 2)

    with get_connection(db_path) as connection:
        connection.execute(
            """
            UPDATE replay_state
            SET is_running = 1, current_stage = ?, current_label = ?, progress = ?, updated_at = ?
            WHERE id = 1
            """,
            (stage["order"], stage["label"], progress, _utcnow()),
        )
        connection.commit()

    return get_replay_status(db_path)


def get_replay_status(db_path: Optional[Path] = None) -> dict[str, Any]:
    manifest = json.loads(settings.replay_manifest_path.read_text(encoding="utf-8"))
    with get_connection(db_path) as connection:
        row = connection.execute("SELECT * FROM replay_state WHERE id = 1").fetchone()
        state = dict(row) if row else {
            "is_running": 0,
            "current_stage": 0,
            "current_label": manifest["stages"][0]["label"],
            "progress": 0.0,
            "updated_at": _utcnow(),
        }
        state["is_running"] = bool(state["is_running"])
        state["stages"] = manifest["stages"]
        state["name"] = manifest["name"]
        return state
