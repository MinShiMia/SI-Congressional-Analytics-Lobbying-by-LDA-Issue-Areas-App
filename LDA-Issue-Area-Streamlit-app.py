import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import io
import requests
# from streamlit_plotly_events import plotly_events  # For capturing click events
# import json
# from io import StringIO
# import os
# import re
# import ssl



# Set the page layout to 'wide'
st.set_page_config(layout="wide")


# Load the data from GitHub
# ssl._create_default_https_context = ssl._create_unverified_context  # Disable SSL verification
df_frequency_path = "https://raw.githubusercontent.com/MinShiMia/SI-Congressional-Analytics-Lobbying-by-Issue-Areas-App/main/lda_frequency_by_LDA_issue_area_over_time.csv"
df_expenses_path = "https://raw.githubusercontent.com/MinShiMia/SI-Congressional-Analytics-Lobbying-by-Issue-Areas-App/main/lda_quarterly_total_lobbying_expenses_by_LDA_issue_area_over_time.csv"


response1 = requests.get(df_frequency_path)
response1.raise_for_status()  # Raise an error for bad status codes (e.g., 404, 403)
csv_data1 = response1.content.decode('utf-8')
df_frequency = pd.read_csv(io.StringIO(csv_data1))
print(df_frequency.head())

response2 = requests.get(df_expenses_path)
response2.raise_for_status()  # Raise an error for bad status codes (e.g., 404, 403)
csv_data2 = response2.content.decode('utf-8')
df_expenses = pd.read_csv(io.StringIO(csv_data2))
print(df_expenses.head())


# Sidebar Filters
st.sidebar.header("Filters")
selected_year_range = st.sidebar.slider("Select Year Range", min_value=int(df_frequency['Year'].min()), max_value=int(df_frequency['Year'].max()), value=(2010, 2024), step=1)
selected_quarters = st.sidebar.multiselect("Select Quarter", sorted(df_frequency['Quarter'].unique()), default=sorted(df_frequency['Quarter'].unique()))
selected_issue_area = st.sidebar.multiselect("Select Issue Area", sorted(df_frequency['issue_description'].unique()), default=sorted(df_frequency['issue_description'].unique()))

# Filter the DataFrames
filtered_df_frequency = df_frequency[
    (df_frequency['Year'] >= selected_year_range[0]) &
    (df_frequency['Year'] <= selected_year_range[1]) &
    (df_frequency['Quarter'].isin(selected_quarters)) &
    (df_frequency['issue_description'].isin(selected_issue_area))
]

filtered_df_expenses = df_expenses[
    (df_expenses['Year'] >= selected_year_range[0]) &
    (df_expenses['Year'] <= selected_year_range[1]) &
    (df_expenses['Quarter'].isin(selected_quarters)) &
    (df_expenses['issue_description'].isin(selected_issue_area))
]

# Aggregate Data
# Frequency: Sum the 'LDA_frequency'
frequency_data = filtered_df_frequency.groupby('issue_description')['LDA_frequency'].sum().reset_index(name='Total Frequency')

# Expenses: Sum the 'lobbying_expenses'
expenses_data = filtered_df_expenses.groupby('issue_description')['lobbying_expenses'].sum().reset_index(name='Total Expenses')

# Convert Total Expenses to millions for readability
expenses_data['Total Expenses'] = expenses_data['Total Expenses'] / 1_000_000

# Streamlit App
st.title("Interactive Lobbying Data by LDA Issue Area Dashboard")
# st.markdown("### Comparing LDA Frequency and Lobbying Expenses by Issue Area")
# Display Selected Filters
st.markdown(f"### Selected Year Range: {selected_year_range[0]} to {selected_year_range[1]}")

# Plot Frequency Bar Chart
st.markdown("### LDA Frequency by LDA Issue Area")
fig_bar1 = px.bar(
    frequency_data,
    x='issue_description',
    y='Total Frequency',
    height=800,
    color_discrete_sequence=['teal']
)
fig_bar1.update_layout(
    xaxis_title='LDA Issue Area',
    yaxis_title='LDA Frequency',
    bargap=0.2,
    xaxis_tickangle=-45
)
st.plotly_chart(fig_bar1, use_container_width=True)

