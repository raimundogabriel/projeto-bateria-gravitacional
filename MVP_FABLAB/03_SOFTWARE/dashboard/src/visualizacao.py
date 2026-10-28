"""Funções gráficas do dashboard (Altair)."""
import altair as alt
import pandas as pd
import streamlit as st

# Uma cor fixa por grandeza, em todo o dashboard (claro, escuro)
CORES = {
    "h_m": ("#2a78d6", "#3987e5"),
    "nivel_pct": ("#2a78d6", "#3987e5"),
    "p_subida_w": ("#eb6834", "#d95926"),
    "p_gerada_w": ("#1baf7a", "#199e70"),
    "p_leds_w": ("#8a5cd6", "#9d74e3"),
    "tarifa_rs_kwh": ("#c98a0c", "#e0a526"),
    "comando": ("#5b6470", "#a7afba"),
    "v_gen_v": ("#1baf7a", "#199e70"),
    "demanda_w": ("#8a5cd6", "#9d74e3"),
}
SERIE = [("#2a78d6", "#3987e5"), ("#eb6834", "#d95926"), ("#1baf7a", "#199e70"), ("#8a5cd6", "#9d74e3")]
NEUTRO = ("#f0efec", "#383835")
TINTA = ("#0b0b0b", "#ffffff")
APAGADO = "#898781"
CRITICO = "#d03b3b"


def tema_escuro():
    try:
        return st.context.theme.type == "dark"
    except Exception:
        return False


def _cor(par):
    return par[1] if tema_escuro() else par[0]


def cor_da_variavel(coluna):
    return _cor(CORES[coluna])


def _mostrar(grafico):
    st.altair_chart(grafico, width="stretch")


def _formato_x(df):
    return "%H:%M:%S" if (df["timestamp"].max() - df["timestamp"].min()) <= pd.Timedelta(minutes=20) else "%H:%M"


def grafico_linha(df, coluna, titulo, unidade, limite=None, altura=230, degrau=False, dominio=None):
    """Série temporal de uma grandeza, com valor atual destacado e tooltip."""
    cor = cor_da_variavel(coluna)
    escala = alt.Scale(domain=dominio) if dominio else alt.Scale(zero=False, nice=True)

    base = alt.Chart(df).encode(
        x=alt.X("timestamp:T", title=None, axis=alt.Axis(format=_formato_x(df), grid=False, tickCount=6)),
        y=alt.Y(f"{coluna}:Q", title=unidade, scale=escala),
    )
    linha = base.mark_line(strokeWidth=2, color=cor, interpolate="step-after" if degrau else "linear")

    perto = alt.selection_point(nearest=True, on="pointerover", fields=["timestamp"], empty=False, clear="pointerout")
    dicas = [
        alt.Tooltip("timestamp:T", title="Horário", format="%d/%m %H:%M:%S"),
        alt.Tooltip(f"{coluna}:Q", title=f"{titulo} ({unidade})", format=".2f"),
        alt.Tooltip("estado:N", title="Estado"),
    ]
    alvo = base.mark_rule(strokeWidth=1, color=APAGADO).encode(
        opacity=alt.condition(perto, alt.value(0.7), alt.value(0)), tooltip=dicas
    ).add_params(perto)
    ponto = base.mark_point(size=70, filled=True, color=cor, opacity=1).transform_filter(perto)

    atual = alt.Chart(df.tail(1)).mark_point(size=80, filled=True, color=cor, opacity=1).encode(
        x="timestamp:T", y=f"{coluna}:Q"
    )
    camadas = [linha, alvo, ponto, atual]

    if limite is not None:
        regua = alt.Chart(pd.DataFrame({"y": [limite], "rotulo": [f"limite {limite:g} {unidade}"]}))
        camadas.append(regua.mark_rule(strokeWidth=1.5, strokeDash=[6, 4], color=CRITICO).encode(y="y:Q"))
        camadas.append(regua.mark_text(align="left", dx=4, dy=-7, fontSize=11, color=_cor(TINTA), opacity=0.75).encode(
            x=alt.value(0), y="y:Q", text="rotulo:N"
        ))

    _mostrar(alt.layer(*camadas).properties(height=altura, title=alt.Title(titulo, anchor="start", fontSize=14)))


