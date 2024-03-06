import pandas as pd
df = pd.read_csv('./data/todas_las_regiones.csv')

# Hacer columna total de miembros
df['TotalMiembros'] = df['Socios'] + df['Socias']
df.FinMandato = pd.to_datetime(df.FinMandato)

# Filtrar los sindicatos unicos, me en orden de preferencia con DIRECTOR, PRESIDENTE, SECRETARIO, TESORERO de a columa glosa2
# Son string los cargos ordenados por jerarquia
dic_prioridad = {'DIRECTOR': 0, 'PRESIDENTE': 1, 'SECRETARIO': 2, 'TESORERO': 3}
df['Prioridad'] = df['glosa2'].map(dic_prioridad)
df = df.sort_values(by=['nombre', 'Prioridad'], ascending=[True, True])
# Eliminar los duplicados
df = df.drop_duplicates(subset='nombre', keep='first')

df.to_excel('data/sindicatos_todas_las_regiones_para_streamlit.xlsx', index=False)