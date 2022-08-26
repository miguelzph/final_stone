import streamlit as st
from tabs.clients import helper
import plotly.graph_objects as go

def show_clients_page(tab, data):

    with tab:
        
        data = helper.add_time_columns(data)
        
        # link afiliado
        link = 'https://www.collact.com.br/fale-com-especialista?utm_source=teste'
        text = """Obs: Nós consideramos um cartão como um cliente. 
                 Quer ter dados mais precisos? Entender o comportamento dos clientes mesmo que ele use vários cartões?
                 Acesse a [collact]({link}) e confira como podemos ajudar.""".format(link=link)
        
        
        st.markdown(text, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            percentage_has_more_than_one_buy = helper.calculate_has_more_than_one_buy(data)
            text = "Compraram mais de uma vez no mês"
            fig = helper.generate_velocimeter_fig(percentage_has_more_than_one_buy, text)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            new_clients = 2000
            text = "Novos clientes no mês"
            fig = helper.generate_card_fig(new_clients, text)
            st.plotly_chart(fig, use_container_width=True)
            
        with col3:
            returned_from_last_week = helper.calculate_returned_from_last_week(data)
            fig = helper.generate_returned_from_last_week_plot(returned_from_last_week)

            st.plotly_chart(fig, use_container_width=True)
        
        
        st.markdown("""---""") 
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Cohort Semanal: Retenção de usuário')
            helper.cohort_analysis(data)
        
        with col2:
            st.subheader('Como interpretar a análise de Cohort?')
            st.video('https://www.youtube.com/watch?v=GolJlR_KZuU')
            
            
