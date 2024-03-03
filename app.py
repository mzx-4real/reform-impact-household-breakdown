import streamlit as st
import pandas as pd
from policyengine_us import Microsimulation
from policyengine_core.reforms import Reform
from policyengine_core.periods import instant
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np

# Start of streamlit application
st.title("Policy Reform Impact Visualization")
# Input Section
# Input field for code copied from website
input_code = st.text_area(
    "Enter code copied from PolicyEngine website.\n\n Beware: Baseline microsimulation variable name must be baseline\n\n Reform microsimulation variable name must be reformed."
)

# Button to trigger the calculation
if st.button("Start simulation"):
    # Create an empty output container
    output_container = st.empty()
    try:
        # Execute the Python code with the global dictionary
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
            output_container.success("Code executed successfully!")
            # Display the dataframes for debugging; Delete when confirmed
            output_container.write("Baseline Household DataFrame:")
            output_container.dataframe(baseline_household_df)
            output_container.write("Reformed Household DataFrame:")
            output_container.dataframe(reformed_household_df)
            output_container.write("Final Household DataFrame:")
            output_container.dataframe(fin_household_df)
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
