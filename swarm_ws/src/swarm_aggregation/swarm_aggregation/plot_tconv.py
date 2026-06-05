import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot TP7 tconv(N) with error bars.")
    parser.add_argument("summary_csv", help="CSV with columns N,run,tconv")
    parser.add_argument("--output", default="tconv_by_n.png")
    args = parser.parse_args()

    grouped: dict[int, list[float]] = defaultdict(list)
    with Path(args.summary_csv).open("r", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            if row["tconv"].strip().lower() in {"", "nan", "not_reached"}:
                continue
            grouped[int(row["N"])].append(float(row["tconv"]))

    if not grouped:
        raise SystemExit("No finite tconv values found.")

    ns = sorted(grouped)
    means = [float(np.mean(grouped[n])) for n in ns]
    stds = [float(np.std(grouped[n])) for n in ns]
    plt.figure(figsize=(7, 4))
    plt.errorbar(ns, means, yerr=stds, marker="o", capsize=4)
    plt.xlabel("Swarm size N")
    plt.ylabel("Convergence time tconv (s)")
    plt.title("TP7 convergence time versus swarm size")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(args.output, dpi=150)
    print(f"Wrote {args.output}")