# Plot Lobbying Expenses Bar Chart
st.markdown("### LDA Lobbying Expenses by LDA Issue Area")
fig_bar2 = px.bar(
    expenses_data,
    x='issue_description',
    y='Total Expenses',
    labels={"Total Expenses": "Total Expenses ($ Million)"},
    height=800,
    color_discrete_sequence=['orange']
)
fig_bar2.update_layout(
    xaxis_title='LDA Issue Area',
    yaxis_title='Total Expenses ($ Million)',
    bargap=0.2,
    xaxis_tickangle=-45
)
st.plotly_chart(fig_bar2, use_container_width=True)


# Dropdown for selecting an issue area to view its time series plot
st.markdown("### Time Series Line Plot for a Specific Issue Area")
selected_issue = st.selectbox("Select an Issue Area for Time Series Analysis", frequency_data['issue_description'].unique())

# Time Series Plot for Frequency
issue_data_freq = df_frequency[df_frequency['issue_description'] == selected_issue].groupby(['Year', 'Quarter'])['LDA_frequency'].sum().reset_index()
issue_data_freq['Year_Quarter'] = issue_data_freq['Year'].astype(str) + " Q" + issue_data_freq['Quarter'].astype(str)

if not issue_data_freq.empty:
    st.markdown(f"#### LDA Frequency Over Time for {selected_issue}")
    plt.figure(figsize=(12, 4))
    plt.plot(issue_data_freq['Year_Quarter'], issue_data_freq['LDA_frequency'], marker='o', linestyle='-', color='teal')
    plt.xlabel("Year-Quarter")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45, fontsize=8)
    plt.grid(False)
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()
else:
    st.write(f"No frequency data available for {selected_issue}.")

# Time Series Plot for Lobbying Expenses
issue_data_exp = df_expenses[df_expenses['issue_description'] == selected_issue].groupby(['Year', 'Quarter'])['lobbying_expenses'].sum().reset_index()
issue_data_exp['Year_Quarter'] = issue_data_exp['Year'].astype(str) + " Q" + issue_data_exp['Quarter'].astype(str)
issue_data_exp['lobbying_expenses'] = issue_data_exp['lobbying_expenses'] / 1_000_000  # Convert to millions

if not issue_data_exp.empty:
    st.markdown(f"#### LDA Lobbying Expenses Over Time for {selected_issue} (in Millions)")
    plt.figure(figsize=(12, 4))
    plt.plot(issue_data_exp['Year_Quarter'], issue_data_exp['lobbying_expenses'], marker='o', linestyle='-', color='orange')
    plt.xlabel("Year-Quarter")
    plt.ylabel("Lobbying Expenses (in Millions)")
    plt.xticks(rotation=45, fontsize=8)
    plt.grid(False)
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()
else:
    st.write(f"No lobbying expenses data available for {selected_issue}.")



# # Helper function to truncate issue names
# def truncate_text(text, max_length=9):
#     return text[:max_length] + '...' if len(text) > max_length else text

