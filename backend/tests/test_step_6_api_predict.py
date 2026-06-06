def test_step_6_dashboard_contracts_return_seeded_data(api_client) -> None:
    summary_response = api_client.get("/api/v1/dashboard/summary")
    trends_response = api_client.get("/api/v1/dashboard/trends")
    top_sources_response = api_client.get("/api/v1/dashboard/top-sources")
    metrics_response = api_client.get("/api/v1/metrics/summary")
    settings_response = api_client.get("/api/v1/settings")

    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["total_predictions"] >= 1
    assert summary["blacklist_count"] >= 1
    assert "replay_running" in summary

    assert trends_response.status_code == 200
    assert trends_response.json()["items"]

    assert top_sources_response.status_code == 200
    assert top_sources_response.json()["items"]

    assert metrics_response.status_code == 200
    metrics = metrics_response.json()
    assert "models" in metrics
    assert "feature_importance" in metrics

    assert settings_response.status_code == 200
    config = settings_response.json()
    assert config["default_model_name"]
    assert config["supported_models"]


def test_step_6_predict_creates_alert_and_blacklist_after_repeated_hits(api_client) -> None:
    payload = {
        "source_ip": "10.10.0.200",
        "destination_ip": "172.16.0.99",
        "source_port": 43111,
        "destination_port": 80,
        "packet_len_mean": 132.6,
        "packet_len_max": 526.0,
        "packet_len_min": 60.0,
        "packet_len_std": 45.0,
        "packets_per_sec": 1490.4,
        "bytes_per_sec": 194880.0,
        "flow_duration": 3.1,
        "model_name": "random_forest",
    }

    first = api_client.post("/api/v1/predict", json=payload)
    second = api_client.post("/api/v1/predict", json=payload)

    assert first.status_code == 200, first.json()
    assert second.status_code == 200, second.json()

    first_json = first.json()
    second_json = second.json()
    assert first_json["predicted_label"] == "ddos"
    assert first_json["alert_created"] is True
    assert first_json["blacklist_action"] in {"candidate", "upserted"}
    assert second_json["blacklist_action"] == "upserted"

    alerts = api_client.get("/api/v1/alerts").json()["items"]
    assert any(alert["source_ip"] == payload["source_ip"] for alert in alerts)

    blacklist = api_client.get("/api/v1/blacklist").json()["items"]
    assert any(item["source_ip"] == payload["source_ip"] and item["attack_type"] == "ddos" for item in blacklist)


def test_step_6_blacklist_manual_crud_and_replay_status(api_client) -> None:
    create_response = api_client.post(
        "/api/v1/blacklist",
        json={
            "source_ip": "192.168.55.2",
            "source_port": 4040,
            "attack_type": "trojan",
            "risk_level": "medium",
            "reason": "Manual verification during demo.",
            "created_by": "tester",
        },
    )
    assert create_response.status_code == 201
    created_item = create_response.json()["item"]
    assert created_item["source_ip"] == "192.168.55.2"

    start_response = api_client.post("/api/v1/replay/start", json={"stage_order": 2})
    status_response = api_client.get("/api/v1/replay/status")
    assert start_response.status_code == 200
    assert status_response.status_code == 200
    assert status_response.json()["is_running"] is True
    assert status_response.json()["current_stage"] == 2
    assert status_response.json()["stages"]

    delete_response = api_client.delete(f"/api/v1/blacklist/{created_item['id']}")
    assert delete_response.status_code == 204

    blacklist = api_client.get("/api/v1/blacklist").json()["items"]
    assert all(item["id"] != created_item["id"] for item in blacklist)
