import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de Escena
st.set_page_config(page_title="Executive Education Control", layout="wide")

# Estilo "Electric Blue" - Adiós al amarillo y marrón
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #e0e0e0; }
    div[data-testid="stMetric"] {
        background-color: #161b22; 
        border-left: 5px solid #00d4ff; /* Azul Cian Eléctrico */
        border-radius: 10px; 
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    div[data-testid="stMetricValue"] { color: #00d4ff; font-weight: bold; }
    /* Espaciado entre componentes */
    .stPlotlyChart { margin-top: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/datos_educacion_limpios.csv")
    return df

df = load_data()

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header(" Auditoría")
    anos_disp = sorted(df['ano'].unique(), reverse=True)
    anos_sel = st.multiselect("Línea de Tiempo", anos_disp, default=[anos_disp[0]])
    deptos_disp = sorted(df['departamento'].unique())
    deptos_sel = st.multiselect("Departamentos", deptos_disp, default=deptos_disp[:3])

# Filtrado
df_f = df[(df['ano'].isin(anos_sel)) & (df['departamento'].isin(deptos_sel))].sort_values('ano')

st.title(" Monitor de Calidad Educativa")
st.markdown("---")

if not df_f.empty:
    # --- BLOQUE 1: 5 KPIs ESTRATÉGICOS ---
    c1, c2, c3, c4, c5 = st.columns(5)
    
    pob_total = df_f.groupby('ano')['poblacion_5_16'].sum().mean()
    cob_neta_avg = df_f['cobertura_neta'].mean()
    deser_avg = df_f['desercion'].mean()
    repit_avg = df_f['repitencia'].mean()
    # NUEVO KPI: Retención (Desempeño Real)
    retencion_avg = 1 - deser_avg

    c1.metric("Población Total", f"{int(pob_total):,}".replace(",", "."))
    c2.metric("Cobertura Neta", f"{cob_neta_avg*100:.1f}%")
    c3.metric("Tasa Deserción", f"{deser_avg*100:.1f}%")
    c4.metric("Desempeño (Retención)", f"{retencion_avg*100:.1f}%")
    c5.metric("Índice Repitencia", f"{repit_avg*100:.1f}%")

    st.markdown("---")

    # --- BLOQUE 2: TENDENCIA Y RANKING (Paleta Azul/Cian/Gris) ---
    col_a, col_b = st.columns([1.2, 0.8])

    with col_a:
        st.subheader("📈 Evolución de la Deserción")
        # Colores: Azules y Verdes Fríos
        fig_line = px.line(df_f, x="ano", y="desercion", color="departamento",
                          markers=True, template="plotly_dark",
                          color_discrete_sequence=["#00d4ff", "#7efbff", "#2b65ec", "#a5f2f3"])
        fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)

    with col_b:
        st.subheader(" Ranking de Cobertura")
        ultimo_ano = max(anos_sel)
        df_rank = df_f[df_f['ano'] == ultimo_ano].sort_values('cobertura_neta')
        # Escala: Gris Oscuro a Cian Eléctrico
        fig_rank = px.bar(df_rank, x="cobertura_neta", y="departamento", orientation='h',
                          template="plotly_dark", color="cobertura_neta",
                          color_continuous_scale=['#1f2937', '#00d4ff'])
        fig_rank.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_rank, use_container_width=True)

    st.markdown("---")

    # --- BLOQUE 3: BALANCE Y BRECHA ---
    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader(" Balance Académico")
        pie_data = pd.DataFrame({
            "Estado": ["Aprobados", "Reprobados", "Desertores"],
            "Valor": [df_f['aprobacion'].mean(), df_f['reprobacion'].mean(), df_f['desercion'].mean()]
        })
        # Colores: Esmeralda, Carmín suave y Azul
        fig_pie = px.pie(pie_data, values="Valor", names="Estado", hole=0.6,
                         color_discrete_sequence=["#10b981", "#ef4444", "#3b82f6"],
                         template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_d:
        st.subheader(" Cobertura: Neta vs Bruta")
        # Colores: Cian y Pizarra
        fig_bar = px.bar(df_f, x="departamento", y=["cobertura_neta", "cobertura_bruta"],
                         barmode="group", template="plotly_dark",
                         animation_frame="ano",
                         color_discrete_map={"cobertura_neta": "#00d4ff", "cobertura_bruta": "#4b5563"})
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- TABLA ---
    with st.expander("🔎 Ver Matriz de Auditoría Detallada"):
        st.dataframe(df_f, use_container_width=True)
else:
    st.info("Seleccione parámetros para generar el reporte.")