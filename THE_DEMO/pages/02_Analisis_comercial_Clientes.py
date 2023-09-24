# Contents of ~/my_app/pages/page_2.py
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import squarify
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from st_aggrid import AgGrid
import streamlit.components.v1 as components

st.set_page_config(page_title = "Analisis comercial clientes",
                    page_icon = ":bar_chart:")

st.markdown("# Analisis comercial de clientes ⚕️")
#st.sidebar.markdown("# Analisis comercial de clientes ⚕️")

st.sidebar.image("data/Logotipo_Cenabast_2018.png", use_column_width=True)

rfm_segments_en ={'Campeones':'champions',
                    'Potenciales fieles':'potential_loyalists',
                    'Nuevos clientes':'new_customers',
                    'En riesgo':'at_Risk',
                    'No puede perderlos':"cant_loose",
                    'Hibernando':'hibernating',
                    'A punto de riesgo':'about_to_sleep',
                    'Necesita atención':'need_attention',
                    'Clientes fieles':'loyal_customers',
                    'Prometedores':'promising'}


############################### FUNCTIONS ###############################
# RFM FUNCTIONS
# definition of rfm function to get the data
@st.cache 
def rfm_df():
    conn = sqlite3.connect('data/data_cenabast.db')
    c = conn.cursor()
    sqlquery = f""" SELECT * FROM rfm """
    rfm_df =  pd.read_sql_query(sqlquery,con = conn)
    c.close()
    conn.close()

    return rfm_df

@st.cache
def df_info_rfm(segment):

    segment_en = rfm_segments_en[segment]

    conn = sqlite3.connect('data/data_cenabast.db')
    c = conn.cursor()

    sqlquery = f""" SELECT tbl1.client_id as 'ID Cliente',
                    tbl2.name_client as 'Nombre cliente',
                    tbl1.rfm_score as 'RFM Score',
                    tbl1.recency as 'Días desde ultima compra',
                    tbl1.frequency as 'Frecuencia de compra',
                    tbl1.monetary as 'Monto total comprado'
            FROM rfm as tbl1
            LEFT JOIN 
            clients_cenabast as tbl2
            ON tbl1.client_id = tbl2.ID_CLIENT
            WHERE tbl1.segment = '{segment_en}'
            order by tbl1.monetary desc"""
    df_info_rfm = pd.read_sql(sqlquery, con=conn)
    c.close()
    conn.close()
    return df_info_rfm

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

def info_strategy_rfm_segment(segment):

    conn = sqlite3.connect('data/data_cenabast.db')
    c = conn.cursor()

    rfm_segment = segment
    sqlquery_1 = f""" SELECT * FROM rfm_segment_definition WHERE Spanish_name = '{rfm_segment}' """
    df =  pd.read_sql_query(sqlquery_1,con = conn)
    definition_segment = df.iloc[0,2]
    strategy_segment = df.iloc[0,3]
    return definition_segment, strategy_segment

@st.cache
def metrics_rfm(segment):
    conn = sqlite3.connect('data/data_cenabast.db')
    c = conn.cursor()

    segment_en = rfm_segments_en[segment]
    sqlquery_1 = f"""
    select * from
        (SELECT segment,
                count(distinct client_id) as total,
                ROUND(cast(count(distinct client_id) as REAL)/(select count(distinct client_id) from rfm),3)*100 AS Porcentaje_total_clientes,
                ROUND(avg(recency),2) as promedio_dias_ultima_compra,
                ROUND(avg(frequency),2) as promedio_frequecia_compra,
                ROUND(avg(monetary),2) as promedio_monto_total
        FROM rfm
        group by segment) tbl1
    where segment = "{segment_en}"
    """
    df =  pd.read_sql_query(sqlquery_1,con = conn)
    Total_clientes = df.iloc[0,1]
    porcentaje_del_total_clientes = df.iloc[0,2]
    promedio_dias_ultima_compra = df.iloc[0,3]
    promedio_frequecia_compra = df.iloc[0,4]
    promedio_monto_total = df.iloc[0,5]

    return Total_clientes, porcentaje_del_total_clientes, promedio_dias_ultima_compra, promedio_frequecia_compra, promedio_monto_total

############################### VARIABLES ###############################

RFM_segment_list = ['Campeones',
'Potenciales fieles',
'Nuevos clientes',
'En riesgo',
'No puede perderlos',
'Hibernando',
'A punto de riesgo',
'Necesita atención',
'Clientes fieles',
'Prometedores']
############################### SIDEBAR ###############################

with st.sidebar:

    # RFM
    st.header("Menú de segmento")
    RFM_type = st.selectbox('Seleccione segmento que desea revisar:', RFM_segment_list)

