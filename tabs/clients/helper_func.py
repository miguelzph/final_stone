import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import pandas as pd
from streamlit import pyplot
import plotly.graph_objects as go

def add_time_columns(df):
    """Adiciona colunas temporais necessárias para analises dos clientes

    Args:
        df (pd.DataFrame): dados das compras
    """
    df['full_datetime'] = pd.to_datetime(df['transaction_date'].astype(str) + ' ' + df['transaction_time'].astype(str))
    df['week_of_year'] = df['full_datetime'].dt.isocalendar().week.astype(int)
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

    cohort_df['order_month'] = cohort_df['full_datetime'].dt.to_period('W').dt.start_time
    cohort_df['cohort'] = cohort_df.groupby('card_id')['full_datetime'] \
                     .transform('min') \
                     .dt.to_period('W') \
                     .dt.start_time

    cohort_df = cohort_df.groupby(['cohort', 'order_month']) \
                  .agg(n_customers=('card_id', 'nunique')) \
                  .reset_index(drop=False)
    cohort_df['period_number'] = ((cohort_df.order_month - cohort_df.cohort).dt.days / 7).astype(int)


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