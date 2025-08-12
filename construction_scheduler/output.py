from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


def save_gantt(df: pd.DataFrame, output_path: str | Path):
    """Save a simple Gantt chart from schedule DataFrame."""
    fig, ax = plt.subplots(figsize=(12, 6))

    df_sorted = df.sort_values("start")
    y_pos = range(len(df_sorted))

    for idx, row in enumerate(df_sorted.itertuples(index=False)):
        start = mdates.date2num(row.start)
        end = mdates.date2num(row.end)
        ax.barh(
            y=idx,
            width=end - start,
            left=start,
            height=0.4,
            align="center",
        )
        ax.text(end, idx, f" {row.name}", va="center", fontsize=8)

    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(df_sorted["task_id"].tolist())
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))

    plt.tight_layout()
    output_path = Path(output_path)
    fig.savefig(output_path)
    plt.close(fig)