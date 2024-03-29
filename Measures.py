from datetime import datetime, timedelta

import pyodbc
import pandas as pd

def config_setup():
    db_filepath = r'D:\Data\Documents\Business\Pandecia Bakery\Database\Pandecia.accdb'
    conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + db_filepath + ';'
    conn = pyodbc.connect(conn_str)
    return conn



def measures():
    conn = config_setup()
    ### Distinct Measure ###
    sql = f"""
        SELECT
            COUNT(*) AS order_count,
            month_year,
            branch_name
        FROM 
            (SELECT DISTINCT [reference],
            FORMAT(DATA.business_date, 'yyyy-mm') as month_year,
            [DATA.branch_name] as branch_name
            FROM DATA)
        GROUP BY
            month_year, branch_name
        ORDER BY
            month_year, branch_name;
    """
    order_count = pd.read_sql(sql, conn)

    ### Distinct Measure ###
    sql = f"""
        SELECT
            COUNT(*) AS order_count,
            month_year,
            branch_name
        FROM 
            (
            SELECT DISTINCT [reference],
            FORMAT(DATA.business_date, 'yyyy-mm') as month_year,
            [DATA.branch_name] as branch_name
            FROM DATA
            WHERE [DATA.status] = 'Done'
            )
        GROUP BY
            month_year, branch_name
        ORDER BY
            month_year, branch_name;
    """
    confirmed_orders = pd.read_sql(sql, conn)

    ### Universal Measure ###
    sql = f"""
        SELECT 
            FORMAT(business_date, 'yyyy-mm') AS month_year,
            [branch_name],
            SUM([discounts line]) AS discount_amount,
            SUM(IIF([status] = 'Done', [tax exclusive discount amount order line], 0)) AS tax_exclusive_discount,
            SUM(IIF([ITEMSstatus] = 'Done' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) AS item_total_done,
            SUM(IIF([ITEMSstatus] = 'Returned' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) AS order_item_return_total_price,
            SUM(IIF([ITEMSstatus] = 'Done' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) -
            SUM(IIF([ITEMSstatus] = 'Returned' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) AS item_total_cost,
            SUM(IIF([ITEMSstatus] = 'Done', [ITEMSquantity], 0)) AS done_item_count,
            SUM(IIF([ITEMSstatus] = 'Returned', [ITEMSquantity], 0)) AS returned_item_count,
            SUM(IIF([status] = 'Returned', [tax exclusive discount amount order line], 0)) AS returned_discount,
            SUM(IIF([ITEMSstatus] = 'Done', [ITEMStax_exclusive_discount_amount], 0)) AS product_discount,
            SUM(IIF([status] = 'Done', [total taxes line], 0)) -
            SUM(IIF([status] = 'Returned', [total taxes line], 0)) AS total_tax_amount,
            SUM([ITEMSquantity]) AS total_qty,
            SUM(IIF([ITEMSstatus] = 'Returned' AND [ITEMStype] = 'Product', [ITEMSquantity], 0)) AS qty_returned,
            SUM(IIF([ITEMSstatus] = 'Void' AND [ITEMStype] = 'Product', [ITEMSquantity], 0)) AS qty_void,
            SUM(IIF([ITEMSstatus] = 'Done' AND [ITEMStype] = 'Product', [ITEMSquantity], 0))  -
            SUM(IIF([ITEMSstatus] = 'Returned' AND [ITEMStype] = 'Product', [ITEMSquantity], 0)) AS product_sold,
            SUM(IIF([ITEMSstatus] = 'Void' AND [ITEMStype] = 'Product', [ITEMStax_exclusive_total_price], 0)) +
            SUM(IIF([ITEMSstatus] = 'Void' AND [ITEMStype] = 'Product', [ITEMStax_exclusive_discount_amount], 0)) as void_amount,
            SUM(IIF([ITEMSstatus] = 'Returned' AND [ITEMStype] = 'Product', [total_price], 0)) as returned_amount
        FROM 
            DATA
        GROUP BY 
            FORMAT(business_date, 'yyyy-mm'), [branch_name]
        ORDER BY 
            FORMAT(business_date, 'yyyy-mm'), [branch_name];
    """
    main_df = pd.read_sql(sql, conn)

    df = pd.merge(pd.merge(main_df, order_count, on=['month_year', 'branch_name']), confirmed_orders, on=['month_year', 'branch_name'])
    df['total_discount_amount'] = df['tax_exclusive_discount'] - df['returned_discount'] + df['product_discount']
    df['total_gross_amount'] = (df['item_total_cost'] + df['total_discount_amount']) - df['discount_amount']
    df['total_net_sales'] = df['total_gross_amount'] - df['total_discount_amount'] - df['total_tax_amount']
    df.rename(columns={'order_count_x': 'order_count'}, inplace=True)
    df.rename(columns={'order_count_y': 'confirmed_orders'}, inplace=True)
    df['gross_sales_without_tax'] = df['total_net_sales'] + df['total_discount_amount']
    df['net_sales_with_tax'] = df['total_net_sales'] + df['total_tax_amount']
    conn.close()
    return df

def prev_month_string_function(str_month):
    date_obj = datetime.strptime(str_month, '%Y-%m')
    previous_month = date_obj.replace(day=1) - timedelta(days=1)
    previous_month_str = previous_month.strftime('%Y-%m')
    return previous_month_str

def metrics(measures_df, sel_month):
    barsha_cur_month_sales = measures_df[(measures_df['branch_name'] == 'Barsha') & (measures_df['month_year'] == sel_month)]['total_net_sales'].iloc[0]
    satwa_cur_month_sales = \
    measures_df[(measures_df['branch_name'] == 'Satwa') & (measures_df['month_year'] == sel_month)]['total_net_sales'].iloc[0]
    return barsha_cur_month_sales, satwa_cur_month_sales