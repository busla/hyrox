import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from processor import (
    load_data,
    process_data,
    split_order,
    calculate_overall_performance,
)
from about import render_about

# Load and process data
data_file = "hyrox_results.json"
df = load_data(data_file)
df, splits_df, club_stats = process_data(df)
overall_performance = calculate_overall_performance(df)

# Get the list of categories
categories = df["Category"].unique()

# Define the navigation sidebar
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Charts", "About"])

if menu == "Charts":
    st.sidebar.title("Charts")
    page = st.sidebar.selectbox(
        "Choose a chart",
        [
            "Split Comparison",
            "Club Winners",
            "Overall Performance",
            "Best Splits",
            "Heatmap",
        ],
    )

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

    # Function to render the overall performance chart
    def render_overall_performance():
        st.write("Overall Performance Comparison")
        st.dataframe(overall_performance)
        overall_performance_chart = px.bar(
            overall_performance,
            x="Team",
            y="AverageTimeInSeconds",
            title="Overall Performance Comparison",
            labels={"Team": "Team", "AverageTimeInSeconds": "Total Time (seconds)"},
            hover_name="Team",
            hover_data={"AverageTimeInSeconds": True, "TotalTime": True},
        )
        st.plotly_chart(overall_performance_chart)

    # Function to render the best splits comparison chart
    def render_best_splits():
        st.write("Comparison of Best Splits")
        best_splits = (
            splits_df.groupby("SplitLabel")["SplitTimeInSeconds"].min().reset_index()
        )
        best_splits_chart = px.bar(
            best_splits,
            x="SplitLabel",
            y="SplitTimeInSeconds",
            title="Comparison of Best Splits",
            labels={"SplitLabel": "Split", "SplitTimeInSeconds": "Best Time (seconds)"},
            hover_name="SplitLabel",
            hover_data={"SplitTimeInSeconds": True},
        )
        st.plotly_chart(best_splits_chart)

    # Function to render the heatmap of performance
    def render_heatmap():
        st.write("Heatmap of Performance")

        # Pivot the data for the heatmap
        heatmap_data = splits_df.pivot_table(
            index="Team",
            columns="SplitLabel",
            values="SplitTimeInSeconds",
            fill_value=None,  # Keep None for meaningful heatmap colors
        )

        # Define the heatmap
        heatmap_chart = go.Figure(
            data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale="Viridis",
                colorbar=dict(title="Time (seconds)"),
                hoverongaps=False,
                text=heatmap_data.values,
                hoverinfo="x+y+z",
            )
        )

        # Add layout details
        heatmap_chart.update_layout(
            title="Heatmap of Performance",
            xaxis=dict(title="Split Label"),
            yaxis=dict(title="Team"),
            autosize=True,
            height=800,
        )

        st.plotly_chart(heatmap_chart)

    # Render the selected chart
    if page == "Split Comparison":
        render_split_comparison()
    elif page == "Club Winners":
        render_club_winners()
    elif page == "Overall Performance":
        render_overall_performance()
    elif page == "Best Splits":
        render_best_splits()
    elif page == "Heatmap":
        render_heatmap()

elif menu == "About":
    render_about()
