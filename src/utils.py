from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

# load the .env file variables
load_dotenv()


def db_connect():
    import os
    engine = create_engine(os.getenv('DATABASE_URL'))
    engine.connect()
    return engine

def obtener_lista_destinos(df, columna):
    """
    Obtiene una lista de valores únicos de una columna de un DataFrame, 
    elimina duplicados y la ordena alfabéticamente.
    
    Parámetros:
    - df: DataFrame de pandas.
    - columna: str, nombre de la columna de la cual se obtendrán los valores únicos.

    Retorna:
    - lista_destinos: list, valores únicos de la columna en orden alfabético.
    """
    lista_destinos = sorted(list(set(df[columna].unique().tolist())))
    return lista_destinos


