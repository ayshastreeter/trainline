import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv('df_sales_processed.csv')

# Sidebar: select ru11ind (rural/urban indicator)
selected_ru11ind = st.selectbox("Select RU11 Indicator:", options=sorted(df['ru11ind'].unique()))

# Filter stations based on selected ru11ind
stations_for_ru11ind = df[df['ru11ind'] == selected_ru11ind]['station'].unique()
selected_stations = st.multiselect("Select station(s):", options=sorted(stations_for_ru11ind), default=stations_for_ru11ind)

# Filter dataframe by ru11ind and stations
filtered_df = df[(df['ru11ind'] == selected_ru11ind) & (df['station'].isin(selected_stations))]

# Group by year and month_day
sales_by_day = filtered_df.groupby(['year', 'month_day'])['sales'].sum().reset_index()

# Create a dummy date in a leap year to support 02-29
sales_by_day['dummy_date'] = pd.to_datetime("2000-" + sales_by_day['month_day'], format="%Y-%m-%d")

# Plot
fig = px.line(
    sales_by_day,
    x='dummy_date',
    y='sales',
    color='year',
    title=f"Ticket Sales by Day of Year (RU11 Indicator={selected_ru11ind})",
    labels={'dummy_date': 'Day of Year', 'sales': 'Total Ticket Sales'}
)

# Format ticks and hover
fig.update_xaxes(
    tickformat="%m-%d",
    dtick="D1",
    tickangle=-45
)
fig.update_traces(hovertemplate="Day: %{x|%m-%d}<br>Year: %{legendgroup}<br>Sales: %{y}<extra></extra>")

# Display chart
st.plotly_chart(fig, use_container_width=True)
