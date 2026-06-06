from __future__ import annotations

from typing import Any, Optional

from app.schemas.monitor import SimulationRunRequest, SiteTargetRequest, TrafficObservationRequest
from app.services.monitor_service import ingest_observation, set_site_target


SCENARIOS: dict[str, dict[str, Any]] = {
    "normal_visit": {
        "label": "benign",
        "title": "正常访问",
        "description": "模拟普通用户浏览网页、加载静态资源和短连接访问。",
        "base": {
            "source_ip": "198.51.100.21",
            "source_port": 51514,
            "packet_len_mean": 612.5,
            "packet_len_max": 1514,
            "packet_len_min": 64,
            "packet_len_std": 228.2,
            "packets_per_sec": 18.4,
            "bytes_per_sec": 11270.5,
            "flow_duration": 12.5,
        },
    },
    "http_flood": {
        "label": "ddos",
        "title": "HTTP 洪泛",
        "description": "模拟大量短连接请求造成的突发流量窗口，默认只生成模型观测事件。",
        "base": {
            "source_ip": "198.51.100.200",
            "source_port": 42350,
            "packet_len_mean": 128.4,
            "packet_len_max": 512,
            "packet_len_min": 60,
            "packet_len_std": 44.7,
            "packets_per_sec": 1420.6,
            "bytes_per_sec": 182530.0,
            "flow_duration": 3.2,
        },
    },
    "suspicious_c2": {
        "label": "trojan",
        "title": "疑似木马通信",
        "description": "模拟低频、持续时间较长、包长波动明显的命令控制通信特征。",
        "base": {
            "source_ip": "198.51.100.88",
            "source_port": 50344,
            "packet_len_mean": 246.1,
            "packet_len_max": 890,
            "packet_len_min": 54,
            "packet_len_std": 120.6,
            "packets_per_sec": 32.5,
            "bytes_per_sec": 7998.3,
            "flow_duration": 18.7,
        },
    },
    "arp_spoof_lab": {
        "label": "arp_spoof",
        "title": "实验室 ARP 欺骗",
        "description": "仅用于隔离实验网段的二层攻击特征演示，不适合作为公网网站攻击验证。",
        "base": {
            "source_ip": "198.51.100.66",
            "source_port": 0,
            "packet_len_mean": 58.0,
            "packet_len_max": 60,
            "packet_len_min": 42,
            "packet_len_std": 5.8,
            "packets_per_sec": 96.0,
            "bytes_per_sec": 5568.0,
            "flow_duration": 4.0,
        },
    },
}


def list_scenarios() -> list[dict[str, str]]:
    return [
        {
            "id": key,
            "label": value["label"],
            "title": value["title"],
            "description": value["description"],
        }
        for key, value in SCENARIOS.items()
    ]


def _vary(value: float, index: int, ratio: float = 0.025) -> float:
    offset = ((index % 5) - 2) * ratio
    return round(value * (1 + offset), 4)


def _source_ip(base_ip: str, index: int, override: Optional[str]) -> str:
    if override:
        return override
    parts = base_ip.split(".")
    if len(parts) == 4 and parts[-1].isdigit():
        parts[-1] = str(min(254, max(1, int(parts[-1]) + index)))
        return ".".join(parts)
    return base_ip


def run_simulation(request: SimulationRunRequest) -> dict[str, Any]:
    if request.scenario not in SCENARIOS:
        raise ValueError(f"Unsupported simulation scenario: {request.scenario}")

    target_id = request.target_id
    if request.target:
        target = set_site_target(SiteTargetRequest(target=request.target, scheme=request.scheme, port=request.port))
        target_id = int(target["id"])

    scenario = SCENARIOS[request.scenario]
    base = scenario["base"]
    events = []
    for index in range(request.count):
        observation = TrafficObservationRequest(
            target_id=target_id,
            source_ip=_source_ip(base["source_ip"], index, request.source_ip),
            source_port=int(base["source_port"]) + index,
            scenario=request.scenario,
            request_count=1,
            packet_len_mean=_vary(float(base["packet_len_mean"]), index),
            packet_len_max=_vary(float(base["packet_len_max"]), index),
            packet_len_min=_vary(float(base["packet_len_min"]), index),
            packet_len_std=_vary(float(base["packet_len_std"]), index),
            packets_per_sec=_vary(float(base["packets_per_sec"]), index),
            bytes_per_sec=_vary(float(base["bytes_per_sec"]), index),
            flow_duration=max(0.1, _vary(float(base["flow_duration"]), index)),
            model_name=request.model_name,
        )
        events.append(ingest_observation(observation))

    return {
        "scenario": request.scenario,
        "expected_label": scenario["label"],
        "count": len(events),
        "events": events,
    }
