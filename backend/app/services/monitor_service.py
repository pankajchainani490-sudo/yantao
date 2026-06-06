from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlparse

from app.db.database import get_connection
from app.schemas.monitor import LocalPortTargetRequest, SiteTargetRequest, TrafficObservationRequest
from app.schemas.prediction import PredictionRequest
from app.services.prediction_service import run_prediction


DEFAULT_TARGET = {
    "target_host": "localhost",
    "scheme": "http",
    "port": 5173,
}


def _utcnow() -> str:
    return datetime.utcnow().isoformat()


def _normalize_scheme(scheme: str) -> str:
    normalized = scheme.strip().lower()
    if normalized not in {"http", "https"}:
        raise ValueError("Target scheme must be http or https")
    return normalized


def _build_target_url(host: str, scheme: str, port: int) -> str:
    target_url = f"{scheme}://{host}"
    if (scheme == "http" and port != 80) or (scheme == "https" and port != 443):
        target_url = f"{target_url}:{port}"
    return target_url


def _normalize_target(target: str, scheme: str = "https", port: int = 443) -> dict[str, Any]:
    raw = target.strip()
    parsed = urlparse(raw if "://" in raw else f"{scheme}://{raw}")
    target_scheme = _normalize_scheme(parsed.scheme or scheme)

    host = parsed.hostname or raw
    if not host:
        raise ValueError("Target host is required")

    normalized_port = parsed.port or port
    target_url = _build_target_url(host, target_scheme, normalized_port)

    return {
        "target_host": host,
        "scheme": target_scheme,
        "port": normalized_port,
        "target_url": target_url,
        "display_name": f"{host}:{normalized_port}",
    }


def _row_to_target(row: Any) -> dict[str, Any]:
    target = dict(row)
    if "is_active" in target:
        target["is_active"] = bool(target["is_active"])
    return target


def _select_target_by_unique(connection: Any, target: dict[str, Any]) -> dict[str, Any]:
    row = connection.execute(
        """
        SELECT * FROM site_targets
        WHERE target_host = ? AND scheme = ? AND port = ?
        """,
        (target["target_host"], target["scheme"], target["port"]),
    ).fetchone()
    if not row:
        raise ValueError("Target was not saved")
    return _row_to_target(row)


def list_site_targets() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM site_targets
            WHERE is_active = 1
            ORDER BY port ASC, id ASC
            """
        ).fetchall()
        return [_row_to_target(row) for row in rows]


def get_site_target(target_id: Optional[int] = None) -> dict[str, Any]:
    with get_connection() as connection:
        if target_id is not None:
            row = connection.execute("SELECT * FROM site_targets WHERE id = ?", (target_id,)).fetchone()
            if not row:
                raise ValueError(f"Target {target_id} does not exist")
            return _row_to_target(row)

        row = connection.execute(
            """
            SELECT * FROM site_targets
            WHERE is_active = 1
            ORDER BY updated_at DESC, id DESC
            LIMIT 1
            """
        ).fetchone()
        if row:
            return _row_to_target(row)

    return {
        "id": 0,
        **DEFAULT_TARGET,
        "target_url": "http://localhost:5173",
        "display_name": "localhost:5173",
        "is_active": True,
        "updated_at": _utcnow(),
    }


def set_site_target(request: SiteTargetRequest) -> dict[str, Any]:
    target = _normalize_target(request.target, request.scheme, request.port)
    updated_at = _utcnow()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO site_targets (
                target_host, scheme, port, target_url, display_name, is_active, updated_at
            ) VALUES (?, ?, ?, ?, ?, 1, ?)
            ON CONFLICT(target_host, scheme, port) DO UPDATE SET
                target_url = excluded.target_url,
                display_name = excluded.display_name,
                is_active = 1,
                updated_at = excluded.updated_at
            """,
            (
                target["target_host"],
                target["scheme"],
                target["port"],
                target["target_url"],
                target["display_name"],
                updated_at,
            ),
        )
        connection.commit()
        return _select_target_by_unique(connection, target)


