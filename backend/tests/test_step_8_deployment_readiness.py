from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_step_8_deployment_templates_exist() -> None:
    required_files = [
        "deploy/nginx/malicious-traffic.conf",
        "deploy/systemd/malicious-traffic-backend.service",
        "deploy/docker/docker-compose.yml",
        "deploy/ubuntu/backend.env.example",
        "deploy/ubuntu/deploy_backend.sh",
        "deploy/ubuntu/deploy_frontend.sh",
        "docs/deployment/README.md",
    ]

    missing = [path for path in required_files if not (PROJECT_ROOT / path).is_file()]
    assert not missing, f"Missing deployment assets: {missing}"


def test_step_8_deployment_docs_reference_core_assets() -> None:
    deployment_doc = (PROJECT_ROOT / "docs/deployment/README.md").read_text(encoding="utf-8")

    assert "malicious-traffic.conf" in deployment_doc
    assert "malicious-traffic-backend.service" in deployment_doc
    assert "deploy_backend.sh" in deployment_doc
    assert "deploy_frontend.sh" in deployment_doc
