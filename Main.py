import streamlit as st
import pandas as pd
import pyodbc
from tqdm import tqdm
from streamlit_echarts import st_echarts
st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

def config_setup():
    db_filepath = r'D:\Data\Documents\Business\Pandecia Bakery\Database\Pandecia.accdb'
    conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + db_filepath + ';'
    conn = pyodbc.connect(conn_str)
    return conn

@st.cache_data
def load_data(month):
    conn = config_setup()
    total_rows = pd.read_sql(f"SELECT COUNT(*) as count FROM DATA WHERE [Year Month] IN ('{month}')", conn)['count'][0]
    print(total_rows)
    tqdm.pandas()
    df_list = []
    for chunk in tqdm(pd.read_sql(f"SELECT * FROM DATA WHERE [Year Month] IN ('{month}')", conn, chunksize=1000), total=total_rows//1000 + 1):
        df_list.append(chunk)
    df = pd.concat(df_list, ignore_index=True)

    #drop some columns
    col_to_drop = ['external_number',
                   'branch_reference',
                   'original_order_reference',
                   'coupon_code',
                   'coupon_name',
                   'rounding',
                   'accepted_at',
                   'due_at',
                   'tags',
                   'customer_name', 'customer_dial_code',
                   'customer_phone', 'customer_address_delivery_zone_name',
                   'customer_address_name', 'customer_address_description',
                   'receipt_notes', 'kitchen_notes', 'kitchen_received_at',
                   'kitchen_done_at', 'preparation_period']
    df.drop(columns=col_to_drop, inplace=True)
    return df

def load_filters():
    conn = config_setup()
    query = "SELECT DISTINCT [Year Month] FROM DATA;"
    year_month = [row[0] for row in conn.execute(query)]
    conn.close()
    return year_month

def measures():
    conn = config_setup()
    q_discount = f"""
    SELECT 
        FORMAT(business_date, 'yyyy-mm') AS month,
        [branch_name],
        SUM([discounts line]) AS discount_amount
    FROM 
        DATA
    GROUP BY 
        FORMAT(business_date, 'yyyy-mm'), [branch_name]
    ORDER BY 
        FORMAT(business_date, 'yyyy-mm'), [branch_name];
    """



    df = pd.read_sql(q_discount, conn)

    # Close the database connection
    conn.close()

    # Display the DataFrame



    return df

def main():
    st.title('Streamlit App with Large Dataset')
    year_month = load_filters()
    sel_month = st.sidebar.selectbox("Select Year Month:", year_month)
    data_df = load_data(sel_month)

    a = measures()
    a
    st.write(data_df)

    options = {
        "xAxis": {
            "type": "category",
            "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "data": [
                    120,
                    {"value": 200, "itemStyle": {"color": "#a90000"}},
                    150,
                    80,
                    70,
                    110,
                    130,
                ],
                "type": "bar",
            }
        ],
    }
    st_echarts(
        options=options,
        height="400px",
    )



if __name__ == '__main__':
    main()




