QUERY_PRODUCTS = """  
    SELECT 
        products.product_id ,
        products.product_name,
        CASE 
            WHEN SUM(quantity)  IS NULL THEN 0 
            ELSE SUM(quantity)  END AS total_quantity,
        CASE 
            WHEN SUM(detailed_sale.quantity * price)  IS NULL THEN 0 
            ELSE SUM(detailed_sale.quantity * price)  END AS total_sales
    FROM 
        products
    LEFT JOIN 
        detailed_sale
    ON 
        products.product_id = detailed_sale.product_id
    LEFT join 
        sale
    ON 
        detailed_sale.transaction_id  = sale.transaction_id 
    GROUP BY 
        products.product_id
    order by 
        total_quantity DESC"""
        
       
QUERY_SALES = """
    select
        *
    from 
       sale
"""