############################### CONTAINERS ###############################

rfm_plot_container_st = st.container()
rfm_metrics = st.container()
rfm_info_container_st = st.container()



# RFM table by segment type
with rfm_plot_container_st:

    # List of different rfm segments for the selectbox

    st.title('Segmentación RFM')
    text_menu_pharmacy = """Segmentación de clientes según su comportamiento respecto a las variables: 
                            dias desde la ultima compra (**Recency = R**), Frecuencia (**Frequency = F**) y Monetario (**Monetary = M**)"""
    st.markdown(f"""<span style="word-wrap:break-word;">{text_menu_pharmacy}</span>""", unsafe_allow_html=True)

    st.components.v1.html("""<div class='tableauPlaceholder' id='viz1657492225223' style='position: relative'><noscript><a href='#'><img alt='Customer Segments ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Cu&#47;Customer_Segments_DataCare&#47;Customer_Segment&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='Customer_Segments_DataCare&#47;Customer_Segment' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Cu&#47;Customer_Segments_DataCare&#47;Customer_Segment&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='fr-FR' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1657492225223');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>""",
                        width=1378, height=637, scrolling=True)

    RFM_segment_list = ['hibernating', 'at_Risk', 'cant_loose', 'about_to_sleep', 'need_attention', 'loyal_customers',
                        'promising', 'new_customers', 'potential_loyalists', 'champions']

    
    # Calculate average values for each RFM_Level, and return a size of each segment
    #rfm_df_plot = rfm_df()
    #rfm_level_agg = rfm_df_plot.groupby('segment').agg( recency_mean=('recency', 'mean'),
    #                                                    freq_mean=('frequency', 'mean'),
    #                                                    money_mean=('monetary', 'mean'),
    #                                                    money_count=('monetary', 'count')).round(1)
    #rfm_level_agg.columns = ['RecencyMean', 'FrequencyMean', 'MonetaryMean', 'Count']

    #sq1 = rfm_df_plot.groupby('segment')['client_id'].nunique().sort_values(ascending=True).reset_index()
    #cmap = plt.cm.coolwarm
    #mini = min(sq1.reset_index()['client_id'])
    #maxi = max(sq1.reset_index()['client_id'])
    #norm = mcolors.Normalize(vmin=mini, vmax=maxi)

    # Create our plot and resize it.
    #segments = ['about_to_sleep',
    #            'at_Risk',
    #            'cant_loose',
    #            'champions',
    #            'hibernating',
    #            'loyal_customers',
    #            'need_attention',
    #            'new_customers',
    #            'potential_loyalists',
    #            'promising']

    # colors = ['red','green','yellow','blue','gray','black','orange','purple','cyan','pink']

    #fig = plt.gcf()
    #ax = fig.add_subplot()
    #norm = mcolors.Normalize(vmin=mini, vmax=maxi)
    #colors = [cmap(norm(value)) for value in sq1.reset_index()['client_id']]
    #fig.set_size_inches(16, 10)
    #squarify.plot(sizes=rfm_level_agg['Count'],
    #                label=segments, alpha=.6)
    #plt.title("\nSegmentos RFM Cenabast\n", fontsize=18, fontweight="bold")
    #plt.axis('off')
    #plt.show()
    #st.pyplot(fig)

with rfm_metrics:
    st.subheader(RFM_type)
    Total_clientes, porcentaje_del_total_clientes, promedio_dias_ultima_compra, promedio_frequecia_compra, promedio_monto_total = metrics_rfm(RFM_type)
    
    col1, col2 = st.columns(2)
    
    col1.metric("Total Clientes",Total_clientes)
    col2.metric("Porcentaje del total de clientes",str(round(porcentaje_del_total_clientes,2))+"%")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Promedio días ultima compra", str(promedio_dias_ultima_compra))
    col_b.metric("Promedio de frecuencia de compra",str(promedio_frequecia_compra))
    promedio_monto_total = "{:,}".format(round(promedio_monto_total,2))
    col_c.metric("Monto total promedio (CLP)","$"+promedio_monto_total)


with rfm_info_container_st:
  
    rfm_important_fields = df_info_rfm(RFM_type)
    definition_segment, strategy_segment = info_strategy_rfm_segment(RFM_type)

    st.subheader('Definición')
    st.markdown(definition_segment)
    st.subheader('Estrategia recomendada')
    st.markdown(strategy_segment)

    st.header(f"Lista de clientes del segmento '{RFM_type}'")
    # show relevant rfm table
    AgGrid(rfm_important_fields, 
            theme='blue',
            fit_columns_on_grid_load=False,
            height= 300
            )
