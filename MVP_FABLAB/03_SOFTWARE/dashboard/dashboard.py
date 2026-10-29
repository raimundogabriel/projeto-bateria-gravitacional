import pandas as pd
import streamlit as st

from src.energia import E_TEORICA_J, em_wh, resumo_energia, tabela_ciclos
from src.fuzzy_bateria import (
    REGRAS,
    ativar_regras,
    calcular_comando,
    classificar_comando,
    curvas_pertinencia,
    superficie,
    velocidade_alvo,
)
from src.load_data import FONTE_SIMULADOR, FONTES, JANELAS, obter_leituras
from src.simulador import CURSO, DIA_SIMULADO_S, POSTOS, TARIFAS_PADRAO
from src.visualizacao import (
    grafico_barras_ciclos,
    grafico_barras_estado,
    grafico_disp,
    grafico_linha,
    grafico_pertinencia,
    grafico_series,
    histograma,
    mapa_comando,
)

# =====================================================================
# CONFIGURAÇÃO DO DASHBOARD
# =====================================================================
st.set_page_config(
    page_title="Dashboard — Bateria Gravitacional (MVP fablab)",
    layout="wide",
    page_icon="🔋",
)

POTENCIAS = {
    "p_subida_w": "Consumida na subida",
    "p_gerada_w": "Gerada na descida",
    "p_leds_w": "Nos LEDs de nível",
}

ROTULOS_FUZZY = {
    "baixa": "Baixa", "media": "Média", "alta": "Alta",
    "baixo": "Baixo", "medio": "Médio", "alto": "Alto",
    "descer": "Descer", "descer_parcial": "Descer parcial", "manter": "Manter", "subir": "Subir",
}

# estado do firmware -> (nível da faixa, texto)
ESTADOS = {
    "MANTER": ("low", "⏸️ MANTER — ponte LIVRE, lingueta engatada"),
    "SUBINDO": ("medium", "⬆️ SUBINDO — ponte SUBIR, armazenando energia"),
    "PREP_DESCIDA": ("medium", "🔓 PREP_DESCIDA — aliviando a lingueta, servo soltando"),
    "DESCENDO": ("high", "⬇️ DESCENDO — ponte GERAR, gerando energia"),
    "PARANDO": ("medium", "⏹️ PARANDO — ponte CURTO, frenagem a 100 %"),
    "FALHA": ("high", "🚨 FALHA — aguardando rearme"),
    "REARME": ("medium", "🔁 REARME — descendo até o fim de curso inferior"),
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
    .risk-high   { background-color: rgba(42, 120, 214, 0.16); border: 1px solid rgba(42, 120, 214, 0.5); }
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


def hora_simulada(hora):
    h = int(hora)
    return f"{h:02d}:{int((hora - h) * 60):02d}"


def reais(valor):
    return f"R$ {valor:.6f}".replace(".", ",")


# =====================================================================
# BARRA LATERAL
# =====================================================================
with st.sidebar:
    st.title("🔋 Bateria Gravitacional")
    st.caption("MVP fablab · 6 kg · 1,70 m")

    fonte = st.radio("Fonte de dados", FONTES)
    janela = st.selectbox("Janela de tempo", list(JANELAS), index=1)

    st.divider()
    ao_vivo = st.toggle("Atualização automática", value=True, disabled=fonte != FONTE_SIMULADOR)
    intervalo = st.slider("Intervalo de atualização (s)", 2, 30, 5, disabled=not ao_vivo)

    st.divider()
    st.subheader("Tarifas (R$/kWh)")
    st.caption("No protótipo, vão ao ESP32 pelo tópico `grav/tarifas`.")
    tarifas = {
        posto: st.number_input(POSTOS[posto], 0.0, 2.0, valor, step=0.05, format="%.2f", key=f"tarifa_{posto}")
        for posto, valor in TARIFAS_PADRAO.items()
    }

    st.divider()
    st.caption(
        f"Simulador — nenhum ESP32 conectado. O dia de tarifas é acelerado: "
        f"um dia inteiro a cada {DIA_SIMULADO_S // 60} minutos."
    )

atualizar_a_cada = intervalo if (ao_vivo and fonte == FONTE_SIMULADOR) else None

# =====================================================================
# TÍTULO
# =====================================================================
st.title("Bateria Gravitacional — Painel Remoto (MVP fablab)")
st.markdown(
    "<div class='mock-aviso'>🧪 <b>Simulação</b> — planta virtual de 6 kg e 1,70 m, igual à do firmware do MVP. "
    "A conexão com o ESP32 (MQTT <code>grav/*</code>) entra em <code>src/load_data.py</code>.</div>",
    unsafe_allow_html=True,
)

# =====================================================================
# CARREGAR DADOS
# =====================================================================
df = obter_leituras(fonte, janela, tarifas)

# =====================================================================
# TABS DO DASHBOARD
# =====================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Tempo Real",
    "Histórico",
    "Energia",
    "Lógica Fuzzy",
    "Controle",
    "Mini Relatório",
])


