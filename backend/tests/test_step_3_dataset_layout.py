import csv
import json

from conftest import PROJECT_ROOT


EXPECTED_LABEL_MAP = {
    "benign": 0,
    "arp_spoof": 1,
    "ddos": 2,
    "trojan": 3,
}

EXPECTED_SAMPLE_FILES = {
    "benign": "ml/data/sample/sample_features_benign.csv",
    "arp_spoof": "ml/data/sample/sample_features_arp_spoof.csv",
    "ddos": "ml/data/sample/sample_features_ddos.csv",
    "trojan": "ml/data/sample/sample_features_trojan.csv",
}

REQUIRED_SAMPLE_COLUMNS = {
    "flow_id",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "packet_len_mean",
    "packet_len_max",
    "packet_len_min",
    "packet_len_std",
    "packets_per_sec",
    "bytes_per_sec",
    "flow_duration",
    "label",
}


def test_step_3_label_map_is_stable() -> None:
    label_map_path = PROJECT_ROOT / "ml/configs/label_map.json"
    assert label_map_path.is_file(), "label_map.json is missing"

    label_map = json.loads(label_map_path.read_text(encoding="utf-8"))
    assert label_map == EXPECTED_LABEL_MAP


def test_step_3_dataset_docs_and_manifests_exist() -> None:
    required_paths = [
        "ml/data/README.md",
        "ml/data/raw/README.md",
        "ml/data/interim/README.md",
        "ml/data/processed/README.md",
        "ml/data/sample/README.md",
        "docs/dataset/README.md",
        "ml/data/sample/sample_sources_manifest.json",
        "ml/data/sample/replay_manifest.json",
    ]

    missing = [path for path in required_paths if not (PROJECT_ROOT / path).is_file()]
    assert not missing, f"Missing dataset docs or manifests: {missing}"


def test_step_3_source_manifest_covers_all_labels() -> None:
    manifest_path = PROJECT_ROOT / "ml/data/sample/sample_sources_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    labels = {entry["label"] for entry in manifest["labels"]}
    assert labels == set(EXPECTED_LABEL_MAP)

    for entry in manifest["labels"]:
        assert entry["primary_sources"], f"No sources declared for {entry['label']}"
        assert entry["notes"].strip(), f"No notes declared for {entry['label']}"


def test_step_3_replay_manifest_references_expected_labels() -> None:
    manifest_path = PROJECT_ROOT / "ml/data/sample/replay_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    stages = manifest["stages"]
    assert [stage["order"] for stage in stages] == [1, 2, 3, 4]
    assert {stage["label"] for stage in stages} == set(EXPECTED_LABEL_MAP)


def test_step_3_sample_feature_files_match_label_policy() -> None:
    for label, relative_path in EXPECTED_SAMPLE_FILES.items():
        sample_path = PROJECT_ROOT / relative_path
        assert sample_path.is_file(), f"Missing sample file for {label}: {relative_path}"

        with sample_path.open("r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            assert reader.fieldnames is not None, f"No header found in {relative_path}"
            assert REQUIRED_SAMPLE_COLUMNS.issubset(reader.fieldnames)

            rows = list(reader)
            assert rows, f"No sample rows found in {relative_path}"
            assert all(row["label"] == label for row in rows)
