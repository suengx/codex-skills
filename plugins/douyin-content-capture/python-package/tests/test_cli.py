from douyin_capture import cli


def test_build_parser_supports_extract_flag() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(["extract", "https://v.douyin.com/abc", "--skip-transcribe"])
    assert args.command == "extract"
    assert args.skip_transcribe is True


def test_build_parser_supports_doctor_json_flag() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(["doctor", "--json"])
    assert args.command == "doctor"
    assert args.json is True
