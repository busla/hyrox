import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Load the CSV file
df = pd.read_csv('/home/ubuntu/hyrox_competition_results.csv')

# Extract relevant columns for the chart
teams = df['Team']
split_times = df.iloc[:, 7:]  # Columns 7 and onwards are the split times

# Convert time strings to numerical values (seconds)
def time_to_seconds(time_str):
    if isinstance(time_str, str):
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    return time_str  # Return the original value if it's not a string

split_times = split_times.applymap(time_to_seconds)

# Prepare data for the chart
data = []
for i, team in enumerate(teams):
    team_data = {
        "label": team,
        "data": split_times.iloc[i].dropna().tolist()
    }
    data.append(team_data)

# Streamlit app
st.title("Hyrox Competition Time Splits")
st.write("This line chart visualizes the time splits for each team in the Hyrox competition.")

# Create the line chart
chart_data = pd.DataFrame(split_times.values, columns=[f"Split {i+1}" for i in range(split_times.shape[1])], index=teams)
st.line_chart(chart_data)

# Display the data table
st.write("Competition Results Data")
st.dataframe(df)
