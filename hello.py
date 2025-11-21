import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import pingouin as pg
from scipy.stats import shapiro, levene
import warnings

# Ignorar warnings (por ejemplo, de pingouin o matplotlib)
warnings.filterwarnings("ignore")

# --- INYECCIÓN DE CSS PARA CAMBIAR LA FUENTE DE TODO, EL COLOR DE LA BARRA LATERAL Y ESTILIZAR KPIS ---
SIDEBAR_BACKGROUND_COLOR = "#f0f2f6" 
KPI_CARD_BACKGROUND_COLOR = "#e0f2f7" # Un azul muy clarito para las tarjetas de KPI
KPI_BORDER_COLOR = "#b2ebf2" # Un azul un poco más oscuro para el borde

st.markdown(f"""
<style>
/* Aplicar Times New Roman o fuente con serifa a todo el cuerpo del texto */
html, body, [class*="st-"] {{
    font-family: "Times New Roman", Times, serif;
}}

/* Asegurar que los títulos de Streamlit (H1, H2, H3, H4) también usen Times New Roman. */
h1, h2, h3, h4, 
.st-emotion-cache-10trblm, /* Selector común para st.header y st.subheader */
.st-emotion-cache-1avcm0n, /* Selector común para st.title */
.st-emotion-cache-q824g5, /* Selector específico para sidebar h1 */
.st-emotion-cache-1inwz65, /* Otro selector de encabezado */
.st-emotion-cache-1nd8t9t /* Otro selector de encabezado */
{{
    font-family: "Times New Roman", Times, serif !important;
}}

/* CAMBIO DE COLOR DE FONDO DE LA BARRA LATERAL (Sidebar) */
.st-emotion-cache-12quk7v {{ 
    background-color: {SIDEBAR_BACKGROUND_COLOR};
}}

/* ESTILO PARA LAS TARJETAS DE KPI */
/* Este selector apunta al contenedor principal de los st.metric en las columnas */
.st-emotion-cache-13k62yr {{ /* Este selector puede variar ligeramente en diferentes versiones de Streamlit */
    background-color: {KPI_CARD_BACKGROUND_COLOR};
    border-radius: 10px; /* Bordes redondeados */
    border: 1px solid {KPI_BORDER_COLOR}; /* Borde sutil */
    padding: 15px; /* Espaciado interno */
    box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1); /* Sombra suave */
    margin-bottom: 10px; /* Espacio entre tarjetas si están apiladas */
}}

/* Ajustar el tamaño de fuente si es necesario, ya que Times New Roman se ve más pequeño */
body {{
    font-size: 16px; 
}}
</style>
""", unsafe_allow_html=True)
# -------------------------------------------------------------------------------------

