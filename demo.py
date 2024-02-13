import streamlit as st
import pandas as pd
import random
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.graph_objects as go
import numpy as np
from policyengine_core.charts import format_fig


# Create sample data
# Actual data may have 'NA'/'0' value
column_names = [
    "person_id",
    "household_id",
    "age",
    "household_net_income_diff",
    "household_income_decile",
    "in_poverty",
    "household_tax",
    "household_benefits",
    "household_net_income_base",
    "relative_change",
]
sample_value = [[random.randint(1, 10) for _ in range(10)] for _ in range(20)]
difference_person_df = pd.DataFrame(sample_value, columns=column_names)

st.title(":rainbow[_Output Demo_]")
header_description = st.write(
    "This application shows how households are affected by certain policy reform, based on policyengine simulation."
)
repo_link = st.markdown(
    "This application utilizes the policyengine <a href='https://github.com/PolicyEngine/policyengine-us'>API</a>.",
    unsafe_allow_html=True,
)

# Create data display table
st.divider()
st.header("Raw Data", divider="rainbow")


# dataframe styling
# Define a function to apply CSS styles
def apply_styles(df):
    temp = df.style.set_properties(
        **{
            "font-family": "Roboto Serif",
            "color": "black",
        },
    ).set_table_styles(
        [
            {
                "selector": "th",
                "props": [
                    ("background-color", "lightblue"),
                    ("color", "black"),
                    ("font-size", "14px"),
                ],
            },
            {
                "selector": "tbody",
                "props": [
                    ("background-color", "white"),
                    ("color", "black"),
                    ("font-size", "14px"),
                ],
            },
        ]
    )

    return temp


st.dataframe(difference_person_df)
col1, col2 = st.columns([0.8, 0.2])
col2.image(
    "https://raw.githubusercontent.com/PolicyEngine/policyengine-app/master/src/images/logos/policyengine/blue.png",
    width=100,  # Manually Adjust the width of the image as per requirement
)
st.table(
    apply_styles(difference_person_df),
)

st.divider()

# Penalty
temp = (
    difference_person_df.groupby(by="household_id", as_index=False)
    .agg(
        {
            "person_id": "count",
        }
    )
    .rename(columns={"person_id": "family_size"})
)
penalty_df = difference_person_df.merge(temp, how="inner", on="household_id")
penalty_df["relative_change"][penalty_df["relative_change"].isna()] = 0
penalty_df = penalty_df.sort_values(
    by="relative_change", ascending=True
).rename(
    columns={
        "relative_change": "household_net_income_relative_diff",
        "household_net_income_base": "household_net_income",
    }
)

st.header("Household net income changes", divider="rainbow")

# Add histogram data
x1 = np.random.randn(200)
x2 = np.random.randn(200) + 2
# Group data together
hist_data = [x1, x2]
group_labels = ["Before reform", "After reform"]
fig = ff.create_distplot(hist_data, group_labels, bin_size=[0.1, 0.25, 0.5])
fig = format_fig(fig)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# histogram
fig1, ax1 = plt.subplots()
ax1.hist(penalty_df["household_net_income_relative_diff"], rwidth=0.85)
ax1.set_title("Distribution of household net income relative differences")
ax1.set_xlabel("Frequency")
ax1.set_ylabel("Ralative difference")
st.pyplot(fig1)
st.divider()

# histogram
# Create a histogram using Plotly
fig = go.Figure(
    data=[go.Histogram(x=penalty_df["household_net_income_relative_diff"])]
)

# Update layout with custom x and y axis labels
fig.update_layout(
    title="Distribution of household net income relative differences",
    xaxis=dict(title="Ralative difference"),  # Custom x-axis label
    yaxis=dict(title="Frequency"),  # Custom y-axis label
)
fig = format_fig(fig)
st.plotly_chart(fig, use_container_width=True)
st.divider()