# =====================================================================
# TAB 1 — TEMPO REAL
# =====================================================================
@st.fragment(run_every=atualizar_a_cada)
def painel_tempo_real():
    dados = obter_leituras(fonte, janela, tarifas)
    atual = dados.iloc[-1]

    st.caption(
        f"Última leitura: {atual['timestamp']:%d/%m/%Y %H:%M:%S} · hora simulada {hora_simulada(atual['hora_sim'])}"
        + (f" · atualiza a cada {atualizar_a_cada} s" if atualizar_a_cada else " · atualização pausada")
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.markdown(
        card("Nível de carga", f"{atual['nivel_pct']:.0f}", "%",
             f"altura {atual['h_m']:.2f} m de {CURSO:.2f} m · {atual['nivel_pct'] / 100 * E_TEORICA_J:.0f} J"),
        unsafe_allow_html=True,
    )
    col2.markdown(
        card("Velocidade", f"{atual['v_ms'] * 100:+.1f}", "cm/s",
             f"frenagem {atual['frenagem_pct']:.0f} % · gerador {atual['v_gen_v']:.1f} V"),
        unsafe_allow_html=True,
    )
    potencia = atual["p_subida_w"] if atual["estado"] == "SUBINDO" else atual["p_gerada_w"]
    col3.markdown(
        card("Potência", f"{potencia:.2f}", "W", "consumida na subida" if atual["estado"] == "SUBINDO" else "gerada na descida"),
        unsafe_allow_html=True,
    )
    col4.markdown(
        card("LEDs de nível", f"{atual['p_leds_w']:.2f}", "W", f"demanda {atual['demanda_w']:.1f} W (chave ou painel)"),
        unsafe_allow_html=True,
    )
    col5.markdown(
        card("Tarifa", f"{atual['tarifa_rs_kwh']:.2f}", "R$/kWh", f"{atual['posto']} · fuzzy {atual['comando']:+.0f}"),
        unsafe_allow_html=True,
    )

    st.write("")
    faixa(*ESTADOS.get(atual["estado"], ("medium", atual["estado"])))

    colA, colB = st.columns(2)
    with colA:
        grafico_linha(dados, "nivel_pct", "Nível de carga", "%", dominio=[0, 100])
    with colB:
        grafico_series(dados, POTENCIAS, "Potências", "W", altura=230)
    colC, colD = st.columns(2)
    with colC:
        grafico_linha(dados, "tarifa_rs_kwh", "Tarifa", "R$/kWh", altura=200, degrau=True)
    with colD:
        grafico_linha(dados, "comando", "Comando fuzzy", "−100 a +100", altura=200, dominio=[-100, 100])


with tab1:
    st.header("Leituras em Tempo Real")
    painel_tempo_real()

# =====================================================================
# TAB 2 — HISTÓRICO
# =====================================================================
with tab2:
    st.header("Histórico das Leituras")
    st.caption(f"{len(df)} leituras · de {df['timestamp'].min():%d/%m %H:%M} até {df['timestamp'].max():%d/%m %H:%M}")

    st.subheader("🔹 Decisões e Trocas de Estado")
    trocas = df[df["estado"] != df["estado"].shift()].iloc[1:]
    if trocas.empty:
        st.info("Nenhuma troca de estado na janela.")
    else:
        st.dataframe(
            trocas[["timestamp", "estado", "comando", "tarifa_rs_kwh", "posto", "nivel_pct", "demanda_w"]]
            .sort_values("timestamp", ascending=False),
            width="stretch",
            hide_index=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Horário", format="DD/MM HH:mm:ss"),
                "estado": "Novo estado",
                "comando": st.column_config.NumberColumn("Comando fuzzy", format="%.0f"),
                "tarifa_rs_kwh": st.column_config.NumberColumn("Tarifa (R$/kWh)", format="%.2f"),
                "posto": "Posto",
                "nivel_pct": st.column_config.NumberColumn("Nível (%)", format="%.0f"),
                "demanda_w": st.column_config.NumberColumn("Demanda (W)", format="%.1f"),
            },
        )
        st.caption("A amostragem da janela pode esconder estados curtos, como PARANDO (cerca de 1 s).")

    colA, colB = st.columns(2)
    with colA:
        grafico_barras_estado(df)
    with colB:
        histograma(df, "nivel_pct", "Distribuição do nível de carga", "%")

    st.subheader("🔹 Dados Recebidos")
    st.dataframe(
        df.sort_values("timestamp", ascending=False),
        width="stretch",
        hide_index=True,
        column_config={
            "timestamp": st.column_config.DatetimeColumn("Horário", format="DD/MM/YYYY HH:mm:ss"),
            "estado": "Estado",
            "h_m": st.column_config.NumberColumn("Altura (m)", format="%.3f"),
            "nivel_pct": st.column_config.NumberColumn("Nível (%)", format="%.1f"),
            "v_ms": st.column_config.NumberColumn("Velocidade (m/s)", format="%.3f"),
            "p_subida_w": st.column_config.NumberColumn("P subida (W)", format="%.2f"),
            "p_gerada_w": st.column_config.NumberColumn("P gerada (W)", format="%.2f"),
            "p_leds_w": st.column_config.NumberColumn("P LEDs (W)", format="%.3f"),
            "v_gen_v": st.column_config.NumberColumn("Tensão gerada (V)", format="%.1f"),
            "frenagem_pct": st.column_config.NumberColumn("Frenagem (%)", format="%.0f"),
            "tarifa_rs_kwh": st.column_config.NumberColumn("Tarifa (R$/kWh)", format="%.2f"),
            "posto": "Posto",
            "demanda_w": st.column_config.NumberColumn("Demanda (W)", format="%.1f"),
            "comando": st.column_config.NumberColumn("Comando", format="%.0f"),
            "hora_sim": st.column_config.NumberColumn("Hora simulada", format="%.2f"),
            "ciclo": st.column_config.NumberColumn("Ciclos"),
            "e_subida_j": st.column_config.NumberColumn("E subida (J)", format="%.0f"),
            "e_gerada_j": st.column_config.NumberColumn("E gerada (J)", format="%.0f"),
            "e_leds_j": st.column_config.NumberColumn("E LEDs (J)", format="%.1f"),
            "e_aux_j": st.column_config.NumberColumn("E eletrônica (J)", format="%.0f"),
        },
    )
    st.download_button(
        "⬇️ Baixar CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="leituras_bateria.csv",
        mime="text/csv",
    )

