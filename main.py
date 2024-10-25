import streamlit as st
import pandas as pd
import plotly.express as px
# import yaml
# from yaml.loader import SafeLoader
# import streamlit_authenticator as stauth
# from streamlit_authenticator import Authenticate

# with open('./config.yaml') as file:
#     config = yaml.load(file, Loader=SafeLoader)

# hashed_passwords = stauth.Hasher(['abc123', 'def']).generate()
# print(hashed_passwords)


# authenticator = Authenticate(
#     config['credentials'],
#     config['cookie']['name'],
#     config['cookie']['key'],
#     config['cookie']['expiry_days'],
#     config['preauthorized']
# )
# authenticator.login()



# if st.session_state["authentication_status"]:
#     authenticator.logout()
#     st.write(f'Bienvenido *{st.session_state["name"]}*')

# elif st.session_state["authentication_status"] is False:
#     st.error('Username/password is incorrect')
# elif st.session_state["authentication_status"] is None:
#     st.warning('Please enter your username and password')

# if st.session_state["authentication_status"] is None or st.session_state["authentication_status"] is False:
#     # NO Mostrar el resto de la app
#     st.stop()
        

st.title('Sindicatos próximos a renovar mandato')

df = pd.read_excel('./data/sindicatos_todas_las_regiones_para_streamlit.xlsx', sheet_name='Sheet1')
#df = pd.read_excel('./data/sindicatos_puntaje.xlsx', sheet_name='Sheet1')


# Hacer una side bar para poner los filtros
st.sidebar.title('Filtros')
# Hacer columna total de miembros
df['TotalMiembros'] = df['Socios'] + df['Socias']
try:
    df.FinMandato = pd.to_datetime(df.FinMandato)
    df.FechaDepositoEstatutos = pd.to_datetime(df.FechaDepositoEstatutos)
except:
    # Desde este formato: "27/09/2024"
    df.FinMandato = pd.to_datetime(df.FinMandato, format='%d/%m/%Y')
    df.FechaDepositoEstatutos = pd.to_datetime(df.FechaDepositoEstatutos, format='%d/%m/%Y')
    

# Agregar columna con las filas en que la columna sea menor a 2017 en la columna FechaDepositoEstatutos con un valor de SI o NO
df['NecesitaRenovacion'] = df['FechaDepositoEstatutos'].apply(lambda x: 'Si' if x < pd.to_datetime('2017-01-01') else 'No')
# Filtra depositos de estatutos menores a 2017
varRenovacion = st.sidebar.radio('Necesita renovación', ['Si', 'No', 'Todos'], index=2)
# Filtrar por la columna NecesitaRenovacion
if varRenovacion == 'Si':
    df = df[df['NecesitaRenovacion'] == 'Si']
elif varRenovacion == 'No':
    df = df[df['NecesitaRenovacion'] == 'No']
else:
    pass

# Filtro si tiene telefono o no por defecto todos
varTelefono = st.sidebar.radio('Telefono', ['Si', 'No', 'Todos'], index=2)
if varTelefono == 'Si':
    df = df[df['fono'].notnull()]
elif varTelefono == 'No':
    df = df[df['fono'].isnull()]
else:
    pass

# Filtro si tiene correo o no por defecto todos
varCorreo = st.sidebar.radio('Correo', ['Si', 'No', 'Todos'], index=2)
if varCorreo == 'Si':
    df = df[df['Email'].notnull()]
elif varCorreo == 'No':
    df = df[df['Email'].isnull()]
else:
    pass

# Hacer un filtro por palabras clave 1
palabras = st.sidebar.text_input('Palabras clave', '')
if palabras:
    palabras = palabras.split()
    for palabra in palabras:
        # Solo por nombre
        df = df[df['nombre'].str.contains(palabra, case=False)]
        
# Hacer un filtro por palabras clave 2
palabras = st.sidebar.text_input('Palabras clave 2', '')
if palabras:
    palabras = palabras.split()
    for palabra in palabras:
        # Solo por nombre
        df = df[df['nombre'].str.contains(palabra, case=False)]
        


