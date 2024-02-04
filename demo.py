import streamlit as st
import pandas as pd
import random
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.graph_objects as go
import numpy as np

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
    "This application utilizes the policyengine <a href='https://github.com/PolicyEngine/reform-impact-household-breakdown'>API</a>.",
    unsafe_allow_html=True,
)
# Create data display table
# Random Raw data
st.divider()
st.header("Raw Data", divider="rainbow")
st.dataframe(
    difference_person_df,
    hide_index=True,
)


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

# penalties section
st.subheader("Top 10 :red[Penalties] :arrow_down:")
st.dataframe(penalty_df.head(10).reset_index(drop=True), hide_index=True)
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
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=penalty_df.head(10)["household_income_decile"]
                    .value_counts()
                    .index,
                    values=penalty_df.head(10)["household_income_decile"]
                    .value_counts()
                    .values,
                    hole=0.3,
                )
            ]
        )
        fig.update_traces(
            hoverinfo="label+percent",
            textinfo="value",
            textfont_size=20,
            marker=dict(line=dict(color="#000000", width=2)),
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Household income data table"):
        # Total Household income (Table)
        st.dataframe(
            penalty_df[["household_id", "household_net_income"]]
            .head(10)
            .reset_index(drop=True),
            hide_index=True,
        )
with penalty_family_tab:
    st.metric(
        label="Average family size",
        value=str(int(average_family_size)),
    )
    with st.expander("Family size distribution"):
        # Family Size distribution (pie chart)
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=penalty_df.head(10)["family_size"]
                    .value_counts()
                    .index,
                    values=penalty_df.head(10)["family_size"]
                    .value_counts()
                    .values,
                    hole=0.3,
                )
            ]
        )
        fig.update_traces(
            hoverinfo="label+percent",
            textinfo="value",
            textfont_size=20,
            marker=dict(line=dict(color="#000000", width=2)),
        )
        st.plotly_chart(fig, use_container_width=True)
    with st.expander("Family size data table"):
        # Total Family Size (Table)
        st.dataframe(
            penalty_df.head(10)[["household_id", "family_size"]],
            hide_index=True,
        )
st.divider()

# Bonus section
st.subheader("Top 10 :green[Bonuses] :arrow_up:")
st.dataframe(
    penalty_df.sort_values(
        by="household_net_income_relative_diff", ascending=False
    )
    .head(10)
    .reset_index(drop=True),
    hide_index=True,
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
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=temp["household_income_decile"]
                    .value_counts()
                    .index,
                    values=temp["household_income_decile"]
                    .value_counts()
                    .values,
                    hole=0.3,
                )
            ]
        )
        fig.update_traces(
            hoverinfo="label+percent",
            textinfo="value",
            textfont_size=20,
            marker=dict(line=dict(color="#000000", width=2)),
        )
        st.plotly_chart(fig, use_container_width=True)
    with st.expander("Household income data table"):
        # Total Household income (Table)
        st.dataframe(
            temp[["household_id", "household_net_income"]],
            hide_index=True,
        )
with bonus_family_tab:
    st.metric(
        label="Average family size",
        value=str(int(average_family_size)),
    )
    with st.expander("Family size distribution"):
        # Family Size distribution (pie chart)
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=temp["family_size"].value_counts().index,
                    values=temp["family_size"].value_counts().values,
                    hole=0.3,
                )
            ]
        )
        fig.update_traces(
            hoverinfo="label+percent",
            textinfo="value",
            textfont_size=20,
            marker=dict(line=dict(color="#000000", width=2)),
        )
        st.plotly_chart(fig, use_container_width=True)
    with st.expander("Family size data table"):
        # Total Family Size (Table)
        st.dataframe(
            temp[["household_id", "family_size"]],
            hide_index=True,
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
                    "Base Decile 1",
                    "Base Decile 2",
                    "Base Decile 3",
                    "Base Decile 4",
                    "Base Decile 5",
                    "Base Decile 6",
                    "Base Decile 7",
                    "Base Decile 8",
                    "Base Decile 9",
                    "Base Decile 10",  # index 9
                    "After Decile 1",  # index 10
                    "After Decile 2",
                    "After Decile 3",
                    "After Decile 4",
                    "After Decile 5",
                    "After Decile 6",
                    "After Decile 7",
                    "After Decile 8",
                    "After Decile 9",
                    "After Decile 10",
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
st.plotly_chart(fig, use_container_width=True)
# Dataframe styling
