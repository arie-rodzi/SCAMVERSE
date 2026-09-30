"""Runtime benchmark for the SCAMVERSE analysis engine.

Replicates the synthetic demonstration transcript to reach target corpus sizes and
reports the median of five runs of analyze_text() for each size.

    python examples/benchmark.py
"""
import os
import platform
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modules.engine import analyze_text  # noqa: E402

BASE = (Path(__file__).parent / "demo_transcript.txt").read_text(encoding="utf-8")
TARGETS = [1_000, 10_000, 50_000, 100_000, 250_000]


def main(runs: int = 5):
    words_per_copy = len(BASE.split())
    print(f"Python {platform.python_version()} | {platform.machine()} | {os.cpu_count()} logical CPUs")
    print("words\tmedian_s\tmin_s\tmax_s")
    for target in TARGETS:
        text = "\n".join([BASE] * max(1, round(target / words_per_copy)))
        times = []
        for _ in range(runs):
            t0 = time.perf_counter()
            analyze_text(text)
            times.append(time.perf_counter() - t0)
        print(f"{len(text.split())}\t{statistics.median(times):.3f}\t{min(times):.3f}\t{max(times):.3f}")


if __name__ == "__main__":
    main()
