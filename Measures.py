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
            b_month,
            branch
        FROM 
            (SELECT DISTINCT [reference],
            FORMAT(DATA.business_date, 'yyyy-mm') as b_month,
            [DATA.branch_name] as branch
            FROM DATA)
        GROUP BY
            b_month, branch
        ORDER BY
            b_month, branch;
    """
    order_count = pd.read_sql(sql, conn)

    ### Distinct Measure ###
    sql = f"""
        SELECT
            COUNT(*) AS order_count,
            b_month,
            branch
        FROM 
            (
            SELECT DISTINCT [reference],
            FORMAT(DATA.business_date, 'yyyy-mm') as b_month,
            [DATA.branch_name] as branch
            FROM DATA
            WHERE [DATA.status] = 'Done'
            )
        GROUP BY
            b_month, branch
        ORDER BY
            b_month, branch;
    """
    confirmed_orders = pd.read_sql(sql, conn)

    ### Universal Measure ###
    sql = f"""
        SELECT 
            FORMAT(business_date, 'yyyy-mm') AS month_year,
            [branch_name],
            SUM([discounts line]) AS discount_amount,
            SUM(IIF([Status] = 'Done', [tax_exclusive_discount_amount], 0)) AS tax_exclusive_discount,
            SUM(IIF([ITEMSstatus] = 'Done' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) AS item_total_done,
            SUM(IIF([ITEMSstatus] = 'Returned' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) AS order_item_return_total_price,
            SUM(IIF([ITEMSstatus] = 'Returned' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) - 
            SUM(IIF([ITEMSstatus] = 'Done' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) AS item_total_cost,
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
            SUM(IIF([ITEMSstatus] = 'ITEMSstatus' AND [ITEMStype] = 'Product', [total_price], 0)) as returned_amount
        FROM 
            DATA
        GROUP BY 
            FORMAT(business_date, 'yyyy-mm'), [branch_name]
        ORDER BY 
            FORMAT(business_date, 'yyyy-mm'), [branch_name];
    """
    df = pd.read_sql(sql, conn)

    conn.close()
    return df




