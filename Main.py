import streamlit as st
import pandas as pd
from tqdm import tqdm
from chart import ytd_bar_chart
from Measures import config_setup, prev_month_string_function, metrics
from Measures import measures
from datetime import datetime, timedelta

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")


@st.cache_data
def load_data(month,branch_filter):
    conn = config_setup()
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
    measures_df = measures()
    #data_df = load_data(sel_month, sel_branch)
    filtered_measures_df = measures_df[measures_df['branch_name'].isin(sel_branch)]
    #filtered_measures_df

    # Header metrics #
    prev_month_sel = prev_month_string_function(sel_month)
    barsha_cur_month_sales, satwa_cur_month_sales = metrics(measures_df,sel_month)
    barsha_prev_month_sales, satwa_prev_month_sales = metrics(measures_df, prev_month_sel)
    barsha_delta = barsha_cur_month_sales - barsha_prev_month_sales
    satwa_delta = satwa_cur_month_sales - satwa_prev_month_sales
    metric_col = st.columns(2)
    with metric_col[0]:
        st.metric(label="Barsha Sales", value="{:,.1f}k".format(barsha_cur_month_sales/1000), label_visibility="visible", delta="{:,.1f}k".format(barsha_delta/1000))
    with metric_col[1]:
        st.metric(label="Satwa Sales", value="{:,.1f}k".format(satwa_cur_month_sales/1000), label_visibility="visible", delta="{:,.1f}k".format(satwa_delta/1000))

    ytd_values = measures_df.groupby(['month_year', 'branch_name'])['total_net_sales'].sum().reset_index()
    ytd_bar_chart(ytd_values[ytd_values['branch_name'].isin(sel_branch)])









if __name__ == '__main__':
    main()




