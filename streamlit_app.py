import streamlit as st
import json
import pandas as pd
import plotly.express as px

# Load the JSON data
with open("hyrox_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert the JSON data to a DataFrame
df = pd.json_normalize(data)

# Ensure the 'Rank' column is numeric
df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")

# Define the correct order of splits
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


# Create a function to map split labels to the correct order
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


# Convert to DataFrame and add placeholders for missing splits
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


# Convert time strings to seconds for comparison
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


splits_df["SplitTimeInSeconds"] = splits_df["SplitTime"].apply(convert_time_to_seconds)


# Normalize club names
def normalize_club_name(club: str) -> str:
    normalization_map = {
        "CFR": "CFR",
        "CFRVK": "CFR",
        "CfRvk": "CFR",
        "CrossFit Reykjavík": "CFR",
        "Cfr": "CFR",
        "CF RVK": "CFR",
        "Crossfit Reykjavík": "CFR",
        "Crossfit Reykjavik": "CFR",
        "Cfrvk": "CFR",
        "CF RVK": "CFR",
        "cfr": "CFR",
    }
    return normalization_map.get(club, club)


# Add normalized club names
df["NormalizedClubs"] = df["Club"].apply(
    lambda clubs: [normalize_club_name(club) for club in clubs]
)

# Explode the DataFrame for club visualization
exploded_df = df.explode("NormalizedClubs")

# Get the list of categories
categories = df["Category"].unique()

# Define the navigation sidebar
st.sidebar.title("Hyrox Results Visualization")
page = st.sidebar.selectbox("Choose a chart", ["Split Comparison", "Club Winners"])


# Function to render the split comparison chart
def render_split_comparison():
    selected_category = st.selectbox("Select a category", categories)

    filtered_df = df[df["Category"] == selected_category]
    filtered_teams = filtered_df["Team"].unique()

    st.write(f"Results for {selected_category}")
    st.dataframe(
        filtered_df[["Rank", "BIB", "Team", "Members", "Club", "Time", "Category"]]
    )

    filtered_splits_df = splits_df[splits_df["Team"].isin(filtered_teams)]

    if not filtered_splits_df.empty:
        st.write(f"Split Comparison for Teams in {selected_category}")
        fig = px.bar(
            filtered_splits_df,
            x="SplitLabel",
            y="SplitTimeInSeconds",
            color="Team",
            barmode="group",
            title=f"Split Comparison for {selected_category}",
            labels={"SplitLabel": "Split", "SplitTimeInSeconds": "Time (seconds)"},
            hover_name="Team",
            hover_data={"SplitTimeInSeconds": True},
        )

        fig.update_layout(
            xaxis={"categoryorder": "array", "categoryarray": split_order}
        )
        st.plotly_chart(fig)
    else:
        st.write("No data available for the selected category.")


# Function to render the club winners chart
def render_club_winners():
    selected_category = st.selectbox("Select a category", categories)

    club_winners_df = exploded_df[exploded_df["Category"] == selected_category]

    if not club_winners_df.empty:
        st.write(f"Club Winners for {selected_category}")
        club_winners_chart = px.bar(
            club_winners_df,
            x="NormalizedClubs",
            y="Rank",
            color="NormalizedClubs",
            title=f"Club Winners for {selected_category}",
            labels={"NormalizedClubs": "Club", "Rank": "Rank"},
            hover_name="Team",
            hover_data={"Rank": True, "Team": True},
        )
        st.plotly_chart(club_winners_chart)
    else:
        st.write("No data available for the selected category.")


# Render the selected page
if page == "Split Comparison":
    render_split_comparison()
elif page == "Club Winners":
    render_club_winners()
