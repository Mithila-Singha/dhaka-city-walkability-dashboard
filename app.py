import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="Dhaka Walkability Dashboard",
    page_icon="🚶",
    layout="wide"
)

# --------------------------------------------------
# Load data
# --------------------------------------------------

grid = gpd.read_file(
    "dhaka_walkability.gpkg",
    layer="walkability_grid"
)

# --------------------------------------------------
# Header
# --------------------------------------------------

# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🚶 How Walkable Is Dhaka City?")

st.markdown(
    """
    **A GIS-based Walkability Index for Dhaka City**

    This interactive dashboard evaluates walkability across Dhaka using
    street connectivity, essential-service accessibility, public transport,
    green-space accessibility, and network-based walking accessibility.
    """
)
# --------------------------------------------------
# Map layer selector
# --------------------------------------------------

st.subheader("Interactive Walkability Map")

layer_options = {
    "Overall Walkability": "walkability_score",
    "Street Connectivity": "street_connectivity_score",
    "Essential Services": "essential_services_score",
    "Public Transport": "public_transport_score",
    "Green Space": "green_space_score",
    "Walking Accessibility": "walking_accessibility_score",
    "Problem Zones": "problem_count"
}
selected_layer = st.selectbox(
    "Select map layer",
    list(layer_options.keys())
)

selected_column = layer_options[selected_layer]
layer_title = selected_layer



# --------------------------------------------------
# Summary
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        f"{selected_layer} Average",
        f"{grid[selected_column].mean():.1f}/100"
    )

with col2:
    st.metric(
        f"{selected_layer} Minimum",
        f"{grid[selected_column].min():.1f}/100"
    )

with col3:
    st.metric(
        f"{selected_layer} Maximum",
        f"{grid[selected_column].max():.1f}/100"
    )
# --------------------------------------------------
# Convert to latitude / longitude
# --------------------------------------------------

grid_map = grid.to_crs(epsg=4326)

# --------------------------------------------------
# Center map
# --------------------------------------------------

center = grid_map.geometry.union_all().centroid

m = folium.Map(
    location=[center.y, center.x],
    zoom_start=11,
    tiles="OpenStreetMap"
)

# --------------------------------------------------
# Color function
# --------------------------------------------------

def get_color(score):

    if selected_layer == "Problem Zones":

        if score == 0:
            return "#2ca25f"
        elif score <= 2:
            return "#fec44f"
        elif score == 3:
            return "#fe9929"
        elif score == 4:
            return "#ec7014"
        else:
            return "#cc4c02"

    else:

        if score >= 80:
            return "#006837"

        elif score >= 60:
            return "#31a354"

        elif score >= 40:
            return "#addd8e"

        elif score >= 20:
            return "#fec44f"

        else:
            return "#d7301f"
# --------------------------------------------------
# Add grid cells
# --------------------------------------------------

for _, row in grid_map.iterrows():

    selected_score = row[selected_column]

    popup_text = f"""
<div style="font-family: Arial; width: 260px;">

<h4 style="margin-bottom: 8px;">
🚶 {row['grid_id']}
</h4>

<b>Overall Walkability:</b>
{row['walkability_score']:.1f}/100<br>

<b>Class:</b>
{row['walkability_class']}<br>

<b>Main Weakness:</b>
{row['main_weakness']}<br>

<b>Problems:</b>
{row['problem_count']} / 5

<hr>

<b>Street Connectivity:</b>
{row['street_connectivity_score']:.1f}<br>

<b>Essential Services:</b>
{row['essential_services_score']:.1f}<br>

<b>Public Transport:</b>
{row['public_transport_score']:.1f}<br>

<b>Green Space:</b>
{row['green_space_score']:.1f}<br>

<b>Walking Accessibility:</b>
{row['walking_accessibility_score']:.1f}

    </div>
    """

    folium.GeoJson(
        row["geometry"],

        style_function=lambda feature,
        score=selected_score: {
            "fillColor": get_color(score),
            "color": "white",
            "weight": 0.5,
            "fillOpacity": 0.7
        },

        tooltip=folium.Tooltip(
            f"{selected_layer}: {selected_score:.1f}"
        ),

        popup=folium.Popup(
            popup_text,
            max_width=350
        )
    ).add_to(m)

# --------------------------------------------------
# Display map
# --------------------------------------------------

st_folium(
    m,
    width=None,
    height=650
)

