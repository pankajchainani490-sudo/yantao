#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


SCENARIOS = ("normal_visit", "http_flood", "suspicious_c2", "arp_spoof_lab")


def parse_target(raw: str) -> dict[str, Any]:
    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    scheme = parsed.scheme or "https"
    host = parsed.hostname or raw
    port = parsed.port or (443 if scheme == "https" else 80)
    target_url = f"{scheme}://{host}"
    if (scheme == "https" and port != 443) or (scheme == "http" and port != 80):
        target_url = f"{target_url}:{port}"
    return {
        "target": host,
        "scheme": scheme,
        "port": port,
        "target_url": target_url,
    }


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(url: str) -> dict[str, Any]:
    with urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def put_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def send_bounded_http_probe(target_url: str, count: int, delay: float) -> None:
    safe_count = min(count, 20)
    for index in range(safe_count):
        request = Request(
            target_url,
            headers={
                "User-Agent": "YantaoSecuritySimulator/1.0 controlled-validation",
                "X-Simulator-Event": str(index + 1),
            },
        )
        try:
            with urlopen(request, timeout=3) as response:
                response.read(256)
                print(f"[http] {index + 1}/{safe_count} status={response.status}")
        except URLError as error:
            print(f"[http] {index + 1}/{safe_count} request failed: {error}")
        time.sleep(max(delay, 0.2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate controlled traffic-observation events for the malicious traffic dashboard. "
            "By default this does not attack the target; it submits simulated telemetry to the backend."
        )
    )
    parser.add_argument("--backend", default="http://127.0.0.1:8000", help="FastAPI backend base URL.")
    parser.add_argument("--target", default=None, help="Your authorized website domain, IP, or URL.")
    parser.add_argument("--target-id", type=int, default=None, help="Existing monitor target id to receive events.")
    parser.add_argument(
        "--localhost-port",
        type=int,
        default=None,
        help="Add or reuse http://localhost:<port> as the monitor target.",
    )
    parser.add_argument("--scenario", choices=SCENARIOS, default="http_flood", help="Simulation scenario.")
    parser.add_argument("--count", type=int, default=5, help="Observation events to generate, capped by backend at 50.")
    parser.add_argument("--source-ip", default=None, help="Optional simulated source IP.")
    parser.add_argument(
        "--send-http",
        action="store_true",
        help="Also send a small number of real HTTP GET requests before submitting telemetry.",
    )
    parser.add_argument(
        "--i-own-this-target",
        action="store_true",
        help="Required with --send-http to confirm the target is yours or explicitly authorized.",
    )
    parser.add_argument("--http-count", type=int, default=5, help="Real HTTP probe requests, hard-capped at 20.")
    parser.add_argument("--http-delay", type=float, default=0.4, help="Delay between real HTTP probe requests.")
    args = parser.parse_args()

    backend = args.backend.rstrip("/")
    target_id = args.target_id
    target_url = None

    if args.localhost_port is not None:
        target = post_json(
            f"{backend}/api/v1/monitor/targets/localhost",
            {
                "port": args.localhost_port,
                "scheme": "http",
                "display_name": f"localhost:{args.localhost_port}",
            },
        )
        target_id = int(target["id"])
        target_url = target["target_url"]
    elif args.target:
        parsed_target = parse_target(args.target)
        target = put_json(
            f"{backend}/api/v1/monitor/target",
            {
                "target": parsed_target["target"],
                "scheme": parsed_target["scheme"],
                "port": parsed_target["port"],
            },
        )
        target_id = int(target["id"])
        target_url = target["target_url"]
    elif target_id is not None:
        target = get_json(f"{backend}/api/v1/monitor/target?target_id={target_id}")
        target_url = target["target_url"]
    else:
        raise SystemExit("Use --localhost-port, --target-id, or --target to choose a monitor object.")

    print(f"[target] id={target_id} url={target_url}")

    if args.send_http:
        if not args.i_own_this_target:
            raise SystemExit("--send-http requires --i-own-this-target for safety.")
        send_bounded_http_probe(target_url, args.http_count, args.http_delay)

    result = post_json(
        f"{backend}/api/v1/simulator/run",
        {
            "target_id": target_id,
            "scenario": args.scenario,
            "count": args.count,
            "source_ip": args.source_ip,
        },
    )
    print(
        "[simulation] "
        f"scenario={result['scenario']} expected={result['expected_label']} events={result['count']}"
    )
    for item in result["events"]:
        event = item["event"]
        prediction = item["prediction"]
        print(
            "[event] "
            f"id={event['id']} source={event['source_ip']} "
            f"predicted={prediction['predicted_label']} confidence={prediction['confidence']}"
        )


if __name__ == "__main__":
    main()
