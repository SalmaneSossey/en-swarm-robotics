import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def label_for(path: Path, explicit_label: str | None, index: int) -> str:
    if explicit_label:
        labels = [label.strip() for label in explicit_label.split(",") if label.strip()]
        if index < len(labels):
            return labels[index]
    return path.stem


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot TP6 fitness and survival metrics.")
    parser.add_argument("csv", nargs="+", help="One or more evaluator CSV files.")
    parser.add_argument("--labels", default=None, help="Comma-separated labels for the input CSV files.")
    parser.add_argument("--output", default="tp6_metrics.png")
    args = parser.parse_args()

    paths = [Path(item) for item in args.csv]
    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

    for index, path in enumerate(paths):
        df = pd.read_csv(path)
        label = label_for(path, args.labels, index)
        axes[0].plot(df["t"], df["mean_center_fitness"], linewidth=1.5, label=label)
        axes[1].plot(df["t"], df["survival_percent"], linewidth=1.5, label=label)

    axes[0].set_ylabel("Mean center fitness (m)")
    axes[0].set_title("TP6 swarm convergence")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Survival (%)")
    axes[1].set_ylim(0, 105)
    axes[1].grid(alpha=0.3)
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(args.output, dpi=150)
    print(f"Wrote {args.output}")
