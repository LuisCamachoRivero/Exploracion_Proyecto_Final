# Librerías
from pickle import load
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium


# Modelo y Diccionarios
model = load(open('/opt/render/project/src/models/xgboost_regressor_lr_0_15_mx_dp_8_n_esti_310_42.pkl', 'rb'))
with open('/opt/render/project/src/data/processed/region_origen_dict.json', 'r', encoding='utf-8') as f:
    region_origen_dict = json.load(f)
with open('/opt/render/project/src/data/processed/region_destino_dict.json', 'r', encoding='utf-8') as f:
    region_destino_dict = json.load(f)
with open('/opt/render/project/src/data/processed/region_temp_dict.json', 'r', encoding='utf-8') as f:
    region_temp_dict = json.load(f)
with open('/opt/render/project/src/data/processed/region_pib_dict.json', 'r', encoding='utf-8') as f:
    region_pib_dict = json.load(f)
with open('/opt/render/project/src/data/processed/cut_comuna_dict.json', 'r', encoding='utf-8') as f:
    cut_comuna_dict = json.load(f)
with open('/opt/render/project/srcl/data/processed/cut_provincia_dict.json', 'r', encoding='utf-8') as f:
    cut_provincia_dict = json.load(f)
with open('/opt/render/project/src/data/processed/cut_region_dict.json', 'r', encoding='utf-8') as f:
    cut_region_dict = json.load(f)
logo='/opt/render/project/src/data/interim/TourData-remove-background.com.png'

# Funciones
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
    
def convert_df(df):
    return df.to_csv().encode("utf-8")



# Cambio de Temas (Light/Dark)
ms = st.session_state
if "themes" not in ms: 
  ms.themes = {"current_theme": "light",
                    "refreshed": True,
                    
                    "light": {"theme.base": "dark",
                              "theme.backgroundColor": "black",
                              "theme.primaryColor": "#5591f5",
                              "theme.secondaryBackgroundColor": "#82E1D7",
                              "theme.textColor": "white",
                              "theme.textColor": "white",
                              "button_face": "🌜"},

                    "dark":  {"theme.base": "light",
                              "theme.backgroundColor": "white",
                              "theme.primaryColor": "#5591f5",
                              "theme.secondaryBackgroundColor": "#82E1D7",
                              "theme.textColor": "#0a1464",
                              "button_face": "🌞"},
                    }
  
def ChangeTheme():
  previous_theme = ms.themes["current_theme"]
  tdict = ms.themes["light"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]
  for vkey, vval in tdict.items(): 
    if vkey.startswith("theme"): st._config.set_option(vkey, vval)

  ms.themes["refreshed"] = False
  if previous_theme == "dark": ms.themes["current_theme"] = "light"
  elif previous_theme == "light": ms.themes["current_theme"] = "dark"

btn_face = ms.themes["light"]["button_face"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]["button_face"]
st.sidebar.button(btn_face, on_click=ChangeTheme)

if ms.themes["refreshed"] == False:
  ms.themes["refreshed"] = True
  st.rerun()



# APP 
st.logo(logo)
col1, col2 = st.columns(2,vertical_alignment="center")
with col1:
    st.image(logo)
with col2:
    st.title('Predicción Viajes Ocasionales Chile')
    

# Mapas
col1, col2 = st.columns(2,vertical_alignment="center")
map = folium.Map(location=[-36.523557,-70.206001],zoom_start=5)
map_regiones = '/opt/render/project/src/data/interim/mapa-01-2.png'
with col1:
    st_map =st_folium(map, width=450, height=470)
with col2:
    st.image(map_regiones, width=450)

# Recoleción de Dator Origen 
st.sidebar.title('Origen de los viajes:')
nombre_regiones_origen = list(region_origen_dict.keys())
option = st.sidebar.selectbox(
    "Región de Origen:",
    (nombre_regiones_origen),
    key='selectbox_1'
)

option2 = st.sidebar.selectbox(
    "Provincia Origen:",
    (obtener_info(option, region_origen_dict, tipo='provincias')),
    key='selectbox_2'
)

option3 = st.sidebar.selectbox(
    "Comuna Origen:",
    (obtener_info(option, region_origen_dict, tipo='comunas',provincia=option2)),
    key='selectbox_3'
)

proyeccion_pib_origen = st.sidebar.slider('Proyección porcentual (%) varianza mensual de Region Origen', min_value=-1.5, max_value=1.5, step=0.1,value=0.0)
pib_origen = (region_pib_dict.get(option, "Región no encontrada")) * (1 + proyeccion_pib_origen / 100)

# Recolección Datos Destino
st.sidebar.title('Destino de los viajes:')
nombre_regiones_destino = list(region_destino_dict.keys())
option4 = st.sidebar.selectbox(
    "Región Destino:",
    (nombre_regiones_destino),
    key='selectbox_4'
)

option5 = st.sidebar.selectbox(
    "Provincia Destino:",
    (obtener_info(option4, region_destino_dict, tipo='provincias')),
    key='selectbox_5'
)

option6 = st.sidebar.selectbox(
    "Comuna Destino:",
    (obtener_info(option4, region_destino_dict, tipo='comunas',provincia=option5)),
    key='selectbox_6'
)