def add_localhost_target(request: LocalPortTargetRequest) -> dict[str, Any]:
    scheme = _normalize_scheme(request.scheme)
    host = "localhost"
    target = {
        "target_host": host,
        "scheme": scheme,
        "port": request.port,
        "target_url": _build_target_url(host, scheme, request.port),
        "display_name": (request.display_name or f"localhost:{request.port}").strip(),
    }
    updated_at = _utcnow()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO site_targets (
                target_host, scheme, port, target_url, display_name, is_active, updated_at
            ) VALUES (?, ?, ?, ?, ?, 1, ?)
            ON CONFLICT(target_host, scheme, port) DO UPDATE SET
                target_url = excluded.target_url,
                display_name = excluded.display_name,
                is_active = 1,
                updated_at = excluded.updated_at
            """,
            (
                target["target_host"],
                target["scheme"],
                target["port"],
                target["target_url"],
                target["display_name"],
                updated_at,
            ),
        )
        connection.commit()
        return _select_target_by_unique(connection, target)


def ingest_observation(request: TrafficObservationRequest) -> dict[str, Any]:
    target = get_site_target(request.target_id)
    prediction_request = PredictionRequest(
        source_ip=request.source_ip,
        destination_ip=target["target_host"],
        source_port=request.source_port,
        destination_port=int(target["port"]),
        packet_len_mean=request.packet_len_mean,
        packet_len_max=request.packet_len_max,
        packet_len_min=request.packet_len_min,
        packet_len_std=request.packet_len_std,
        packets_per_sec=request.packets_per_sec,
        bytes_per_sec=request.bytes_per_sec,
        flow_duration=request.flow_duration,
        model_name=request.model_name,
    )
    prediction = run_prediction(prediction_request)
    event = create_monitor_event(
        {
            "target_id": target["id"],
            "target_host": target["target_host"],
            "target_url": target["target_url"],
            "source_ip": request.source_ip,
            "source_port": request.source_port,
            "destination_port": target["port"],
            "scenario": request.scenario,
            "request_count": request.request_count,
            "packets_per_sec": request.packets_per_sec,
            "bytes_per_sec": request.bytes_per_sec,
            "flow_duration": request.flow_duration,
            "predicted_label": prediction["predicted_label"],
            "risk_level": prediction["risk_level"],
            "confidence": prediction["confidence"],
            "prediction_id": prediction["prediction_id"],
        }
    )
    return {
        "target": target,
        "event": event,
        "prediction": prediction,
    }


def create_monitor_event(payload: dict[str, Any]) -> dict[str, Any]:
    created_at = payload.get("created_at", _utcnow())
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO traffic_events (
                target_id, target_host, target_url, source_ip, source_port, destination_port,
                scenario, request_count, packets_per_sec, bytes_per_sec, flow_duration,
                predicted_label, risk_level, confidence, prediction_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["target_id"],
                payload["target_host"],
                payload["target_url"],
                payload["source_ip"],
                payload["source_port"],
                payload["destination_port"],
                payload["scenario"],
                payload["request_count"],
                payload["packets_per_sec"],
                payload["bytes_per_sec"],
                payload["flow_duration"],
                payload["predicted_label"],
                payload["risk_level"],
                payload["confidence"],
                payload["prediction_id"],
                created_at,
            ),
        )
        connection.commit()
        row = connection.execute("SELECT * FROM traffic_events WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


def list_monitor_events(
    limit: int = 50,
    target_id: Optional[int] = None,
    target_host: Optional[str] = None,
) -> list[dict[str, Any]]:
    with get_connection() as connection:
        if target_id is not None:
            rows = connection.execute(
                """
                SELECT * FROM traffic_events
                WHERE target_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (target_id, limit),
            ).fetchall()
        elif target_host:
            rows = connection.execute(
                """
                SELECT * FROM traffic_events
                WHERE target_host = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (target_host, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT * FROM traffic_events
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]


def get_monitor_summary(target_id: Optional[int] = None) -> dict[str, Any]:
    target = get_site_target(target_id)
    params = (target["id"],)
    with get_connection() as connection:
        total_events = int(
            connection.execute("SELECT COUNT(*) FROM traffic_events WHERE target_id = ?", params).fetchone()[0]
        )
        malicious_events = int(
            connection.execute(
                "SELECT COUNT(*) FROM traffic_events WHERE target_id = ? AND predicted_label != 'benign'",
                params,
            ).fetchone()[0]
        )
        benign_events = int(
            connection.execute(
                "SELECT COUNT(*) FROM traffic_events WHERE target_id = ? AND predicted_label = 'benign'",
                params,
            ).fetchone()[0]
        )
        open_alerts = int(
            connection.execute(
                """
                SELECT COUNT(*)
                FROM alerts
                JOIN traffic_events ON traffic_events.prediction_id = alerts.prediction_id
                WHERE alerts.status = 'open' AND traffic_events.target_id = ?
                """,
                params,
            ).fetchone()[0]
        )
        latest_row = connection.execute(
            """
            SELECT created_at
            FROM traffic_events
            WHERE target_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            params,
        ).fetchone()
        attack_rows = connection.execute(
            """
            SELECT predicted_label AS label, COUNT(*) AS count
            FROM traffic_events
            WHERE target_id = ? AND predicted_label != 'benign'
            GROUP BY predicted_label
            ORDER BY count DESC, predicted_label ASC
            """,
            params,
        ).fetchall()
        source_rows = connection.execute(
            """
            SELECT source_ip, predicted_label AS attack_type, COUNT(*) AS hit_count,
                   MAX(confidence) AS max_confidence
            FROM traffic_events
            WHERE target_id = ? AND predicted_label != 'benign'
            GROUP BY source_ip, predicted_label
            ORDER BY hit_count DESC, max_confidence DESC
            LIMIT 5
            """,
            params,
        ).fetchall()

    return {
        "target": target,
        "total_events": total_events,
        "malicious_events": malicious_events,
        "benign_events": benign_events,
        "open_alerts": open_alerts,
        "latest_event_at": latest_row["created_at"] if latest_row else None,
        "attack_counts": [dict(row) for row in attack_rows],
        "top_sources": [dict(row) for row in source_rows],
    }
