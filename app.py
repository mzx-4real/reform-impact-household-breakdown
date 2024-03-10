import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from policyengine_core.charts import format_fig


# dataframe styling
# Define a function to apply CSS styles
def apply_styles(df: pd.DataFrame):
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


# function to create income distribution graph
def household_income_graph(scope_df: pd.DataFrame):
    # Household income decile distribution (pie chart)
    label_list = (
        scope_df.head(10)["household_income_decile_baseline"]
        .value_counts()
        .index
    )
    prefix_label_list = [f"Income Decile {number}" for number in label_list]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=prefix_label_list,
                values=scope_df.head(10)["household_income_decile_baseline"]
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
    return fig


# function to display styled datatable
def styled_datatable(scope_df: pd.DataFrame):
    temp = (
        scope_df[
            [
                "household_id",
                "household_net_income_baseline",
                "net_income_change",
                "net_income_relative_change",
            ]
        ]
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


# function to display key metric
def household_key_metric(scope_df: pd.DataFrame, metric: str):
    if metric == "income":
        average_household_income = (
            scope_df["household_net_income_baseline"].head(10).mean()
        )
        st.metric(
            label="Average Household income",
            value="$" + str(int(average_household_income)),
        )
    elif metric == "family":
        average_family_size = scope_df["family_size"].head(10).mean()
        st.metric(
            label="Average family size",
            value=str(int(average_family_size)),
        )


# Start of streamlit application
st.title("Policy Reform Impact Visualization")
# Input Section
# Input field for code copied from website
input_code = st.text_area(
    "Enter code copied from PolicyEngine website.\n\n Beware: Baseline microsimulation variable name must be baseline\n\n Reform microsimulation variable name must be reformed."
)

# Button to trigger the calculation
if st.button("Start simulation"):
    try:
        # Execute the Python code
        exec(input_code)
        # Access variables from the local namespace
        local_vars = locals()
        # Retrieve the value of the ***desired variable*** from the local vars
        # Retrieve microsimulation object
        baseline = local_vars.get("baseline")
        reformed = local_vars.get("reformed")
        # Household variable list
        HOUSEHOLD_VARIABLES = [
            "household_id",
            "age",
            "household_net_income",
            "household_income_decile",
            "in_poverty",
            "household_tax",
            "household_benefits",
        ]
        # Calculate household microdataframe
        baseline_household_df = baseline.calculate_dataframe(
            HOUSEHOLD_VARIABLES, map_to="household", use_weights=False
        )
        reformed_household_df = reformed.calculate_dataframe(
            HOUSEHOLD_VARIABLES, map_to="household", use_weights=False
        )
        # Create merged dataframe with difference between household_net_income,
        # household_tax and household_benefits
        fin_household_df = baseline_household_df.merge(
            reformed_household_df,
            on="household_id",
            suffixes=("_baseline", "_reformed"),
        )
        fin_household_df["net_income_change"] = (
            fin_household_df["household_net_income_reformed"]
            - fin_household_df["household_net_income_baseline"]
        )
        fin_household_df["household_tax_change"] = (
            fin_household_df["household_tax_reformed"]
            - fin_household_df["household_tax_baseline"]
        )
        fin_household_df["household_benefits_change"] = (
            fin_household_df["household_benefits_reformed"]
            - fin_household_df["household_benefits_baseline"]
        )
        fin_household_df["net_income_relative_change"] = (
            fin_household_df["net_income_change"]
            / fin_household_df["household_net_income_baseline"]
        )

        # Check result and display
        if (
            isinstance(baseline_household_df, pd.DataFrame)
            and isinstance(reformed_household_df, pd.DataFrame)
            and isinstance(fin_household_df, pd.DataFrame)
        ):
            st.success("Code executed successfully!")
            # Display the dataframes for debugging; Delete when the whole
            # application is done
            st.write("Baseline Household DataFrame:")
            st.dataframe(baseline_household_df)
            st.write("Reformed Household DataFrame:")
            st.dataframe(reformed_household_df)
            st.write("Final Household DataFrame:")
            st.dataframe(fin_household_df)

            # Output Section
            # penalties section
            st.subheader("Top 10 :red[Penalties] :arrow_down:")
            scope_df = fin_household_df.sort_values(
                by="net_income_relative_change", ascending=True
            )
            penalty_income_tab, penalty_family_tab = st.tabs(
                ["Income Status", "Family Status"]
            )
            with penalty_income_tab:
                household_key_metric(scope_df=scope_df, metric="income")
                with st.expander("Household income decile distribution"):
                    distribution_fig = household_income_graph(
                        scope_df=scope_df
                    )
                    st.plotly_chart(distribution_fig, use_container_width=True)
                with st.expander("Household income data table"):
                    styled_datatable(scope_df=scope_df)
        elif baseline is None or reformed is None:
            st.error(
                "Target microsimulation object not found. Check if the output variable names are in the expected format."
            )
        else:
            st.error(
                "One of the dataframes return none. Check if policyengine simulation codes are pasted correctly."
            )
    except SyntaxError as se:
        st.error(
            f"Error message: {se}. Invalid syntax. Please check the corresponding line."
        )
    except Exception as e:
        st.error(f"Error: {e}")