# --- 1. CONFIGURACIÓN DE PÁGINA Y CARGA DE DATOS ---
st.set_page_config(
    page_title="Dashboard Sesgos Raciales",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de Colores Nueva (Azulito y Rosa Clarito)
COLOR_AZULITO = "#A5D6A7" # Azul verdoso suave para Histogramas/Q-Q Plots
COLOR_ROSITA = "#F8BBD0"   # Rosa pálido para Transformados
COLOR_PRIME_BLACK = '#3949AB' # Azul profundo para Black prime/Gun (Clase dominante)
COLOR_PRIME_WHITE = '#E91E63' # Rosa brillante para White prime/Tool (Clase contrastante)

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
        # Gráficos de Datos Brutos (COLORES ACTUALIZADOS)
        plt.style.use('seaborn-v0_8-whitegrid')
        fig_raw, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        sns.histplot(data=data_limpia, x='rt_raw', bins=30, color=COLOR_AZULITO, edgecolor='black', ax=ax1)
        ax1.set_title('Histograma: Datos Brutos', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Tiempo de reacción (ms)', fontsize=12)
        
        stats.probplot(data_limpia['rt_raw'], dist="norm", plot=ax2)
        ax2.get_lines()[0].set_markerfacecolor(COLOR_AZULITO)
        ax2.get_lines()[0].set_markeredgecolor(COLOR_AZULITO)  # <-- CORREGIDO
        ax2.get_lines()[1].set_color('black')
        ax2.set_title('Q-Q Plot: Datos Brutos', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        st.pyplot(fig_raw)
        st.markdown("**Comentario**: Los tiempos de reacción brutos muestran una fuerte asimetría positiva, lo que viola el supuesto de normalidad. Se justifica la transformación logarítmica.")

    with col_log_dist:
        st.subheader("Datos Transformados ($RT_{log}$)")
        # Gráficos de Datos Transformados (COLORES ACTUALIZADOS)
        plt.style.use('seaborn-v0_8-whitegrid')
        fig_log, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 6))
        
        sns.histplot(data=data_limpia, x='rt_log', bins=30, color=COLOR_ROSITA, edgecolor='black', ax=ax3)
        ax3.set_title('Histograma: Datos Transformados', fontsize=14, fontweight='bold')
        ax3.set_xlabel('log(Tiempo de reacción)', fontsize=12)

        stats.probplot(data_limpia['rt_log'], dist="norm", plot=ax4)
        ax4.get_lines()[0].set_markerfacecolor(COLOR_ROSITA)
        ax4.get_lines()[0].set_markeredgecolor(COLOR_ROSITA) # <-- CORREGIDO
        ax4.get_lines()[1].set_color('black')
        ax4.set_title('Q-Q Plot: Datos Transformados', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        st.pyplot(fig_log)
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
        # Generación del Boxplot (COLORES ACTUALIZADOS)
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(14, 8))
        
        sns.boxplot(data=data_limpia, x='prime', y='rt_log', hue='target', 
                    palette={"gun": COLOR_PRIME_BLACK, "tool": COLOR_PRIME_WHITE},
                    dodge=True, width=0.8, ax=ax, showfliers=False)
        
        sns.stripplot(data=data_limpia, x='prime', y='rt_log', hue='target',
                      palette={"gun": COLOR_PRIME_BLACK, "tool": COLOR_PRIME_WHITE},
                      dodge=True, ax=ax, size=3, alpha=0.5, jitter=True, legend=False)
        
        ax.set_title('Diagrama de cajas de tiempo de respuesta (log)\\n', fontsize=16, fontweight='bold')
        ax.set_xlabel('Raza del prime', fontsize=14, labelpad=10)
        ax.set_ylabel('Tiempo de respuesta (log)', fontsize=14, labelpad=10)
        
        handles, labels = ax.get_legend_handles_labels()
        unique_labels = ['Arma', 'Herramienta']
        ax.legend(handles[:2], unique_labels, title='Target', loc='upper right', framealpha=0.9)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        st.pyplot(fig)

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
    
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Crear gráfico de interacción con seaborn (COLORES ACTUALIZADOS)
    sns.pointplot(data=data_limpia, x='target', y='rt_log', hue='prime',
                  palette={"Black": COLOR_PRIME_BLACK, "White": COLOR_PRIME_WHITE},
                  dodge=0.2, join=True, errwidth=2, capsize=0.1,
                  markers=['o', 's'], markersize=8, linestyles=['-', '-'],
                  ax=ax)
    
    ax.set_title('Interacción entre Prime y Target en TR (log)\\n', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Target', fontsize=14, labelpad=15)
    ax.set_ylabel('Tiempo de respuesta (log)', fontsize=14, labelpad=15)
    
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, title='Raza', loc='upper right', framealpha=0.9, fontsize=12)
    
    # Añadir anotaciones con valores medios
    for target_idx, target_val in enumerate(data_limpia['target'].unique()):
        for prime_idx, prime_val in enumerate(data_limpia['prime'].unique()):
            subset = data_limpia[(data_limpia['target'] == target_val) & (data_limpia['prime'] == prime_val)]
            if len(subset) > 0:
                mean_val = subset['rt_log'].mean()
                x_pos = target_idx + (prime_idx - 0.5) * 0.2
                ax.text(x_pos, mean_val + 0.02, f'{mean_val:.2f}', 
                        ha='center', va='bottom', fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown(
        "**Comentario**: Este gráfico muestra claramente la no-paralelidad, indicando una interacción significativa entre prime y target: la línea para el prime Black (**Azul**) muestra una mayor separación entre herramientas y armas, mientras que la del prime White (**Rosa**) es más plana. Este patrón refleja que los participantes responden más lentamente a herramientas tras un prime Black, pero su velocidad para identificar armas no varía significativamente según el prime — evidencia conductual del sesgo racial implícito."
    )

# ==============================================================================
# === TAB 3: ANOVA CONDUCTUAL (RT) ===
# ==============================================================================
with tab_anova_beh:
    st.header("📊 ANOVA de Medidas Repetidas: Tiempos de Reacción ($RT_{log}$)")
    
    # CÁLCULO ANOVA 
    anova_rt = pg.rm_anova(
        data=data_limpia, 
        dv='rt_log', 
        within=['prime', 'target'], 
        subject='id', 
        detailed=True
    )
    
    st.subheader("Resultados ANOVA: Conductual")
    st.dataframe(anova_rt.round(4))
    
    st.subheader("📈 Resumen de Significancia")
    def get_significance(p_val):
        if p_val < 0.001: return "***"
        elif p_val < 0.01: return "**"
        elif p_val < 0.05: return "*"
        else: return "ns"
        
    for _, row in anova_rt.iterrows():
        efecto = row['Source']
        p_val = row['p-unc']
        st.write(f"- **{efecto}**: p = {p_val:.4f} ({get_significance(p_val)})")
        
    st.markdown(
        "**Interpretación**: Se confirma una interacción **significativa** entre prime y target (p = .016), lo que respalda la hipótesis de sesgo racial implícito. No hay efecto principal de prime (p = .133), pero sí un fuerte efecto de target (p < .001)."
    )
    
    st.markdown("---")
    
    st.header("🔍 Análisis de Supuestos (Residuos Conductuales)")
    
    # 1. CÁLCULO DE RESIDUOS 
    y_bar_total = data_limpia['rt_log'].mean()
    mean_sujeto = data_limpia.groupby('id')['rt_log'].mean().reset_index().rename(columns={'rt_log': 'y_bar_sujeto'})
    mean_celda = data_limpia.groupby(['prime', 'target'])['rt_log'].mean().reset_index().rename(columns={'rt_log': 'y_bar_celda'})
    
    data_resid = data_limpia.merge(mean_sujeto, on='id').merge(mean_celda, on=['prime', 'target'])
    data_resid['residual'] = data_resid['rt_log'] - data_resid['y_bar_celda'] - data_resid['y_bar_sujeto'] + y_bar_total
    residuos = data_resid['residual']
    
    col_test, col_qq = st.columns([1, 2])
    
    with col_test:
        st.subheader("Pruebas Estadísticas")
        # Shapiro-Wilk
        shapiro_stat, shapiro_p = shapiro(residuos)
        st.metric("Normalidad (Shapiro-Wilk)", f"p = {shapiro_p:.4f}")
        # Levene
        grupos = [grupo['residual'].values for _, grupo in data_resid.groupby(['prime', 'target'])]
        levene_stat, levene_p = levene(*grupos)
        st.metric("Homogeneidad (Levene)", f"p = {levene_p:.4f}")
        
    with col_qq:
        st.subheader("Q-Q Plot de Residuos")
        # Q-Q Plot Residuos (COLOR ACTUALIZADO)
        fig, ax = plt.subplots(figsize=(10, 6))
        stats.probplot(residuos, dist="norm", plot=ax)
        ax.get_lines()[0].set_markerfacecolor(COLOR_AZULITO)
        ax.get_lines()[0].set_markeredgecolor(COLOR_AZULITO) # <-- CORREGIDO
        ax.get_lines()[1].set_color('black')
        ax.set_title('Q-Q Plot de los residuos (ANOVA - tiempos de reacción)')
        plt.tight_layout()
        st.pyplot(fig)
        
    st.markdown(
        "**Comentario sobre supuestos**: La normalidad y homocedasticidad de los residuos son razonables para proseguir con el ANOVA. El diseño de medidas repetidas asume independencia de ensayos, lo cual se considera válido por la aleatorización del orden experimental."
    )

# ==============================================================================
# === TAB 4: ANOVA MVPA (Sensitive WIT) ===
# ==============================================================================
with tab_anova_mvpa:
    st.header("🧠 ANOVA de Medidas Repetidas: MVPA - Sensitive WIT")
    
    if not data_limpiamvpa.empty:
        # CÁLCULO ANOVA
        anova_mvpa = pg.rm_anova(
            data=data_limpiamvpa, 
            dv='value', 
            within=['prime', 'target'], 
            subject='id', 
            detailed=True
        )
        
        st.subheader("Resultados ANOVA: MVPA")
        st.dataframe(anova_mvpa.round(4))
        
        st.subheader("📈 Resumen de Significancia")
        for _, row in anova_mvpa.iterrows():
            efecto = row['Source']
            p_val = row['p-unc']
            st.write(f"- **{efecto}**: p = {p_val:.4f} ({get_significance(p_val)})")
            
        st.markdown("---")
        
        st.header("🔍 Análisis de Supuestos (Residuos MVPA)")
        
        # 1. CÁLCULO DE RESIDUOS 
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
            st.subheader("Pruebas Estadísticas")
            # Shapiro-Wilk
            shapiro_stat, shapiro_p = shapiro(residuos_mvpa)
            st.metric("Normalidad (Shapiro-Wilk)", f"p = {shapiro_p:.4f}")
            # Levene
            grupos = [grupo['residual_mvpa'].values for _, grupo in data_resid_mvpa.groupby(['prime', 'target'])]
            levene_stat, levene_p = levene(*grupos)
            st.metric("Homogeneidad (Levene)", f"p = {levene_p:.4f}")
            
        with col_qq_mvpa:
            st.subheader("Q-Q Plot de Residuos MVPA")
            # Q-Q Plot Residuos MVPA (COLOR ACTUALIZADO)
            fig, ax = plt.subplots(figsize=(10, 6))
            stats.probplot(residuos_mvpa, dist="norm", plot=ax)
            ax.get_lines()[0].set_markerfacecolor(COLOR_PRIME_BLACK)
            ax.get_lines()[0].set_markeredgecolor(COLOR_PRIME_BLACK) # <-- CORREGIDO
            ax.get_lines()[1].set_color('black')
            ax.set_title('Q-Q Plot de los residuos (ANOVA - MVPA)')
            plt.tight_layout()
            st.pyplot(fig)
            
        st.markdown(
            "**Comentario**: Los supuestos del ANOVA para los datos MVPA se evalúan mediante normalidad de residuos (Shapiro-Wilk) y homocedasticidad entre celdas (Levene). Un p > 0.05 en ambas pruebas apoya la validez del modelo."
        )
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
        
        st.subheader("Resultados ANOVA: Searchlight")
        st.dataframe(anova_search.round(4))
        
        st.subheader("📈 Resumen de Significancia")
        for _, row in anova_search.iterrows():
            efecto = row['Source']
            p_val = row['p-unc']
            st.write(f"- **{efecto}**: p = {p_val:.4f} ({get_significance(p_val)})")
            
        st.markdown("---")
        
        st.header("🔍 Análisis de Supuestos (Residuos Searchlight)")
        
        # 1. CÁLCULO DE RESIDUOS 
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
            st.subheader("Pruebas Estadísticas")
            # Shapiro-Wilk
            shapiro_stat, shapiro_p = shapiro(residuos_search)
            st.metric("Normalidad (Shapiro-Wilk)", f"p = {shapiro_p:.4f}")
            # Levene
            grupos = [grupo['residual_search'].values for _, grupo in data_resid_search.groupby(['prime', 'target'])]
            levene_stat, levene_p = levene(*grupos)
            st.metric("Homogeneidad (Levene)", f"p = {levene_p:.4f}")
            
        with col_qq_search:
            st.subheader("Q-Q Plot de Residuos Searchlight")
            # Q-Q Plot Residuos Searchlight (COLOR ACTUALIZADO)