# =====================================================================
# TAB 3 — ENERGIA
# =====================================================================
with tab3:
    st.header("Energia e Economia Simulada")

    resumo = resumo_energia(df)
    ciclos = tabela_ciclos(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(card("Descidas concluídas", f"{resumo['ciclos']}", "", f"na janela de {janela}"), unsafe_allow_html=True)
    rendimento = resumo["rendimento"]
    col2.markdown(
        card("Rendimento do ramo de potência", f"{rendimento * 100:.0f}" if rendimento else "—", "%",
             "gerada ÷ consumida na subida (estimado: ~10 %)"),
        unsafe_allow_html=True,
    )
    col3.markdown(
        card("Nos LEDs de nível", f"{resumo['e_leds_j']:.1f}", "J", f"{em_wh(resumo['e_leds_j']) * 1000:.2f} mWh"),
        unsafe_allow_html=True,
    )
    col4.markdown(
        card("Economia simulada", reais(resumo["economia_rs"]), "", "gerada × tarifa − consumida × tarifa"),
        unsafe_allow_html=True,
    )

    st.write("")
    st.info(
        f"⚡ Consumo da eletrônica (mostrado à parte): {em_wh(resumo['e_aux_j']):.2f} Wh na janela, "
        f"{reais(resumo['custo_aux_rs'])} — mais que toda a energia gerada "
        f"({em_wh(resumo['e_gerada_j']):.3f} Wh). O protótipo demonstra o conceito, não economiza."
    )

    if ciclos.empty:
        st.warning("Nenhuma descida concluída na janela.")
    else:
        colA, colB = st.columns([3, 2])
        with colA:
            grafico_barras_ciclos(ciclos)
        with colB:
            descidas = df[(df["estado"] == "DESCENDO") & (df["v_ms"] < 0)].assign(v_desc=lambda d: -d["v_ms"])
            if descidas.empty:
                st.caption("Nenhuma leitura durante descida nesta amostragem.")
            else:
                grafico_disp(descidas, "v_desc", "v_gen_v", "Velocidade de descida (m/s)", "Tensão gerada (V)",
                             "Tensão gerada × velocidade", altura=260)

        st.subheader("Descidas")
        st.dataframe(
            ciclos,
            width="stretch",
            hide_index=True,
            column_config={
                "ciclo": "Descida",
                "fim": st.column_config.DatetimeColumn("Fim da descida", format="DD/MM HH:mm:ss"),
                "e_subida_j": st.column_config.NumberColumn("Subida antes (J)", format="%.0f"),
                "e_gerada_j": st.column_config.NumberColumn("Gerada (J)", format="%.0f"),
                "e_leds_j": st.column_config.NumberColumn("LEDs (J)", format="%.1f"),
                "tarifa_subida": st.column_config.NumberColumn("Tarifa subida", format="%.2f"),
                "tarifa_descida": st.column_config.NumberColumn("Tarifa descida", format="%.2f"),
                "economia_rs": st.column_config.NumberColumn("Economia (R$)", format="%.6f"),
                "rendimento": st.column_config.NumberColumn("Gerada ÷ subida", format="%.2f"),
            },
        )
        st.caption(
            "Cada linha é uma descida, com a energia de subida consumida desde a descida anterior. "
            "Uma descida parcial (regras R6 e R9) gera menos que os ~29,7 J de uma descida inteira, "
            "e duas descidas seguidas aparecem sem subida entre elas."
        )

# =====================================================================
# TAB 4 — LÓGICA FUZZY
# =====================================================================
with tab4:
    st.header("Controlador Fuzzy (Mamdani)")

    st.write("Mesmo controlador do firmware. Teste o **comando** para cada combinação de entradas:")

    ultima = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    tarifa = col1.slider("Tarifa (R$/kWh)", 0.0, 2.0, float(ultima["tarifa_rs_kwh"]), step=0.05, format="%.2f", key="fuzzy_tarifa")
    nivel = col2.slider("Nível de carga (%)", 0.0, 100.0, float(round(ultima["nivel_pct"])), step=1.0, format="%.0f", key="fuzzy_nivel")
    demanda = col3.slider("Demanda da saída (W)", 0.0, 10.0, float(ultima["demanda_w"]), step=0.1, format="%.1f", key="fuzzy_demanda")

    comando = calcular_comando(tarifa, nivel, demanda)
    alvo = velocidade_alvo(comando)

    st.subheader(f"🔍 Comando fuzzy: **{comando:+.0f}**")
    faixa(*classificar_comando(comando))
    if comando < -30:
        st.caption(f"Velocidade-alvo de descida: {alvo:.3f} m/s (0,02 a 0,05 m/s).")
    st.caption("Histerese do firmware: começa a mover com |comando| > 30 e continua enquanto |comando| > 10.")

    colA, colB = st.columns(2)
    with colA:
        grafico_pertinencia(curvas_pertinencia("tarifa"), "Tarifa", "R$/kWh", tarifa, ROTULOS_FUZZY)
        grafico_pertinencia(curvas_pertinencia("demanda"), "Demanda da saída", "W", demanda, ROTULOS_FUZZY)
    with colB:
        grafico_pertinencia(curvas_pertinencia("nivel"), "Nível de carga", "%", nivel, ROTULOS_FUZZY)
        grafico_pertinencia(curvas_pertinencia("comando"), "Comando (saída)", "−100 a +100", comando, ROTULOS_FUZZY)

    st.write("### Regras")
    disparos = {regra: grau for regra, _, grau in ativar_regras(tarifa, nivel, demanda)}

    def _rotulo(valor):
        if valor is None:
            return "qualquer"
        if isinstance(valor, tuple):
            return " ou ".join(ROTULOS_FUZZY[v] for v in valor)
        return ROTULOS_FUZZY[valor]

    tabela_regras = pd.DataFrame([
        {"Regra": r, "Tarifa": _rotulo(t), "Nível": _rotulo(n), "Demanda": _rotulo(d),
         "Ação": ROTULOS_FUZZY[a], "Disparo": disparos[r]}
        for r, t, n, d, a in REGRAS
    ])
    st.dataframe(
        tabela_regras,
        width="stretch",
        hide_index=True,
        column_config={"Disparo": st.column_config.ProgressColumn("Disparo agora", min_value=0.0, max_value=1.0, format="%.2f")},
    )

    st.write("### Mapa do comando")
    st.caption(f"Comando para cada tarifa e nível, com a demanda em {demanda:.1f} W. O quadrado marca as entradas atuais.")
    mapa_comando(superficie(demanda), tarifa, nivel)

# =====================================================================
# TAB 5 — CONTROLE
# =====================================================================
with tab5:
    st.header("Controle Remoto")

    ultima = df.iloc[-1]
    colA, colB = st.columns(2)

    with colA:
        st.subheader("Comandos")
        st.caption("Simulados — nada é enviado. No protótipo, vão ao tópico `grav/comando`.")
        acoes = {"Automático (fuzzy)": "auto", "Subir": "subir", "Descer": "descer", "Parar": "parar", "Rearmar": "rearmar"}
        escolha = st.radio("Modo", list(acoes), horizontal=True)
        st.json({"acao": acoes[escolha]})
        if st.button("Enviar comando"):
            st.toast(f"Comando “{acoes[escolha]}” enviado (simulado).", icon="✅")

        st.subheader("Tarifas")
        st.caption("Altere na barra lateral. Mensagem retida do tópico `grav/tarifas`:")
        st.json(tarifas)

    with colB:
        st.subheader("Formato da Leitura")
        st.caption("JSON que o ESP32 publica em `grav/estado` (ver `03_SOFTWARE/contrato_dados.md`).")
        st.json({
            "ts": int(ultima["timestamp"].timestamp()),
            "estado": ultima["estado"],
            "modo": "AUTOMATICO",
            "h_m": float(ultima["h_m"]),
            "nivel_pct": float(ultima["nivel_pct"]),
            "v_ms": float(ultima["v_ms"]),
            "p_subida_w": float(ultima["p_subida_w"]),
            "p_gerada_w": float(ultima["p_gerada_w"]),
            "p_leds_w": float(ultima["p_leds_w"]),
            "v_gen_v": float(ultima["v_gen_v"]),
            "frenagem_pct": int(ultima["frenagem_pct"]),
            "tarifa_rs_kwh": float(ultima["tarifa_rs_kwh"]),
            "posto": ultima["posto"],
            "demanda_w": float(ultima["demanda_w"]),
        })

    st.subheader("Proteções do firmware")
    st.dataframe(
        pd.DataFrame([
            ("Velocidade > 0,07 m/s", "Falha: lingueta engata, frenagem 100 %, ponte em CURTO"),
            ("Tensão gerada > 14 V", "Falha (a TVS de 15 V protege o barramento)"),
            ("Corrente de subida > 1,5 A por 500 ms", "Falha: massa travada"),
            ("Fim de curso inesperado", "Falha"),
            ("Botão de emergência", "Falha + corte do 12V_POT por hardware (motor e servo)"),
            ("ESP32 travado ou desligado", "Ponte LIVRE: a carga fixa de 100 Ω limita a descida a ~0,05 m/s"),
            ("Trava não solta em 3 s", "Falha: trava presa"),
        ], columns=["Condição", "Ação"]),
        width="stretch",
        hide_index=True,
    )

# =====================================================================
# TAB 6 — MINI RELATÓRIO
# =====================================================================
with tab6:
    st.header("Mini Relatório — Análise dos Resultados")

    resumo = resumo_energia(df)
    trocas = df[df["estado"] != df["estado"].shift()].iloc[1:]
    subidas = int((trocas["estado"] == "SUBINDO").sum())
    descidas = int((trocas["estado"].isin(["PREP_DESCIDA", "DESCENDO"]) & (trocas["estado"].shift() != "PREP_DESCIDA")).sum())
    tempo_manter = 100 * (df["estado"] == "MANTER").mean()

    st.markdown("""
    ## 🎯 Objetivo Geral
    Armazenar energia elevando 6 kg de anilhas por 1,70 m quando a tarifa está baixa e
    liberá-la na descida, quando a tarifa está alta, acendendo os LEDs de nível. A decisão de
    subir, manter ou descer é tomada por lógica fuzzy no ESP32.
    """)

    st.markdown("---")

    st.subheader("1) Operação na Janela")
    st.markdown(f"""
    - **Janela analisada:** `{janela}` ({len(df)} leituras)
    - **Subidas iniciadas:** `{subidas}` · **descidas iniciadas:** `{descidas}`
    - **Tempo em MANTER:** `{tempo_manter:.0f}` % da janela
    - **Nível médio:** `{df['nivel_pct'].mean():.0f}` % (último: `{df['nivel_pct'].iloc[-1]:.0f}` %)
    """)

    st.markdown("---")

    st.subheader("2) Energia")
    rend = resumo["rendimento"]
    st.markdown(f"""
    - **Consumida na subida:** `{resumo['e_subida_j']:.0f}` J
    - **Gerada na descida:** `{resumo['e_gerada_j']:.0f}` J
      (rendimento do ramo de potência: `{f'{rend * 100:.0f} %' if rend else '—'}`)
    - **Nos LEDs de nível:** `{resumo['e_leds_j']:.1f}` J
    - **Economia simulada:** `{reais(resumo['economia_rs'])}`
    - **Consumo da eletrônica, à parte:** `{em_wh(resumo['e_aux_j']):.2f}` Wh

    Uma subida completa armazena `{E_TEORICA_J:.1f}` J (0,0278 Wh). A eletrônica, com cerca de 0,8 W,
    gasta isso em cerca de 2 minutos: o MVP é didático e mostra a estratégia de decisão,
    não economia real.
    """)

    st.markdown("---")

    st.subheader("3) Lógica Fuzzy")
    st.markdown("""
    O controlador combina tarifa, nível de carga e demanda da saída (chave ou painel) em 11 regras, como:

    - **Tarifa baixa + nível baixo ou médio → Subir**
    - **Tarifa alta + nível alto + demanda ligada → Descer**
    - **Tarifa alta + sem demanda → Manter**

    O comando vai de **−100 (descer)** a **+100 (subir)**:

    - `> +30` → ⬆️ começa a subir
    - `−30 a +30` → ⏸️ mantém (com histerese de ±10 para parar)
    - `< −30` → ⬇️ começa a descer, a 0,02–0,05 m/s
    """)

    st.success("Relatório gerado automaticamente com base nas leituras e cálculos do dashboard.")
    st.caption("As leituras são simuladas; os números acima não vêm de um ESP32 real.")
