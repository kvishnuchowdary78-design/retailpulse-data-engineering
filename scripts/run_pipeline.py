
from pathlib import Path
import subprocess
import sys
import os
import json
import time

from datetime import datetime, timezone


def main():
    root = Path(__file__).resolve().parents[1]

    steps = [
        ("INGESTION", "scripts.run_ingestion"),
        ("VALIDATION", "scripts.run_validation"),
        ("TRANSFORMATION", "scripts.run_transformation"),
        ("WAREHOUSE", "scripts.run_warehouse"),
        ("MONITORING", "scripts.run_monitoring"),
        ("ANALYTICS", "scripts.run_analytics"),
    ]

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "src")

    started_at = datetime.now(timezone.utc)
    pipeline_start = time.perf_counter()

    completed_steps = []
    failed_step = None
    stage_durations = {}
    status = "SUCCESS"

    print("\nRETAILPULSE END-TO-END PIPELINE")
    print("=" * 55)
    print(f"Started: {started_at.isoformat()}")

    try:
        for step_name, module_name in steps:
            print(f"\n{'=' * 55}")
            print(f"RUNNING: {step_name}")
            print("=" * 55)

            stage_start = time.perf_counter()

            try:
                subprocess.run(
                    [sys.executable, "-m", module_name],
                    cwd=root,
                    env=environment,
                    check=True
                )

                duration = time.perf_counter() - stage_start
                stage_durations[step_name] = round(duration, 3)

                completed_steps.append(step_name)

                print(f"\n{step_name}: SUCCESS")
                print(f"Execution time: {duration:.3f} seconds")

            except subprocess.CalledProcessError as error:
                duration = time.perf_counter() - stage_start
                stage_durations[step_name] = round(duration, 3)

                failed_step = step_name
                status = "FAILED"

                print(f"\n{step_name}: FAILED")
                print(f"Execution time: {duration:.3f} seconds")
                print(f"Error code: {error.returncode}")

                raise

    except subprocess.CalledProcessError as error:
        print(f"\nPIPELINE FAILED: {error}")

    finally:
        ended_at = datetime.now(timezone.utc)
        total_duration = time.perf_counter() - pipeline_start

        report = {
            "pipeline_name": "RetailPulse",
            "status": status,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "total_duration_seconds": round(total_duration, 3),
            "completed_steps": completed_steps,
            "failed_step": failed_step,
            "total_steps": len(steps),
            "successful_steps": len(completed_steps),
            "stage_durations_seconds": stage_durations,
        }

        output_dir = root / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(
            output_dir / "pipeline_report.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(report, file, indent=4)

        print("\nPIPELINE SUMMARY")
        print("=" * 55)
        print(f"Status: {status}")
        print(
            f"Completed steps: "
            f"{len(completed_steps)}/{len(steps)}"
        )
        print(f"Total execution time: {total_duration:.3f} seconds")

        print("\nSTAGE EXECUTION TIMES")
        for stage, duration in stage_durations.items():
            print(f"{stage}: {duration:.3f} seconds")

        if failed_step:
            print(f"Failed stage: {failed_step}")

        print("Report: outputs/pipeline_report.json")


if __name__ == "__main__":
    main()