# df_frequency = fetch_csv_from_s3(BUCKET_NAME, FOLDER_NAME, FILE_NAME1)
# df_expenses = fetch_csv_from_s3(BUCKET_NAME, FOLDER_NAME, FILE_NAME2)
#
# # Ensure that LDA_frequency and lobbying_expenses are numeric
# df_frequency['LDA_frequency'] = pd.to_numeric(df_frequency['LDA_frequency'], errors='coerce').fillna(0)
# df_expenses['lobbying_expenses'] = pd.to_numeric(df_expenses['lobbying_expenses'], errors='coerce').fillna(0)
#
#
# # Sidebar Filters
# st.sidebar.header("Filters")
# selected_year_range = st.sidebar.slider("Select Year Range", min_value=int(df_frequency['Year'].min()), max_value=int(df_frequency['Year'].max()), value=(2010, 2024), step=1)
# selected_quarters = st.sidebar.multiselect("Select Quarter", sorted(df_frequency['Quarter'].unique()), default=sorted(df_frequency['Quarter'].unique()))
# selected_issue_area = st.sidebar.multiselect("Select Issue Area", sorted(df_frequency['issue_name'].unique()), default=sorted(df_frequency['issue_name'].unique()))
#
# # Filter the DataFrames
# filtered_df_frequency = df_frequency[
#     (df_frequency['Year'] >= selected_year_range[0]) &
#     (df_frequency['Year'] <= selected_year_range[1]) &
#     (df_frequency['Quarter'].isin(selected_quarters)) &
#     (df_frequency['issue_name'].isin(selected_issue_area))
# ]
#
# filtered_df_expenses = df_expenses[
#     (df_expenses['Year'] >= selected_year_range[0]) &
#     (df_expenses['Year'] <= selected_year_range[1]) &
#     (df_expenses['Quarter'].isin(selected_quarters)) &
#     (df_expenses['issue_name'].isin(selected_issue_area))
# ]
#
# # Aggregate and truncate data for bar charts
# frequency_by_issue = (
#     filtered_df_frequency.groupby('issue_name')['LDA_frequency']
#     .sum()
#     .reset_index(name='total_frequency')
#     .sort_values(by='total_frequency', ascending=False)
# )
#
# frequency_by_issue['short_issue_name'] = frequency_by_issue['issue_name'].apply(truncate_text)
#
# expenses_by_issue = (
#     filtered_df_expenses.groupby('issue_name')['lobbying_expenses']
#     .sum()
#     .reset_index()
#     .sort_values(by='lobbying_expenses', ascending=False)
# )
# expenses_by_issue['lobbying_expenses'] = expenses_by_issue['lobbying_expenses'] / 1_000_000  # Convert to millions
# expenses_by_issue['short_issue_name'] = expenses_by_issue['issue_name'].apply(truncate_text)
#
# # Mapping from short_issue_name to full issue_name
# short_to_full_mapping = dict(zip(frequency_by_issue['short_issue_name'], frequency_by_issue['issue_name']))
#
# # Plot Frequency Bar Chart
# st.markdown("### LDA Frequency by Issue Area")
# fig_freq = px.bar(
#     frequency_by_issue,
#     x='short_issue_name',
#     y='total_frequency',
#     labels={"total_frequency": "LDA Frequency", "short_issue_name": "Issue Name"},
#     text='total_frequency',  # Show values on bars
#     color_discrete_sequence=['teal'],
#     height=400,
#     width=1000,
#     category_orders={"short_issue_name": frequency_by_issue['short_issue_name'].tolist()}
# )
# fig_freq.update_layout(
#     xaxis_tickangle=-45,
#     xaxis_title=None,
#     yaxis_title="LDA Frequency",
#     uniformtext_minsize=10,
#     uniformtext_mode='hide'
# )
# selected_point_freq = plotly_events(fig_freq, click_event=True, override_height=400)
#
# # Plot Lobbying Expenses Bar Chart
# st.markdown("### LDA Lobbying Expenses by Issue Area")
# fig_expenses = px.bar(
#     expenses_by_issue,
#     x='short_issue_name',
#     y='lobbying_expenses',
#     labels={"lobbying_expenses": "LDA Lobbying Expenses ($ Million)", "short_issue_name": "Issue Name"},
#     text='lobbying_expenses',  # Show values on bars
#     color_discrete_sequence=['orange'],
#     height=400,
#     width=1000,
#     category_orders={"short_issue_name": expenses_by_issue['short_issue_name'].tolist()}
# )
# fig_expenses.update_layout(
#     xaxis_tickangle=-45,
#     xaxis_title=None,
#     yaxis_title="LDA Lobbying Expenses ($ Million)",
#     uniformtext_minsize=10,
#     uniformtext_mode='hide'
# )
# selected_point_expenses = plotly_events(fig_expenses, click_event=True, override_height=400)
#
#
# # # Plot Frequency Bar Chart
# # st.markdown("### LDA Frequency by Issue Area")
# # fig_freq = px.bar(
# #     frequency_by_issue,
# #     x='short_issue_name',
# #     y='total_frequency',
# #     labels={"total_frequency": "LDA Frequency", "short_issue_name": "Issue Name"},
# #     color_discrete_sequence=['teal'],
# #     height=400,
# #     width=1000,
# #     category_orders={"short_issue_name": frequency_by_issue['short_issue_name'].tolist()}
# # )
# # fig_freq.update_layout(xaxis_tickangle=-45, xaxis_title=None, yaxis_title="LDA Frequency")
# # selected_point_freq = plotly_events(fig_freq, click_event=True, override_height=400)
# #
# # # Plot Lobbying Expenses Bar Chart
# # st.markdown("### LDA Lobbying Expenses by Issue Area")
# # fig_expenses = px.bar(
# #     expenses_by_issue,
# #     x='short_issue_name',
# #     y='lobbying_expenses',
# #     labels={"lobbying_expenses": "LDA Lobbying Expenses ($ Million)", "short_issue_name": "Issue Name"},
# #     color_discrete_sequence=['orange'],
# #     height=400,
# #     width=1000,
# #     category_orders={"short_issue_name": expenses_by_issue['short_issue_name'].tolist()}
# # )
# # fig_expenses.update_layout(xaxis_tickangle=-45, xaxis_title=None, yaxis_title="LDA Lobbying Expenses ($ Million)")
# # selected_point_expenses = plotly_events(fig_expenses, click_event=True, override_height=400)
#
# # Determine the selected issue area
# selected_issue = None
# if selected_point_freq:
#     short_name_selected = selected_point_freq[0]['x']
#     selected_issue = short_to_full_mapping.get(short_name_selected)
# elif selected_point_expenses:
#     short_name_selected = selected_point_expenses[0]['x']
#     selected_issue = short_to_full_mapping.get(short_name_selected)
#
# # Time Series Plot for Frequency and Expenses
# if selected_issue:
#     st.markdown(f"## Time Series Line Plot for {selected_issue}")
#
#     # Frequency Time Series
#     issue_data_freq = (
#         filtered_df_frequency[filtered_df_frequency['issue_name'] == selected_issue]
#         .groupby(['Year', 'Quarter'])
#         .size()
#         .reset_index(name='Frequency')
#     )
#     issue_data_freq['Year_Quarter'] = issue_data_freq['Year'].astype(str) + " Q" + issue_data_freq['Quarter'].astype(str)
#
#     if not issue_data_freq.empty:
#         st.markdown(f"### LDA Frequency Over Time for {selected_issue}")
#         plt.figure(figsize=(10, 4))
#         plt.plot(issue_data_freq['Year_Quarter'], issue_data_freq['Frequency'], marker='o', linestyle='-', color='teal')
#         plt.xlabel("Year-Quarter")
#         plt.ylabel("Frequency")
#         plt.xticks(rotation=45, fontsize=8)
#         plt.grid(True)
#         plt.tight_layout()
#         st.pyplot(plt)
#         plt.clf()
#     else:
#         st.write("No frequency data available for this issue area.")
#
#     # Expenses Time Series
#     issue_data_exp = (
#         filtered_df_expenses[filtered_df_expenses['issue_name'] == selected_issue]
#         .groupby(['Year', 'Quarter'])['lobbying_expenses']
#         .sum()
#         .reset_index()
#     )
#     issue_data_exp['Year_Quarter'] = issue_data_exp['Year'].astype(str) + " Q" + issue_data_exp['Quarter'].astype(str)
#     issue_data_exp['lobbying_expenses'] = issue_data_exp['lobbying_expenses'] / 1_000_000  # Convert to millions
#
#     if not issue_data_exp.empty:
#         st.markdown(f"### LDA Lobbying Expenses Over Time for {selected_issue} (in Millions)")
#         plt.figure(figsize=(10, 4))
#         plt.plot(issue_data_exp['Year_Quarter'], issue_data_exp['lobbying_expenses'], marker='o', linestyle='-', color='orange')
#         plt.xlabel("Year-Quarter")
#         plt.ylabel("Lobbying Expenses (in Millions)")
#         plt.xticks(rotation=45, fontsize=8)
#         plt.grid(True)
#         plt.tight_layout()
#         st.pyplot(plt)
#         plt.clf()
#     else:
#         st.write("No lobbying expenses data available for this issue area.")
#





