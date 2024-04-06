import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from policyengine_core.charts import format_fig
import ast

# Initialize period variable
input_period = None


# Define a visitor subclass to traverse the AST and extract the period number
class PeriodExtractor(ast.NodeVisitor):
    def visit_Assign(self, node):
        global input_period
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "baseline_person":
                # Extract the period number from the 'baseline_person' line
                for kw in node.value.keywords:
                    if kw.arg == "period":
                        input_period = kw.value.n


# Use ast.NodeTransformer to traverse the AST and filter out the unwanted lines
class FilterTransformer(ast.NodeTransformer):
    # Define a function to filter out the lines you want to remove
    def filter_lines(self, node):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.startswith(
                    ("baseline_person", "reformed_person", "difference_person")
                ):
                    return None
        return node

    def visit(self, node):
        node = self.filter_lines(node)
        return (
            ast.NodeTransformer.visit(self, node) if node is not None else None
        )


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


# function to display distribution graph
def household_pie_graph(scope_df: pd.DataFrame, metric: str):
    if metric == "income":
        variable = "household_income_decile_baseline"
        label_list = scope_df[variable].value_counts().index
        prefix_label_list = [
            f"Income Decile {number}" for number in label_list
        ]
    elif metric == "family_size":
        variable = "family_size"
        label_list = scope_df[variable].value_counts().index
        prefix_label_list = [
            f"Family Size of {number}" for number in label_list
        ]
    # metric distribution (pie chart)
    fig = go.Figure(
        data=[
            go.Pie(
                labels=prefix_label_list,
                values=scope_df[variable].value_counts().values,
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


# function to display styled datatable
def styled_datatable(scope_df: pd.DataFrame):
    st.table(
        apply_styles(scope_df),
    )
    col1, col2 = st.columns([0.8, 0.2])
    col2.image(
        "https://raw.githubusercontent.com/PolicyEngine/policyengine-app/master/src/images/logos/policyengine/blue.png",
        width=80,  # Manually Adjust the width of the image as per requirement
    )


# function to display key metric
def household_key_metric(scope_df: pd.DataFrame, metric: str):
    if metric == "income":
        average_household_income = scope_df[
            "household_net_income_baseline"
        ].mean()
        st.metric(
            label="Average Household income",
            value="$" + str(round(average_household_income)),
        )
    elif metric == "family_size":
        average_family_size = scope_df["family_size"].mean()
        st.metric(
            label="Average family size",
            value=str(round(average_family_size)),
        )
    elif metric == "age":
        top_family_average_age = scope_df["family_average_age"].mean()
        st.metric(
            label="Average family age",
            value=str(round(top_family_average_age)),
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
    # Preprocess input_code to extract period and delete last three line of code to save runtime
    try:
        # Parse the code into an abstract syntax tree (AST)
        tree = ast.parse(input_code)

        # Instantiate the visitor and visit the AST
        period_extractor = PeriodExtractor()
        period_extractor.visit(tree)

        # Apply the transformation to remove the unwanted lines
        transformer = FilterTransformer()
        new_tree = transformer.visit(tree)

        # Convert the modified AST back to code
        modified_code = ast.unparse(new_tree)
        # Print out for debugging purpose, delete when confirmed
        st.text(
            f"Extracted Period:{input_period}\nModified Code:\n{modified_code}"
        )
    except Exception as e:
        st.error(f"Error: {e}")
    try:
        # Execute the Python code
        exec(modified_code)
        # Access variables from the local namespace
        local_vars = locals()
        # Retrieve the value of the ***desired variable*** from the local vars
        # Retrieve microsimulation object
        baseline = local_vars.get("baseline")
        reformed = local_vars.get("reformed")
        # Household variable list for calculating income status
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
            HOUSEHOLD_VARIABLES,
            period=input_period,
            map_to="household",
            use_weights=False,
        )
        reformed_household_df = reformed.calculate_dataframe(
            HOUSEHOLD_VARIABLES,
            period=input_period,
            map_to="household",
            use_weights=False,
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
        # Create person-level data to aggregate family status
        PERSON_VARIABLES = [
            "person_id",
            "household_id",
            "age",
        ]
        person_df = baseline.calculate_dataframe(
            PERSON_VARIABLES,
            period=input_period,
            map_to="person",
            use_weights=False,
        )
        person_df = (
            person_df.groupby(by="household_id", as_index=False)
            .agg({"person_id": "count", "age": "mean"})
            .rename(
                columns={
                    "person_id": "family_size",
                    "age": "family_average_age",
                }
            )
        )
        fin_household_df = fin_household_df.merge(
            person_df[["household_id", "family_size", "family_average_age"]],
            on="household_id",
        )
        # Imputation
        fin_household_df.fillna(
            value={"net_income_relative_change": 0}, inplace=True
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
            st.write("Person-Level Data:")
            st.dataframe(person_df)
            st.write("Final Household DataFrame:")
            st.dataframe(fin_household_df)

            # Output Section
            # penalties section
            st.subheader("Top 10 :red[Penalties] :arrow_down:")
            scope_df = (
                fin_household_df.sort_values(
                    by="net_income_relative_change", ascending=True
                )
                .head(10)
                .reset_index(drop=True)
            )
            penalty_income_tab, penalty_family_tab = st.tabs(
                ["Income Status", "Family Status"]
            )
            with penalty_income_tab:
                household_key_metric(scope_df=scope_df, metric="income")
                with st.expander("Household income decile distribution"):
                    household_pie_graph(scope_df=scope_df, metric="income")
                with st.expander("Household income data table"):
                    temp = scope_df[
                        [
                            "household_id",
                            "household_net_income_baseline",
                            "net_income_change",
                            "net_income_relative_change",
                        ]
                    ]
                    styled_datatable(scope_df=temp)
            with penalty_family_tab:
                col1, col2 = st.columns(2)
                with col1:
                    household_key_metric(
                        scope_df=scope_df, metric="family_size"
                    )
                with col2:
                    household_key_metric(scope_df=scope_df, metric="age")
                with st.expander("Household family size distribution"):
                    household_pie_graph(
                        scope_df=scope_df, metric="family_size"
                    )
                with st.expander("Household family status table"):
                    temp = scope_df[
                        [
                            "household_id",
                            "family_size",
                            "family_average_age",
                        ]
                    ]
                    styled_datatable(scope_df=temp)
            # bonus section
            st.subheader("Top 10 :green[Bonuses] :arrow_up:")
            scope_df = (
                fin_household_df.sort_values(
                    by="net_income_relative_change", ascending=False
                )
                .head(10)
                .reset_index(drop=True)
            )
            bonus_income_tab, bonus_family_tab = st.tabs(
                ["Income Status", "Family Status"]
            )
            with bonus_income_tab:
                household_key_metric(scope_df=scope_df, metric="income")
                with st.expander("Household income decile distribution"):
                    household_pie_graph(scope_df=scope_df, metric="income")
                with st.expander("Household income data table"):
                    temp = scope_df[
                        [
                            "household_id",
                            "household_net_income_baseline",
                            "net_income_change",
                            "net_income_relative_change",
                        ]
                    ]
                    styled_datatable(scope_df=temp)
            with bonus_family_tab:
                col1, col2 = st.columns(2)
                with col1:
                    household_key_metric(
                        scope_df=scope_df, metric="family_size"
                    )
                with col2:
                    household_key_metric(scope_df=scope_df, metric="age")
                with st.expander("Household family size distribution"):
                    household_pie_graph(
                        scope_df=scope_df, metric="family_size"
                    )
                with st.expander("Household family status table"):
                    temp = scope_df[
                        [
                            "household_id",
                            "family_size",
                            "family_average_age",
                        ]
                    ]
                    styled_datatable(scope_df=temp)
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