# penalties section
st.subheader("Top 10 :red[Penalties] :arrow_down:")
temp = penalty_df.head(10).reset_index(drop=True)
st.table(
    apply_styles(temp),
)
col1, col2 = st.columns([0.8, 0.2])
col2.image(
    "https://raw.githubusercontent.com/PolicyEngine/policyengine-app/master/src/images/logos/policyengine/blue.png",
    width=80,  # Manually Adjust the width of the image as per requirement
)
penalty_income_tab, penalty_family_tab = st.tabs(
    ["Income Status", "Family Status"]
)
with penalty_income_tab:
    average_household_income = (
        penalty_df["household_net_income"].head(10).mean()
    )
    average_family_size = penalty_df["family_size"].head(10).mean()
    # Average of household income (metric)
    st.metric(
        label="Average Household income",
        value="$" + str(int(average_household_income)),
    )

    with st.expander("Household income decile distribution"):
        # Household income decile distribution (pie chart)
        label_list = (
            penalty_df.head(10)["household_income_decile"].value_counts().index
        )
        prefix_label_list = [
            f"Income Decile {number}" for number in label_list
        ]
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=prefix_label_list,
                    values=penalty_df.head(10)["household_income_decile"]
                    .value_counts()
                    .values,
                    hole=0.3,
                )
            ]
        )
        fig.update_traces(
            hoverinfo="label+value",
            textinfo="percent",
            textfont_size=20,
            marker=dict(line=dict(color="#000000", width=2)),
        )
        fig = format_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Household income data table"):
        # Total Household income (Table)
        temp = (
            penalty_df[["household_id", "household_net_income"]]
            .head(10)
            .reset_index(drop=True)
        )
        st.table(
            apply_styles(temp),
        )
        col1, col2 = st.columns([0.8, 0.2])
        col2.image(
            "https://raw.githubusercontent.com/PolicyEngine/policyengine-app/master/src/images/logos/policyengine/blue.png",
            width=80,  # Manually Adjust the width of the image as per requirement
        )
with penalty_family_tab:
    st.metric(
        label="Average family size",
        value=str(int(average_family_size)),
    )
    with st.expander("Family size distribution"):
        # Family Size distribution (pie chart)
        label_list = penalty_df.head(10)["family_size"].value_counts().index
        prefix_label_list = [
            f"Family Size of {number}" for number in label_list
        ]
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=prefix_label_list,
                    values=penalty_df.head(10)["family_size"]
                    .value_counts()
                    .values,
                    hole=0.3,
                )
            ]
        )
        fig.update_traces(
            hoverinfo="label+value",
            textinfo="percent",
            textfont_size=20,
            marker=dict(line=dict(color="#000000", width=2)),
        )
        fig = format_fig(fig)
        st.plotly_chart(fig, use_container_width=True)
    with st.expander("Family size data table"):
        # Total Family Size (Table)
        temp = penalty_df.head(10)[
            ["household_id", "family_size"]
        ].reset_index(drop=True)
        st.table(
            apply_styles(temp),
        )
        col1, col2 = st.columns([0.8, 0.2])
        col2.image(
            "https://raw.githubusercontent.com/PolicyEngine/policyengine-app/master/src/images/logos/policyengine/blue.png",
            width=80,  # Manually Adjust the width of the image as per requirement
        )
st.divider()

# Bonus section
st.subheader("Top 10 :green[Bonuses] :arrow_up:")
temp = (
    penalty_df.sort_values(
        by="household_net_income_relative_diff", ascending=False
    )
    .head(10)
    .reset_index(drop=True)
)
st.table(
    apply_styles(temp),
)
col1, col2 = st.columns([0.8, 0.2])
col2.image(
    "https://raw.githubusercontent.com/PolicyEngine/policyengine-app/master/src/images/logos/policyengine/blue.png",
    width=80,  # Manually Adjust the width of the image as per requirement
)
bonus_income_tab, bonus_family_tab = st.tabs(
    ["Income Status", "Family Status"]
)
with bonus_income_tab:
    temp = (
        penalty_df.sort_values(
            by="household_net_income_relative_diff", ascending=False
        )[
            [
                "household_id",
                "household_net_income",
                "household_income_decile",
                "family_size",
            ]
        ]
        .head(10)
        .reset_index(drop=True)
    )
    average_household_income = temp["household_net_income"].mean()
    average_family_size = temp["family_size"].mean()
    # Average of household income (metric)
    st.metric(
        label="Average Household income",
        value="$" + str(int(average_household_income)),
    )
    with st.expander("Household income decile distribution"):
        # Household income decile distribution (pie chart)
        label_list = temp["household_income_decile"].value_counts().index
        prefix_label_list = [
            f"Income Decile {number}" for number in label_list
        ]
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=prefix_label_list,
                    values=temp["household_income_decile"]
                    .value_counts()
                    .values,
                    hole=0.3,
                )
            ]
        )
        fig.update_traces(
            hoverinfo="label+value",
            textinfo="percent",
            textfont_size=20,
            marker=dict(line=dict(color="#000000", width=2)),
        )
        fig = format_fig(fig)
        st.plotly_chart(fig, use_container_width=True)
    with st.expander("Household income data table"):
        # Total Household income (Table)
        temp2 = temp[["household_id", "household_net_income"]]
        st.table(
            apply_styles(temp2),
        )
        col1, col2 = st.columns([0.8, 0.2])
        col2.image(
            "https://raw.githubusercontent.com/PolicyEngine/policyengine-app/master/src/images/logos/policyengine/blue.png",
            width=80,  # Manually Adjust the width of the image as per requirement
        )

