# Contents of ~/my_app/pages/page_3.py
from traitlets import default
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from st_aggrid import AgGrid
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
#from yellowbrick.cluster import SilhouetteVisualizer
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from sklearn.metrics import r2_score

st.set_page_config(page_title = "Clustering de clientes",
                    page_icon = ":bar_chart:")




@st.cache
def data_model_cluster():
    conn = sqlite3.connect('data/data_cenabast.db')
    c = conn.cursor()
    sqlquery_1 = f""" SELECT * FROM cluster_model """
    df =  pd.read_sql_query(sqlquery_1,con = conn)
    return df

@st.cache
def selected_fields(fields_selected):
    data_model_clutering_2 =  data_model_cluster()[fields_selected]
    return data_model_clutering_2

@st.cache(allow_output_mutation=True)
def one_hot_encoding_and_standarize(df):
    df_1 = df.copy()
    list_columns = df_1.columns
    list_characters = ['Contexto_pais_1','Contexto_pais_2']

    for column in list_columns:
        if column in list_characters:
            df_1 = pd.get_dummies(df_1, columns=[column])
        else:
            df_1[column] = pd.to_numeric(df_1[column])

    cols_to_standardize = df_1.columns
    data_to_standardize = df_1[cols_to_standardize]
    scaler = StandardScaler().fit(data_to_standardize)
    # Standardize the columns.
    standardized_data = df_1.copy()
    standardized_columns = scaler.transform(data_to_standardize)
    standardized_data[cols_to_standardize] = standardized_columns
    df_cluster_st = standardized_data.copy()

    return df_cluster_st

@st.cache
def elbow_information(df):
    distortions = []
    K = range(1,10)
    for k in K:
        kmeanModel = KMeans(n_clusters=k)
        kmeanModel.fit(df)
        distortions.append(kmeanModel.inertia_)
    return K, distortions

@st.cache(allow_output_mutation=True)
def kmeans(k,df,fields_selected):
    kmeanModel = KMeans(n_clusters=k, init='k-means++', n_init=10, max_iter=100, random_state=42)
    kmeanModel.fit(df)
    df['k_means']=kmeanModel.predict(df)
    
    list_columns_1 = ['nombre_cliente']
    list_columns_2 = list(fields_selected)
    
    list_columns = list_columns_1+list_columns_2
    df_final = data_model_cluster().copy()
    df_final = df_final[list_columns]
    df_final['kmeans'] = df['k_means'] 

    return df, df_final

@st.cache
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data
    
st.sidebar.image("data/Logotipo_Cenabast_2018.png", use_column_width=True)

################ DEF CONTAINERS ################
presentation = st.container()
data_cluster = st.container()
select_field_for_cluster = st.container()
elbow_test = st.container()
clustering_calculations = st.container()
clustering_results = st.container()
silhoutte_analysis = st.container()



################ CONTAINERS ################
with presentation:
    st.markdown("# Clustering de clientes")
    st.write('El clustering de clientes tiene por fin generar grupos (clusters) de clientes dependiendo de las distintas variables que tenga el modelo de datos que lo genera.  \n  Esta herramienta permite al mismo clientes generar los clusters según las variables y número de grupo que el desee.  \n  Experimenta con esta aplicación y encuentra los grupo que más sentido tengan para establecer una buena estrategia de negocios.')


with data_cluster:
    st.title(f'Modelo de datos para cluster')
    st.write('En la tabla de abajo puedes encontrar el modelo de datos general que existe para generar clusters de clientes.  \n  Acá encontrar diferentes campos generados por clientes y se relacionan principalmente a los habitos de consumo, como temporalidad y nivel de compras, información geográfica e información relacionada a los productos que estos prefieren.')
    AgGrid(data_model_cluster(), 
            theme='blue',
            fit_columns_on_grid_load=False,
            height= 400)


st.sidebar.markdown("# Clustering de clientes")
st.sidebar.title('Seleccione tamaño de gráfico de codo:')
width = st.sidebar.slider("Ancho de gráfico", 0.1, 25., 10.)
height = st.sidebar.slider("Altura de gráfico", 0.1, 25., 3.)

