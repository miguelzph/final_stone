import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import pandas as pd
from streamlit import pyplot
import plotly.graph_objects as go
import plotly.express as px

def add_time_columns(df):
    """Adiciona colunas temporais necessárias para analises dos clientes

    Args:
        df (pd.DataFrame): dados das compras
    """
    df['full_datetime'] = pd.to_datetime(df['transaction_date'].astype(str) + ' ' + df['transaction_time'].astype(str))
    df['first_day_of_week'] = df['full_datetime'].dt.to_period('W').dt.start_time
    df['id_day_of_week'] = df['full_datetime'].dt.dayofweek
    df['day_of_week'] = df['full_datetime'].dt.day_name()
    df['hour_sale'] = df['full_datetime'].dt.strftime('%H').astype(int)
    
    return df


def cohort_analysis(df):
    """A partir do dataframe gera um heatmap com cohort dos clientes. 
    Aplicação baseada em baseado em: 
    https://towardsdatascience.com/a-step-by-step-introduction-to-cohort-analysis-in-python-a2cbbd8460ea

    Args:
        df (pd.DataFrame): dados das compras
    """
    
    retention_matrix, cohort_size = get_cohort_data(df)
    
    create_fig_cohort(retention_matrix, cohort_size)
    
    return None


def get_cohort_data(df):
    """Processa os dados de compra para gerar uma matriz de retenção.

    Args:
         df (pd.DataFrame): dados das compras

    Returns:
        retention_matrix (pd.DataFrame): dataframe com os dados de retenção
        cohort_size (pd.Series): quantidade de novos clientes por cohort
    """

    cohort_df = df[['transaction_id', 'card_id', 'full_datetime']].copy()

    cohort_df['order_week'] = cohort_df['full_datetime'].dt.to_period('W').dt.start_time
    cohort_df['cohort'] = cohort_df.groupby('card_id')['full_datetime'] \
                     .transform('min') \
                     .dt.to_period('W') \
                     .dt.start_time

    cohort_df = cohort_df.groupby(['cohort', 'order_week']) \
                  .agg(n_customers=('card_id', 'nunique')) \
                  .reset_index(drop=False)
    cohort_df['period_number'] = ((cohort_df.order_week - cohort_df.cohort).dt.days / 7).astype(int)


    cohort_pivot = cohort_df.pivot_table(index = 'cohort',
                                         columns = 'period_number',
                                         values = 'n_customers')

    cohort_pivot.index = cohort_pivot.index.to_series().astype(str)

    cohort_size = cohort_pivot.iloc[:,0]
    retention_matrix = cohort_pivot.divide(cohort_size, axis = 0)
    
    return (retention_matrix, cohort_size)


def create_fig_cohort(retention_matrix, cohort_size):
    """ Plota uma figura a partir da tabela com retenções e quantidade de clientes de cada cohort.

    Args:
        retention_matrix (pd.DataFrame): dataframe com os dados de retenção
        cohort_size (pd.Series): quantidade de novos clientes por cohort

    """
    with sns.axes_style("white"):
        fig, ax = plt.subplots(1, 2, figsize=(12, 8), sharey=True, gridspec_kw={'width_ratios': [1, 11]})

        # retention matrix
        sns.heatmap(retention_matrix, 
                    mask=retention_matrix.isnull(), 
                    annot=True, 
                    fmt='.0%', 
                    cmap='RdYlGn', 
                    ax=ax[1])
        ax[1].set(xlabel='Semanas',
                  ylabel='')

        # cohort size
        cohort_size_df = pd.DataFrame(cohort_size).rename(columns={0: 'cohort_size'})
        white_cmap = mcolors.ListedColormap(['white'])
        sns.heatmap(cohort_size_df, 
                    annot=True, 
                    cbar=False, 
                    fmt='g', 
                    cmap=white_cmap, 
                    ax=ax[0])

        # efetivamente gera o grafico no streamlit
        pyplot(fig)
        
        return None
    

