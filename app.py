import streamlit as st
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, ColorBar, LinearColorMapper
from bokeh.transform import cumsum
from math import pi

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("thyroid_cancer_risk_data.csv")
    return df

df = load_data()

st.title("📊 Thyroid Cancer Risk Interactive Dashboard")

# Sidebar Filters
st.sidebar.header("Filter Options")
age_range = st.sidebar.slider("Select Age Range", 0, 100, (20, 60))
gender_filter = st.sidebar.selectbox("Select Gender", ["All"] + sorted(df["Gender"].unique().tolist()))
country_filter = st.sidebar.selectbox("Select Country", ["All"] + sorted(df["Country"].unique().tolist()))
y_metric = st.sidebar.selectbox("Y-Axis Metric", ["TSH_Level", "T3_Level", "T4_Level"])
bin_count = st.sidebar.slider("Histogram Bin Count", 5, 30, 10)
heatmap_cols = st.sidebar.multiselect(
    "Select Numeric Columns for Heatmap",
    ["Age", "TSH_Level", "T3_Level", "T4_Level", "Nodule_Size"],
    default=["Age", "TSH_Level", "T3_Level", "T4_Level", "Nodule_Size"]
)

# Apply Filters
filtered_df = df[(df["Age"] >= age_range[0]) & (df["Age"] <= age_range[1])]
if gender_filter != "All":
    filtered_df = filtered_df[filtered_df["Gender"] == gender_filter]
if country_filter != "All":
    filtered_df = filtered_df[filtered_df["Country"] == country_filter]

# --- Scatter Plot ---
st.subheader("📈 Nodule Size vs Selected Lab Metric")
source = ColumnDataSource(filtered_df)
p = figure(title="Nodule Size vs " + y_metric,
           x_axis_label='Nodule Size (cm)',
           y_axis_label=y_metric,
           tools="pan,wheel_zoom,box_zoom,reset,hover",
           width=700, height=450)

p.circle(x='Nodule_Size', y=y_metric, source=source,
         size=7, color="navy", alpha=0.6, legend_field="Thyroid_Cancer_Risk")

hover = p.select(dict(type=HoverTool))
hover.tooltips = [
    ("Age", "@Age"),
    ("Gender", "@Gender"),
    ("Risk", "@Thyroid_Cancer_Risk"),
    ("Diagnosis", "@Diagnosis"),
    ("T3", "@T3_Level"),
    ("T4", "@T4_Level")
]

p.legend.location = "top_left"
st.bokeh_chart(p, use_container_width=True)

# --- Bar Chart Risiko ---
st.subheader("📊 Distribution of Thyroid Cancer Risk Levels")
risk_counts = filtered_df["Thyroid_Cancer_Risk"].value_counts().sort_index()
risk_source = ColumnDataSource(data=dict(
    risk=risk_counts.index.tolist(),
    count=risk_counts.values.tolist()
))

bar = figure(x_range=risk_counts.index.tolist(),
             title="Risk Category Distribution",
             x_axis_label="Risk Level", y_axis_label="Number of Cases",
             width=700, height=400,
             tools="pan,wheel_zoom,box_zoom,reset,hover,tap",
             tooltips=[("Risk Level", "@risk"), ("Count", "@count")])

bar.vbar(x='risk', top='count', width=0.6, source=risk_source,
         fill_color="#e84d60", line_color="black", alpha=0.8)
st.bokeh_chart(bar, use_container_width=True)

# --- Histogram Age ---
st.subheader("📉 Age Distribution of Filtered Patients")
hist, edges = np.histogram(filtered_df["Age"], bins=bin_count)
age_source = ColumnDataSource(data=dict(top=hist, left=edges[:-1], right=edges[1:]))

hist_plot = figure(title="Age Histogram",
                   x_axis_label="Age", y_axis_label="Frequency",
                   width=700, height=400,
                   tools="pan,wheel_zoom,box_zoom,reset,hover",
                   tooltips=[("Range", "@left - @right"), ("Count", "@top")])

hist_plot.quad(top='top', bottom=0, left='left', right='right',
               source=age_source, fill_color="orange", line_color="black", alpha=0.7)
st.bokeh_chart(hist_plot, use_container_width=True)

# --- Pie Chart Diagnosis ---
st.subheader("🥧 Diagnosis Distribution (Pie Chart)")
diag_counts = filtered_df["Diagnosis"].value_counts()
diag_data = pd.DataFrame({'diagnosis': diag_counts.index, 'value': diag_counts.values})
diag_data['angle'] = diag_data['value'] / diag_data['value'].sum() * 2 * pi
colors = ["#c9d9d3", "#718dbf", "#e84d60", "#ddb7b1", "#a1dab4"]
diag_data['color'] = colors[:len(diag_data)]

pie = figure(height=400, title="Diagnosis Distribution",
             toolbar_location="right",
             tools="hover,pan,reset,tap", tooltips="@diagnosis: @value",
             x_range=(-0.5, 1.0))

pie.wedge(x=0, y=1, radius=0.4,
          start_angle=cumsum('angle', include_zero=True),
          end_angle=cumsum('angle'),
          line_color="white", fill_color='color',
          legend_field='diagnosis', source=diag_data,
          hover_fill_color="gold", hover_alpha=0.8)

pie.axis.visible = False
pie.grid.visible = False
pie.legend.title = "Diagnosis"
pie.legend.click_policy = "hide"
st.bokeh_chart(pie, use_container_width=True)

# --- Heatmap Korelasi ---
st.subheader("📌 Correlation Heatmap (Numeric Features)")
if len(heatmap_cols) >= 2:
    corr = filtered_df[heatmap_cols].corr().round(2)
    heatmap_data = pd.DataFrame([
        (x, y, corr.loc[y, x]) for x in corr.columns for y in corr.columns
    ], columns=["x", "y", "value"])

    heat_source = ColumnDataSource(heatmap_data)
    mapper = LinearColorMapper(palette="Viridis256", low=-1, high=1)

    heat = figure(title="Correlation Heatmap",
                  x_range=heatmap_cols, y_range=list(reversed(heatmap_cols)),
                  x_axis_location="above",
                  tools="hover,pan,box_zoom,reset",
                  tooltips=[("Pair", "@x ↔ @y"), ("Correlation", "@value")],
                  width=600, height=600)

    heat.rect(x="x", y="y", width=1, height=1, source=heat_source,
              fill_color={'field': 'value', 'transform': mapper},
              line_color="white")

    color_bar = ColorBar(color_mapper=mapper, location=(0, 0))
    heat.add_layout(color_bar, 'right')
    st.bokeh_chart(heat, use_container_width=True)
else:
    st.warning("Please select at least two variables for the heatmap.")

# --- Summary Table ---
st.subheader("📋 Summary Table of Filtered Data")
st.dataframe(filtered_df[[
    "Age", "Gender", "Country", "Thyroid_Cancer_Risk", "Diagnosis",
    "TSH_Level", "T3_Level", "T4_Level", "Nodule_Size"
]].reset_index(drop=True))

# --- Footer ---
st.markdown("---")
st.markdown("**Created for Final Assignment - Interactive Visualization Project**")
