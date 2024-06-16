import streamlit as st


def render_about():
    st.title("About This App")
    st.write("""
        This app visualizes the results of the Hyrox competition. Here are the details on how the calculations are done and how the categories are fixed:
        
        ### Normalizing Club Names
        Club names can vary due to typos or different naming conventions. We normalize club names to ensure consistency. For example:
        - CFR, CFRVK, CfRvk, CrossFit Reykjavík, crossfit reykjavík, Cfr, CF RVK, Crossfit Reykjavík, Crossfit Reykjavik, Cfrvk, cfr are all normalized to 'CFR'.
        
        ### Points Calculation
        We use a points system to rank the clubs based on their teams' performance:
        - Each team is awarded points based on their rank. The formula used is the inverse of the rank: `Points = 1 / Rank`.
        - The total points for each club is the sum of the points of all its teams.
        - The average points per team is also calculated to provide an additional metric.
        
        ### Category Fixes
        We ensure that categories are consistent across the data. If there are known issues with category names, we apply fixes to standardize them.

        ### Minimum Team Count Threshold
        To avoid skewing the results with clubs that have very few teams, we apply a minimum team count threshold. Only clubs with at least a certain number of teams are considered in the final ranking.

        ### Split Comparison
        The split comparison chart shows the performance of teams in each split. Splits are normalized to ensure consistent ordering and labeling.

        We hope this app provides useful insights into the Hyrox competition results. If you have any questions or feedback, please let us know.
    """)