def grafico_series(df, colunas, titulo, unidade, altura=260):
    """Várias grandezas na mesma unidade, com legenda (ex.: potências)."""
    longo = df.melt(id_vars=["timestamp", "estado"], value_vars=list(colunas), var_name="serie", value_name="valor")
    longo["serie"] = longo["serie"].map(colunas)
    ordem = list(colunas.values())
    cores = [cor_da_variavel(c) for c in colunas]

    grafico = alt.Chart(longo).mark_line(strokeWidth=2).encode(
        x=alt.X("timestamp:T", title=None, axis=alt.Axis(format=_formato_x(df), grid=False, tickCount=6)),
        y=alt.Y("valor:Q", title=unidade),
        color=alt.Color("serie:N", sort=ordem, scale=alt.Scale(domain=ordem, range=cores),
                        legend=alt.Legend(title=None, orient="top")),
        tooltip=[
            alt.Tooltip("timestamp:T", title="Horário", format="%d/%m %H:%M:%S"),
            alt.Tooltip("serie:N", title="Grandeza"),
            alt.Tooltip("valor:Q", title=unidade, format=".2f"),
            alt.Tooltip("estado:N", title="Estado"),
        ],
    ).properties(height=altura, title=alt.Title(titulo, anchor="start", fontSize=14))
    _mostrar(grafico)


def histograma(df, coluna, titulo, unidade, altura=220):
    """Distribuição de uma grandeza."""
    grafico = alt.Chart(df).mark_bar(
        color=cor_da_variavel(coluna), cornerRadiusTopLeft=4, cornerRadiusTopRight=4, binSpacing=2
    ).encode(
        x=alt.X(f"{coluna}:Q", bin=alt.Bin(maxbins=18), title=unidade, axis=alt.Axis(grid=False)),
        y=alt.Y("count():Q", title="Leituras"),
        tooltip=[
            alt.Tooltip(f"{coluna}:Q", bin=alt.Bin(maxbins=18), title=f"{titulo} ({unidade})"),
            alt.Tooltip("count():Q", title="Leituras"),
        ],
    ).properties(height=altura, title=alt.Title(titulo, anchor="start", fontSize=14))
    _mostrar(grafico)


def grafico_barras_estado(df, altura=220):
    """Tempo (leituras) em cada estado da máquina de estados."""
    contagem = df["estado"].value_counts().rename_axis("estado").reset_index(name="leituras")
    grafico = alt.Chart(contagem).mark_bar(color=_cor(SERIE[0]), cornerRadiusEnd=4).encode(
        x=alt.X("leituras:Q", title="Leituras"),
        y=alt.Y("estado:N", sort="-x", title=None),
        tooltip=[alt.Tooltip("estado:N", title="Estado"), alt.Tooltip("leituras:Q", title="Leituras")],
    ).properties(height=altura, title=alt.Title("Tempo em cada estado", anchor="start", fontSize=14))
    _mostrar(grafico)


def grafico_disp(df, x, y, titulo_x, titulo_y, titulo, altura=320):
    """Dispersão entre duas grandezas."""
    grafico = alt.Chart(df).mark_circle(size=55, color=_cor(SERIE[2]), opacity=0.6).encode(
        x=alt.X(f"{x}:Q", title=titulo_x, scale=alt.Scale(zero=False)),
        y=alt.Y(f"{y}:Q", title=titulo_y, scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip("timestamp:T", title="Horário", format="%d/%m %H:%M:%S"),
            alt.Tooltip(f"{x}:Q", title=titulo_x, format=".3f"),
            alt.Tooltip(f"{y}:Q", title=titulo_y, format=".1f"),
        ],
    ).properties(height=altura, title=alt.Title(titulo, anchor="start", fontSize=14))
    _mostrar(grafico)