# # Streamlit App
# st.title("Interactive Lobbying Data Dashboard")
# st.markdown("### Comparing LDA Frequency and Lobbying Expenses by Issue Area")
#
# # Sidebar Filters with Ordered Options
# st.sidebar.header("Filters")
#
# # Order the Year range and issue_name list
# ordered_years = sorted(df_frequency['Year'].unique())  # Numeric order for years
#
# selected_year_range = st.sidebar.slider("Select Year Range", min_value=min(ordered_years), max_value=max(ordered_years), value=(2010, 2024), step=1)
#
#
# # For Quarter, ensure it's sorted in numeric order (1, 2, 3, 4)
# ordered_quarters = sorted(df_frequency['Quarter'].unique())
# selected_quarters = st.sidebar.multiselect("Select Quarter", ordered_quarters, default=ordered_quarters)
# # Order issue_name list
# ordered_issue_names = sorted(df_frequency['issue_name'].unique())  # Alphabetical order for issue names
#
# selected_issue_area = st.sidebar.multiselect("Select Issue Area", ordered_issue_names, default=ordered_issue_names)
#
#
# # Filter the DataFrames
# filtered_df_frequency = df_frequency[
#     (df_frequency['Year'] >= selected_year_range[0]) &
#     (df_frequency['Year'] <= selected_year_range[1]) &
#     (df_frequency['Quarter'].isin(selected_quarters)) &
#     (df_frequency['issue_name'].isin(selected_issue_area))
#     ]
#
# filtered_df_expenses = df_expenses[
#     (df_expenses['Year'] >= selected_year_range[0]) &
#     (df_expenses['Year'] <= selected_year_range[1]) &
#     (df_expenses['Quarter'].isin(selected_quarters)) &
#     (df_expenses['issue_name'].isin(selected_issue_area))
#     ]
#
# # Display selected year range
# st.markdown(f"### Selected Year Range: {selected_year_range[0]} to {selected_year_range[1]}")
#
# # Aggregate Data
# # Frequency: Count unique rows based on 'Date'
# frequency_data = filtered_df_frequency.groupby('issue_name')['LDA_frequency'].sum().reset_index(name='Total Frequency')
# # Expenses: Sum up the 'lobbying_expenses'
# expenses_data = filtered_df_expenses.groupby('issue_name')['lobbying_expenses'].sum().reset_index(name='Total Expenses')
#
# # Side-by-side bar charts with different colors and larger plot size
# col1, col2 = st.columns(2)
#
# # Interactive LDA Frequency Bar Chart
# st.markdown("### LDA Frequency by Issue Area")
# fig_bar1 = px.bar(frequency_data, x='issue_name', y='Total Frequency',
#                   height=800, color_discrete_sequence=['teal'])
# fig_bar1.update_layout(xaxis_title='Issue Area', yaxis_title='Frequency', bargap=0.2, xaxis_tickangle=-45)
# st.plotly_chart(fig_bar1, use_container_width=True)
#
# # Interactive Lobbying Expenses Bar Chart
# st.markdown("### LDA Lobbying Expenses by Issue Area")
# fig_bar2 = px.bar(expenses_data, x='issue_name', y='Total Expenses',
#                   height=800, color_discrete_sequence=['orange'])
# fig_bar2.update_layout(xaxis_title='Issue Area', yaxis_title='Total Expenses ($)', bargap=0.2, xaxis_tickangle=-45)
# st.plotly_chart(fig_bar2, use_container_width=True)



