import pandas as pd
import json


def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.json_normalize(data)


def normalize_club_name(club: str) -> str:
    normalization_map = {
        "CFR": "CFR",
        "CFRVK": "CFR",
        "CfRvk": "CFR",
        "CrossFit Reykjavík": "CFR",
        "crossfit reykjavík": "CFR",
        "Cfr": "CFR",
        "CF RVK": "CFR",
        "Crossfit Reykjavík": "CFR",
        "Crossfit Reykjavik": "CFR",
        "Cfrvk": "CFR",
        "cfr": "CFR",
        "Mjönir:": "Mjönir",
        "World Class": "WorldClass",
        "Worldfit": "WorldFit",
        "Grandi101": "Grandi 101",
        "ULTRA form": "Ultraform",
    }
    return normalization_map.get(club, club)


def map_split_labels(splits):
    split_counts = {"Hlaup": 0}
    mapped_splits = []

    for split in splits:
        label = split["label"]
        if "Hlaup" in label:
            split_counts["Hlaup"] += 1
            label = f'Hlaup {split_counts["Hlaup"]}'
        mapped_splits.append({"label": label, "time": split["time"]})

    return mapped_splits


def convert_time_to_seconds(time_str):
    try:
        parts = time_str.split(":")
        if len(parts) == 3:
            h, m, s = map(int, parts)
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m, s = map(int, parts)
            return m * 60 + s
        else:
            return float("inf")
    except Exception as e:
        print(f"Error converting time: {time_str} - {e}")
        return float("inf")


split_order = [
    "Hlaup 1",
    "Ski-Erg",
    "Hlaup 2",
    "Ýta sleða",
    "Hlaup 3",
    "Draga sleða",
    "Hlaup 4",
    "Burpee langstökk",
    "Hlaup 5",
    "Róður",
    "Hlaup 6",
    "Bændaganga",
    "Hlaup 7",
    "Dumbell lovers",
    "Hlaup 8",
    "Wall Balls",
]


def process_data(df):
    df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
    df["NormalizedClubs"] = df["Club"].apply(
        lambda clubs: [normalize_club_name(club) for club in clubs]
    )

    split_records = []
    for index, row in df.iterrows():
        team_splits = {
            split["label"]: split["time"] for split in map_split_labels(row["Splits"])
        }

        for split_label in split_order:
            split_records.append(
                {
                    "Team": row["Team"],
                    "SplitLabel": split_label,
                    "SplitTime": team_splits.get(split_label, "00:00"),
                    "Order": split_order.index(split_label),
                }
            )

    splits_df = pd.DataFrame(split_records)
    splits_df["SplitTimeInSeconds"] = splits_df["SplitTime"].apply(
        convert_time_to_seconds
    )

    exploded_df = df.explode("NormalizedClubs")

    def calculate_points(rank):
        return 1 / rank

    exploded_df["Points"] = exploded_df["Rank"].apply(calculate_points)

    club_stats = (
        exploded_df.groupby("NormalizedClubs")["Points"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "TotalPoints", "count": "TeamCount"})
    )

    club_stats["AveragePoints"] = club_stats["TotalPoints"] / club_stats["TeamCount"]
    club_stats = club_stats.sort_values(
        by=["TotalPoints", "AveragePoints"], ascending=False
    )

    return df, splits_df, club_stats


def calculate_overall_performance(df):
    df["AverageTimeInSeconds"] = df["Time"].apply(convert_time_to_seconds)
    overall_performance = (
        df.groupby("Team")["AverageTimeInSeconds"].mean().reset_index()
    )
    overall_performance["TotalTime"] = overall_performance[
        "AverageTimeInSeconds"
    ].apply(lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02}")
    return overall_performance
