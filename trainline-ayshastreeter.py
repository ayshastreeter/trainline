#################################
# LIBRARIES
#################################

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


#################################
# FORMATTING
#################################

# Page layout
st.set_page_config(layout="wide")

# Sidebar style
sidebar_style = """
    <style>
        /* Sidebar background */
        [data-testid="stSidebar"] > div:first-child {
            background-color: #00a88f;
        }

        /* Make filter labels and text white */
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMultiSelect label,
        [data-testid="stSidebar"] .stRadio label {
            color: white !important;
        }
    </style>
"""
st.markdown(sidebar_style, unsafe_allow_html=True)

# Year colour palette
year_colours = {
    "2023": "#00a88f",
    "2024": "#2d00b1"
}

# Logo
st.sidebar.image("lookups/trainline_logo.png", width=250)   # logo at top of main page
st.sidebar.markdown("Aysha Streeter  \nSenior Data Scientist")                  # header text



#################################
# DATA IMPORT
#################################
df = pd.read_csv("sales_processed.csv")
df_stations = pd.read_csv("stations.csv")



#################################
# PLOTTING
#################################
left_col, mid_col, right_col = st.columns([1,1,1])



#################################
# MAP
#################################
with left_col:
    fig_map = px.scatter_mapbox(
        df.drop_duplicates(subset=['station']), 
        lat="lat",
        lon="lon",
        hover_name='station',
        hover_data=['region_nm', 'operator'],
        zoom=5,
        color='region_nm',
        height=750,
        width=450
    )
    fig_map.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": 54.5, "lon": -3.0},
        mapbox_zoom=4.75,
        showlegend=False  
    )
    st.plotly_chart(fig_map, use_container_width=False)



#################################
# SCORECARDS
#################################

# Filtering by year
df_2023 = df[df['year'] == 2023]
df_2024 = df[df['year'] == 2024]

# Averaging
daily_avg_2023 = df_2023.groupby('date')['sales'].mean().reset_index()
daily_avg_2024 = df_2024.groupby('date')['sales'].mean().reset_index()

# Overall averaging and standard deviations
overall_avg_2023 = daily_avg_2023['sales'].mean()
overall_std_2023 = daily_avg_2023['sales'].std()

overall_avg_2024 = daily_avg_2024['sales'].mean()
overall_std_2024 = daily_avg_2024['sales'].std()

# Percentage change
pct_change = ((overall_avg_2024 - overall_avg_2023) / overall_avg_2023) * 100

# Station level averages
station_avg_2024 = df_2024.groupby('station')['sales'].mean().reset_index()
max_station_2024 = station_avg_2024.loc[station_avg_2024['sales'].idxmax()]
min_station_2024 = station_avg_2024.loc[station_avg_2024['sales'].idxmin()]

# Staion coverage
unique_df_stations = df['station'].nunique()
unique_all_stations = df_stations['station'].nunique()
station_pct = (unique_df_stations / unique_all_stations) * 100

with mid_col:
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)

    # 2024 mean + std
    st.markdown(f"<h4 style='text-align:left;'>mean daily sales for all (2024):</h4>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:left; font-size:2.2rem; font-weight:bold;'>"
        f"£{overall_avg_2024:,.2f} (±£{overall_std_2024:,.2f})</p>",
        unsafe_allow_html=True
    )

    # 2023 mean + std
    st.markdown(f"<h4 style='text-align:left;'>mean daily sales for all (2023):</h4>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:left; font-size:2.2rem; font-weight:bold;'>"
        f"£{overall_avg_2023:,.2f} (±£{overall_std_2023:,.2f})</p>",
        unsafe_allow_html=True
    )

    # Color-coded % change
    color = "green" if pct_change >= 0 else "red"
    st.markdown(f"<h4 style='text-align:left;'>% change</h4>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:left; font-size:2.2rem; font-weight:bold; color:{color};'>{pct_change:.2f}%</p>",
        unsafe_allow_html=True
    )

    # Max station (2024)
    st.markdown(f"<h4 style='text-align:left;'>station with max daily mean: (2024):</h4>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:left; font-size:2.2rem; font-weight:bold;'>"
        f"{max_station_2024['station']} (£{max_station_2024['sales']:,.2f})</p>",
        unsafe_allow_html=True
    )

    # Min station (2024)
    st.markdown(f"<h4 style='text-align:left;'>station with min daily mean (2024):</h4>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:left; font-size:2.2rem; font-weight:bold;'>"
        f"{min_station_2024['station']} (£{min_station_2024['sales']:,.2f})</p>",
        unsafe_allow_html=True
    )

