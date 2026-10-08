import pandas as pd
import streamlit as st

from src.correlacao import calcular_correlacao, descrever_correlacao
from src.fuzzy_ventilador import (
    REGRAS,
    calcular_ventilador_fuzzy,
    classificar_ventilador,
    curvas_pertinencia,
)
from src.load_data import FONTE_SIMULADOR, FONTES, JANELAS, obter_leituras
from src.visualizacao import (
    grafico_disp,
    grafico_linha,
    grafico_pertinencia,
    histograma,
    mapa_calor,
)

# =====================================================================
# CONFIGURAÇÃO DO DASHBOARD
# =====================================================================
st.set_page_config(
    page_title="Dashboard — ESP32 Monitor",
    layout="wide",
    page_icon="📡",
)

# Grandezas medidas: coluna -> (título, unidade)
GRANDEZAS = {
    "temperatura": ("Temperatura", "°C"),
    "umidade": ("Umidade", "%"),
    "luminosidade": ("Luminosidade", "lux"),
}

ROTULOS_FUZZY = {
    "fria": "Fria", "agradavel": "Agradável", "quente": "Quente",
    "seca": "Seca", "ideal": "Ideal", "umida": "Úmida",
    "baixa": "Baixa", "media": "Média", "alta": "Alta",
}

