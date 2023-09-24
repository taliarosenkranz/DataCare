# Contents of ~/my_app/pages/page_2.py
from xml.etree.ElementInclude import DEFAULT_MAX_INCLUSION_DEPTH
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import squarify
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from st_aggrid import AgGrid

st.set_page_config(page_title = "Información por cliente",
                    page_icon = ":bar_chart:")

############################### FUNCTIONS ###############################

# definition of rfm function to get the data
@st.cache
def list_name_clients():
    conn = sqlite3.connect('data/data_cenabast.db')
    c = conn.cursor()
    sqlquery = f""" SELECT DISTINCT name_client
                    FROM clients_cenabast
                    WHERE ID_CLIENT IN (SELECT DISTINCT client_id FROM data_trx_cenabast)"""
    df_clients =  pd.read_sql_query(sqlquery,con = conn)
    list_clients = list(df_clients['name_client'])
    c.close()
    conn.close()
    return list_clients

@st.cache
def commercial_info_client_1(client_name):
    conn = sqlite3.connect('data/data_cenabast.db')
    c = conn.cursor()
    sqlquery = f""" SELECT  ID_CLIENT as 'ID Cliente',
                            name_petitioner as 'Nombre Comprador',
                            name_client as 'Nombre Cliente',
                            executive_name as 'Ejecutivo Cenabast',
                            address_delivery_1 as 'Dirección',
                            Comuna,
                            Region
                    FROM clients_cenabast
                    WHERE name_client = '{client_name}' """
    df_clients_commercial_info_1 =  pd.read_sql_query(sqlquery,con = conn)
    c.close()
    conn.close()
    return df_clients_commercial_info_1

@st.cache
def commercial_info_client_2(client_name):
    conn = sqlite3.connect('data/data_cenabast.db')
    c = conn.cursor()

    sqlquery_1 = f"""SELECT DISTINCT ID_CLIENT,
                            name_client as 'name_clients_tbl'
                    FROM 
                    (SELECT ID_CLIENT,
                            name_client 
                    FROM clients_cenabast) as tbl1
                    INNER JOIN 
                    (SELECT 
                        client_id,
                        client_name
                    FROM data_trx_cenabast) as tbl2
                    ON tbl1.ID_CLIENT = tbl2.client_id
                    WHERE client_id IS NOT NULL AND name_client = '{client_name}'"""

    df =  pd.read_sql_query(sqlquery_1,con = conn)

    id_clients = list(df['ID_CLIENT'])
    id_text_query = ''
    for i,id in enumerate(id_clients):
        if i < len(id_clients)-1:
            id_text = "'"+id+"', "
            id_text_query = id_text_query+id_text
        else:
            id_text = "'"+id+"'"
            id_text_query = id_text_query+id_text

    sqlquery = f""" SELECT * FROM
                    (SELECT name_client as 'nombre cliente',
                            MIN(DATE(date_invoice)) AS 'Primera compra',
                            MAX(DATE(date_invoice)) AS 'Ultima compra',
                            ROUND((JULIANDAY(MAX(DATE(date_invoice)))-JULIANDAY(MIN(DATE(date_invoice))))/365,2) AS Años,
                            COUNT(DISTINCT date_invoice) as 'N° total pedidos',
                            SUM(real_qty*price_cenabast) AS 'Ingreso Cenabast',
                            SUM(real_qty*price_sale) AS 'Ingreso farmacia',
                            SUM(real_qty*avg_price_market) AS 'Ingreso precio mercado',
                            SUM(real_qty*price_sale)-SUM(real_qty*price_cenabast) AS 'Margen total Farmacia',
                            COUNT(DISTINCT hierarchy_cenabast) as 'Variedad de productos',
                            COUNT(DISTINCT product_code) as 'variedad PA',
                            COUNT(DISTINCT material) as 'variedad Productos',
                            COUNT(DISTINCT client_id) as 'puntos de venta'
                    FROM (SELECT * FROM 
                    (SELECT * 
                    FROM data_trx_cenabast) as tbl2
                    LEFT JOIN
                    (SELECT DISTINCT name_client,
                            ID_CLIENT
                    FROM clients_cenabast
                    WHERE ID_CLIENT IN ({id_text_query})) as tbl3
                    ON tbl2.client_id = tbl3.ID_CLIENT
                    WHERE name_client IS NOT NULL
                    ) as tbl1
                    GROUP BY name_client) as tbl4 """

    df_clients_commercial_info_2 =  pd.read_sql_query(sqlquery,con = conn)
    
    c.close()
    conn.close()


    return df_clients_commercial_info_2

