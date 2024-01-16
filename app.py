import streamlit as st

from policyengine_us import Simulation

from policyengine_core.reforms import Reform

from policyengine_core.periods import instant

from policyengine_us import Microsimulation




# The application should take a reform as an input - user should be able to enter it on the front end 

# Instead of pre-set parameter it should be a user input from PE 
def modify_parameters(parameters):

    parameters.gov.irs.credits.ctc.refundable.fully_refundable.update(start=instant("2024-01-01"), stop=instant("2029-12-31"), value=True)
    return parameters


class reform(Reform):
    def apply(self):
        self.modify_parameters(modify_parameters)



baseline = Microsimulation()
reformed = Microsimulation(reform=reform)
HOUSEHOLD_VARIABLES = ["person_id", "household_id", "age", "household_net_income", "household_income_decile", "in_poverty", "household_tax", "household_benefits"]
baseline_person_df = baseline.calculate_dataframe(HOUSEHOLD_VARIABLES, 2024).astype(int)
reformed_person_df = reformed.calculate_dataframe(HOUSEHOLD_VARIABLES, 2024).astype(int)
difference_person_df = reformed_person_df - baseline_person_df


# The output should be, specific household_id's (10 each) which have the largest difference in household_net_income (positive and neagtive)
# Streamlit outputs should display the household_id's and the difference in household_net_income + some of the hsouehold variables whicha re relevant 