with bonus_family_tab:
    st.metric(
        label="Average family size",
        value=str(int(average_family_size)),
    )
    with st.expander("Family size distribution"):
        # Family Size distribution (pie chart)
        label_list = temp["family_size"].value_counts().index
        prefix_label_list = [
            f"Family Size of {number}" for number in label_list
        ]
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=prefix_label_list,
                    values=temp["family_size"].value_counts().values,
                    hole=0.3,
                )
            ]
        )
        fig.update_traces(
            hoverinfo="label+value",
            textinfo="percent",
            textfont_size=20,
            marker=dict(line=dict(color="#000000", width=2)),
        )
        fig = format_fig(fig)
        st.plotly_chart(fig, use_container_width=True)
    with st.expander("Family size data table"):
        # Total Family Size (Table)
        temp2 = temp[["household_id", "family_size"]]
        st.table(
            apply_styles(temp2),
        )
        col1, col2 = st.columns([0.8, 0.2])
        col2.image(
            "https://raw.githubusercontent.com/PolicyEngine/policyengine-app/master/src/images/logos/policyengine/blue.png",
            width=80,  # Manually Adjust the width of the image as per requirement
        )

st.header("Data Analysis", divider="rainbow")

# scatterplot
st.subheader("Relationship between :blue[change] and :orange[age]")
st.scatter_chart(data=difference_person_df, x="age", y="relative_change")
st.subheader("Relationship between :blue[change] and :orange[poverty]")
st.scatter_chart(
    data=difference_person_df,
    x="in_poverty",
    y="relative_change",
    color="#ffaa00",
)

# Income decile transition
st.subheader("Household income decile transition visualization")
# Calculate deciles based on household net income
difference_person_df["household_net_income_reform"] = (
    difference_person_df["household_net_income_base"]
    + difference_person_df["household_net_income_diff"]
)
difference_person_df["household_income_decile_reform"] = (
    pd.qcut(
        difference_person_df["household_net_income_reform"],
        q=10,
        labels=False,
        duplicates="drop",
    )
    + 1
)
# Calculate frequency of transitions between old and new deciles
transition_counts = (
    difference_person_df.groupby(
        ["household_income_decile", "household_income_decile_reform"]
    )
    .size()
    .reset_index()
    .rename(columns={0: "Count"}, inplace=False)
)

# Create Plotly Sankey diagram
fig = go.Figure(
    data=[
        go.Sankey(
            arrangement="snap",
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=[
                    "Base 1st Decile",
                    "Base 2th Decile",
                    "Base 3th Decile",
                    "Base 4th Decile",
                    "Base 5th Decile",
                    "Base 6th Decile",
                    "Base 7th Decile",
                    "Base 8th Decile",
                    "Base 9th Decile",
                    "Base 10th Decile",  # index 9
                    "After reform 1st Decile",  # index 10
                    "After reform 2th Decile",
                    "After reform 3th Decile",
                    "After reform 4th Decile",
                    "After reform 5th Decile",
                    "After reform 6th Decile",
                    "After reform 7th Decile",
                    "After reform 8th Decile",
                    "After reform 9th Decile",
                    "After reform 10th Decile",
                ],
            ),
            link=dict(
                source=(transition_counts["household_income_decile"] - 1),
                target=(
                    transition_counts["household_income_decile_reform"] + 9
                ),
                value=transition_counts["Count"],
            ),
        )
    ]
)

# Set layout options
fig.update_layout(title="Income Decile Transitions", font=dict(size=12))
fig = format_fig(fig)
st.plotly_chart(fig, use_container_width=True)
# Person-Level dataframe and Household-Level dataframe problem
