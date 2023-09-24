# Contents of ~/my_app/pages/page_3.py
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title = "Canasta de mercado",
                    page_icon = ":bar_chart:")

st.markdown("# Market Basket Analysis")

st.sidebar.image("data/Logotipo_Cenabast_2018.png", use_column_width=True)

st.sidebar.markdown("# MBA 🧺")

st.write("Análisis de canasta de mercado. Este gráfico muestra la asociación entre las categorías de productos compradas con mayor frequencia. Es decir, se ilustran los tipos de producto comprados en conjunto frecuentemente. Entre mayor sea su asociación, más intenso es su color. Se muestran únicamente productos altamente asociados entre sí. Para ver los productos más frecuentemente asociados con una categoría específica, seleccionar categoría en el botón en la esquina izquierda superior del gráfico. El azul oscuro indica mayor asociación.")

st.components.v1.html("""<div class='tableauPlaceholder' id='viz1656260935668' style='position: relative'><noscript><a href='#'><img alt='MBA ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;MB&#47;MBA_16562606562150&#47;MBA&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='MBA_16562606562150&#47;MBA' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;MB&#47;MBA_16562606562150&#47;MBA&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='fr-FR' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1656260935668');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='1000px';vizElement.style.height='827px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='1000px';vizElement.style.height='827px';} else { vizElement.style.width='100%';vizElement.style.height='727px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>""",
                        width=1378, height=637, scrolling=True)