# Filtro de regiones
dict_regiones_chile = {
    'Arica y Parinacota': 15,
    'Tarapacá': 1,
    'Antofagasta': 2,
    'Atacama': 3,
    'Coquimbo': 4,
    'Valparaíso': 5,
    'Metropolitana': 13,
    'O’Higgins': 6,
    'Maule': 7,
    'Ñuble': 16,
    'Biobío': 8,
    'Araucanía': 9,
    'Los Ríos': 14,
    'Los Lagos': 10,
    'Aysén': 11,
    'Magallanes': 12

}
# por defecto la region metropolitana
varRegion = st.sidebar.multiselect('Regiones', list(dict_regiones_chile.keys()), default=['Metropolitana'])
# Devolver el valor numerico de la region
varRegion = [dict_regiones_chile[i] for i in varRegion]
df = df[df['Region'].isin(varRegion)]


# Filtrar los sindicatos cuyo fin de mandato está próximo a cumplirse (por ejemplo, en el proximo año)
# El filtro debe ser entre hoy y el proximo año
hoy = pd.Timestamp('today')

# Seleccionar si se quiere filtrar por año, mes o semana, valor por defecto es año a 1
varTiempo = st.sidebar.radio('Tiempo', ['Año', 'Mes', 'Semana'], index=0)

if varTiempo == 'Año':
    varAno = st.sidebar.slider('Vencimiento en cuantos años', 1, 5, 1)
    
    df = df[(df['FinMandato'] > hoy) & (df['FinMandato'] < hoy + pd.DateOffset(years=varAno))]
    
elif varTiempo == 'Mes':
    varMes = st.sidebar.slider('Vencimiento en cuantos meses', 1, 12, 6)
    df = df[(df['FinMandato'] > hoy) & (df['FinMandato'] < hoy + pd.DateOffset(months=varMes))]
else:
    varSemana = st.sidebar.slider('Vencimiento en cuantas semanas', 1, 52, 1)
    df = df[(df['FinMandato'] > hoy) & (df['FinMandato'] < hoy + pd.DateOffset(weeks=varSemana))]

# Filtrar por el número de miembros
maxTotalMiembros = df['TotalMiembros'].max()
maxTotalMiembros = int(maxTotalMiembros)
miembros = st.sidebar.slider('TotalMiebros', 0, maxTotalMiembros, (0, maxTotalMiembros))


# Filtrar por el número total de miembros
df = df[(df['TotalMiembros'] >= miembros[0]) & (df['TotalMiembros'] <= miembros[1])]


# Ordenar de manera descendente por el por el fin de mandato mas cercano y el total de miembros
df = df.sort_values(by=['FinMandato', 'TotalMiembros'], ascending=[True, False])

#Dropear la columna prioridad
try:
    df = df.drop(columns=['Prioridad'])
except:
    pass
# Mostrar el DataFrame filtrado en streamlit
st.dataframe(df)

# Mostrar cantidad de sindicatos filtrados
st.write(f'Cantidad de sindicatos filtrados: {len(df)}')
# Mostras la cantidad total de miembros de los sindicatos filtrados
st.write(f'Total de miembros de los sindicatos filtrados: {df["TotalMiembros"].sum()}')

# Filtrar outliers
df = df[df['TotalMiembros'] < df['TotalMiembros'].quantile(0.95)]

st.plotly_chart(px.histogram(df, x='TotalMiembros', nbins=100, title='Distribución de sindicatos filtrados'))

# Si esta en filtro de renovación todos, mostrar un porcentaje de los sindicatos que necesitan renovación
if varRenovacion == 'Todos':
    porcentaje_renovacion = len(df[df['NecesitaRenovacion'] == 'Si']) / len(df) * 100
    st.write(f'Porcentaje de sindicatos que necesitan renovación: {porcentaje_renovacion:.2f}%')