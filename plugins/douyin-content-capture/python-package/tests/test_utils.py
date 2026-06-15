from pathlib import Path

from douyin_capture.utils import build_output_dir, build_transcript_preview, sanitize_filename


def test_sanitize_filename_keeps_short_cjk_slug() -> None:
    assert sanitize_filename("这是 一个 Douyin 标题!!!") == "这是-一个-douyin-标题"


def test_build_output_dir_uses_aweme_id_prefix() -> None:
    output_dir = build_output_dir(Path("/tmp/out"), "123", "test title")
    assert output_dir == Path("/tmp/out/123-test-title")


def test_build_transcript_preview_truncates() -> None:
    preview = build_transcript_preview("a" * 205)
    assert preview.endswith("...")
    assert len(preview) == 203

