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
        WITH Counts AS (
            SELECT 
                Format([business_date], 'yyyy-mm') AS month, 
                [branch_name], 
                COUNT(DISTINCT [reference]) AS order_count, 
                SUM([discounts line]) AS discount_amount 
            FROM 
                DATA 
            GROUP BY 
                Format([business_date], 'yyyy-mm'), [branch_name]
        ) 
        SELECT 
            month, 
            [branch_name], 
            order_count, 
            discount_amount 
        FROM 
            Counts 
        ORDER BY 
            month, [branch_name];
    """
    df = pd.read_sql(sql1, conn)

    conn.close()
    return df