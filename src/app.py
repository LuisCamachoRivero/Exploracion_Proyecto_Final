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
with open('/Users/luiscamacho/VSCProjects/Exploracion_Proyecto_Final/data/processed/region_temp_dict.json', 'r', encoding='utf-8') as f:
    region_temp_dict = json.load(f)
with open('/Users/luiscamacho/VSCProjects/Exploracion_Proyecto_Final/data/processed/region_pib_dict.json', 'r', encoding='utf-8') as f:
    region_pib_dict = json.load(f)
with open('/Users/luiscamacho/VSCProjects/Exploracion_Proyecto_Final/data/processed/cut_comuna_dict.json', 'r', encoding='utf-8') as f:
    cut_comuna_dict = json.load(f)
with open('/Users/luiscamacho/VSCProjects/Exploracion_Proyecto_Final/data/processed/cut_provincia_dict.json', 'r', encoding='utf-8') as f:
    cut_provincia_dict = json.load(f)
with open('/Users/luiscamacho/VSCProjects/Exploracion_Proyecto_Final/data/processed/cut_region_dict.json', 'r', encoding='utf-8') as f:
    cut_region_dict = json.load(f)

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

def consultar_temporada(region, mes, region_mes_dict_str_keys):
    clave_str = f"({region}, {mes})"
    temporada = region_mes_dict_str_keys.get(clave_str, "No disponible")
    return temporada

def buscar_cut(diccionario, entidad):
    resultado = diccionario.get(entidad, "La entidad no fue encontrada en el diccionario.")
    return resultado




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
mes_anio = calcular_meses(cantidad_meses_a_predecir)

temporada = consultar_temporada(option, mes_anio[0][0], region_temp_dict)

proyeccion_pib_origen = st.slider('Proyección varianza mensual de Region Origen', min_value=-1.5, max_value=1.5, step=0.1)
pib_origen = (region_pib_dict.get(option4, "Región no encontrada")) * (1 + proyeccion_pib_origen / 100)

proyeccion_pib_destino = st.slider('Proyección varianza mensual de Region Destino', min_value=-1.5, max_value=1.5, step=0.1)
pib_destino = (region_pib_dict.get(option, "Región no encontrada")) * (1 + proyeccion_pib_destino / 100)



consulta = pd.DataFrame({
    'Comuna Origen': [option6],
    'Provincia Origen': [option5],
    'Region Origen': [option4],
    'Comuna Destino': [option3],
    'Provincia Destino': [option2],
    'Region Destino': [option],
    'Anio': [mes_anio[0][1]],
    'Mes': [mes_anio[0][0]],
    'Temporada': [temporada],
    'PIB Region Origen': [pib_origen],
    'PIB Region Destino': [pib_destino],
    'covid_periodo_num': [0],
})


consulta_trans = pd.DataFrame({
    'CUT Comuna Origen': [buscar_cut(cut_comuna_dict, option6)],
    'CUT Provincia Origen': [buscar_cut(cut_provincia_dict, option5)],
    'CUT Region Origen': [buscar_cut(cut_region_dict, option4)],
    'CUT Comuna Destino': [buscar_cut(cut_comuna_dict, option3)],
    'CUT Provincia Destino': [buscar_cut(cut_provincia_dict, option2)],
    'CUT Region Destino': [buscar_cut(cut_region_dict, option)],
    'Anio': [mes_anio[0][1]],
    'CUT Mes': [mes_anio[0][0]],
    'CUT Temporada': [temporada],
    'PIB Region Origen': [pib_origen],
    'PIB Region Destino': [pib_destino],
    'covid_periodo_num': [0],
})

st.write("consulta:", consulta)
st.write("consulta:", consulta_trans)


prediccion = model.predict(consulta_trans)

st.write(f'Prediccion de Viajes Ocasionales: {prediccion[0]}')