# =====================================================================
# CSS PERSONALIZADO
# =====================================================================
st.markdown("""
    <style>
    .card {
        padding: 16px 18px;
        border-radius: 12px;
        background-color: rgba(128, 128, 128, 0.07);
        border: 1px solid rgba(128, 128, 128, 0.25);
        height: 100%;
    }
    .card-titulo { font-size: 0.85rem; opacity: 0.7; margin-bottom: 4px; }
    .card-valor { font-size: 2rem; font-weight: 600; line-height: 1.15; }
    .card-valor span { font-size: 1rem; font-weight: 400; opacity: 0.7; }
    .card-detalhe { font-size: 0.8rem; opacity: 0.65; margin-top: 4px; }
    .risk-low, .risk-medium, .risk-high {
        padding: 14px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 6px 0 14px 0;
    }
    .risk-low    { background-color: rgba(12, 163, 12, 0.16);  border: 1px solid rgba(12, 163, 12, 0.45); }
    .risk-medium { background-color: rgba(250, 178, 25, 0.18); border: 1px solid rgba(250, 178, 25, 0.55); }
    .risk-high   { background-color: rgba(208, 59, 59, 0.16);  border: 1px solid rgba(208, 59, 59, 0.5); }
    .mock-aviso {
        padding: 8px 14px;
        border-radius: 8px;
        border: 1px dashed rgba(128, 128, 128, 0.6);
        font-size: 0.85rem;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)


def card(titulo, valor, unidade="", detalhe=""):
    return (
        f"<div class='card'><div class='card-titulo'>{titulo}</div>"
        f"<div class='card-valor'>{valor}<span> {unidade}</span></div>"
        f"<div class='card-detalhe'>{detalhe}</div></div>"
    )


def faixa(nivel, texto):
    st.markdown(f"<div class='risk-{nivel}'>{texto}</div>", unsafe_allow_html=True)


def formatar_uptime(segundos):
    dias, resto = divmod(int(segundos), 86400)
    horas, resto = divmod(resto, 3600)
    minutos = resto // 60
    return f"{dias}d {horas:02d}h {minutos:02d}min"


def qualidade_wifi(rssi):
    if rssi >= -60:
        return "Excelente"
    if rssi >= -70:
        return "Bom"
    if rssi >= -80:
        return "Fraco"
    return "Muito fraco"


def avaliar_ambiente(leitura, temp_max, umid_max):
    """Estado do ambiente a partir da última leitura: (nível, texto)."""
    if leitura["temperatura"] > temp_max:
        return "high", f"🔴 Alerta — temperatura acima do limite de {temp_max:g} °C"
    if leitura["umidade"] > umid_max:
        return "medium", f"🟡 Atenção — umidade acima do limite de {umid_max:g} %"
    if leitura["temperatura"] > temp_max - 1.5:
        return "medium", f"🟡 Atenção — temperatura próxima do limite de {temp_max:g} °C"
    return "low", "🟢 Ambiente dentro dos limites"


# =====================================================================
# BARRA LATERAL
# =====================================================================
with st.sidebar:
    st.title("📡 ESP32 Monitor")

    fonte = st.radio("Fonte de dados", FONTES)
    janela = st.selectbox("Janela de tempo", list(JANELAS), index=1)

    st.divider()
    ao_vivo = st.toggle("Atualização automática", value=True, disabled=fonte != FONTE_SIMULADOR)
    intervalo = st.slider("Intervalo de atualização (s)", 2, 30, 5, disabled=not ao_vivo)

    st.divider()
    st.subheader("Limites de alerta")
    temp_max = st.number_input("Temperatura máxima (°C)", 15.0, 45.0, 30.0, step=0.5, format="%.1f")
    umid_max = st.number_input("Umidade máxima (%)", 30.0, 100.0, 75.0, step=1.0, format="%.0f")

    st.divider()
    st.caption("Mockup — nenhum ESP32 conectado. Todas as leituras são simuladas.")

atualizar_a_cada = intervalo if (ao_vivo and fonte == FONTE_SIMULADOR) else None

# =====================================================================
# TÍTULO
# =====================================================================
st.title("Dashboard de Monitoramento — ESP32")
st.markdown(
    "<div class='mock-aviso'>🧪 <b>Mockup</b> — dados simulados. "
    "A conexão com o ESP32 entra em <code>src/load_data.py</code>.</div>",
    unsafe_allow_html=True,
)

# =====================================================================
# CARREGAR DADOS
# =====================================================================
df = obter_leituras(fonte, janela)

# =====================================================================
# TABS DO DASHBOARD
# =====================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Tempo Real",
    "Histórico",
    "Correlação",
    "Lógica Fuzzy",
    "Dispositivo",
    "Mini Relatório",
])


# =====================================================================
# TAB 1 — TEMPO REAL
# =====================================================================
@st.fragment(run_every=atualizar_a_cada)
def painel_tempo_real():
    dados = obter_leituras(fonte, janela)
    atual = dados.iloc[-1]
    ventilador = calcular_ventilador_fuzzy(atual["temperatura"], atual["umidade"])

    st.caption(
        f"Última leitura: {atual['timestamp']:%d/%m/%Y %H:%M:%S}"
        + (f" · atualiza a cada {atualizar_a_cada} s" if atualizar_a_cada else " · atualização pausada")
    )

    col1, col2, col3, col4 = st.columns(4)
    for col, (coluna, (titulo, unidade)) in zip((col1, col2, col3), GRANDEZAS.items()):
        casas = 1
        col.markdown(
            card(
                titulo, f"{atual[coluna]:.{casas}f}", unidade,
                f"média {dados[coluna].mean():.{casas}f} · mín {dados[coluna].min():.{casas}f} · máx {dados[coluna].max():.{casas}f}",
            ),
            unsafe_allow_html=True,
        )
    col4.markdown(
        card("Ventilador (fuzzy)", f"{ventilador:.0f}", "%", classificar_ventilador(ventilador)[1]),
        unsafe_allow_html=True,
    )

    st.write("")
    faixa(*avaliar_ambiente(atual, temp_max, umid_max))

    colA, colB = st.columns(2)
    with colA:
        grafico_linha(dados, "temperatura", "Temperatura", "°C", limite=temp_max)
    with colB:
        grafico_linha(dados, "umidade", "Umidade", "%", limite=umid_max)
    grafico_linha(dados, "luminosidade", "Luminosidade", "lux", altura=200)


with tab1:
    st.header("Leituras em Tempo Real")
    painel_tempo_real()

# =====================================================================
# TAB 2 — HISTÓRICO
# =====================================================================
with tab2:
    st.header("Histórico das Leituras")
    st.caption(f"{len(df)} leituras · de {df['timestamp'].min():%d/%m %H:%M} até {df['timestamp'].max():%d/%m %H:%M}")

    st.subheader("🔹 Resumo Estatístico")
    resumo = df[list(GRANDEZAS)].agg(["mean", "min", "max", "std"]).T
    resumo.index = [f"{titulo} ({unidade})" for titulo, unidade in GRANDEZAS.values()]
    resumo.columns = ["Média", "Mínimo", "Máximo", "Desvio padrão"]
    st.dataframe(resumo.style.format("{:.1f}"), width="stretch")

    st.subheader("🔹 Distribuição das Variáveis")
    colA, colB, colC = st.columns(3)
    for col, (coluna, (titulo, unidade)) in zip((colA, colB, colC), GRANDEZAS.items()):
        with col:
            histograma(df, coluna, titulo, unidade)

    st.subheader("🔹 Dados Recebidos")
    st.dataframe(
        df.sort_values("timestamp", ascending=False),
        width="stretch",
        hide_index=True,
        column_config={
            "timestamp": st.column_config.DatetimeColumn("Horário", format="DD/MM/YYYY HH:mm:ss"),
            "temperatura": st.column_config.NumberColumn("Temperatura (°C)", format="%.1f"),
            "umidade": st.column_config.NumberColumn("Umidade (%)", format="%.1f"),
            "luminosidade": st.column_config.NumberColumn("Luminosidade (lux)", format="%.0f"),
            "rssi": st.column_config.NumberColumn("Wi-Fi (dBm)"),
            "heap_livre": st.column_config.NumberColumn("Heap livre (kB)", format="%.1f"),
            "uptime_s": st.column_config.NumberColumn("Uptime (s)"),
        },
    )
    st.download_button(
        "⬇️ Baixar CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="leituras_esp32.csv",
        mime="text/csv",
    )

# =====================================================================
# TAB 3 — CORRELAÇÃO
# =====================================================================
with tab3:
    st.header("Correlação entre Variáveis")

    corr = calcular_correlacao(df)

    colA, colB = st.columns([1, 1])

    with colA:
        st.subheader("Mapa de Calor da Correlação")
        mapa_calor(corr)

    with colB:
        st.subheader("Dispersão")
        grafico_disp(df)

    st.subheader("Tabela de Correlação")
    st.dataframe(corr.style.format("{:.2f}"), width="stretch")

# =====================================================================
# TAB 4 — LÓGICA FUZZY
# =====================================================================
with tab4:
    st.header("Sistema Fuzzy de Controle do Ventilador")

    st.write("Use os controles abaixo para testar a **velocidade fuzzy** do ventilador:")

    ultima = df.iloc[-1]
    col1, col2 = st.columns(2)

    temperatura = col1.slider("Temperatura (°C)", 10.0, 45.0, float(round(ultima["temperatura"] * 2) / 2), step=0.5, format="%.1f", key="fuzzy_temperatura")
    umidade = col2.slider("Umidade (%)", 0.0, 100.0, float(round(ultima["umidade"])), step=1.0, format="%.0f", key="fuzzy_umidade")

    ventilador_fuzzy = calcular_ventilador_fuzzy(temperatura, umidade)

    st.subheader(f"🔍 Velocidade Fuzzy do Ventilador: **{ventilador_fuzzy:.0f} %**")
    faixa(*classificar_ventilador(ventilador_fuzzy))

    colA, colB, colC = st.columns(3)
    with colA:
        grafico_pertinencia(curvas_pertinencia("temperatura"), "Temperatura", "°C", temperatura, ROTULOS_FUZZY)
    with colB:
        grafico_pertinencia(curvas_pertinencia("umidade"), "Umidade", "%", umidade, ROTULOS_FUZZY)
    with colC:
        grafico_pertinencia(curvas_pertinencia("ventilador"), "Ventilador (saída)", "% PWM", ventilador_fuzzy, ROTULOS_FUZZY)

    st.write("### Como funciona o modelo fuzzy?")
    st.write("O sistema fuzzy utiliza regras linguísticas. Cada combinação de temperatura e umidade leva a uma velocidade:")

    tabela_regras = (
        pd.DataFrame(REGRAS, columns=["temperatura", "umidade", "ventilador"])
        .replace(ROTULOS_FUZZY)
        .pivot(index="temperatura", columns="umidade", values="ventilador")
        .loc[["Fria", "Agradável", "Quente"], ["Seca", "Ideal", "Úmida"]]
    )
    tabela_regras.index.name = "Temperatura ↓ / Umidade →"
    tabela_regras.columns.name = None
    st.dataframe(tabela_regras, width="stretch")

    st.write("""
Com isso, produz uma saída contínua entre 0 e 100 % — o valor de PWM que o ESP32
aplicaria no ventilador. A linha tracejada em cada gráfico mostra o valor atual.
    """)

# =====================================================================
# TAB 5 — DISPOSITIVO
# =====================================================================
with tab5:
    st.header("Estado do Dispositivo")

    ultima = df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(card("Conexão", "Online", "", "ESP32-WROOM-32 · v0.1.0"), unsafe_allow_html=True)
    col2.markdown(
        card("Sinal Wi-Fi", f"{ultima['rssi']:.0f}", "dBm", qualidade_wifi(ultima["rssi"])),
        unsafe_allow_html=True,
    )
    col3.markdown(card("Memória livre", f"{ultima['heap_livre']:.0f}", "kB", "heap"), unsafe_allow_html=True)
    col4.markdown(
        card("Ligado há", formatar_uptime(ultima["uptime_s"]), "", "desde a última reinicialização"),
        unsafe_allow_html=True,
    )

    st.write("")
    colA, colB = st.columns(2)

    with colA:
        st.subheader("Controles")
        st.caption("Simulados — nenhum comando é enviado.")
        led = st.toggle("LED de status", value=True)
        modo_auto = st.toggle("Ventilador em modo automático (fuzzy)", value=True)
        pwm_manual = st.slider("Velocidade manual do ventilador (%)", 0, 100, 50, disabled=modo_auto)
        envio = st.select_slider("Intervalo de envio das leituras", ["1 s", "5 s", "10 s", "30 s", "60 s"], value="5 s")
        if st.button("Enviar configuração"):
            st.toast("Configuração enviada (simulado).", icon="✅")

    with colB:
        st.subheader("Formato da Leitura")
        st.caption("JSON que o ESP32 deve enviar a cada leitura.")
        st.json({
            "timestamp": ultima["timestamp"].isoformat(),
            "temperatura": float(ultima["temperatura"]),
            "umidade": float(ultima["umidade"]),
            "luminosidade": float(ultima["luminosidade"]),
            "rssi": int(ultima["rssi"]),
            "heap_livre": float(ultima["heap_livre"]),
            "uptime_s": int(ultima["uptime_s"]),
        })

# =====================================================================
# TAB 6 — MINI RELATÓRIO
# =====================================================================
with tab6:
    st.header("Mini Relatório — Análise dos Resultados")

    corr = calcular_correlacao(df)
    acima = int((df["temperatura"] > temp_max).sum())
    pct_acima = 100 * acima / len(df)
    ventilador_agora = calcular_ventilador_fuzzy(df.iloc[-1]["temperatura"], df.iloc[-1]["umidade"])

    st.markdown("""
    ## 🎯 Objetivo Geral
    Monitorar o ambiente com um ESP32 a partir de três grandezas principais:
    - Temperatura
    - Umidade
    - Luminosidade

    A análise usa estatísticas, gráficos e lógica fuzzy para acompanhar o ambiente e decidir a ventilação.
    """)

    st.markdown("---")

    st.subheader("1) Estatísticas Gerais das Leituras")

    st.markdown(f"""
    - **Janela analisada:** `{janela}` ({len(df)} leituras)
    - **Temperatura média:** `{df['temperatura'].mean():.1f}` °C (máx. `{df['temperatura'].max():.1f}` °C)
    - **Umidade média:** `{df['umidade'].mean():.1f}` %
    - **Luminosidade média:** `{df['luminosidade'].mean():.0f}` lux

    A temperatura ficou acima do limite de `{temp_max:g}` °C em `{acima}` leituras (`{pct_acima:.0f}` % da janela).
    """)

    st.markdown("---")

    st.subheader("2) Correlação Entre Variáveis")

    st.markdown(f"""
    Principais relações observadas:

    - **Temperatura × Umidade:** correlação {descrever_correlacao(corr.loc['Temperatura', 'Umidade'])} (`{corr.loc['Temperatura', 'Umidade']:.2f}`)
    - **Temperatura × Luminosidade:** correlação {descrever_correlacao(corr.loc['Temperatura', 'Luminosidade'])} (`{corr.loc['Temperatura', 'Luminosidade']:.2f}`)
    - **Umidade × Luminosidade:** correlação {descrever_correlacao(corr.loc['Umidade', 'Luminosidade'])} (`{corr.loc['Umidade', 'Luminosidade']:.2f}`)
    """)

    st.markdown("---")

    st.subheader("3) Análise Fuzzy da Ventilação")

    st.markdown(f"""
    O sistema fuzzy combina temperatura e umidade em regras linguísticas como:

    - **Quente + Úmida → ventilação Alta**
    - **Agradável + Úmida → ventilação Média**
    - **Fria (qualquer umidade) → ventilação Baixa**

    A saída varia de **0 a 100 %**, com a classificação:

    - `0 a 30` → 🟢 Baixa
    - `30 a 60` → 🟡 Moderada
    - `60 a 100` → 🔴 Alta

    Para a última leitura, a velocidade calculada é **{ventilador_agora:.0f} %** ({classificar_ventilador(ventilador_agora)[1]}).
    """)

    st.markdown("---")

    st.subheader("4) Estado do Dispositivo")

    st.markdown(f"""
    - Sinal Wi-Fi médio de `{df['rssi'].mean():.0f}` dBm ({qualidade_wifi(df['rssi'].mean()).lower()}).
    - Memória livre mínima de `{df['heap_livre'].min():.0f}` kB na janela.
    """)

    st.success("Relatório gerado automaticamente com base nas leituras e cálculos do dashboard.")
    st.caption("As leituras deste mockup são simuladas; os números acima não vêm de um ESP32 real.")