# # Dropdown for selecting an issue area to view its time series plot
# st.markdown("### Time Series Line Plot for a Specific Issue Area")
# selected_issue = st.selectbox("Select an Issue Area for Time Series Analysis", frequency_data['issue_name'].unique())
#
# # Time Series Plot for Frequency
# issue_data_freq = df_frequency[df_frequency['issue_name'] == selected_issue].groupby(['Year', 'Quarter'])['LDA_frequency'].sum().reset_index()
# issue_data_freq['Year_Quarter'] = issue_data_freq['Year'].astype(str) + " Q" + issue_data_freq['Quarter'].astype(str)
#
# if not issue_data_freq.empty:
#     st.markdown(f"#### LDA Frequency Over Time for {selected_issue}")
#     plt.figure(figsize=(12, 6))
#     plt.plot(issue_data_freq['Year_Quarter'], issue_data_freq['LDA_frequency'], marker='o', linestyle='-', color='teal')
#     plt.xlabel("Year-Quarter")
#     plt.ylabel("Frequency")
#     plt.xticks(rotation=45, fontsize=8)
#     plt.grid(True)
#     plt.tight_layout()
#     st.pyplot(plt)
#     plt.clf()
# else:
#     st.write(f"No frequency data available for {selected_issue}.")
#
# # Time Series Plot for Lobbying Expenses
# issue_data_exp = df_expenses[df_expenses['issue_name'] == selected_issue].groupby(['Year', 'Quarter'])['lobbying_expenses'].sum().reset_index()
# issue_data_exp['Year_Quarter'] = issue_data_exp['Year'].astype(str) + " Q" + issue_data_exp['Quarter'].astype(str)
# issue_data_exp['lobbying_expenses'] = issue_data_exp['lobbying_expenses'] / 1_000_000  # Convert to millions
#
# if not issue_data_exp.empty:
#     st.markdown(f"#### LDA Lobbying Expenses Over Time for {selected_issue} (in Millions)")
#     plt.figure(figsize=(12, 6))
#     plt.plot(issue_data_exp['Year_Quarter'], issue_data_exp['lobbying_expenses'], marker='o', linestyle='-', color='orange')
#     plt.xlabel("Year-Quarter")
#     plt.ylabel("Lobbying Expenses (in Millions)")
#     plt.xticks(rotation=45, fontsize=8)
#     plt.grid(True)
#     plt.tight_layout()
#     st.pyplot(plt)
#     plt.clf()
# else:
#     st.write(f"No lobbying expenses data available for {selected_issue}.")