def grafico_barras_ciclos(ciclos, altura=260):
    """Energia de subida, gerada e entregue aos LEDs, por descida."""
    nomes = {"e_subida_j": "Consumida na subida", "e_gerada_j": "Gerada na descida", "e_leds_j": "Nos LEDs"}
    longo = ciclos.melt(id_vars="ciclo", value_vars=list(nomes), var_name="serie", value_name="energia")
    longo["serie"] = longo["serie"].map(nomes)
    ordem = list(nomes.values())
    cores = [cor_da_variavel(c) for c in ("p_subida_w", "p_gerada_w", "p_leds_w")]
    grafico = alt.Chart(longo).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X("ciclo:O", title="Descida"),
        xOffset=alt.XOffset("serie:N", sort=ordem),
        y=alt.Y("energia:Q", title="J"),
        color=alt.Color("serie:N", sort=ordem, scale=alt.Scale(domain=ordem, range=cores),
                        legend=alt.Legend(title=None, orient="top")),
        tooltip=[alt.Tooltip("ciclo:O", title="Descida"), alt.Tooltip("serie:N", title="Energia"),
                 alt.Tooltip("energia:Q", title="J", format=".0f")],
    ).properties(height=altura, title=alt.Title("Energia por descida", anchor="start", fontSize=14))
    _mostrar(grafico)


def mapa_comando(superficie, tarifa=None, nivel=None, altura=340):
    """Comando fuzzy na grade tarifa × nível (azul = descer, laranja = subir)."""
    dados = pd.DataFrame(superficie)
    escuro = tema_escuro()
    polos = ["#3987e5", NEUTRO[1], "#d95926"] if escuro else ["#2a78d6", NEUTRO[0], "#eb6834"]

    celulas = alt.Chart(dados).mark_rect().encode(
        x=alt.X("tarifa:O", title="Tarifa (R$/kWh)", axis=alt.Axis(labelAngle=0, values=[0.0, 0.5, 1.0, 1.5, 2.0])),
        y=alt.Y("nivel:O", title="Nível de carga (%)", sort="descending", axis=alt.Axis(values=[0, 25, 50, 75, 100])),
        color=alt.Color(
            "comando:Q",
            scale=alt.Scale(type="linear", domain=[-100, 0, 100], range=polos, interpolate="rgb"),
            legend=alt.Legend(title="Comando", gradientLength=altura - 80),
        ),
        tooltip=[
            alt.Tooltip("tarifa:Q", title="Tarifa (R$/kWh)", format=".1f"),
            alt.Tooltip("nivel:Q", title="Nível (%)", format=".0f"),
            alt.Tooltip("comando:Q", title="Comando", format=".0f"),
        ],
    )
    camadas = [celulas]
    if tarifa is not None and nivel is not None:
        marca = pd.DataFrame({"tarifa": [round(round(tarifa * 10) / 10, 1)], "nivel": [float(round(nivel / 5) * 5)]})
        camadas.append(alt.Chart(marca).mark_rect(fill=None, stroke=_cor(TINTA), strokeWidth=2).encode(
            x="tarifa:O", y=alt.Y("nivel:O", sort="descending")
        ))
    _mostrar(alt.layer(*camadas).properties(height=altura))


def grafico_pertinencia(linhas, titulo, unidade, valor=None, rotulos=None, altura=260):
    """Funções de pertinência de uma variável fuzzy, com o valor atual marcado."""
    dados = pd.DataFrame(linhas)
    rotulos = rotulos or {}
    dados["conjunto"] = dados["conjunto"].map(lambda c: rotulos.get(c, c))
    ordem = list(dict.fromkeys(dados["conjunto"]))
    cores = [_cor(c) for c in SERIE[: len(ordem)]]

    curvas = alt.Chart(dados).mark_line(strokeWidth=2).encode(
        x=alt.X("x:Q", title=unidade, axis=alt.Axis(grid=False)),
        y=alt.Y("pertinencia:Q", title="Pertinência", scale=alt.Scale(domain=[0, 1.05]), axis=alt.Axis(tickCount=3)),
        color=alt.Color("conjunto:N", sort=ordem, scale=alt.Scale(domain=ordem, range=cores),
                        legend=alt.Legend(title=None, orient="top")),
        tooltip=[
            alt.Tooltip("conjunto:N", title="Conjunto"),
            alt.Tooltip("x:Q", title=unidade, format=".2f"),
            alt.Tooltip("pertinencia:Q", title="Pertinência", format=".2f"),
        ],
    )
    camadas = [curvas]
    if valor is not None:
        marca = alt.Chart(pd.DataFrame({"x": [valor]}))
        camadas.append(marca.mark_rule(strokeWidth=1.5, strokeDash=[6, 4], color=_cor(TINTA), opacity=0.7).encode(x="x:Q"))
    _mostrar(alt.layer(*camadas).properties(height=altura, title=alt.Title(titulo, anchor="start", fontSize=14)))
