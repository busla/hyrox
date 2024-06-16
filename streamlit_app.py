import streamlit as st
import json
import pandas as pd
import plotly.express as px

# Load the JSON data
with open("hyrox_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert the JSON data to a DataFrame
df = pd.json_normalize(data)

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
        h, m, s = map(int, time_str.split(":"))
        return h * 3600 + m * 60 + s
    except:
        return float("inf")


# Use the lower of the two total times
df["TotalTimeInSeconds"] = df["Time"].apply(
    lambda x: min(convert_time_to_seconds(x[0]), convert_time_to_seconds(x[1]))
    if x[0] and x[1]
    else (convert_time_to_seconds(x[0]) if x[0] else convert_time_to_seconds(x[1]))
)


# Convert split time to seconds
def convert_split_time_to_seconds(time_str):
    try:
        parts = list(map(int, time_str.split(":")))
        if len(parts) == 3:
            h, m, s = parts
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m, s = parts
            return m * 60 + s
        else:
            return float("inf")
    except Exception as e:
        print(f"Error converting time: {time_str} - {e}")
        return None


splits_df["SplitTimeInSeconds"] = splits_df["SplitTime"].apply(
    convert_split_time_to_seconds
)

# Drop rows with invalid time conversions
splits_df = splits_df.dropna(subset=["SplitTimeInSeconds"])

# Get the list of categories
categories = df["Category"].unique()

# Streamlit app
st.title("Hyrox Results Visualization")

# Select a category
selected_category = st.selectbox("Select a category", categories)

# Filter the DataFrame based on the selected category
filtered_df = df[df["Category"] == selected_category]
filtered_teams = filtered_df["Team"].unique()

# Display the DataFrame
st.write(f"Results for {selected_category}")
st.dataframe(
    filtered_df[["Rank", "BIB", "Team", "Members", "Club", "Time", "Category"]]
)

# Plot the splits comparison
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

    # Ensure the correct order of splits
    fig.update_layout(xaxis={"categoryorder": "array", "categoryarray": split_order})
    st.plotly_chart(fig)
else:
    st.write("No data available for the selected category.")