with right_col:
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)

#################################
# OPERATOR SHARE
#################################

    operator_sales_2023 = df_2023.groupby('operator')['sales'].sum().reset_index()
    operator_sales_2024 = df_2024.groupby('operator')['sales'].sum().reset_index()

    operator_sales_2023['proportion'] = operator_sales_2023['sales'] / operator_sales_2023['sales'].sum() * 100
    operator_sales_2024['proportion'] = operator_sales_2024['sales'] / operator_sales_2024['sales'].sum() * 100

    operator_sales_2023['year'] = "2023"
    operator_sales_2024['year'] = "2024"
    operator_sales = pd.concat([operator_sales_2023, operator_sales_2024], ignore_index=True)

    custom_colours = ["#00a88f", "#2d00b1", "#f4a300"]
    fig_bar = px.bar(
        operator_sales,
        y="year",             
        x="proportion",       
        color='operator',    
        barmode="stack",
        orientation="h",      
        labels={"proportion": "percentage of total sales", "year": "Year"},
        title="share of sales by operator",
        color_discrete_sequence=custom_colours
    )

    fig_bar.update_layout(
            title=dict(
        text="share of sales by operator",
        x=0.5,             
        y=0.95,           
        xanchor="center",  
        yanchor="top"     
    ),
        height=300,
        title_x=0.5, 
        margin=dict(t=40, b=40),
        uniformtext_minsize=8,
        uniformtext_mode='hide'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Adding spacing to separate plots.
    st.markdown("<div style='margin-top:50px'></div>", unsafe_allow_html=True)



#################################
# GAUGE 
#################################

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=station_pct,
        title={'text': "station data coverage (%)", 'font': {'size': 16}}, 
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "teal"},  
            'bgcolor': "white",
            'steps': [],               
            'threshold': {
                'line': {'color': "teal", 'width': 3},
                'thickness': 0.75,
                'value': station_pct
            }
        }
    ))
    fig_gauge.update_layout(
        height=175,                    
        margin=dict(t=40, b=20)       
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
        


#################################
# FILTERS
#################################-

# Adding space for alignment.
for _ in range(5):
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Operator dropdown
operators_with_all = ['all operators'] + sorted(df['operator'].unique())
selected_operator = st.sidebar.selectbox('operator:', options=operators_with_all)

# Setting defaults
filtered_regions, region_label = [], ''
filtered_stations, station_label = [], ''

# Conditional dropdowns
if selected_operator:

    # Region dropdown
    if selected_operator == 'all operators':
        regions_for_operator = sorted(df['region_nm'].unique())
    else:
        regions_for_operator = sorted(df[df['operator'] == selected_operator]['region_nm'].unique())

    regions_with_all = ['all regions'] + regions_for_operator
    selected_regions = st.sidebar.multiselect('region(s):', options=regions_with_all)

    if 'all regions' in selected_regions or not selected_regions:
        filtered_regions = regions_for_operator
        region_label = 'all regions'
    else:
        filtered_regions = selected_regions
        region_label = ", ".join(filtered_regions)

    # Station dropdown
    if selected_operator == 'all operators':
        stations_for_selection = sorted(df[df['region_nm'].isin(filtered_regions)]['station'].unique())
    else:
        stations_for_selection = sorted(
            df[(df['operator'] == selected_operator) & (df['region_nm'].isin(filtered_regions))]['station'].unique()
        )

    stations_with_all = ['all stations'] + stations_for_selection
    selected_stations = st.sidebar.multiselect('station(s):', options=stations_with_all)

    if 'all stations' in selected_stations or not selected_stations:
        filtered_stations = stations_for_selection
        station_label = 'all stations'
    else:
        filtered_stations = selected_stations
        station_label = ", ".join(filtered_stations)

if selected_operator:
    if selected_operator == 'all operators':
        filtered_df = df[(df['region_nm'].isin(filtered_regions)) & (df['station'].isin(filtered_stations))]
    else:
        filtered_df = df[
            (df['operator'] == selected_operator)
            & (df['region_nm'].isin(filtered_regions))
            & (df['station'].isin(filtered_stations))
        ]

    if filtered_df.empty:
        st.info('no data for the selected filters')
    else:



#################################
# SALES BY DAY
#################################
        sales_by_day = filtered_df.groupby(["year", "month_day"])["sales"].sum().reset_index()
        sales_by_day["dummy_date"] = pd.to_datetime("2000-" + sales_by_day["month_day"], format="%Y-%m-%d")

        # Convert year to string so it matches year_colors keys
        sales_by_day["year"] = sales_by_day["year"].astype(str)

        chart_title = (
            f"Total sales by day and year <br>"
            f"operator: {selected_operator} | regions: {region_label} | stations: {station_label}"
        )

        year_colors = {
            "2023": "#00a88f",  # teal
            "2024": "#2d00b1"   # purple
        }

        fig = px.line(
            sales_by_day,
            x="dummy_date",
            y="sales",
            color="year",
            title=chart_title,
            labels={"dummy_date": "date", "sales": "total sales gbp"},
            color_discrete_map=year_colors  # apply custom colors
        )

        fig.update_layout(
            height=600,
            margin=dict(l=40, r=40, t=80, b=40),
            title_x=0.5,
            title_font=dict(size=20),
            title=dict(x=0.5, xanchor="center", yanchor="top")
        )

        fig.update_yaxes(title_text="total sales gbp")

        fig.update_xaxes(
            tickangle=-45,
            rangeslider_visible=True,
            tickformatstops=[
                dict(dtickrange=[None, "M1"], value="%b-%d"),
                dict(dtickrange=["M1", None], value="%b"),
            ],
        )

        fig.update_traces(
            customdata=sales_by_day["year"], 
            hovertemplate="day: %{x|%b-%d}<br>year: %{customdata}<br>sales: %{y}<extra></extra>"
            )

        for day in sales_by_day["dummy_date"].unique():
            if day.weekday() >= 5:
                fig.add_vrect(
                    x0=day,
                    x1=day + pd.Timedelta(days=1),
                    fillcolor="lightgrey",
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                )

        st.plotly_chart(fig, use_container_width=True)



#################################
# SALES BY STATION AND TIME
#################################

        if "date" not in filtered_df.columns:
            filtered_df["date"] = pd.to_datetime(
                filtered_df["year"].astype(str) + "-" + filtered_df["month_day"], format="%Y-%m-%d"
            )

        mask = (filtered_df["date"] >= "2023-01-01") & (filtered_df["date"] <= "2024-12-01")
        time_filtered_df = filtered_df.loc[mask]

        sales_over_time = (
            time_filtered_df.groupby(["date", 'station'])["sales"].sum().reset_index()
        )

        chart_title2 = (
            f"Total sales over time by station(s)<br>"
            f"operator: {selected_operator} | region(s): {region_label} | station(s): {station_label}"
        )

        fig2 = px.line(
            sales_over_time,
            x="date",
            y="sales",
            color='station',
            title=chart_title2,
            labels={"date": "date", "sales": "total sales gbp", 'station': 'station'},
            hover_data={'station': True}
        )

        fig2.update_layout(
            height=600,
            margin=dict(l=40, r=40, t=80, b=40),
            title_x=0.5,
            title_font=dict(size=20),
            title=dict(x=0.5, xanchor="center", yanchor="top")
        )

        fig2.update_yaxes(title_text="total sales gbp")

        fig2.update_xaxes(
            tickangle=-45,
            rangeslider_visible=True,
            tickformat="%b %Y"
        )

        fig2.update_traces(
            hovertemplate="station: %{customdata[0]}<br>date: %{x|%b-%d-%Y}<br>sales: %{y}<extra></extra>"
        )

        st.plotly_chart(fig2, use_container_width=True)

else:
    st.sidebar.warning("please select an operator to begin")



#################################
# DISTRIBUTION
#################################

fig3 = go.Figure()

year_colors = {
    2024: "#2d00b1",
    2023: "#00a88f"
}

for year in [2023, 2024]:
    year_data = time_filtered_df[time_filtered_df["year"] == year]
    fig3.add_trace(
        go.Box(
            x=year_data["month"],         
            y=year_data["sales"],
            name=str(year),               
            boxpoints="all",
            hovertext=year_data['station'],
            marker=dict(opacity=0.6, color=year_colors[year]),
        )
    )

chart_title3 = (
    f"Sales distribution by month<br>"
    f"operator: {selected_operator} | region(s): {region_label} | station(s): {station_label}"
)

fig3.update_layout(
    width=1200,
    height=700,
    title=dict(
        text=chart_title3,
        x=0.5,
        xanchor="center",
        yanchor="top"
    ),
    title_font=dict(size=20),
    xaxis_title="month",
    yaxis_title="sales gbp",
    template="plotly_white",
    showlegend=True, 
    xaxis=dict(
        tickmode="array",
        tickvals=list(range(1, 13)), 
        ticktext=[str(m) for m in range(1, 13)],
        categoryorder="array",
        categoryarray=list(range(1, 13))
    ),
    boxmode="group"
)

st.plotly_chart(fig3, use_container_width=True)



#################################
# DISTRIBUTION
#################################

# Ensuring date column exists
if "date" not in time_filtered_df.columns:
    time_filtered_df["date"] = pd.to_datetime(
        time_filtered_df["year"].astype(str) + "-" + time_filtered_df["month_day"],
        format="%Y-%m-%d"
    )

# Aggregating sales
agg = (
    time_filtered_df.groupby(["month", "week_day"])["sales"]
    .sum()
    .reset_index()
)

# Converting to percentages within each month
agg["pct"] = agg.groupby("month")["sales"].transform(lambda x: x / x.sum() * 100)

# Setting axis names
weekday_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

fig = go.Figure()
for wd in weekday_order:
    wd_data = agg[agg["week_day"] == wd]
    fig.add_trace(
        go.Bar(
            x=wd_data["month"],
            y=wd_data["pct"],
            name=wd.capitalize(),  # capitalize for nicer legend labels
            text=wd_data["pct"].round(1).astype(str) + "%",
            textposition="inside"
        )
    )

#  Chart title
chart_title = (
    f"Sales distribution by weekday percentages per month<br>"
    f"operator: {selected_operator} | region(s): {region_label} | station(s): {station_label}"
)

fig.update_layout(
    barmode="stack",
    width=1200,
    height=700,
    title=dict(
        text=chart_title,
        x=0.5,
        xanchor="center",
        yanchor="top"
    ),
    title_font=dict(size=20),
    xaxis=dict(
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=[str(m) for m in range(1, 13)],
        title="month"
    ),
    yaxis=dict(title="Sales (%)"),
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)



#################################
# CHANGE
#################################

# Ensuring date column exists
if "date" not in time_filtered_df.columns:
    time_filtered_df["date"] = pd.to_datetime(
        time_filtered_df["year"].astype(str) + "-" + time_filtered_df["month_day"],
        format="%Y-%m-%d"
    )

# Aggregating sales by (year, week)
weekly_sales = (
    time_filtered_df.groupby(["year", "week_number"])["sales"]
    .sum()
    .reset_index()
)

# Pivoting for 2023 and 2024
pivot = weekly_sales.pivot(index="week_number", columns="year", values="sales")

# Ensuring all weeks 1–52 are present
pivot = pivot.reindex(range(1, 53), fill_value=0)

# Calculating percentage change.
# Avoiding division by zero by replacing 0 with NaN, then filling with 0
pivot["pct_change"] = (pivot[2024] - pivot[2023]) / pivot[2023].replace(0, pd.NA) * 100
pivot["pct_change"] = pivot["pct_change"].fillna(0)

# Building bar chart.
fig = go.Figure()
fig.add_trace(
    go.Bar(
        x=pivot.index,
        y=pivot["pct_change"],
        text=pivot["pct_change"].round(1).astype(str) + "%",
        textposition="outside",
        marker=dict(color="#00a88f")
    )
)

chart_title = (
    f"Change in sales by week % (2024 vs 2023)<br>"
    f"operator: {selected_operator} | region(s): {region_label} | station(s): {station_label}"
)

fig.update_layout(
    width=1200,
    height=700,
    title=dict(
        text=chart_title,
        x=0.5,
        xanchor="center",
        yanchor="top"
    ),
    title_font=dict(size=20),
    xaxis=dict(
        tickmode="array",
        tickvals=list(range(1, 53)),
        ticktext=[str(w) for w in range(1, 53)],
        title="week"
    ),
    yaxis=dict(title = 'sales change %'),
    template="plotly_white",
    shapes=[  # add a horizontal line at 0%
        dict(
            type="line",
            xref="paper", x0=0, x1=1,
            yref="y", y0=0, y1=0,
            line=dict(color="black", dash="dash")
        )
    ]
)

st.plotly_chart(fig, use_container_width=True)



#################################
# COASTAL
#################################

# Define custom colors
year_colors = {
    "2023": "#00a88f",  # teal
    "2024": "#2d00b1"   # purple
}

if selected_operator:
    if selected_operator == 'all operators':
        filtered_df = df[(df['region_nm'].isin(filtered_regions)) & (df['station'].isin(filtered_stations))]
    else:
        filtered_df = df[
            (df['operator'] == selected_operator)
            & (df['region_nm'].isin(filtered_regions))
            & (df['station'].isin(filtered_stations))
        ]

    if filtered_df.empty:
        st.info("No data for the selected filters.")
    else:
        # --- Coastal Chart ---
        weekly_total = filtered_df.groupby(['year','week_number'])['sales'].sum().reset_index(name='total_sales')

        weekly_coastal = (
            filtered_df[filtered_df['coastal_flag'] == 1]
            .groupby(['year','week_number'])['sales']
            .sum()
            .reset_index(name='coastal_sales')
        )

        weekly_sales = pd.merge(weekly_total, weekly_coastal, on=['year','week_number'])
        weekly_sales['coastal_pct'] = (weekly_sales['coastal_sales'] / weekly_sales['total_sales']) * 100
        weekly_sales['year'] = weekly_sales['year'].astype(str)

        fig_coastal = px.line(
            weekly_sales,
            x='week_number',
            y='coastal_pct',
            color='year',
            markers=True,
            labels={
                'week_number': 'week',
                'coastal_pct': 'coastal sales %',
                'year': 'Year'
            },
            title=(
                f"Sales from coastal stations by week<br>"
                f"operator: {selected_operator} | regions: {region_label} | stations: {station_label}"
            ),
            color_discrete_map=year_colors
        )

        fig_coastal.update_xaxes(tickmode='linear', tick0=1, dtick=1)
        st.plotly_chart(fig_coastal, use_container_width=True, key="coastal_chart")



#################################
# RURALITY
#################################

# Aggregating monthly totals
if selected_operator:
    if selected_operator == 'all operators':
        filtered_df = df[
            (df['region_nm'].isin(filtered_regions)) &
            (df['station'].isin(filtered_stations))
        ]
    else:
        filtered_df = df[
            (df['operator'] == selected_operator) &
            (df['region_nm'].isin(filtered_regions)) &
            (df['station'].isin(filtered_stations))
        ]

    if filtered_df.empty:
        st.info("no data for the selected filters")
    else:

        monthly_total = (
            filtered_df.groupby(['month'])['sales']
            .sum()
            .reset_index(name='total_sales')
        )

        monthly_rurality = (
            filtered_df.groupby(['month','rurality_nm'])['sales']
            .sum()
            .reset_index(name='rurality_sales')
        )

        # Merge totals with rurality breakdown
        monthly_sales = pd.merge(monthly_total, monthly_rurality, on=['month'], how='inner')

        # Calculate percentage share
        monthly_sales['rurality_pct'] = (
            monthly_sales['rurality_sales'] / monthly_sales['total_sales'] * 100
        )

        # --- Plot ---
        fig_rurality = px.bar(
            monthly_sales,
            x="month",
            y="rurality_pct",
            color="rurality_nm",
            barmode="stack",
            labels={
                "month": "Month",
                "rurality_pct": "Sales share %",
                "rurality_nm": "Rurality"
            },
            title=(
                f"Sales share by rurality and month<br>"
                f"operator: {selected_operator} | regions: {region_label} | stations: {station_label}"
            ),
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig_rurality.update_layout(
            barmode="stack",
            xaxis=dict(
                tickmode="linear",
                tick0=1,
                dtick=1,
                title="Month"
            ),
            yaxis=dict(title="Sales share %")
        )

        st.plotly_chart(fig_rurality, use_container_width=True, key="rurality_chart")
