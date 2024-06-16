import streamlit as st
import plotly.express as px
from processor import load_data, process_data, split_order
from about import render_about

# Load and process data
data_file = "hyrox_results.json"
df = load_data(data_file)
df, splits_df, club_stats = process_data(df)

# Get the list of categories
categories = df["Category"].unique()

# Define the navigation sidebar
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Charts", "About"])

if menu == "Charts":
    st.sidebar.title("Charts")
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
        st.write("Overall Club Winners")
        st.dataframe(club_stats)
        club_winners_chart = px.bar(
            club_stats,
            x="NormalizedClubs",
            y="TotalPoints",
            color="NormalizedClubs",
            title="Overall Club Winners",
            labels={"NormalizedClubs": "Club", "TotalPoints": "Total Points"},
            hover_name="NormalizedClubs",
            hover_data={"TotalPoints": True, "TeamCount": True, "AveragePoints": True},
        )
        st.plotly_chart(club_winners_chart)

    # Render the selected chart
    if page == "Split Comparison":
        render_split_comparison()
    elif page == "Club Winners":
        render_club_winners()

elif menu == "About":
    render_about()
