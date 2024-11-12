from pickle import load
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta


model = load(open('/Users/luiscamacho/VSCProjects/Exploracion_Proyecto_Final/models/xgboost_regressor_lr_0_15_mx_dp_8_n_esti_310_42.pkl', 'rb'))
with open('/Users/luiscamacho/VSCProjects/Exploracion_Proyecto_Final/data/processed/region_origen_dict.json', 'r', encoding='utf-8') as f:
    region_origen_dict = json.load(f)
with open('/Users/luiscamacho/VSCProjects/Exploracion_Proyecto_Final/data/processed/region_destino_dict.json', 'r', encoding='utf-8') as f:
    region_destino_dict = json.load(f)

def obtener_info(region, region_dict, tipo='provincias', provincia=None):
    if region not in region_dict:
        return f"La región '{region}' no se encuentra en el diccionario."
    
    if tipo == 'provincias' and provincia is None:
        return list(region_dict[region].keys())
    
    elif tipo == 'comunas' and provincia is None:
        comunas = []
        for comunas_provincia in region_dict[region].values():
            comunas.extend(comunas_provincia)
        return comunas
    
    elif tipo == 'comunas' and provincia is not None:
        if provincia not in region_dict[region]:
            return f"La provincia '{provincia}' no se encuentra en la región '{region}'."
        return region_dict[region][provincia]

    else:
        return "Tipo no válido. Usa 'provincias' o 'comunas'."
    
def calcular_meses(cantidad_meses):
    fecha_inicial = datetime(2024, 7, 1)
    
    meses_anios = []

    for i in range(cantidad_meses):
        nueva_fecha = fecha_inicial + relativedelta(months=i)
        
        meses_anios.append((nueva_fecha.month, nueva_fecha.year))
        
    return meses_anios




st.title('Predicción Viajes Ocasionales Chile')


nombre_regiones_destino = list(region_destino_dict.keys())
option = st.selectbox(
    "Región a predecir:",
    (nombre_regiones_destino),
    key='selectbox_1'
)
st.write("You selected:", option)

option2 = st.selectbox(
    "Provincia a predecir:",
    (obtener_info(option, region_destino_dict, tipo='provincias')),
    key='selectbox_2'
)
st.write("You selected:", option2)

option3 = st.selectbox(
    "Comuna a predecir:",
    (obtener_info(option, region_destino_dict, tipo='comunas',provincia=option2)),
    key='selectbox_3'
)
st.write("You selected:", option3)




nombre_regiones_origen = list(region_origen_dict.keys())
option4 = st.selectbox(
    "Región a predecir:",
    (nombre_regiones_origen),
    key='selectbox_4'
)
st.write("You selected:", option4)

option5 = st.selectbox(
    "Provincia a predecir:",
    (obtener_info(option4, region_origen_dict, tipo='provincias')),
    key='selectbox_5'
)
st.write("You selected:", option5)

option6 = st.selectbox(
    "Comuna a predecir:",
    (obtener_info(option4, region_origen_dict, tipo='comunas',provincia=option5)),
    key='selectbox_6'
)
st.write("You selected:", option6)

cantidad_meses_a_predecir = st.slider('Cantidad de meses a predecir', min_value=1, max_value=12, step=1)
resultado = calcular_meses(cantidad_meses_a_predecir)


datos_entrada = pd.DataFrame({
    'CUT Comuna Origen': [1101],
    'CUT Provincia Origen': [11],
    'CUT Region Origen': [1],
    'CUT Comuna Destino': [1402],
    'CUT Provincia Destino': [14],
    'CUT Region Destino': [1],
    'Anio': [2019],
    'CUT Mes': [1],
    'CUT Temporada': [1],
    'PIB Region Origen': [1061.580205],
    'PIB Region Destino': [1061.580205],
    'covid_periodo_num': [0],
})

prediccion = model.predict(datos_entrada)

st.write(f'Prediccion de Viajes Ocasionales: {prediccion[0]}')
