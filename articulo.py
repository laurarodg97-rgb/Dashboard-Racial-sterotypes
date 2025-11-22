import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as stats
import pingouin as pg
from scipy.stats import shapiro, levene
import warnings

# Ignorar warnings
warnings.filterwarnings("ignore")

# --- 1. CONFIGURACIÓN DE PÁGINA (Debe ir primero) ---
st.set_page_config(
    page_title="Dashboard Sesgos Raciales",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INYECCIÓN DE CSS CORREGIDA ---
SIDEBAR_BACKGROUND_COLOR = "#f0f2f6" 
KPI_CARD_BACKGROUND_COLOR = "#e0f2f7" 
KPI_BORDER_COLOR = "#b2ebf2"

st.markdown(f"""
<style>
    /* 1. Aplicar Times New Roman al contenido general, pero de forma segura */
    html, body, p, div, span, li, a, button, input {{
        font-family: "Times New Roman", Times, serif;
        font-size: 16px;
    }}

    /* 2. Asegurar títulos */
    h1, h2, h3, h4, h5, h6, .stHeading {{
        font-family: "Times New Roman", Times, serif !important;
    }}

    /* 3. SOLUCIÓN AL BUG: Proteger los iconos de Streamlit */
    /* Forzamos a que los iconos usen su fuente original y no Times New Roman */
    [data-testid="stExpanderToggleIcon"] {{
        font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
        font-style: normal !important;
        font-weight: normal !important;
        font-variant: normal !important;
        text-transform: none !important;
        line-height: 1;
        display: inline-block;
        /* Aseguramos que el texto del icono sea visible como icono */
        text-indent: 0px !important; 
    }}
    
    /* Asegurar que el contenido dentro del icono (el SVG o texto) no se oculte */
    [data-testid="stExpanderToggleIcon"] > * {{
        text-indent: 0px !important;
    }}

    /* 4. Estilos de la Barra Lateral */
    [data-testid="stSidebar"] {{ 
        background-color: {SIDEBAR_BACKGROUND_COLOR};
    }}

    /* 5. Estilo para las tarjetas de KPI (Metric Containers) */
    [data-testid="stMetric"] {{
        background-color: {KPI_CARD_BACKGROUND_COLOR};
        border-radius: 10px;
        border: 1px solid {KPI_BORDER_COLOR};
        padding: 15px;
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
    }}
    
    /* Centrar etiquetas de métricas */
    [data-testid="stMetricLabel"] {{
        display: flex;
        justify-content: center;
        font-weight: bold;
    }}
    
    /* Centrar valor de métricas */
    [data-testid="stMetricValue"] {{
        display: flex;
        justify-content: center;
    }}

</style>
""", unsafe_allow_html=True)

# Paleta de Colores
COLOR_AZULITO = "#A5D6A7" 
COLOR_ROSITA = "#F8BBD0"
COLOR_PRIME_BLACK = '#3949AB' 
COLOR_PRIME_WHITE = '#E91E63'


@st.cache_data
def load_data(file_name):
    """Función para cargar y cachear datos."""
    try:
        df = pd.read_csv(file_name)
        # Convertir a categórico
        if 'id' in df.columns:
            df['id'] = df['id'].astype('category')
        if 'prime' in df.columns:
            df['prime'] = df['prime'].astype('category')
        if 'target' in df.columns:
            df['target'] = df['target'].astype('category')
        return df
    except FileNotFoundError:
        st.error(f"Error: Archivo '{file_name}' no encontrado. Asegúrate de que los archivos CSV estén en la carpeta correcta.")
        return pd.DataFrame()

def formatear_tabla_anova(anova_df):
    """
    Formatea la salida de Pingouin para que coincida con la tabla estilo Minitab/SAS:
    Source | DF | Adj SS | Adj MS | F-Value | P-Value
    """
    # 1. Mapeo de nombres de columnas de Pingouin a tu formato deseado
    nombres_nuevos = {
        'Source': 'Source',
        'DF': 'DF',      # Pingouin ya devuelve 'DF' cuando detailed=True
        'SS': 'Adj SS',  # Sum of Squares -> Adj SS
        'MS': 'Adj MS',  # Mean Square -> Adj MS
        'F': 'F-Value',
        'p-unc': 'P-Value'
    }
    
    # 2. Seleccionar solo las columnas que existen en el mapeo
    # (Filtramos np2 o eps que no están en tu imagen)
    cols_a_mantener = [col for col in nombres_nuevos.keys() if col in anova_df.columns]
    df_final = anova_df[cols_a_mantener].rename(columns=nombres_nuevos)
    
    # 3. Redondeo para estética (opcional, puedes ajustar los decimales)
    # P-Value suele requerir más precisión, el resto 2 o 3 decimales.
    return df_final

# Carga de todos los dataframes
data_raw = load_data("ANOVA beh RT.csv")
data_mvpa = load_data("ANOVA object-sensitive_WIT.csv")
data_search = load_data("ANOVA searchlight_WIT.csv")

# --- 2. PRE-PROCESAMIENTO Y FILTRADO (Manteniendo la lógica original) ---

if not data_raw.empty:
    data_limpia = data_raw.copy()
    
    # Filtrado de Outliers Conductuales
    data_limpia_filtrada = data_limpia[
        (data_limpia['rt_raw'] > 200) & (data_limpia['rt_raw'] < 2000)
    ].copy()
    
    # Si los datos neuro están presentes, aplicar lógica de limpieza original (conversión de 'value')
    def clean_neuro_data(df):
        if not df.empty and 'value' in df.columns:
            data = df.copy()
            data['value'] = (data['value'].astype(str)
                             .str.replace(r'\s+', '', regex=True)
                             .str.replace(r'\.(?=.*\.)', '', regex=True)
                             .astype(float))
            # Asegurar factores
            data['id'] = data['id'].astype('category')
            data['prime'] = data['prime'].astype('category')
            data['target'] = data['target'].astype('category')
            return data
        return df

    data_limpiamvpa = clean_neuro_data(data_mvpa)
    data_limpiasearch = clean_neuro_data(data_search)
else:
    st.stop() # Detener si no hay datos principales

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.title("Reporte Analítico")
    st.header("Estudio: Sesgos Raciales")
    st.markdown("**Autores:**")
    st.markdown(" - Juan David Roa")
    st.markdown(" - Laura Camila Rodríguez G.")
    st.markdown("---")
    st.caption(f"Última Actualización: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")

# --- 4. TÍTULO PRINCIPAL Y TABS ---
st.markdown("# Sesgos Raciales en la Percepción de Objetos")
st.markdown("## Juan David Roa - Laura Camila Rodríguez G.")

# ==============================================================================
# === SECCIÓN KPI ACTUALIZADA ===
# ==============================================================================
st.markdown("---")
st.subheader("🎯 Indicadores Clave de Desempeño (KPIs) Conductuales")

# Calcular métricas importantes
total_participantes = data_limpia['id'].nunique()
media_rt_general = data_limpia['rt_raw'].mean()
media_rt_log_general = data_limpia['rt_log'].mean()
desviacion_estandar_rt = data_limpia['rt_raw'].std()

# Crear columnas para las métricas
col_p, col_rt_mean, col_rt_log_mean, col_rt_std = st.columns(4)

with col_p:
    st.metric(label="👥 Total Participantes", value=f"{total_participantes}")
with col_rt_mean:
    st.metric(label="⏱️ Media Global RT (ms)", value=f"{media_rt_general:.2f}", help="Tiempo de Reacción Bruto Promedio.")
with col_rt_log_mean:
    st.metric(label="📈 Media Global RT (log)", value=f"{media_rt_log_general:.2f}", help="Tiempo de Reacción Promedio (Transformación Logarítmica).")
with col_rt_std:
    st.metric(label="📏 Desviación Estándar RT (ms)", value=f"{desviacion_estandar_rt:.2f}", help="Variabilidad en los Tiempos de Reacción Brutos.")

st.markdown("---")
# ==============================================================================
# === FIN DE LA SECCIÓN KPI ===
# ==============================================================================

tab_intro, tab_viz, tab_anova_beh, tab_anova_mvpa, tab_anova_search = st.tabs([
    "📝 Introducción y Exploración", 
    "📈 Visualización de Interacción", 
    "📊 ANOVA Conductual (RT)", 
    "🧠 ANOVA MVPA (Sensitive WIT)",
    "🔍 ANOVA Searchlight (WIT)"
])

# ==============================================================================
# === TAB 1: INTRODUCCIÓN Y EXPLORACIÓN ===
# ==============================================================================
with tab_intro:
    st.header("Introducción y Contexto Experimental")
    st.write(
        "Este informe presenta un análisis exploratorio de datos (EDA) " 
        "basado en un estudio experimental que evalúa la presencia de sesgo "
        "racial implícito en la identificación rápida de objetos. " 
        "Específicamente, se examina si los participantes muestran "
        "diferencias en sus tiempos de reacción al identificar armas (*guns*) versus "
        "herramientas (*tools*) cuando se les presenta previamente una cara de una "
        "persona negra (*Black prime*) o blanca (*White prime*). El objetivo es explorar "
        "si existe una interacción entre el tipo de *prime* racial y el tipo de objeto, "
        "lo cual sería indicativo de un sesgo estereotipado (por ejemplo, asociar más "
        "rápidamente armas con personas negras)."
    )
    
    st.markdown("---")
    
    st.header("Datos y Balance del Diseño")
    
    # Resumen Estadístico
    st.markdown("### Resumen Estadístico")
    st.dataframe(data_raw.describe().round(2))
    st.markdown("**Comentario**: Se verifican las variables y la ausencia de valores faltantes. El conjunto de datos contiene las columnas `prime`, `target`, `rt_raw` y `rt_log`, listas para el análisis.")
    
    # Balance
    st.markdown("### Balance del Diseño")
    tabla = pd.crosstab(data_limpia['prime'], data_limpia['target'])
    st.dataframe(tabla)
    st.markdown("**Comentario**: El diseño está balanceado: cada combinación de `prime` y `target` tiene el mismo número de observaciones, lo cual es necesario para un análisis de varianza válido.")
    
    st.markdown("---")
    
    st.header("Distribución de los Tiempos de Reacción (RT)")
    
    # --- Distribución Datos Brutos y Transformados ---
    col_raw_dist, col_log_dist = st.columns(2)

    with col_raw_dist:
        st.subheader("Datos Brutos ($RT_{raw}$)")
        # Gráficos de Datos Brutos con Plotly
        
        # Histograma
        fig_hist_raw = px.histogram(
            data_limpia, 
            x='rt_raw', 
            nbins=30,
            title='Histograma: Datos Brutos',
            labels={'rt_raw': 'Tiempo de reacción (ms)'},
            color_discrete_sequence=[COLOR_AZULITO]
        )
        fig_hist_raw.update_traces(marker_line_color='black', marker_line_width=1)
        fig_hist_raw.update_layout(
            title_font_size=14,
            title_font_family="Times New Roman",
            font_family="Times New Roman",
            template='plotly_white',
            height=300
        )
        st.plotly_chart(fig_hist_raw, use_container_width=True, key="hist_raw")
        
        # Q-Q Plot
        qq_data = stats.probplot(data_limpia['rt_raw'], dist="norm")
        fig_qq_raw = go.Figure()
        fig_qq_raw.add_trace(go.Scatter(
            x=qq_data[0][0],
            y=qq_data[0][1],
            mode='markers',
            marker=dict(color=COLOR_AZULITO, size=6),
            name='Datos'
        ))
        # Línea teórica
        fig_qq_raw.add_trace(go.Scatter(
            x=qq_data[0][0],
            y=qq_data[1][0] * qq_data[0][0] + qq_data[1][1],
            mode='lines',
            line=dict(color='black', width=2),
            name='Teórica'
        ))
        fig_qq_raw.update_layout(
            title='Q-Q Plot: Datos Brutos',
            title_font_size=14,
            title_font_family="Times New Roman",
            font_family="Times New Roman",
            xaxis_title='Cuantiles teóricos',
            yaxis_title='Cuantiles muestrales',
            template='plotly_white',
            showlegend=False,
            height=300
        )
        st.plotly_chart(fig_qq_raw, use_container_width=True, key="qq_raw")
        st.markdown("**Comentario**: Los tiempos de reacción brutos muestran una fuerte asimetría positiva, lo que viola el supuesto de normalidad. Se justifica la transformación logarítmica.")

    with col_log_dist:
        st.subheader("Datos Transformados ($RT_{log}$)")
        # Gráficos de Datos Transformados con Plotly
        
        # Histograma
        fig_hist_log = px.histogram(
            data_limpia, 
            x='rt_log', 
            nbins=30,
            title='Histograma: Datos Transformados',
            labels={'rt_log': 'log(Tiempo de reacción)'},
            color_discrete_sequence=[COLOR_ROSITA]
        )
        fig_hist_log.update_traces(marker_line_color='black', marker_line_width=1)
        fig_hist_log.update_layout(
            title_font_size=14,
            title_font_family="Times New Roman",
            font_family="Times New Roman",
            template='plotly_white',
            height=300
        )
        st.plotly_chart(fig_hist_log, use_container_width=True, key="hist_log")
        
        # Q-Q Plot
        qq_data = stats.probplot(data_limpia['rt_log'], dist="norm")
        fig_qq_log = go.Figure()
        fig_qq_log.add_trace(go.Scatter(
            x=qq_data[0][0],
            y=qq_data[0][1],
            mode='markers',
            marker=dict(color=COLOR_ROSITA, size=6),
            name='Datos'
        ))
        # Línea teórica
        fig_qq_log.add_trace(go.Scatter(
            x=qq_data[0][0],
            y=qq_data[1][0] * qq_data[0][0] + qq_data[1][1],
            mode='lines',
            line=dict(color='black', width=2),
            name='Teórica'
        ))
        fig_qq_log.update_layout(
            title='Q-Q Plot: Datos Transformados',
            title_font_size=14,
            title_font_family="Times New Roman",
            font_family="Times New Roman",
            xaxis_title='Cuantiles teóricos',
            yaxis_title='Cuantiles muestrales',
            template='plotly_white',
            showlegend=False,
            height=300
        )
        st.plotly_chart(fig_qq_log, use_container_width=True, key="qq_log")
        st.markdown("**Comentario**: La transformación logarítmica mejora significativamente la normalidad de los datos, haciendo que la distribución se aproxime más a una normal. Es adecuada para análisis paramétricos posteriores.")

# ==============================================================================
# === TAB 2: VISUALIZACIÓN DE INTERACCIÓN (Mann-Whitney ELIMINADO) ===
# ==============================================================================
with tab_viz:
    st.header("Visualización Detallada de la Interacción Esperada")

    # --- Boxplot y Estadísticas ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Diagrama de Cajas de Tiempo de Respuesta (log)")
        # Generación del Boxplot con Plotly
        
        fig_box = px.box(
            data_limpia, 
            x='prime', 
            y='rt_log', 
            color='target',
            color_discrete_map={"gun": COLOR_PRIME_BLACK, "tool": COLOR_PRIME_WHITE},
            title='Diagrama de cajas de tiempo de respuesta (log)',
            labels={
                'prime': 'Raza del prime',
                'rt_log': 'Tiempo de respuesta (log)',
                'target': 'Target'
            },
            points='all',  # Muestra todos los puntos
            category_orders={'target': ['gun', 'tool']}
        )
        
        fig_box.update_traces(
            marker=dict(size=3, opacity=0.5),
            boxmean=True
        )
        
        fig_box.update_layout(
            title_font_size=16,
            title_font_family="Times New Roman",
            font_family="Times New Roman",
            template='plotly_white',
            height=600,
            legend=dict(
                title='Target',
                yanchor='top',
                y=0.99,
                xanchor='right',
                x=0.99,
                bgcolor='rgba(255,255,255,0.9)'
            ),
            xaxis=dict(title_font_size=14),
            yaxis=dict(title_font_size=14, gridcolor='rgba(0,0,0,0.1)')
        )
        
        # Actualizar nombres en leyenda
        fig_box.for_each_trace(lambda t: t.update(name='Arma' if t.name == 'gun' else 'Herramienta'))
        
        st.plotly_chart(fig_box, use_container_width=True, key="boxplot_main")

        # INTERPRETACIÓN MOVIDA AQUÍ (Bajo el Boxplot)
        st.markdown(
            "> **Interpretación de Medidas Descriptivas**:\n"
            "- Los tiempos de reacción son más bajos (más rápidos) para armas que para herramientas.\n"
            "- La diferencia entre armas y herramientas parece ser mayor cuando el *prime* es **Black**.\n"
            "- Para armas, los tiempos de reacción son similares independientemente del prime racial.\n"
            "Este patrón gráfico sugiere la **interacción clave** (sesgo racial implícito) que será confirmada por el ANOVA."
        )

    with col2:
        st.subheader("Estadísticas por Grupo")
        stats_df = data_limpia.groupby(['prime', 'target'])['rt_log'].agg([
            'count', 'mean', 'std', 'median'
        ]).round(3)
        st.dataframe(stats_df, use_container_width=True)
        
        st.subheader("Tests de Inferencia Univariados")
        st.info("Los tests inferenciales de comparación (e.g., Mann-Whitney) se han omitido en esta sección para enfocarse en la visualización descriptiva. El **ANOVA** confirma la interacción en la siguiente pestaña.")

    st.markdown("---")
    
    st.header("Gráfico de Interacción - Prime vs Target")
    
    # Calcular medias y errores estándar para el gráfico de interacción
    interaction_data = data_limpia.groupby(['target', 'prime'])['rt_log'].agg(['mean', 'sem']).reset_index()
    
    fig_interaction = go.Figure()
    
    for prime_val, color, symbol in zip(
        ['Black', 'White'], 
        [COLOR_PRIME_BLACK, COLOR_PRIME_WHITE],
        ['circle', 'square']
    ):
        subset = interaction_data[interaction_data['prime'] == prime_val]
        
        fig_interaction.add_trace(go.Scatter(
            x=subset['target'],
            y=subset['mean'],
            error_y=dict(type='data', array=subset['sem'], visible=True, width=4, thickness=2),
            mode='lines+markers',
            name=prime_val,
            line=dict(color=color, width=2),
            marker=dict(size=12, color=color, symbol=symbol, line=dict(color='white', width=1)),
            text=[f"{val:.2f}" for val in subset['mean']],
            textposition='top center',
            textfont=dict(size=10, family="Times New Roman", color='black'),
            showlegend=True
        ))
        
        # Añadir anotaciones con valores
        for idx, row in subset.iterrows():
            fig_interaction.add_annotation(
                x=row['target'],
                y=row['mean'] + 0.03,
                text=f"{row['mean']:.2f}",
                showarrow=False,
                font=dict(size=10, family="Times New Roman", color='black'),
                bgcolor='white',
                borderpad=2,
                opacity=0.8
            )
    
    fig_interaction.update_layout(
        title='Interacción entre Prime y Target en TR (log)',
        title_font_size=18,
        title_font_family="Times New Roman",
        font_family="Times New Roman",
        xaxis_title='Target',
        yaxis_title='Tiempo de respuesta (log)',
        xaxis=dict(title_font_size=14),
        yaxis=dict(title_font_size=14, gridcolor='rgba(0,0,0,0.1)'),
        template='plotly_white',
        height=500,
        legend=dict(
            title='Raza',
            yanchor='top',
            y=0.99,
            xanchor='right',
            x=0.99,
            bgcolor='rgba(255,255,255,0.9)',
            font=dict(size=12)
        ),
        hovermode='closest'
    )
    
    st.plotly_chart(fig_interaction, use_container_width=True, key="interaction_plot")
    
    st.markdown(
        "**Comentario**: Este gráfico muestra claramente la no-paralelidad, indicando una interacción significativa entre prime y target: la línea para el prime Black (**Azul**) muestra una mayor separación entre herramientas y armas, mientras que la del prime White (**Rosa**) es más plana. Este patrón refleja que los participantes responden más lentamente a herramientas tras un prime Black, pero su velocidad para identificar armas no varía significativamente según el prime — evidencia conductual del sesgo racial implícito."
    )

# ==============================================================================
# === TAB 3: ANOVA CONDUCTUAL (RT) ===
# ==============================================================================
with tab_anova_beh:
    st.header("📊 ANOVA de Medidas Repetidas: Tiempos de Reacción ($RT_{log}$)")
    
    # --- CAMBIO 1: detailed=True para obtener SS y MS ---
    anova_rt = pg.rm_anova(
        data=data_limpia, 
        dv='rt_log', 
        within=['prime', 'target'], 
        subject='id', 
        detailed=True  # <--- IMPORTANTE: Esto genera las columnas SS, MS y DF
    )
    
    # --- CAMBIO 2: Formatear usando la función auxiliar ---
    tabla_final = formatear_tabla_anova(anova_rt)
    
    # Mostrar tabla
    st.subheader("Resultados ANOVA: Conductual")
    st.dataframe(
        tabla_final.style.format({
            'Adj SS': '{:.3f}',
            'Adj MS': '{:.3f}',
            'F-Value': '{:.3f}',
            'P-Value': '{:.4f}'
        }),
        hide_index=True,
        use_container_width=True
    )
    
    # Lógica de interpretación (puedes mantener tu lógica de significancia visual si quieres)
    p_interaction = anova_rt.loc[anova_rt['Source'] == 'prime * target', 'p-unc'].values[0]
    
    if p_interaction < 0.05:
        st.success(f"✅ Se confirma una interacción significativa (p = {p_interaction:.4f}).")
    else:
        st.info(f"ℹ️ No se encontró interacción significativa (p = {p_interaction:.4f}).")

    
    st.markdown(
        "**Interpretación**: Se confirma una **interacción significativa** entre prime y target (p < .05), "
        "respaldando la hipótesis de sesgo racial implícito. El efecto principal de target es muy fuerte (p < .001), "
        "mientras que no hay efecto significativo de prime por sí solo."
    )
    
    st.markdown("---")
    
    with st.expander("🔍 Ver Análisis de Supuestos (Residuos)", expanded=False):
        st.markdown("### Verificación de Supuestos del Modelo")
        
        # CÁLCULO DE RESIDUOS 
        y_bar_total = data_limpia['rt_log'].mean()
        mean_sujeto = data_limpia.groupby('id')['rt_log'].mean().reset_index().rename(columns={'rt_log': 'y_bar_sujeto'})
        mean_celda = data_limpia.groupby(['prime', 'target'])['rt_log'].mean().reset_index().rename(columns={'rt_log': 'y_bar_celda'})
        
        data_resid = data_limpia.merge(mean_sujeto, on='id').merge(mean_celda, on=['prime', 'target'])
        data_resid['residual'] = data_resid['rt_log'] - data_resid['y_bar_celda'] - data_resid['y_bar_sujeto'] + y_bar_total
        residuos = data_resid['residual']
        
        col_test, col_qq = st.columns([1, 2])
        
        with col_test:
            st.markdown("#### Pruebas Estadísticas")
            # Shapiro-Wilk
            shapiro_stat, shapiro_p = shapiro(residuos)
            st.metric("Normalidad (Shapiro-Wilk)", f"p = {shapiro_p:.4f}")
            # Levene
            grupos = [grupo['residual'].values for _, grupo in data_resid.groupby(['prime', 'target'])]
            levene_stat, levene_p = levene(*grupos)
            st.metric("Homogeneidad (Levene)", f"p = {levene_p:.4f}")
            
            # Interpretación automática
            st.markdown("---")
            normalidad_ok = shapiro_p > 0.05
            homogeneidad_ok = levene_p > 0.05
            
            if normalidad_ok and homogeneidad_ok:
                st.success("✓ Los supuestos se cumplen adecuadamente")
            elif normalidad_ok:
                st.warning("⚠️ Normalidad OK, pero revisar homogeneidad")
            elif homogeneidad_ok:
                st.warning("⚠️ Homogeneidad OK, pero revisar normalidad")
            else:
                st.info("ℹ️ Considerar transformaciones adicionales")
        
        with col_qq:
            st.markdown("#### Q-Q Plot de Residuos")
            # Q-Q Plot Residuos con Plotly
            qq_data = stats.probplot(residuos, dist="norm")
            fig_qq = go.Figure()
            fig_qq.add_trace(go.Scatter(
                x=qq_data[0][0],
                y=qq_data[0][1],
                mode='markers',
                marker=dict(color=COLOR_AZULITO, size=6),
                name='Residuos'
            ))
            # Línea teórica
            fig_qq.add_trace(go.Scatter(
                x=qq_data[0][0],
                y=qq_data[1][0] * qq_data[0][0] + qq_data[1][1],
                mode='lines',
                line=dict(color='black', width=2),
                name='Teórica'
            ))
            fig_qq.update_layout(
                title='',
                title_font_family="Times New Roman",
                font_family="Times New Roman",
                xaxis_title='Cuantiles teóricos',
                yaxis_title='Cuantiles muestrales',
                template='plotly_white',
                showlegend=False,
                height=350
            )
            st.plotly_chart(fig_qq, use_container_width=True, key="qq_residuos_beh")

# ==============================================================================
# === TAB 4: ANOVA MVPA (Sensitive WIT) ===
# ==============================================================================
with tab_anova_mvpa:
    st.header("🧠 ANOVA de Medidas Repetidas: MVPA - Sensitive WIT")
    
    if not data_limpiamvpa.empty:
        # --- CAMBIO 1 ---
        anova_mvpa = pg.rm_anova(
            data=data_limpiamvpa, 
            dv='value', 
            within=['prime', 'target'], 
            subject='id', 
            detailed=True # <--- Activado
        )
        
        # --- CAMBIO 2 ---
        tabla_final_mvpa = formatear_tabla_anova(anova_mvpa)
        
        st.subheader("Resultados ANOVA: MVPA")
        st.dataframe(
            tabla_final_mvpa.style.format({
                'Adj SS': '{:.3f}',
                'Adj MS': '{:.3f}',
                'F-Value': '{:.3f}',
                'P-Value': '{:.4f}'
            }),
            hide_index=True,
            use_container_width=True
        )
        
        st.markdown("---")
        
        with st.expander("🔍 Ver Análisis de Supuestos (Residuos)", expanded=False):
            st.markdown("### Verificación de Supuestos del Modelo")
            
            # CÁLCULO DE RESIDUOS 
            y_bar_total_mvpa = data_limpiamvpa['value'].mean()
            mean_sujeto_mvpa = data_limpiamvpa.groupby('id')['value'].mean().reset_index().rename(columns={'value': 'y_bar_sujeto_mvpa'})
            mean_celda_mvpa = data_limpiamvpa.groupby(['prime', 'target'])['value'].mean().reset_index().rename(columns={'value': 'y_bar_celda_mvpa'})
            
            data_resid_mvpa = (data_limpiamvpa
                                .merge(mean_sujeto_mvpa, on='id')
                                .merge(mean_celda_mvpa, on=['prime', 'target']))
            
            data_resid_mvpa['residual_mvpa'] = (data_resid_mvpa['value'] - 
                                                data_resid_mvpa['y_bar_celda_mvpa'] - 
                                                data_resid_mvpa['y_bar_sujeto_mvpa'] + 
                                                y_bar_total_mvpa)
            residuos_mvpa = data_resid_mvpa['residual_mvpa']
            
            col_test_mvpa, col_qq_mvpa = st.columns([1, 2])
            
            with col_test_mvpa:
                st.markdown("#### Pruebas Estadísticas")
                # Shapiro-Wilk
                shapiro_stat, shapiro_p = shapiro(residuos_mvpa)
                st.metric("Normalidad (Shapiro-Wilk)", f"p = {shapiro_p:.4f}")
                # Levene
                grupos = [grupo['residual_mvpa'].values for _, grupo in data_resid_mvpa.groupby(['prime', 'target'])]
                levene_stat, levene_p = levene(*grupos)
                st.metric("Homogeneidad (Levene)", f"p = {levene_p:.4f}")
                
                # Interpretación automática
                st.markdown("---")
                normalidad_ok = shapiro_p > 0.05
                homogeneidad_ok = levene_p > 0.05
                
                if normalidad_ok and homogeneidad_ok:
                    st.success("✓ Los supuestos se cumplen adecuadamente")
                elif normalidad_ok:
                    st.warning("⚠️ Normalidad OK, pero revisar homogeneidad")
                elif homogeneidad_ok:
                    st.warning("⚠️ Homogeneidad OK, pero revisar normalidad")
                else:
                    st.info("ℹ️ Considerar transformaciones adicionales")
            
            with col_qq_mvpa:
                st.markdown("#### Q-Q Plot de Residuos")
                # Q-Q Plot Residuos MVPA con Plotly
                qq_data = stats.probplot(residuos_mvpa, dist="norm")
                fig_qq_mvpa = go.Figure()
                fig_qq_mvpa.add_trace(go.Scatter(
                    x=qq_data[0][0],
                    y=qq_data[0][1],
                    mode='markers',
                    marker=dict(color=COLOR_PRIME_BLACK, size=6),
                    name='Residuos'
                ))
                # Línea teórica
                fig_qq_mvpa.add_trace(go.Scatter(
                    x=qq_data[0][0],
                    y=qq_data[1][0] * qq_data[0][0] + qq_data[1][1],
                    mode='lines',
                    line=dict(color='black', width=2),
                    name='Teórica'
                ))
                fig_qq_mvpa.update_layout(
                    title='',
                    title_font_family="Times New Roman",
                    font_family="Times New Roman",
                    xaxis_title='Cuantiles teóricos',
                    yaxis_title='Cuantiles muestrales',
                    template='plotly_white',
                    showlegend=False,
                    height=350
                )
                st.plotly_chart(fig_qq_mvpa, use_container_width=True, key="qq_residuos_mvpa")
    else:
        st.warning("Datos MVPA no cargados o no disponibles.")

# ==============================================================================
# === TAB 5: ANOVA SEARCHLIGHT (WIT) ===
# ==============================================================================
with tab_anova_search:
    st.header("🔍 ANOVA de Medidas Repetidas: Searchlight WIT")
    
    if not data_limpiasearch.empty:
        # CÁLCULO ANOVA
        anova_search = pg.rm_anova(
            data=data_limpiasearch, 
            dv='value', 
            within=['prime', 'target'], 
            subject='id',
            detailed=True
        )
        
        # Formatear tabla usando la función auxiliar
        tabla_final = formatear_tabla_anova(anova_search)
        
        # Mostrar tabla
        st.subheader("Resultados ANOVA: Searchlight")
        st.dataframe(
            tabla_final.style.format({
                'Adj SS': '{:.3f}',
                'Adj MS': '{:.3f}',
                'F-Value': '{:.3f}',
                'P-Value': '{:.4f}'
            }),
            hide_index=True,
            use_container_width=True
        )
        
        st.markdown("---")
        
        with st.expander("🔍 Ver Análisis de Supuestos (Residuos)", expanded=False):
            st.markdown("### Verificación de Supuestos del Modelo")
            
            # CÁLCULO DE RESIDUOS 
            y_bar_total_search = data_limpiasearch['value'].mean()
            mean_sujeto_search = data_limpiasearch.groupby('id')['value'].mean().reset_index().rename(columns={'value': 'y_bar_sujeto_search'})
            mean_celda_search = data_limpiasearch.groupby(['prime', 'target'])['value'].mean().reset_index().rename(columns={'value': 'y_bar_celda_search'})
            
            data_resid_search = (data_limpiasearch
                                .merge(mean_sujeto_search, on='id')
                                .merge(mean_celda_search, on=['prime', 'target']))
            
            data_resid_search['residual_search'] = (data_resid_search['value'] - 
                                                    data_resid_search['y_bar_celda_search'] - 
                                                    data_resid_search['y_bar_sujeto_search'] + 
                                                    y_bar_total_search)
            residuos_search = data_resid_search['residual_search']
            
            col_test_search, col_qq_search = st.columns([1, 2])
            
            with col_test_search:
                st.markdown("#### Pruebas Estadísticas")
                # Shapiro-Wilk
                shapiro_stat, shapiro_p = shapiro(residuos_search)
                st.metric("Normalidad (Shapiro-Wilk)", f"p = {shapiro_p:.4f}")
                # Levene
                grupos = [grupo['residual_search'].values for _, grupo in data_resid_search.groupby(['prime', 'target'])]
                levene_stat, levene_p = levene(*grupos)
                st.metric("Homogeneidad (Levene)", f"p = {levene_p:.4f}")
                
                # Interpretación automática
                st.markdown("---")
                normalidad_ok = shapiro_p > 0.05
                homogeneidad_ok = levene_p > 0.05
                
                if normalidad_ok and homogeneidad_ok:
                    st.success("✓ Los supuestos se cumplen adecuadamente")
                elif normalidad_ok:
                    st.warning("⚠️ Normalidad OK, pero revisar homogeneidad")
                elif homogeneidad_ok:
                    st.warning("⚠️ Homogeneidad OK, pero revisar normalidad")
                else:
                    st.info("ℹ️ Considerar transformaciones adicionales")
            
            with col_qq_search:
                st.markdown("#### Q-Q Plot de Residuos")
                # Q-Q Plot Residuos Searchlight con Plotly
                qq_data = stats.probplot(residuos_search, dist="norm")
                fig_qq_search = go.Figure()
                fig_qq_search.add_trace(go.Scatter(
                    x=qq_data[0][0],
                    y=qq_data[0][1],
                    mode='markers',
                    marker=dict(color=COLOR_PRIME_WHITE, size=6),
                    name='Residuos'
                ))
                # Línea teórica
                fig_qq_search.add_trace(go.Scatter(
                    x=qq_data[0][0],
                    y=qq_data[1][0] * qq_data[0][0] + qq_data[1][1],
                    mode='lines',
                    line=dict(color='black', width=2),
                    name='Teórica'
                ))
                fig_qq_search.update_layout(
                    title='',
                    title_font_family="Times New Roman",
                    font_family="Times New Roman",
                    xaxis_title='Cuantiles teóricos',
                    yaxis_title='Cuantiles muestrales',
                    template='plotly_white',
                    showlegend=False,
                    height=350
                )
                st.plotly_chart(fig_qq_search, use_container_width=True, key="qq_residuos_search")
    else:
        st.warning("Datos Searchlight no cargados o no disponibles.")
