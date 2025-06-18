import streamlit as st
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool

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
gender_filter = st.sidebar.selectbox("Select Gender", ["All"] + sorted(df["Gender"].dropna().unique().tolist()))
country_filter = st.sidebar.selectbox("Select Country", ["All"] + sorted(df["Country"].dropna().unique().tolist()))
y_metric = st.sidebar.selectbox("Y-Axis Metric", ["TSH_Level", "T3_Level", "T4_Level"])

# Apply Filters
filtered_df = df[(df["Age"] >= age_range[0]) & (df["Age"] <= age_range[1])]
if gender_filter != "All":
    filtered_df = filtered_df[filtered_df["Gender"] == gender_filter]
if country_filter != "All":
    filtered_df = filtered_df[filtered_df["Country"] == country_filter]

# Check if data is empty
if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters.")
else:
    st.subheader("📈 Nodule Size vs Selected Lab Metric")

    source = ColumnDataSource(filtered_df)

    p = figure(
        title=f"Nodule Size vs {y_metric}",
        x_axis_label='Nodule Size (cm)',
        y_axis_label=y_metric,
        tools="pan,wheel_zoom,box_zoom,reset,hover",
        width=700,
        height=450
    )

    p.circle(
        x='Nodule_Size',
        y=y_metric,
        source=source,
        size=7,
        fill_color="navy",
        fill_alpha=0.6,
        line_color=None,
        legend_field="Thyroid_Cancer_Risk"
    )

    hover = p.select_one(HoverTool)
    hover.tooltips = [
        ("Age", "@Age"),
        ("Gender", "@Gender"),
        ("Country", "@Country"),
        ("Risk", "@Thyroid_Cancer_Risk"),
        ("Diagnosis", "@Diagnosis"),
        ("T3", "@T3_Level"),
        ("T4", "@T4_Level"),
        ("TSH", "@TSH_Level"),
        ("Nodule Size", "@Nodule_Size")
    ]

    p.legend.location = "top_left"

    st.bokeh_chart(p, use_container_width=True)

    st.subheader("📌 Summary Table of Filtered Data")
    st.dataframe(filtered_df[[
        "Age", "Gender", "Country", "Thyroid_Cancer_Risk", "Diagnosis",
        "TSH_Level", "T3_Level", "T4_Level", "Nodule_Size"
    ]].reset_index(drop=True))

# Footer
st.markdown("---")
st.markdown("**Created for Final Assignment – Interactive Visualization Project**")
