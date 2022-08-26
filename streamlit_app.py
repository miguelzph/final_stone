import streamlit as st

from database.query_texts import QUERY_PRODUCTS, QUERY_SALES
from database.query_functions import query_data

from tabs.products.products import show_products_page
from tabs.clients.clients_page import show_clients_page



st.set_page_config(layout='wide')

st.title('Statistics Lite')

welcolme_page, clients_page, products_page = st.tabs(['Bem Vindo!', 'Clientes', 'Produtos'])

if __name__ == '__main__':
    
    with welcolme_page:
        st.subheader('Ola! ...')
        st.write('Vídeo Explicativo:')
            
    data_for_products_page = query_data(QUERY_PRODUCTS)
    show_products_page(products_page, data_for_products_page)
    
    data_for_products_page = query_data(QUERY_SALES)
    show_clients_page(clients_page, data_for_products_page)
    
    