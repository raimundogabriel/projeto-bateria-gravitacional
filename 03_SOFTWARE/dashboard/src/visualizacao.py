"""Funções gráficas do dashboard (Altair)."""
import altair as alt
import pandas as pd
import streamlit as st

# Uma cor fixa por grandeza, em todo o dashboard (claro, escuro)
CORES = {
    "temperatura": ("#eb6834", "#d95926"),
    "umidade": ("#2a78d6", "#3987e5"),
    "luminosidade": ("#1baf7a", "#199e70"),
}
SERIE = [("#2a78d6", "#3987e5"), ("#eb6834", "#d95926"), ("#1baf7a", "#199e70")]
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


def grafico_linha(df, coluna, titulo, unidade, limite=None, altura=230):
    """Série temporal de uma grandeza, com valor atual destacado e tooltip."""
    cor = cor_da_variavel(coluna)
    formato_x = "%H:%M:%S" if (df["timestamp"].max() - df["timestamp"].min()) <= pd.Timedelta(minutes=20) else "%H:%M"

    base = alt.Chart(df).encode(
        x=alt.X("timestamp:T", title=None, axis=alt.Axis(format=formato_x, grid=False, tickCount=6)),
        y=alt.Y(f"{coluna}:Q", title=unidade, scale=alt.Scale(zero=False, nice=True)),
    )
    linha = base.mark_line(strokeWidth=2, color=cor, interpolate="monotone")

    perto = alt.selection_point(nearest=True, on="pointerover", fields=["timestamp"], empty=False, clear="pointerout")
    dicas = [
        alt.Tooltip("timestamp:T", title="Horário", format="%d/%m %H:%M:%S"),
        alt.Tooltip(f"{coluna}:Q", title=f"{titulo} ({unidade})", format=".1f"),
    ]
    alvo = base.mark_rule(strokeWidth=1, color=APAGADO).encode(
        opacity=alt.condition(perto, alt.value(0.7), alt.value(0)), tooltip=dicas
    ).add_params(perto)
    ponto = base.mark_point(size=70, filled=True, color=cor, opacity=1).transform_filter(perto)

    ultimo = df.tail(1)
    atual = alt.Chart(ultimo).mark_point(size=80, filled=True, color=cor, opacity=1).encode(
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


def grafico_disp(df, altura=340):
    """Dispersão temperatura × umidade."""
    grafico = alt.Chart(df).mark_circle(
        size=55, color=_cor(SERIE[0]), opacity=0.55
    ).encode(
        x=alt.X("temperatura:Q", title="Temperatura (°C)", scale=alt.Scale(zero=False)),
        y=alt.Y("umidade:Q", title="Umidade (%)", scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip("timestamp:T", title="Horário", format="%d/%m %H:%M:%S"),
            alt.Tooltip("temperatura:Q", title="Temperatura (°C)", format=".1f"),
            alt.Tooltip("umidade:Q", title="Umidade (%)", format=".1f"),
        ],
    ).properties(height=altura, title=alt.Title("Temperatura × Umidade", anchor="start", fontSize=14))
    _mostrar(grafico)


def mapa_calor(corr, altura=340):
    """Mapa de calor da matriz de correlação (azul = negativa, vermelho = positiva)."""
    ordem = list(corr.columns)
    dados = corr.reset_index(names="linha").melt(id_vars="linha", var_name="coluna", value_name="correlacao")
    escuro = tema_escuro()
    polos = ["#3987e5", NEUTRO[1], "#e66767"] if escuro else ["#2a78d6", NEUTRO[0], "#e34948"]

    base = alt.Chart(dados).encode(
        x=alt.X("coluna:N", sort=ordem, title=None, axis=alt.Axis(labelAngle=0, orient="top", labelOverlap=False, labelAlign="center", labelBaseline="bottom")),
        y=alt.Y("linha:N", sort=ordem, title=None),
        tooltip=[
            alt.Tooltip("linha:N", title="Variável"),
            alt.Tooltip("coluna:N", title="Variável"),
            alt.Tooltip("correlacao:Q", title="Correlação", format=".2f"),
        ],
    )
    celulas = base.mark_rect(stroke="#0e1117" if escuro else "#ffffff", strokeWidth=2, cornerRadius=4).encode(
        color=alt.Color(
            "correlacao:Q",
            scale=alt.Scale(type="linear", domain=[-1, 0, 1], range=polos, interpolate="rgb", clamp=True),
            legend=alt.Legend(title="Correlação", gradientLength=altura - 80),
        )
    )
    forte = "#ffffff"
    fraco = TINTA[1] if escuro else TINTA[0]
    rotulos = base.mark_text(fontSize=13).encode(
        text=alt.Text("correlacao:Q", format=".2f"),
        color=alt.condition("abs(datum.correlacao) > 0.55", alt.value(forte), alt.value(fraco)),
    )
    _mostrar((celulas + rotulos).properties(height=altura))


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
            alt.Tooltip("x:Q", title=unidade, format=".1f"),
            alt.Tooltip("pertinencia:Q", title="Pertinência", format=".2f"),
        ],
    )
    camadas = [curvas]
    if valor is not None:
        marca = alt.Chart(pd.DataFrame({"x": [valor]}))
        camadas.append(marca.mark_rule(strokeWidth=1.5, strokeDash=[6, 4], color=_cor(TINTA), opacity=0.7).encode(x="x:Q"))
    _mostrar(alt.layer(*camadas).properties(height=altura, title=alt.Title(titulo, anchor="start", fontSize=14)))
