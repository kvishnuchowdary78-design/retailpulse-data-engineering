
import json
import subprocess

import pytest

from scripts import run_pipeline


def test_pipeline_success_records_all_stages(monkeypatch):
    calls = []

    def fake_run(command, cwd, env, check):
        calls.append(command)

    monkeypatch.setattr(
        run_pipeline.subprocess,
        "run",
        fake_run,
    )

    run_pipeline.main()

    report_path = (
        run_pipeline.Path(__file__).resolve().parents[1]
        / "outputs"
        / "pipeline_report.json"
    )

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    assert report["status"] == "SUCCESS"
    assert report["successful_steps"] == 6
    assert report["total_steps"] == 6
    assert report["failed_step"] is None
    assert len(calls) == 6


def test_pipeline_failure_records_failed_stage_and_exits(
    monkeypatch,
):
    calls = []

    def fake_run(command, cwd, env, check):
        calls.append(command)

        if "scripts.run_transformation" in command:
            raise subprocess.CalledProcessError(
                returncode=2,
                cmd=command,
            )

    monkeypatch.setattr(
        run_pipeline.subprocess,
        "run",
        fake_run,
    )

    with pytest.raises(SystemExit) as error:
        run_pipeline.main()

    assert error.value.code == 1

    report_path = (
        run_pipeline.Path(__file__).resolve().parents[1]
        / "outputs"
        / "pipeline_report.json"
    )

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    assert report["status"] == "FAILED"
    assert report["failed_step"] == "TRANSFORMATION"
    assert report["successful_steps"] == 2
    assert report["total_steps"] == 6
    assert report["completed_steps"] == [
        "INGESTION",
        "VALIDATION",
    ]
    assert len(calls) == 3
