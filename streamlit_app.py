import os
import pandas as pd
import streamlit as st
import plotly.express as px
import psycopg2
from dotenv import load_dotenv
from query import QUERY_PRODUCTS, QUERY_SALES
from tabs.products import show_products_page

load_dotenv() 

st.set_page_config(layout='wide')

st.title('Statistics Lite')

welcolme_page, clients_page, products_page = st.tabs(['Bem Vindo!', 'Clientes', 'Produtos'])

def query_data(query):
        
        host = os.getenv("HOST")
        port = os.getenv("PORT")
        database = os.getenv("DATABASE")
        username = os.getenv("DB_USERNAME")
        password = os.getenv("PASSWORD")

        conn = psycopg2.connect(host=host, 
                 port=port, 
                 user=username, 
                 password=password, 
                 database=database, 
                 options="-c search_path=collect_lite,public")
    
        df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        return df
    
    
if __name__ == '__main__':
    
    with welcolme_page:
        st.write('ola!')
        
    data_for_products_page = query_data(QUERY_PRODUCTS)
    show_products_page(products_page, data_for_products_page)
    
    