proyeccion_pib_destino = st.sidebar.slider('Proyección porcentual (%) varianza mensual de Region Destino', min_value=-1.5, max_value=1.5, step=0.1,value=0.0)
pib_destino = (region_pib_dict.get(option4, "Región no encontrada")) * (1 + proyeccion_pib_destino / 100)

# Meses a predecir 
st.sidebar.title('Cantidad de meses a predecir:')
cantidad_meses_a_predecir = st.sidebar.slider('(Partiendo del 06-2024)', min_value=1, max_value=12, step=1)
mes_anio = calcular_meses(cantidad_meses_a_predecir)

# Busqueda de temporada por región seleccionada
temporada = consultar_temporada(option, mes_anio[0][0], region_temp_dict)




# Tratamiento de datos para predicciones
predicciones_df = pd.DataFrame()
predicciones_trans_df = pd.DataFrame()

pib_origen_base = pib_origen
pib_destino_base = pib_destino

# Loop para iterar por la cantidad de meses a predecir
for i in range(cantidad_meses_a_predecir):
    mes, anio = mes_anio[i]
    temporada = consultar_temporada(option, mes, region_temp_dict)
    pib_origen_ajustado = pib_origen_base * (1 + proyeccion_pib_origen / 100)
    pib_destino_ajustado = pib_destino_base * (1 + proyeccion_pib_destino / 100)

    # Crear la fila para el dataframe original de consulta
    fila_consulta = {
        'Comuna Origen': option3,
        'Provincia Origen': option2,
        'Region Origen': option,
        'Comuna Destino': option6,
        'Provincia Destino': option5,
        'Region Destino': option4,
        'Anio': anio,
        'Mes': mes,
        'Temporada': temporada,
        'PIB Region Origen': pib_origen_ajustado,
        'PIB Region Destino': pib_destino_ajustado,
        'covid_periodo_num': 0
    }
    
    # Crear la fila para el dataframe transformado con los CUT
    fila_trans = {
        'CUT Comuna Origen': buscar_cut(cut_comuna_dict, option3),
        'CUT Provincia Origen': buscar_cut(cut_provincia_dict, option2),
        'CUT Region Origen': buscar_cut(cut_region_dict, option),
        'CUT Comuna Destino': buscar_cut(cut_comuna_dict, option6),
        'CUT Provincia Destino': buscar_cut(cut_provincia_dict, option5),
        'CUT Region Destino': buscar_cut(cut_region_dict, option4),
        'Anio': anio,
        'CUT Mes': mes,
        'CUT Temporada': temporada,
        'PIB Region Origen': pib_origen_ajustado,
        'PIB Region Destino': pib_destino_ajustado,
        'covid_periodo_num': 0
    }

    # Agregar la fila al dataframe de predicciones
    predicciones_df = pd.concat([predicciones_df, pd.DataFrame([fila_consulta])], ignore_index=True)
    predicciones_trans_df = pd.concat([predicciones_trans_df, pd.DataFrame([fila_trans])], ignore_index=True)

    pib_origen_base = pib_origen_ajustado
    pib_destino_base = pib_destino_ajustado

# Mostrar el dataframe final con todas las predicciones
st.title("Consulta a realizar :")
st.write(predicciones_df)


# Predicciones

if st.sidebar.button('Predecir'):

    predicciones = model.predict(predicciones_trans_df)
    predicciones_redondeadas = [int(abs(round(pred))) for pred in predicciones]
    resultado_df = predicciones_trans_df.copy()
    resultado_df['Predicción Viajes Ocasionales'] = predicciones_redondeadas

    # Mostrar el DataFrame con las predicciones
    st.title('Predicciones: ')
    st.write(resultado_df[['Anio','CUT Mes','Predicción Viajes Ocasionales']])



    if cantidad_meses_a_predecir > 1:
        resultado_df['Fecha'] = pd.to_datetime(resultado_df['Anio'].astype(str) + '-' + resultado_df['CUT Mes'].astype(str) + '-01')

        resultado_df = resultado_df.sort_values('Fecha')

        # Crear el gráfico de serie de tiempo
        fig, ax = plt.subplots(figsize=(12, 6))

        # Definir colores para las temporadas
        colors = {1: 'r', 0: 'b'}  

        for i in range(1, len(resultado_df)):
            color = colors[resultado_df['CUT Temporada'].iloc[i]]
            ax.plot(resultado_df['Fecha'].iloc[i-1:i+1], 
                    resultado_df['Predicción Viajes Ocasionales'].iloc[i-1:i+1], 
                    color=color, linestyle='-', linewidth=2)

        ax.set_ylabel('Cantidad de Viajes Ocasionales')
        ax.set_title('Predicciones de Viajes Ocasionales')

        ax.set_xticks(resultado_df['Fecha'])
        ax.set_xticklabels(resultado_df['Fecha'].dt.strftime('%Y-%m'), rotation=45, ha='right')

        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='r', lw=2, label='Temporada Región Alta'),
            Line2D([0], [0], color='b', lw=2, label='Temporada Región Baja')
        ]
        ax.legend(handles=legend_elements, loc='upper left')

        ax.grid()
        plt.tight_layout()

        # Mostrar el gráfico en Streamlit
        st.pyplot(fig)

    # Descargar el DF resultado
    csv = convert_df(resultado_df)

    st.download_button(
        label="Descargar data como CSV",
        data=csv,
        file_name="prediccion_realizada.csv",
        mime="text/csv",
    )

