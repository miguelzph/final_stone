import streamlit as st
from tabs.helper_func import cohort_analysis, add_time_columns, generate_velocimeter_fig, calculate_has_more_than_one_buy
import plotly.graph_objects as go

def show_clients_page(tab, data):

    with tab:
        
        data = add_time_columns(data)
        
        # link afiliado
        link = 'https://www.collact.com.br/fale-com-especialista?utm_source=teste'
        text = """Obs: Nós consideramos um cartão como um cliente. 
                 Quer ter dados mais precisos? Entender o comportamento dos clientes mesmo que ele use vários cartões?
                 Acesse a [collact]({link}) e confira como podemos ajudar.""".format(link=link)
        
        
        st.markdown(text, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            percentage_has_more_than_one_buy = calculate_has_more_than_one_buy(data)
            text = "Compraram mais de uma vez no mês"
            fig = generate_velocimeter_fig(percentage_has_more_than_one_buy, text)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(go.Indicator(
            mode = "number+delta",
            value = 400,
            delta = {'position': "bottom", 'reference': 0}, # nao ha dados anteriores
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': 'Quantidade de novos clientes'}))

            fig.update_layout(paper_bgcolor = "lightgray")
            st.plotly_chart(fig, use_container_width=True)
            
        with col3:
            
            percentage_has_more_than_one_buy = calculate_has_more_than_one_buy(data)
            text = "Quantidade de novos"
            fig = generate_velocimeter_fig(percentage_has_more_than_one_buy, text)

            st.plotly_chart(fig, use_container_width=True)

        
        st.markdown("""---""") 
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Cohort Semanal: Retenção de usuário')
            cohort_analysis(data)
        
        with col2:
            st.subheader('Como interpretar a análise de Cohort?')
            st.video('https://www.youtube.com/watch?v=GolJlR_KZuU')
