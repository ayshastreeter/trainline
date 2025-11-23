import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("sales_processed.csv")

# --- Sidebar filters ---
st.sidebar.header("Filters")

# Operator dropdown with "All Operators"
operators_with_all = ["All Operators"] + sorted(df["operator"].unique())
selected_operator = st.sidebar.selectbox("Select Operator:", options=operators_with_all, index=None)

# Initialize defaults
filtered_regions, region_label = [], ""
filtered_stations, station_label = [], ""

if selected_operator:
    # Regions
    if selected_operator == "All Operators":
        regions_for_operator = sorted(df["rgn_nm"].unique())
    else:
        regions_for_operator = sorted(df[df["operator"] == selected_operator]["rgn_nm"].unique())

    regions_with_all = ["All Regions"] + regions_for_operator
    selected_regions = st.sidebar.multiselect("Select Region(s):", options=regions_with_all, default=[])

    if "All Regions" in selected_regions or not selected_regions:
        filtered_regions = regions_for_operator
        region_label = "All Regions"
    else:
        filtered_regions = selected_regions
        region_label = ", ".join(filtered_regions)

    # Stations
    if selected_operator == "All Operators":
        stations_for_selection = sorted(df[df["rgn_nm"].isin(filtered_regions)]["station"].unique())
    else:
        stations_for_selection = sorted(
            df[(df["operator"] == selected_operator) & (df["rgn_nm"].isin(filtered_regions))]["station"].unique()
        )

    stations_with_all = ["All Stations"] + stations_for_selection
    selected_stations = st.sidebar.multiselect("Select Station(s):", options=stations_with_all, default=[])

    if "All Stations" in selected_stations or not selected_stations:
        filtered_stations = stations_for_selection
        station_label = "All Stations"
    else:
        filtered_stations = selected_stations
        station_label = ", ".join(filtered_stations)

# --- Chart in main area ---
if selected_operator:
    if selected_operator == "All Operators":
        filtered_df = df[(df["rgn_nm"].isin(filtered_regions)) & (df["station"].isin(filtered_stations))]
    else:
        filtered_df = df[
            (df["operator"] == selected_operator)
            & (df["rgn_nm"].isin(filtered_regions))
            & (df["station"].isin(filtered_stations))
        ]

    if filtered_df.empty:
        st.info("No data for the selected filters.")
    else:
        # Group by year and month_day
        sales_by_day = filtered_df.groupby(["year", "month_day"])["sales"].sum().reset_index()
        sales_by_day["dummy_date"] = pd.to_datetime("2000-" + sales_by_day["month_day"], format="%Y-%m-%d")

        chart_title = (
            f"Ticket Sales by Day of Year\n"
            f"Operator: {selected_operator} | Regions: {region_label} | Stations: {station_label}"
        )

        fig = px.line(
            sales_by_day,
            x="dummy_date",
            y="sales",
            color="year",
            title=chart_title,
            labels={"dummy_date": "Day of Year", "sales": "Total Ticket Sales"},
        )

        # Slightly smaller chart height so it fits neatly
        fig.update_layout(height=550)

        # Dynamic y-axis (auto-scale)
        fig.update_yaxes(title_text="Total Ticket Sales")

        # Adaptive x-axis labels: month when broad, day when zoomed in
        fig.update_xaxes(
            tickangle=-45,
            rangeslider_visible=True,
            tickformatstops=[
                dict(dtickrange=[None, "M1"], value="%b-%d"),  # zoomed in → day labels
                dict(dtickrange=["M1", None], value="%b"),     # zoomed out → month labels
            ],
        )

        # Hover always shows exact day
        fig.update_traces(
            hovertemplate="Day: %{x|%b-%d}<br>Year: %{legendgroup}<br>Sales: %{y}<extra></extra>"
        )

        # --- Weekend shading ---
        for day in sales_by_day["dummy_date"].unique():
            if day.weekday() >= 5:  # Saturday or Sunday
                fig.add_vrect(
                    x0=day,
                    x1=day + pd.Timedelta(days=1),
                    fillcolor="lightgrey",
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                )

        st.plotly_chart(fig, use_container_width=True)
else:
    st.sidebar.warning("Please select an operator to begin.")