@st.cache
def recommender_products_client(client_name):
    conn = sqlite3.connect('data/data_cenabast.db')
    c = conn.cursor()
    sqlquery = f""" SELECT * FROM data_recommender"""
    df_recommender =  pd.read_sql_query(sqlquery,con = conn)
    df_recommender['rating'] = pd.to_numeric(df_recommender['rating'])

    from matrix_factorization import BaselineModel, KernelMF, train_update_test_split
    from sklearn.metrics import mean_squared_error
        # Prepare data for online learning
    try:
        (
            X_train_initial,
            y_train_initial,
            X_train_update,
            y_train_update,
            X_test_update,
            y_test_update,
        ) = train_update_test_split(df_recommender,frac_new_users=0.2)
        # Initial training
        matrix_fact = KernelMF(n_epochs=20, n_factors=100, verbose=1, lr=0.001, reg=0.005)
        matrix_fact.fit(X_train_initial, y_train_initial)
        # Update model with new users
        matrix_fact.update_users(X_train_update, y_train_update, lr=0.001, n_epochs=50, verbose=1)
        
        sqlquery_1 = f"""SELECT DISTINCT ID_CLIENT,
                                name_client as 'name_clients_tbl'
                        FROM 
                        (SELECT ID_CLIENT,
                                name_client 
                        FROM clients_cenabast) as tbl1
                        INNER JOIN 
                        (SELECT 
                            client_id,
                            client_name
                        FROM data_trx_cenabast) as tbl2
                        ON tbl1.ID_CLIENT = tbl2.client_id
                        WHERE client_id IS NOT NULL AND name_client = '{client_name}'"""

        df =  pd.read_sql_query(sqlquery_1,con = conn)
        list_id_clients = list(df['ID_CLIENT'])

        users = list_id_clients
        tbl_rec = pd.DataFrame(columns=['user_id','item_id','rating_pred'])

        for user in users:
            items_known = X_train_initial.query("user_id == @user")["item_id"]
            recomend_pred = matrix_fact.recommend(user=user, items_known=items_known)
            recomend_pred.sort_values(by="rating_pred", ascending = False, inplace=True)
            recomend_pred['rating_pred'] = round(recomend_pred['rating_pred'],2)
            tbl_rec = pd.concat([tbl_rec,recomend_pred])

        tbl_rec.columns = ['id_clients','product_code','rating_pred']

        sqlquery_info_client = f"""   SELECT DISTINCT product_code,
                                product_description,
                                hierarchy_cenabast
                            FROM data_trx_cenabast"""
        df_info_client =  pd.read_sql_query(sqlquery_info_client,con = conn)

        tbl_rec = tbl_rec.merge(df_info_client, on ='product_code',how='left')
        tbl_rec = tbl_rec[['id_clients','product_code','product_description','hierarchy_cenabast','rating_pred']]
        tbl_rec.columns = ['ID Cliente','ZGEN','Nombre producto genérico','Jerarquía Cenabast','Rating de recomendación']
        tbl_rec.sort_values(by="Rating de recomendación", ascending = False, inplace=True)

        c.close()
        conn.close()
    except:
        sqlquery_info_client = f"""   
                            SELECT DISTINCT product_code,
                                product_description,
                                hierarchy_cenabast,
                                'Actualizar campo de cliente' as 'Error ML Code'
                            FROM data_trx_cenabast"""
        tbl_rec =  pd.read_sql_query(sqlquery_info_client,con = conn)


    return tbl_rec

st.sidebar.image("data/Logotipo_Cenabast_2018.png", use_column_width=True)

with st.sidebar:

    # Clientes
    st.header("""Menú de clientes""")
    text_menu_pharmacy = 'Seleccione el cliente que desea revisar. Aqui podrá revisar la información de esta y su comportamiento'
    st.markdown(f"""<span style="word-wrap:break-word;">{text_menu_pharmacy}</span>""", unsafe_allow_html=True)
    list_pharmacies = list_name_clients()
    client_name = st.selectbox('Seleccione Farmacia:', list_pharmacies)