# --------------------------------------------------
# Map legend
# --------------------------------------------------

# --------------------------------------------------
# Map legend
# --------------------------------------------------

# --------------------------------------------------
# Map legend
# --------------------------------------------------

if selected_layer == "Overall Walkability":

    st.markdown("""
    **Walkability Score**

    🟢 **Excellent:** 80–100  
    🟢 **Good:** 60–79  
    🟡 **Moderate:** 40–59  
    🟠 **Poor:** 20–39  
    🔴 **Very Poor:** 0–19
    """)

elif selected_layer == "Problem Zones":

    st.markdown("""
    **Number of Walkability Problems**

    🟢 **0 problems**  
    🟡 **1–2 problems**  
    🟠 **3 problems**  
    🟠 **4 problems**  
    🔴 **5 problems**
    """)

else:

    st.markdown(f"""
    **{selected_layer} Score**

    🟢 **Very High:** 80–100  
    🟢 **High:** 60–79  
    🟡 **Moderate:** 40–59  
    🟠 **Low:** 20–39  
    🔴 **Very Low:** 0–19
    """)
# --------------------------------------------------
# Walkability statistics
# --------------------------------------------------


avg_walkability = grid["walkability_score"].mean()

excellent_pct = (
    (grid["walkability_class"] == "Excellent").mean() * 100
)

good_pct = (
    (grid["walkability_class"] == "Good").mean() * 100
)

moderate_pct = (
    (grid["walkability_class"] == "Moderate").mean() * 100
)

poor_pct = (
    (grid["walkability_class"] == "Poor").mean() * 100
)

very_poor_pct = (
    (grid["walkability_class"] == "Very Poor").mean() * 100
)

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Average Walkability",
        f"{avg_walkability:.1f}/100"
    )

with col2:
    poor_or_very_poor = poor_pct + very_poor_pct
    st.metric(
        "Poor / Very Poor",
        f"{poor_or_very_poor:.1f}%"
    )

with col3:
    good_or_excellent = good_pct + excellent_pct
    st.metric(
        "Good / Excellent",
        f"{good_or_excellent:.1f}%"
    )

with col4:
    st.metric(
        "Grid Cells",
        f"{len(grid):,}"
    )
    
# Distribution table
st.write("### Walkability Classification")

classification_summary = (
    grid["walkability_class"]
    .value_counts()
    .reindex(
        ["Excellent", "Good", "Moderate", "Poor", "Very Poor"]
    )
    .fillna(0)
    .astype(int)
    .reset_index()
)

classification_summary.columns = ["Class", "Grid Cells"]

classification_summary["Percentage"] = (
    classification_summary["Grid Cells"]
    / len(grid)
    * 100
).round(2)

st.dataframe(
    classification_summary,
    hide_index=True,
    width="stretch"
)

# --------------------------------------------------
# --------------------------------------------------
# Charts
# --------------------------------------------------

col1, col2 = st.columns(2)

# Walkability classification
with col1:
    st.write("### Walkability Distribution")

    chart_data = classification_summary.set_index("Class")[["Grid Cells"]]

    st.bar_chart(
        chart_data,
        height=350
    )

# Component performance
with col2:
    st.write("### Component Performance")

    component_data = {
        "Street Connectivity": grid["street_connectivity_score"].mean(),
        "Essential Services": grid["essential_services_score"].mean(),
        "Public Transport": grid["public_transport_score"].mean(),
        "Green Space": grid["green_space_score"].mean(),
        "Walking Accessibility": grid["walking_accessibility_score"].mean()
    }

    component_df = (
    pd.Series(component_data)
    .round(2)
    .to_frame("Average Score")
    
    )

    st.bar_chart(
        component_df,
        height=350
    )

# --------------------------------------------------
# Best and worst areas
# --------------------------------------------------

st.write("### Most and Least Walkable Areas")

top_10 = (
    grid[
        [
            "grid_id",
            "walkability_score",
            "walkability_class",
            "main_weakness"
        ]
    ]
    .sort_values("walkability_score", ascending=False)
    .head(10)
    .copy()
)

bottom_10 = (
    grid[
        [
            "grid_id",
            "walkability_score",
            "walkability_class",
            "main_weakness"
        ]
    ]
    .sort_values("walkability_score", ascending=True)
    .head(10)
    .copy()
)

