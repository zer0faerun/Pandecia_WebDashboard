import streamlit as st
import gspread
import pandas as pd
import pyodbc

# Connect to Google Sheets
gc = gspread.service_account(filename='path/to/credentials.json')
sh = gc.open('Google Sheets Workbook Name')
worksheet = sh.sheet1
data_from_sheets = worksheet.get_all_records()
df_sheets = pd.DataFrame(data_from_sheets)

# Connect to MS Access Database
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=path/to/your/database.accdb;'
)
conn = pyodbc.connect(conn_str)

# Retrieve data from MS Access
query = "SELECT * FROM YourTable"
df_access = pd.read_sql(query, conn)

# Display data in Streamlit
st.write("Data from Google Sheets:")
st.write(df_sheets)

st.write("Data from MS Access:")
st.write(df_access)