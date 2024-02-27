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
    "Enter code copied from PolicyEngine website.\n\n Beware: Baseline dataframe variable name must be baseline_person\n\n Reformed dataframe variable name must be reformed_person."
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
        # Retrieve DataFrames if they exist
        baseline = local_vars.get("baseline")
        reformed = local_vars.get("reformed")
        df = baseline.calculate_dataframe(["household_net_income", "employment_income", "state_code"], map_to="household", use_weights=False)
        # Rename household_net_income to baseline_household_net_income.
        df.rename(dict("household_net_income": "baseline_net_income")) # finish syntax
        df["reformed_net_income"] = reformed.calc("household_net_income")
        df["change_net_income"] = df.reformed_net_income - df.baseline_net_income
        print(df)
        if (
            isinstance(baseline_person, pd.DataFrame)
            and isinstance(reformed_person, pd.DataFrame)
            and isinstance(difference_person, pd.DataFrame)
        ):
            output_container.success("Code executed successfully!")
            # Display the dataframes for debugging; Delete when confirmed
            output_container.write("Baseline Person DataFrame:")
            output_container.dataframe(baseline_person)
            output_container.write("Reformed Person DataFrame:")
            output_container.dataframe(reformed_person)
            output_container.write("Difference Person DataFrame:")
            output_container.dataframe(difference_person)
        elif (
            baseline_person is None
            or reformed_person is None
            or difference_person is None
        ):
            st.error(
                "One of the dataframes return none. Check if policyengine simulation codes are pasted correctly."
            )
        else:
            st.error(
                "Target dataFrames not found. Check if the output variable names are in the expected format."
            )
    except SyntaxError as se:
        st.error(
            f"Error message: {se}. Invalid syntax. Please check the corresponding line."
        )
    except Exception as e:
        st.error(f"Error: {e}")