def calculate_has_more_than_one_buy(df):
    """Calcula a % de clientes que compraram mais de uma vez.

    Args:
        df (pd.DataFrame): dados das compras

    Returns:
        float: retorna o % de clientes que compraram mais de uma vez
    """
    count_by_customer = df.groupby('card_id').count().reset_index().copy()
    
    return len(count_by_customer[count_by_customer['transaction_id'] > 1]) / len(count_by_customer)


def generate_velocimeter_fig(value, text):
    """Gera uma figura com um gráfico estilo velocimetro.  

    Args:
        value (float): valor de 0 a 1 representando um % a ser plotado.
        text (str): texto acima do gráfico
    Returns:
        fig: retorna uma figura para plot
    """

    fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = value * 100,
    number= { 'suffix': "%" },
    gauge = {'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps' : [
                    {'range': [0, 30], 'color': "red"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}],},
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': text}))
    
    fig.update_layout(paper_bgcolor = "lightgray")
    
    fig.update_layout(
        margin=dict(l=10,r=10,b=0,t=0))
    
    return fig

def generate_card_fig(value, text, reference_value=0):
    """Gera uma figura representando um card com um valor. 

    Args:
        value (int): valor do card
        text (str): texto acima do gráfico
        reference_value (int): valor referencia para comparacao
    Returns:
        fig: retorna uma figura para plot
    """

    fig = go.Figure(go.Indicator(
            mode = "number+delta",
            value = value,
            delta = {'position': "bottom", 'reference': reference_value},
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': text}))

    fig.update_layout(paper_bgcolor = "lightgray")
    
    return fig


def calculate_returned_from_last_week(df):
    """Calcula a % de clientes que voltaram da ultima semana.

    Args:
        df (pd.DataFrame): dados das compras

    Returns:
        pd.DataFrame: retorna um dataframe com semana e % de clientes que retornou da semana anterior
    """
    # chegaram na semana 1 e voltaram na semana 2, e assim por diante
    frequency_clients_week = df.drop_duplicates(['first_day_of_week', 'card_id']).copy()
    frequency_clients_week['first_day_of_week'] = frequency_clients_week['first_day_of_week'].astype(str)
    frequency_clients_week = frequency_clients_week[['first_day_of_week','card_id','transaction_id']].groupby(['first_day_of_week', 'card_id']).count().reset_index()
    frequency_clients_week = frequency_clients_week.pivot_table(index="card_id",columns="first_day_of_week",values="transaction_id", aggfunc='first')

    returned_from_last_week = {}
    list_columns = frequency_clients_week.columns

    for i, column_week in enumerate(list_columns):
        
        if i == 0: # skip the first week
            continue
        has_come_in_this_and_last_week = len(frequency_clients_week[(frequency_clients_week[list_columns[i-1]]==1) & (frequency_clients_week[column_week] ==1)])
        has_come_last_week = frequency_clients_week[list_columns[i-1]].sum()
        
        returned_from_last_week[f'{column_week} (Week {i+1})'] =  (has_come_in_this_and_last_week / has_come_last_week)
        
    return pd.DataFrame({'first_day_of_week': returned_from_last_week.keys(),
                                        'returned_from_last_week': returned_from_last_week.values()})
    
    
def generate_returned_from_last_week_plot(data):
    """Gera um gráfico de linha representando o % de clientes que retornou da semana anterior

    Args:
        data (pd.DataFrame): dados de retorno por semana
    Returns:
        fig: retorna uma figura para plot
    """

    fig = px.bar(data, x='first_day_of_week', y='returned_from_last_week', text='returned_from_last_week')

    fig.update_yaxes(
        range=(0, 1),
        constrain='domain'
    )

    fig.update_layout(title_text='% de clientes que retornou da semana anterior', 
                      title_x=0.5,margin=dict(l=10,r=10), xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False), plot_bgcolor='rgba(0,0,0,0)', 
                      paper_bgcolor = "lightgray")
    
    fig.update_traces(texttemplate='%{value:.2%}')
    

    return fig