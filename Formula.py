import pandas as pd
import pyodbc
from tqdm import tqdm
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

 @st.cache
 def load_data():
     # Read the entire table into a DataFrame with progress bar terminal
     df = pd.read_sql("SELECT * FROM DATA WHERE [Year Month] IN ('2024-01', '2024-02')", conn, chunksize=1000)
     df = pd.DataFrame
     df_list = []
     progress_bar = st.progress(0)
     for i, chunk in enumerate(tqdm(df, total=total_rows//1000 + 1)):
         df_list.append(chunk)
         progress_value = (i + 1) / (total_rows//1000 + 1)  # Normalize the progress value
         progress_bar.progress(progress_value)
      df = pd.concat(df_list, ignore_index=True)

     # Close the connection
     conn.close()

     db_filepath = r'D:\Data\Documents\Business\Pandecia Bakery\Database\Pandecia.accdb'
     conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + db_filepath + ';'
     conn = pyodbc.connect(conn_str)

     total_rows = \
     pd.read_sql("SELECT COUNT(*) as count FROM DATA WHERE [Year Month] IN ('2024-01', '2024-02')", conn)['count'][0]

     # Initialize tqdm to create a progress bar
     tqdm.pandas()
     return df

 def main():
     st.title('Streamlit App with Large Dataset')

     # Load the data once
     data = load_data()

     # Display the dataset
     st.write(data)

 if __name__ == '__main__':
     main()





# database


# Read the entire table into a DataFrame with progress bar terminal
#df = pd.read_sql("SELECT * FROM DATA WHERE [Year Month] IN ('2024-01', '2024-02')", conn, chunksize=1000)
#df = pd.DataFrame
#df_list = []
#progress_bar = st.progress(0)
#for i, chunk in enumerate(tqdm(df, total=total_rows//1000 + 1)):
#    df_list.append(chunk)
#    progress_value = (i + 1) / (total_rows//1000 + 1)  # Normalize the progress value
#    progress_bar.progress(progress_value)
#df = pd.concat(df_list, ignore_index=True)



# Close the connection
#conn.close()

# Sidebar Prep #################################
st.sidebar.header("Please Filter Here:")
branch = st.sidebar.multiselect(
    "Select the Branch:",
    options=df["branch_name"].unique(),
    default=df["branch_name"].unique()
)

#month = st.sidebar.multiselect(
#    "Select the Year Month:",
#    options=df["Year month"].unique(),
#    default=df["Year month"].unique()
#)



# assign calculations #############################################################
discounts_sum = df['discounts line'].sum() #done
order_count = df['reference'].nunique() #done
tax_exclusive_discount = df.loc[df['status'] == 'Done', 'tax exclusive discount amount order line'].sum() #done
order_item_return_total_price = df.loc[(df['ITEMSstatus'] == 'Returned') & (df['ITEMStype'] == 'Product'), 'ITEMStotal_price'].sum() #done
item_total_cost = df.loc[(df['ITEMSstatus'] == 'Done') & (df['ITEMStype'] == 'Product'), 'ITEMStotal_price'].sum() - order_item_return_total_price #done
item_count = df['ITEMSquantity'].sum() #done
done_item_count = df.loc[df['ITEMSstatus'] == "Done"]['ITEMSquantity'].sum() #done
returned_item_count = df.loc[df['ITEMSstatus'] == "Returned"]['ITEMSquantity'].sum() #done
returned_discount = df.loc[df['status'] == 'Returned', 'tax exclusive discount amount order line'].sum() #d
product_discount = df.loc[df['ITEMSstatus'] == 'Done', 'ITEMStax_exclusive_discount_amount'].sum() #d
total_discount_amount = tax_exclusive_discount - returned_discount + product_discount #later
total_gross_amount = (item_total_cost + total_discount_amount) - discounts_sum #later
returned_tax = df.loc[df['status'] == 'Returned', 'total taxes line'].sum() #d
total_tax_amount = df.loc[df['status'] == 'Done', 'total taxes line'].sum() - returned_tax #
total_net_sales = total_gross_amount - total_discount_amount - total_tax_amount #later
net_sales_with_tax = total_net_sales + total_tax_amount #later
gross_sales_without_tax = total_net_sales + total_discount_amount #laater
confirmed_orders = df.loc[df['status'] == 'Done', 'reference'].nunique()
total_qty = df['ITEMSquantity'].sum()
qty_returned = df.loc[(df['ITEMSstatus'] == 'Returned') & (df['ITEMStype'] == 'Product'), 'ITEMSquantity'].sum()
qty_void = df.loc[(df['ITEMSstatus'] == 'Void') & (df['ITEMStype'] == 'Product'), 'ITEMSquantity'].sum()
product_sold = df.loc[(df['ITEMSstatus'] == 'Done') & (df['ITEMStype'] == 'Product'), 'ITEMSquantity'].sum() - qty_returned
void_amount = df.loc[(df['ITEMSstatus'] == 'Void') & (df['ITEMStype'] == 'Product'), 'ITEMStax_exclusive_total_price'].sum() + df.loc[(df['ITEMSstatus'] == 'Void') & (df['ITEMStype'] == 'Product'), 'ITEMStax_exclusive_discount_amount'].sum()
returned_amount = df.loc[(df['ITEMSstatus'] == 'Returned') & (df['ITEMStype'] == 'Product'), 'total_price'].sum()
avg_unit_price = df['ITEMSunit_price'].mean()



# Calculate the product growth MOM
selected_month = df['business_date'].max()
current_month = selected_month.to_period('M').strftime('%Y-%m')
last_month = (selected_month - pd.DateOffset(months=1)).to_period('M').strftime('%Y-%m')

#c_month_sales = df.loc[df['Year Month'] == current_month, Total Net Sales].sum()
#l_month_sales = df.loc[df['Year Month'] == last_month, 'Total Net Sales'].sum()

#amount_var = c_month_sales - l_month_sales
#growth = amount_var / l_month_sales if l_month_sales != 0 else np.nan

#total_avg_growth = df.groupby('MONTH').apply(lambda x: (x['Total Net Sales'].sum() - x['Total Net Sales'].shift(1).sum()) / x['Total Net Sales'].shift(1).sum() if len(x) > 1 else np.nan).mean()

#grant_tot = total_avg_growth if len(df['MONTH'].unique()) == 1 else growth

echarts_code = """
<div id="main" style="width: 600px;height:400px;"></div>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.3.0/dist/echarts.min.js"></script>
<script>
   var myChart = echarts.init(document.getElementById('main'));
   var option = {
       title: {
           text: 'ECharts in Streamlit'
       },
       tooltip: {},
       legend: {
           data:['Sales']
       },
       xAxis: {
           data: ["Shoes", "Bags", "Clothes", "Accessories", "Jewelry"]
       },
       yAxis: {},
       series: [{
           name: 'Sales',
           type: 'bar',
           data: [150, 200, 300, 180, 250]
       }]
   };
   myChart.setOption(option);
</script>
"""

st.components.v1.html(echarts_code)

sql = f"""
    SELECT 
        FORMAT(business_date, 'yyyy-mm') AS month,
        [branch_name],
        COUNT(*)
    FROM 
        DATA
    GROUP BY 
        FORMAT(business_date, 'yyyy-mm'), [branch_name]
    ORDER BY 
        FORMAT(business_date, 'yyyy-mm'), [branch_name];
"""