with select_field_for_cluster:
    

    st.header('Variables del cluster')

    st.subheader('Análisis exploratorio')
    st.write('Esta sección esta hecha para que puedas estudiar la relación entre las distintas variables que presenta el modelo de datos.  \n  Prueba seleccionando distinta variables y estudia con esto la correlación (R2) que puede existir entre estas.  \n  De esta forma no avanzaras a ciegas en la construcción de tus clusters.')
    list_exp_analysis = list(data_model_cluster().drop(['nombre_cliente','Contexto_pais_1','Contexto_pais_2'],axis=1).columns)
    data_study_var = data_model_cluster()

    var_a = st.selectbox('Seleccione la primera variable para análisis:',list_exp_analysis)
    var_b = st.selectbox('Seleccione la segunda variable para análisis:',list_exp_analysis)

    r2_value = r2_score(data_study_var[var_a], data_study_var[var_b])
    r2_value = round(r2_value,3)

    st.metric('R-cuadrado',str(r2_value))

    fig, ax = plt.subplots(1, figsize=(width, height))
    ax.scatter(data_study_var[var_a], data_study_var[var_b])
    
    #plt.gca().axes.get_xaxis().set_visible(False)
    #plt.gca().axes.get_yaxis().set_visible(False)

    ax.set_yticklabels([])
    ax.set_xticklabels([])

    ax.set_xlabel(var_a)
    ax.set_ylabel(var_b)

    st.pyplot(fig)


    st.subheader('Selección de variables')
    st.write('Selecciona la variables que deseas incluir o quitar de tu análisis cluster.')
    fields_options = list(data_model_cluster().drop(['nombre_cliente'],axis=1).columns)
    fields_selected =st.multiselect('',
                                    fields_options, 
                                    default = fields_options)
    
    df_cluster = selected_fields(fields_selected)
    df_cluster_st = one_hot_encoding_and_standarize(df_cluster)




with elbow_test:
    st.header('Número optimo de clusters')
    st.write('A continuación puedes estimar el número optimo de cluster gracias a la herramienta que tienes abajo.  \n  El gráfico de codos es una buena manera de estimar cual es el número de sgementos ideal considerando las variables seleccionadas anteriormente.  \n  ¿Necesitas ayuda? No te preocupes que en el siguiente links puedes encontrar definiciones utiles que pueden guiarte un poco más en el muundo de los clusters.  \n  [Click aquí para mayor información](https://aprendeia.com/seleccionar-el-numero-adecuado-de-clusteres/)')
    K, distortions = elbow_information(df_cluster_st)
    fig, ax = plt.subplots(figsize=(width, height))
    ax.plot(K, distortions, 'bx-')
    ax.set_title('Diagrama de codo')
    ax.set_xlabel('k')
    ax.set_ylabel('Distortion')
    #ax.title('The Elbow Method showing the optimal k')
    #ax.show()
    st.pyplot(fig)


st.sidebar.title('Seleccione el n° de clusters que desea:')
n_cluster = st.sidebar.slider('',1,10,5)

list_var = list(df_cluster_st.columns)
var_1 = st.sidebar.selectbox('Seleccione la primera variable:',list_var)
var_2 = st.sidebar.selectbox('Seleccione la segunda variable:',list_var)

with clustering_calculations:
    
    df_cluster_result,df_final = kmeans(n_cluster,df_cluster_st,fields_selected)
    st.title('Resultado clustering')
    st.write("Una vez que ya seleccionaste las variables y el número de cluster, ya puedes estudiar los distintos segmento que se han formado.  \n  Selecciona en el panel a mano izquierda las distintas vairables que te gustaria ver relacionadas y por medio de los distintos colores analiza los clusters creados.  \n  Como información adicional, el algoritmo que se utiliza para la construcción de los segmentos es el algoritmo de aprendizaje no supervisado Kmeans. Si necesitas más información sobre este sigue el siguiente link donde encontrarás mayor información.  \n  [Click aquí para mayor información]('https://aprendeia.com/algoritmo-kmeans-clustering-machine-learning/')")
    st.markdown('A continuación puedes revisar como se agrupan los cluster dependiendo de las variables que selecciones:')
    fig, ax = plt.subplots(figsize=(width, height))
    ax.scatter(df_cluster_result[var_1], df_cluster_result[var_2], c=df_cluster_result['k_means'], cmap=plt.cm.Set1)
    ax.set_xlabel(var_1)
    ax.set_ylabel(var_2)
    ax.set_title('Análisis de segmentos creados', fontsize=18)
    st.pyplot(fig)

with clustering_results:
    st.subheader('Cantidad de clientes por cluster')
    total_clients_by_cluster = df_final.groupby('kmeans').agg(total_clientes=('nombre_cliente','count')).reset_index()
    total_clients_by_cluster.columns = ['N° Cluster','Total Clientes']
    total_clients_by_cluster['N° Cluster'] = total_clients_by_cluster['N° Cluster']+1
    AgGrid(total_clients_by_cluster, 
            theme='blue',
            fit_columns_on_grid_load=True,
            height= 120)


    st.header('Los clusters se componen de la siguiente forma:')
    AgGrid(df_final, 
            theme='blue',
            fit_columns_on_grid_load=False,
            height= 400)
    st.text('Haz click en boton para descargar los resultados')
    df_xlsx = to_excel(df_final)
    st.download_button(label='📥 Descarga los resultados del cluster',
                                    data=df_xlsx ,
                                    file_name= 'df_test.xlsx')

#with silhoutte_analysis:
#    silhouette_plot(n_cluster,df_cluster_st)
#    st.pyplot(fig)