# # Aggregate data by Year and Quarter for frequency
# frequency_by_year_quarter = filtered_df_frequency.groupby(['Year', 'Quarter', 'issue_name'])['LDA_frequency'].sum().reset_index()
# frequency_by_year_quarter['Year_Quarter'] = frequency_by_year_quarter['Year'].astype(str) + " Q" + frequency_by_year_quarter['Quarter'].astype(str)
#
# # Aggregate data by Year and Quarter for lobbying expenses
# expenses_by_year_quarter = filtered_df_expenses.groupby(['Year', 'Quarter', 'issue_name'])['lobbying_expenses'].sum().reset_index()
# expenses_by_year_quarter['Year_Quarter'] = expenses_by_year_quarter['Year'].astype(str) + " Q" + expenses_by_year_quarter['Quarter'].astype(str)
#
# # Generate plots for each selected issue area
# for issue in selected_issue_area:
#     st.markdown(f"## {issue}")
#
#     # Frequency Plot
#     issue_data_freq = frequency_by_year_quarter[frequency_by_year_quarter['issue_name'] == issue]
#     st.markdown("### LDA Frequency Over Time")
#     if issue_data_freq.empty:
#         st.write("No frequency data available for this issue area.")
#     else:
#         plt.figure(figsize=(12, 6))
#         plt.plot(issue_data_freq['Year_Quarter'], issue_data_freq['LDA_frequency'], marker='o', linestyle='-', color='teal', label=issue)
#         plt.xlabel("Year-Quarter")
#         plt.ylabel("Frequency")
#         plt.xticks(rotation=45, fontsize=8)
#         plt.grid(True)
#         plt.tight_layout()
#         st.pyplot(plt)
#         plt.clf()
#
#     # Lobbying Expenses Plot
#     # Lobbying Expenses Plot (Y-axis in Millions)
#     issue_data_exp = expenses_by_year_quarter[expenses_by_year_quarter['issue_name'] == issue]
#     issue_data_exp['lobbying_expenses_million'] = issue_data_exp['lobbying_expenses'] / 1_000_000  # Convert to millions
#     st.markdown("### LDA Lobbying Expenses Over Time")
#     if issue_data_exp.empty:
#         st.write("No lobbying expense data available for this issue area.")
#     else:
#         plt.figure(figsize=(12, 6))
#         plt.plot(issue_data_exp['Year_Quarter'], issue_data_exp['lobbying_expenses_million'], marker='o', linestyle='-',
#                  color='orange', label=issue)
#         plt.xlabel("Year-Quarter")
#         plt.ylabel("Lobbying Expenses (in Millions)")
#         plt.xticks(rotation=45, fontsize=8)
#         plt.grid(True)
#         plt.tight_layout()
#         st.pyplot(plt)