top_10["walkability_score"] = top_10["walkability_score"].round(2)
bottom_10["walkability_score"] = bottom_10["walkability_score"].round(2)

col1, col2 = st.columns(2)

with col1:
    st.write("#### 🟢 Top 10 Most Walkable")
    st.dataframe(
        top_10,
        hide_index=True,
        width="stretch"
    )

with col2:
    st.write("#### 🔴 Top 10 Least Walkable")
    st.dataframe(
        bottom_10,
        hide_index=True,
        width="stretch"
    )

# --------------------------------------------------
# --------------------------------------------------
# Problem Zones
# --------------------------------------------------

st.write("### Walkability Problem Zones")

problem_summary = (
    grid["problem_count"]
    .value_counts()
    .reindex([0, 1, 2, 3, 4, 5])
    .fillna(0)
    .astype(int)
    .reset_index()
)

problem_summary.columns = ["Number of Problems", "Grid Cells"]

problem_summary["Percentage"] = (
    problem_summary["Grid Cells"]
    / len(grid)
    * 100
).round(2)

# Summary metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "No Problems",
        f"{problem_summary.loc[problem_summary['Number of Problems'] == 0, 'Grid Cells'].iloc[0]}"
    )

with col2:
    cells_1_2 = problem_summary[
        problem_summary["Number of Problems"].isin([1, 2])
    ]["Grid Cells"].sum()

    st.metric(
        "1–2 Problems",
        f"{cells_1_2}"
    )

with col3:
    cells_3_plus = problem_summary[
        problem_summary["Number of Problems"] >= 3
    ]["Grid Cells"].sum()

    st.metric(
        "3+ Problems",
        f"{cells_3_plus}"
    )

with col4:
    all_five = problem_summary.loc[
        problem_summary["Number of Problems"] == 5,
        "Grid Cells"
    ].iloc[0]

    st.metric(
        "All 5 Problems",
        f"{all_five}"
    )

# Problem distribution chart
st.write("#### Number of Walkability Problems per Grid Cell")

problem_chart = problem_summary.set_index(
    "Number of Problems"
)[["Grid Cells"]]

st.bar_chart(
    problem_chart,
    height=350
)

# Detailed table
st.write("#### Problem Distribution")

st.dataframe(
    problem_summary,
    hide_index=True,
    width="stretch"
)

# --------------------------------------------------
# Key Findings
# --------------------------------------------------

st.write("### Key Findings")

st.markdown(
    f"""
    - The average Walkability Score across Dhaka City is **{avg_walkability:.1f}/100**.
    - **{poor_or_very_poor:.1f}%** of grid cells are classified as **Poor or Very Poor**.
    - **{good_or_excellent:.1f}%** of grid cells are classified as **Good or Excellent**.
    - **Walking Accessibility** is the weakest component on average
      ({grid["walking_accessibility_score"].mean():.1f}/100).
    - **Public Transport** is the strongest component on average
      ({grid["public_transport_score"].mean():.1f}/100).
    - **{(grid["problem_count"] >= 3).mean() * 100:.1f}%** of grid cells experience
      three or more simultaneous walkability problems.
    """
)

# --------------------------------------------------
# Methodology
# --------------------------------------------------

st.write("### Methodology")

st.markdown(
    """
    The Walkability Index is calculated for 500 × 500 m grid cells
    across Dhaka City. Five components are combined using equal
    weights (20% each):

    - **Street Connectivity** — density of intersections within each grid cell.
    - **Essential Services** — availability of essential services within 500 m.
    - **Public Transport** — proximity to the nearest mapped bus stop.
    - **Green Space** — accessibility and amount of mapped green space.
    - **Walking Accessibility** — essential services reachable within 1,000 m
      through the street network.

    Each component is normalized to a 0–100 score and combined to produce
    the overall Walkability Score.

    **Important:** The index represents GIS-based spatial accessibility.
    It does not directly measure sidewalk quality, pedestrian safety,
    crossings, traffic conditions, or footpath obstructions.
    """
)

# --------------------------------------------------
# Limitations
# --------------------------------------------------

st.write("### Limitations")

st.markdown(
    """
    This assessment represents GIS-based spatial accessibility and
    does not directly measure sidewalk quality, pedestrian safety,
    road crossings, traffic conditions, or footpath obstructions.
    Public transport accessibility is represented using mapped bus stops,
    while green-space proximity is based on spatial distance rather than
    walking-network distance.
    """
)