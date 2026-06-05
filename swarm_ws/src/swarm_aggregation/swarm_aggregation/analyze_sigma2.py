import argparse
import csv
from pathlib import Path


def load_rows(path: Path) -> list[dict[str, float]]:
    with path.open("r", encoding="utf-8") as file:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(file)]


def convergence_time(rows: list[dict[str, float]], threshold: float, hold_seconds: float) -> float | None:
    for index, row in enumerate(rows):
        if row["sigma2"] >= threshold:
            continue
        end_time = row["t"] + hold_seconds
        window = [candidate for candidate in rows[index:] if candidate["t"] <= end_time]
        if window and window[-1]["t"] >= end_time - 0.6 and all(
            candidate["sigma2"] < threshold for candidate in window
        ):
            return row["t"]
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize TP7 sigma2 convergence.")
    parser.add_argument("csv", nargs="?", default="sigma2.csv")
    parser.add_argument("--threshold", type=float, default=1.0)
    parser.add_argument("--hold-seconds", type=float, default=10.0)
    args = parser.parse_args()

    rows = load_rows(Path(args.csv))
    if not rows:
        raise SystemExit("No sigma2 rows found.")

    values = [row["sigma2"] for row in rows]
    first = rows[0]
    last = rows[-1]
    minimum = min(rows, key=lambda row: row["sigma2"])
    maximum = max(rows, key=lambda row: row["sigma2"])
    tconv = convergence_time(rows, args.threshold, args.hold_seconds)

    print(f"rows={len(rows)}")
    print(f"duration_s={last['t']:.2f}")
    print(f"first_sigma2={first['sigma2']:.4f}")
    print(f"last_sigma2={last['sigma2']:.4f}")
    print(f"min_sigma2={minimum['sigma2']:.4f} at {minimum['t']:.2f}s")
    print(f"max_sigma2={maximum['sigma2']:.4f} at {maximum['t']:.2f}s")
    print(f"mean_sigma2={sum(values) / len(values):.4f}")
    if tconv is None:
        print("tconv=not_reached")
    else:
        print(f"tconv={tconv:.2f}s")
