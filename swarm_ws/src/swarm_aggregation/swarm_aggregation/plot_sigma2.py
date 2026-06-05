from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    csv_path = Path("sigma2.csv")
    output_path = Path("sigma2.png")
    df = pd.read_csv(csv_path)
    plt.figure(figsize=(7, 4))
    plt.plot(df["t"], df["sigma2"], linewidth=1.5)
    plt.axhline(1.0, linestyle="--", color="red", label="sigma2 threshold")
    plt.xlabel("Time (s)")
    plt.ylabel("sigma2 (m^2)")
    plt.title("Swarm Aggregation Convergence")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Wrote {output_path}")
