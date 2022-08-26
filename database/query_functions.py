import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv() 

def query_data(query):
    """Executa uma query no banco de dados e retorna o resultado em formato de dataframe. 
    A conexão é criada e fechada dentro da função.

    Args:
        query (text): query a ser executada no banco de dados

    Returns:
        pd.DataFrame: Retorna um dataframe com o resultado na query
    """
        
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_DATABASE")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")

    conn = psycopg2.connect(host=host, 
                port=port, 
                user=username, 
                password=password, 
                database=database, 
                options="-c search_path=collect_lite,public")

    df = pd.read_sql_query(query, conn)
    
    conn.close()
    
    return df