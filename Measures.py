import pyodbc
import pandas as pd

def config_setup():
    db_filepath = r'D:\Data\Documents\Business\Pandecia Bakery\Database\Pandecia.accdb'
    conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + db_filepath + ';'
    conn = pyodbc.connect(conn_str)
    return conn



def measures():
    conn = config_setup()
    ### Discount Measures ###
    sql1 = f"""
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
    #discount_df = pd.read_sql(sql, conn)

    ### Order Count ###
    sql = f"""
        SELECT 
            FORMAT(business_date, 'yyyy-mm') AS month,
            [branch_name],
            COUNT(DISTINCT [reference]) AS order_count
        FROM 
            DATA
        GROUP BY 
            FORMAT(business_date, 'yyyy-mm'), [branch_name]
        ORDER BY 
            FORMAT(business_date, 'yyyy-mm'), [branch_name];
    """
    #order_count_df = pd.read_sql(sql, conn)

    sql = f"""
        SELECT 
            FORMAT(business_date, 'yyyy-mm') AS month,
            [branch_name],
            SUM(IIF([ITEMSstatus] = 'Done' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) AS item_total_done,
            SUM(IIF([ITEMSstatus] = 'Returned' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) AS order_item_return_total_price,
            SUM(IIF([ITEMSstatus] = 'Done' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) - 
            SUM(IIF([ITEMSstatus] = 'Returned' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) AS item_total_cost
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

#SUM([discounts line]) AS discount_amount,
#SUM(IIF([Status] = 'Done', [tax_exclusive_discount_amount], 0)) AS tax_exclusive_discount
#COUNT(*) AS order_count
#SUM(IIF([ITEMSstatus] = 'Done' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) AS item_total_done,
#SUM(IIF([ITEMSstatus] = 'Returned' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) AS order_item_return_total_price,
#            SUM(IIF([ITEMSstatus] = 'Done' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) -
#            SUM(IIF([ITEMSstatus] = 'Returned' AND [ITEMStype] = 'Product', [ITEMStotal_price], 0)) AS item_total_cost