import streamlit as st
import json
import pandas as pd
import plotly.express as px
import re

# Load the JSON data
with open("hyrox_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert the JSON data to a DataFrame
df = pd.json_normalize(data)

# Extract split times into a DataFrame
split_records = []
all_splits = []
for index, row in df.iterrows():
    for i, split in enumerate(row["Splits"]):
        split_label = split["label"]
        split_records.append(
            {
                "Team": row["Team"],
                "SplitLabel": split_label,
                "SplitTime": split["time"],
            }
        )
        if split_label not in all_splits:
            all_splits.append(split_label)

splits_df = pd.DataFrame(split_records)


# Convert time strings to seconds for comparison
def convert_time_to_seconds(time_str):
    try:
        h, m, s = map(int, time_str.split(":"))
        return h * 3600 + m * 60 + s
    except:
        return None


# Use the lower of the two total times
df["TotalTimeInSeconds"] = df["Time"].apply(
    lambda x: min(convert_time_to_seconds(x[0]), convert_time_to_seconds(x[1]))
    if x[0] and x[1]
    else (convert_time_to_seconds(x[0]) if x[0] else convert_time_to_seconds(x[1]))
)


# Convert split time to seconds
def convert_split_time_to_seconds(time_str):
    if not time_str:
        return None
    try:
        parts = list(map(int, time_str.split(":")))
        if len(parts) == 3:
            h, m, s = parts
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m, s = parts
            return m * 60 + s
        else:
            return None
    except Exception as e:
        print(f"Error converting time: {time_str} - {e}")
        return None


splits_df["SplitTimeInSeconds"] = splits_df["SplitTime"].apply(
    convert_split_time_to_seconds
)

# Ensure all splits are included for each team
teams = splits_df["Team"].unique()
full_split_records = []

for team in teams:
    team_splits = splits_df[splits_df["Team"] == team]
    team_split_labels = team_splits["SplitLabel"].tolist()

    for split in all_splits:
        if split not in team_split_labels:
            full_split_records.append(
                {
                    "Team": team,
                    "SplitLabel": split,
                    "SplitTime": "",
                    "SplitTimeInSeconds": None,
                }
            )
        else:
            existing_split = team_splits[team_splits["SplitLabel"] == split].iloc[0]
            full_split_records.append(
                {
                    "Team": team,
                    "SplitLabel": split,
                    "SplitTime": existing_split["SplitTime"],
                    "SplitTimeInSeconds": existing_split["SplitTimeInSeconds"],
                }
            )

full_splits_df = pd.DataFrame(full_split_records)

# Remove rows with None in SplitTimeInSeconds for the plot
plot_splits_df = full_splits_df.dropna(subset=["SplitTimeInSeconds"])

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
filtered_splits_df = plot_splits_df[plot_splits_df["Team"].isin(filtered_teams)]

if not filtered_splits_df.empty:
    st.write(f"Split Comparison for Teams in {selected_category}")

    # Ensure SplitLabel is a categorical type with a specified order
    filtered_splits_df["SplitLabel"] = pd.Categorical(
        filtered_splits_df["SplitLabel"], categories=all_splits, ordered=True
    )

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
    fig.update_layout(xaxis={"categoryorder": "array"})
    st.plotly_chart(fig)
else:
    st.write("No data available for the selected category.")
