import argparse
from pathlib import Path

from construction_scheduler.dpr_parser import load_dpr
from construction_scheduler.schedule import Schedule
from construction_scheduler.output import save_gantt


def main():
    parser = argparse.ArgumentParser(
        description="Construction Schedule Generator based on DPR updates",
    )
    parser.add_argument("tasks_yaml", help="Path to tasks YAML definition file")
    parser.add_argument(
        "--dpr",
        help="Path to DPR update file (csv/json). If provided, progress will be merged (feature under development).",
    )
    parser.add_argument(
        "--output-image",
        default="schedule_gantt.png",
        help="Filename for Gantt chart PNG (default: schedule_gantt.png)",
    )
    args = parser.parse_args()

    schedule = Schedule.from_yaml(args.tasks_yaml)
    df_sched = schedule.to_dataframe()

    # TODO: integrate DPR updates into schedule adjustments
    if args.dpr:
        dpr_df = load_dpr(args.dpr)
        print("Loaded DPR updates (progress %, not yet applied):")
        print(dpr_df.head())

    print("Planned Schedule:")
    print(df_sched)

    save_gantt(df_sched, args.output_image)
    print(f"Gantt chart saved to {args.output_image}")


if __name__ == "__main__":
    main()