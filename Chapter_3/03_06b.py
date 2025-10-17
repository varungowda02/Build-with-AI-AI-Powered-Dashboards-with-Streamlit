#Build with AI: AI-Powered Dashboards with Streamlit 
#Identify Key Metrics (KPIs) with the Help of AI

#Import packages
import streamlit as st
import pandas as pd
import os, pickle
from openai import OpenAI
import numpy as np

#Open file with API key
with open("openai_key.txt") as f:
    my_api_key = f.read().strip()

#Initialize OpenAI client with your API key
client = OpenAI(api_key=my_api_key)

#Write title
st.title("Identify KPI Metrics")

#Check if cleaned dataset exists, stop app if not found
if not os.path.exists("cleaned_data_final.pkl"):
    st.error("No cleaned dataset found. Please complete previous lessons first.")
    st.stop()

#Load cleaned dataset from pickle file
with open("cleaned_data_final.pkl", "rb") as f:
    df = pickle.load(f)

#Add subheader for cleaned data preview
st.subheader("Cleaned Data Preview")
#Display first few rows of cleaned data
st.dataframe(df.head())

#Build a summary of each column’s data type, values, and stats
column_summaries = []
#Loop through each column in the dataframe
for col in df.columns:
    #Check if column is numeric and capture min and max values
    if pd.api.types.is_numeric_dtype(df[col]):
        col_summary = f"- `{col}` (numeric): min = {df[col].min()}, max = {df[col].max()}"
    #Check if column is date type and capture date range
    elif pd.api.types.is_datetime64_any_dtype(df[col]):
        col_summary = f"- `{col}` (date): min = {df[col].min().date()}, max = {df[col].max().date()}"
    #Otherwise treat as categorical or text and capture sample values
    else:
        unique_vals = df[col].dropna().unique()
        sample_vals = ", ".join(map(str, unique_vals[:5]))
        col_summary = f"- `{col}` (categorical/text): example values = {sample_vals}"
    #Add column summary to list
    column_summaries.append(col_summary)

#Convert list of column summaries into markdown-formatted string
column_summary_md = "\n".join(column_summaries)

#Create text input area for user to request KPI suggestions or targeted metric questions
user_prompt = st.text_area(
    "Ask for KPI suggestions (or targeted metric questions like 'Which expense metrics should I focus on?')",
    height=200
)

#Check if 'Generate KPI Suggestions' button is clicked
if st.button("Generate KPI Suggestions"):
    #Provide warning if user has not entered a request
    if not user_prompt.strip():
        st.warning("Please enter a request above.")
    else:
        #Display spinner while querying AI
        with st.spinner("AI is analyzing your data for KPI ideas…"):
            try:
                #Construct system prompt to explain available columns and instructions for AI
                system_prompt = (
                    f"You are a data-savvy Python analyst. The pandas DataFrame `df` has the following columns:\n\n"
                    f"{column_summary_md}\n\n"
                    "When asked, return a Markdown-formatted, numbered list of 4–6 KPI metrics or insights to visualize. "
                    "For each KPI, provide:\n"
                    "- A clear title\n"
                    "- Which column(s) to use\n"
                    "- A suggested chart type\n"
                    "- A brief rationale\n\n"
                    "If the user asks a targeted question (e.g. 'Which expense metrics should I focus on?'), "
                    "tailor your recommendations accordingly. "
                    "Do NOT return any code, only a clean, well-formatted Markdown list."
                )

                #Send prompt and system instructions to OpenAI LLM and receive response
                resp = client.chat.completions.create(
                    #Select model
                    model="gpt-3.5-turbo",
                    messages=[
                        #Provide system instructions
                        {"role": "system", "content": system_prompt},
                        #Send user's prompt
                        {"role": "user", "content": user_prompt}
                    ]
                )

                #Extract assistant's reply
                kpi_suggestions = resp.choices[0].message.content
                st.subheader("AI‑Recommended KPI Metrics & Charts")
                #Display assistant's suggestions as markdown
                st.markdown(kpi_suggestions)

            #Handle API errors and display message if request fails
            except Exception as e:
                st.error(f"Error generating KPI suggestions: {e}")
