from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_step_10_presentation_files_exist() -> None:
    required_files = [
        "ppt/final_ppt_content.md",
        "ppt/script/presentation_outline.md",
        "ppt/script/presentation_speech.md",
        "ppt/script/slide_copy.md",
        "ppt/script/defense_qa.md",
        "docs/report/executive_summary.md",
    ]

    missing = [path for path in required_files if not (PROJECT_ROOT / path).is_file()]
    assert not missing, f"Missing presentation deliverables: {missing}"


def test_step_10_outline_and_speech_cover_core_topics() -> None:
    outline = (PROJECT_ROOT / "ppt/script/presentation_outline.md").read_text(encoding="utf-8")
    speech = (PROJECT_ROOT / "ppt/script/presentation_speech.md").read_text(encoding="utf-8")

    required_keywords = [
        "恶意流量识别",
        "ARP",
        "DDoS",
        "木马",
        "黑名单",
        "随机森林",
        "Ubuntu",
        "前端",
        "后端",
    ]

    for keyword in required_keywords:
        assert keyword in outline
        assert keyword in speech
