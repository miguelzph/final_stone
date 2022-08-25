import streamlit as st

def show_products_page(tab, data):
    """Mostra a página de produtos na tab, e com base no dados de data.

    Args:
        tab (st.tabs): Aba em que a pagina deve ser executada
        data (pd.DataFrame): Dados a serem visualizados na pagina
    """
    with tab:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader('Mais vendidos')
            top10_products = data.iloc[:10][['product_name', 'total_quantity']]
            st.write(top10_products.to_html(index=False), unsafe_allow_html=True)
            
        with col2:
            st.subheader('Maior Faturamento')
            top10_products_monetary = data.sort_values('total_sales', ascending=False).iloc[:10][['product_name', 'total_sales']]
            st.write(top10_products_monetary.to_html(index=False), unsafe_allow_html=True)
            
        with col3:
            st.subheader('Menos Vendidos')
            last10_products = data[data['total_quantity'] != 0]
            last10_products = last10_products.iloc[-10:][['product_name', 'total_quantity']]
            st.write(last10_products.to_html(index=False), unsafe_allow_html=True)
            
        # apenas se tiver produtos que não venderam
        if 0 in list(data['total_quantity']):
            st.markdown("""---""")   
            st.subheader('**Além disso, alguns produtos não tiveram vendas esse mês. Já pensou em reavaliar esses pratos?**')
            no_sales_products = data[data['total_quantity'] == 0]
            st.write(no_sales_products[['product_name']].T.to_html(index=False, header=False), unsafe_allow_html=True)
                
    return None
    