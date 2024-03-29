import streamlit as st
import pandas as pd
from tqdm import tqdm
from streamlit_echarts import st_echarts
from Measures import config_setup
from Measures import measures
st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

@st.cache_data
def load_data(month,branch_filter):
    conn = config_setup()
    #total_rows = pd.read_sql(f"SELECT COUNT(*) as count FROM DATA WHERE [Year Month] IN ('{month}') AND WHERE [branch_name] in {branch}", conn)['count'][0]
    total_rows = pd.read_sql(
        f"SELECT COUNT(*) as count FROM DATA WHERE [Year Month] IN ('{month}') AND [branch_name] IN {tuple(branch_filter)}",conn)['count'][0]
    print(total_rows)
    tqdm.pandas()
    df_list = []
    for chunk in tqdm(pd.read_sql(f"SELECT * FROM DATA WHERE [Year Month] IN ('{month}') AND [branch_name] IN {tuple(branch_filter)}", conn, chunksize=1000), total=total_rows//1000 + 1):
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
    query = "SELECT DISTINCT [branch_name] FROM DATA"
    branch_filters = [row[0] for row in conn.execute(query)]
    conn.close()
    return year_month, branch_filters

def main():
    st.title('Pandecia Dashboard')
    year_month, branch_filters = load_filters()
    sel_branch = st.sidebar.multiselect("Select Branch:", options=branch_filters, default=branch_filters)
    sel_month = st.sidebar.selectbox("Select Year Month:", year_month)
    data_df = load_data(sel_month, sel_branch)

    a = measures()
    a
    print(data_df.dtypes)

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




