import streamlit as st
import pandas as pd
import random

# Fetch sample data
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
sample_value = []
for _ in range(8):
    random_numbers = [random.randint(-100, 100) for _ in range(10)]
    sample_value.append(random_numbers)
sample_data = [dict(zip(column_names, value)) for value in sample_value]

difference_person_df = pd.DataFrame(columns=column_names)
difference_person_df = difference_person_df._append(
    sample_data, ignore_index=True
)

# Create data display table
# Raw data
st.title("Demo")
st.subheader("Raw data")
st.dataframe(
    difference_person_df,
    hide_index=True,
)
# Penalty
st.subheader("Top 10 household with biggest penalties")
st.dataframe(
    difference_person_df.sort_values(by="relative_change", ascending=True)
    .loc[:, ["person_id", "relative_change"]]
    .head(10),
    hide_index=True,
)
# Bonus
st.subheader("Top 10 household with biggest bonuses")
st.dataframe(
    difference_person_df.sort_values(by="relative_change", ascending=False)
    .loc[:, ["person_id", "relative_change"]]
    .head(10),
    hide_index=True,
)