client_info = st.container()
recommender_products = st.container()

with client_info:
    st.markdown('<h1 style="float: left;"> Estadisticas por cliente </h1>', unsafe_allow_html=True)
    #st.markdown('Suzieq<img style="float: right;" src="logo_datacare.jpg" />')
    st.write("""La siguiente pagina contiene información sobre los clientes de Cenabast  \n  Aquí podrás encontrar:  \n  * **Metricas** relevantes a tu cliente para entender un poco mejor la realidad de este.  \n  * **Información sobre los puntos de venta**, la cual busca ayudar al contacto y gestión del cliente.  \n  * **Recomedador de productos** que indica que productos pueden ser atractivos para tu cliente considerando el comportamiento comercial con tus productos.  \n  Empieza a investigar y conocer a tus clientes!""")
    st.write('  \n  ')
    #st.write('  \n  ')
    st.title(f'{client_name}')
    #st.write('  \n  ')
    st.title('  \n  ')

    st.header(f'Metricas')

    df_client_metrics = commercial_info_client_2(client_name)

    # Section A
    first_purchase = df_client_metrics.iloc[0,1]
    last_purchase = df_client_metrics.iloc[0,2]
    years_as_client = pd.to_numeric(df_client_metrics.iloc[0,3])
    years_as_client = round(years_as_client,1)

    col_a1,col_a2,col_a3 = st.columns(3)

    col_a1.metric("1era Compra",first_purchase)
    col_a2.metric("Ultima compra Compra",last_purchase)
    col_a3.metric('Tiempo como cliente',str(years_as_client)+" años")
    
    # Section B

    
    cenabast_revenue = df_client_metrics.iloc[0,5]
    cenabast_revenue = "{:,}".format(round(cenabast_revenue,2))
    client_GAP = df_client_metrics.iloc[0,8]
    client_GAP = "{:,}".format(round(client_GAP,2))
    perc_gap = (df_client_metrics.iloc[0,6] - df_client_metrics.iloc[0,5])/df_client_metrics.iloc[0,5]
    perc_gap = round(perc_gap,3)*100

    col_b1,col_b2,col_b3 = st.columns(3)

    
    col_b1.metric("Ingreso Cenabast (CLP)",'$'+str(cenabast_revenue))
    col_b2.metric("Margen cliente (CLP)",'$'+str(client_GAP))
    col_b3.metric("Margen % cliente",str(perc_gap)+"%")
    
    # Section C
    total_purchases = df_client_metrics.iloc[0,4]
    avg_ticket = df_client_metrics.iloc[0,5]/total_purchases
    avg_ticket = "{:,}".format(round(avg_ticket,2))
    pos = df_client_metrics.iloc[0,-1]

    col_c1,col_c2,col_c3 = st.columns(3)

    col_c1.metric('N° pedidos totales',total_purchases)
    col_c2.metric('Ticket promedio cliente',"$"+str(avg_ticket))
    col_c3.metric('Puntos de venta',pos)

    #AgGrid(df_client_metrics,theme='blue',fit_columns_on_grid_load=False,height= 100)


    st.write('  \n  ')
    st.header(f'Información Puntos de Venta')
    AgGrid(commercial_info_client_1(client_name), 
            theme='blue',
            fit_columns_on_grid_load=False,
            height= 100)

    

with recommender_products:
    st.write('  \n  ')
    st.header(f'Productos recomendados')
    st.write("""Mediante la frecuencia de compra, las cantidades compradas y los montos totales ($) por cliente y producto \n  Hemos creado esta herramienta que busca recomendar productos por cliente, de manera de mejorar la oferta.  \n  Dentro de tabla que se muestra abajo, se encuentra la lista de productos por cliente.  \n  La columna "Rating de recomendación" mide cuan acertada el la recomendación del producto para dicho cliente.   \n  Los valores de este rating se mueve entre **1** y **5** puntos. De esta manera mientras más cerca este de 5, más interesante es el producto para dicho cliente.""")
    st.write(":bangbang: En caso que la columna 'Rating de comparación' tome el valor 'Actualizar campo de cliente', seleccionar nuevamente dicho cliente para que el algoritmo corra nuevamente.")
    AgGrid(recommender_products_client(client_name), 
            theme='blue',
            fit_columns_on_grid_load=False,
            height= 400)
