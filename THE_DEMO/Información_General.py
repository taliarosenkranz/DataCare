# Contents of ~/my_app/main_page.py
import streamlit as st
import streamlit.components.v1 as components
from IPython.core.display import HTML
from IPython.display import IFrame
from IPython.core.display import display
import sqlite3
import pandas as pd

@st.cache
def metrics_cenabast(): 
	conn = sqlite3.connect('data/data_cenabast.db')
	c = conn.cursor()
	# Actual Date
	sqlquery_1 = f""" SELECT 	MAX(date_delivery) AS date_evaluation,
			SUM(price_cenabast*real_qty) AS total_sales,
			SUM(real_qty) AS total_products,
			COUNT(DISTINCT client_id) AS total_clients
	FROM data_trx_cenabast
	WHERE date_delivery <= (SELECT actual_date
	FROM 
	(SELECT MAX(STRFTIME('%Y-%m-%d', date_delivery)) AS actual_date,
			datetime(MAX(STRFTIME('%Y-%m-%d', date_delivery)),'-1 month') as last_month,
			datetime(MAX(STRFTIME('%Y-%m-%d', date_delivery)),'-1 year') as last_year
	FROM data_trx_cenabast dtc) AS tbl_dates)"""
	df_info_cenabast_now =  pd.read_sql_query(sqlquery_1,con = conn)

	# Last Month
	sqlquery_2 = f""" SELECT 	MAX(date_delivery) AS date_evaluation,
			SUM(price_cenabast*real_qty) AS total_sales,
			SUM(real_qty) AS total_products,
			COUNT(DISTINCT client_id) AS total_clients
	FROM data_trx_cenabast
	WHERE date_delivery <= (SELECT last_month
	FROM 
	(SELECT MAX(STRFTIME('%Y-%m-%d', date_delivery)) AS actual_date,
			datetime(MAX(STRFTIME('%Y-%m-%d', date_delivery)),'-1 month') as last_month,
			datetime(MAX(STRFTIME('%Y-%m-%d', date_delivery)),'-1 year') as last_year
	FROM data_trx_cenabast dtc) AS tbl_dates)"""
	df_info_cenabast_lm =  pd.read_sql_query(sqlquery_2,con = conn)

	# Last Year
	sqlquery_3 = f""" SELECT 	MAX(date_delivery) AS date_evaluation,
			SUM(price_cenabast*real_qty) AS total_sales,
			SUM(real_qty) AS total_products,
			COUNT(DISTINCT client_id) AS total_clients
	FROM data_trx_cenabast
	WHERE date_delivery <= (SELECT last_year
	FROM 
	(SELECT MAX(STRFTIME('%Y-%m-%d', date_delivery)) AS actual_date,
			datetime(MAX(STRFTIME('%Y-%m-%d', date_delivery)),'-1 month') as last_month,
			datetime(MAX(STRFTIME('%Y-%m-%d', date_delivery)),'-1 year') as last_year
	FROM data_trx_cenabast dtc) AS tbl_dates)"""
	df_info_cenabast_ly =  pd.read_sql_query(sqlquery_3,con = conn)


	# Date now
	date_now = df_info_cenabast_now.iloc[0,0]
	total_sales_now = df_info_cenabast_now.iloc[0,1]
	total_products_now = df_info_cenabast_now.iloc[0,2]
	total_clients_now = df_info_cenabast_now.iloc[0,3]
	# Data last month
	date_lm = df_info_cenabast_lm.iloc[0,0]
	total_sales_lm = df_info_cenabast_lm.iloc[0,1]
	total_products_lm = df_info_cenabast_lm.iloc[0,2]
	total_clients_lm = df_info_cenabast_lm.iloc[0,3]
	# Data last year
	date_ly = df_info_cenabast_ly.iloc[0,0]
	total_sales_ly = df_info_cenabast_ly.iloc[0,1]
	total_products_ly = df_info_cenabast_ly.iloc[0,2]
	total_clients_ly = df_info_cenabast_ly.iloc[0,3]


	return date_now,total_sales_now,total_products_now,total_clients_now, date_lm, total_sales_lm,total_products_lm,total_clients_lm, date_ly, total_sales_ly, total_products_ly, total_clients_ly



st.set_page_config(page_title = "Información General",
                    page_icon = ":bar_chart:")

st.markdown("# Información general 🔬")
st.sidebar.markdown("# Información general")

date_now,total_sales_now,total_products_now,total_clients_now, date_lm, total_sales_lm,total_products_lm,total_clients_lm, date_ly, total_sales_ly, total_products_ly, total_clients_ly = metrics_cenabast()

st.write(f"Métricas al día {date_now}")
st.title('  \n  ')
col_a1,col_a2,col_a3 = st.columns(3)

million = 1000000

total_sales_now = total_sales_now/million
total_sales_lm = total_sales_lm/million
total_sales_ly = total_sales_ly/million

total_sales_now = "{:,}".format(round(total_sales_now,2))
total_sales_lm = "{:,}".format(round(total_sales_lm,2))
total_sales_ly = "{:,}".format(round(total_sales_ly,2))


col_a1.metric('Ventas totales hoy',"$"+str(total_sales_now)+' MM')
col_a2.metric('Ventas totales mes pasado',"$"+str(total_sales_lm)+' MM')
col_a3.metric('Ventas totales año pasado',"$"+str(total_sales_ly)+' MM')
st.title('  \n  ')

col_b1,col_b2,col_b3 = st.columns(3)

total_products_now = total_products_now/1000000
total_products_lm = total_products_lm/1000000
total_products_ly = total_products_ly/1000000

total_products_now = "{:,}".format(round(total_products_now,2))
total_products_lm = "{:,}".format(round(total_products_lm,2))
total_products_ly = "{:,}".format(round(total_products_ly,2))

col_b1.metric('Cantidad total vendida hoy',str(total_products_now)+' MM')
col_b2.metric('Cantidad total vendida mes pasado',str(total_products_lm)+' MM')
col_b3.metric('Cantidad total vendida año pasado',str(total_products_ly)+' MM')
st.title('  \n  ')

col_c1,col_c2,col_c3 = st.columns(3)

col_c1.metric('Clientes totales hoy',total_clients_now)
col_c2.metric('Clientes totales mes pasado',total_clients_lm)
col_c3.metric('Clientes totales año pasado',total_clients_ly)

st.sidebar.image("data/Logotipo_Cenabast_2018.png", use_column_width=True)

st.write("Información general de ventas. Se muestran los productos más vendidos por categoría y los clientes que compran en más cantidad.")

st.components.v1.html("""<div class='tableauPlaceholder' id='viz1651797807664' style='position: relative'><noscript><a href='#'><img alt='Dashboard ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Sa&#47;SampleDashboardDC2022&#47;Dashboard&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='SampleDashboardDC2022&#47;Dashboard' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Sa&#47;SampleDashboardDC2022&#47;Dashboard&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-GB' /><param name='ignore_sticky_session' value='yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1651797807664');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='1000px';vizElement.style.height='827px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='1000px';vizElement.style.height='827px';} else { vizElement.style.width='100%';vizElement.style.height='1427px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>""",
                        width=1378, height=637, scrolling=True)