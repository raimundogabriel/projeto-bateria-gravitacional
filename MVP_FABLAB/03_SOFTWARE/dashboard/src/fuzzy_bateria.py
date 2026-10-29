"""
Sistema fuzzy da bateria gravitacional.

Cópia fiel do fuzzy do firmware do MVP
(`MVP_FABLAB/03_SOFTWARE/firmware/wokwi/sketch.ino`, o mesmo do projeto principal):
Mamdani, AND = mín, OR = máx, centroide com passo 2 e normalização pelo
maior valor que o centroide alcança. Assim o painel mostra exatamente o
comando que o ESP32 calcularia.

Entradas: tarifa (R$/kWh), nível de carga (%) e demanda da saída (W; no MVP,
          chave de demanda ou painel)
Saída:    comando de −100 (descer) a +100 (subir)
"""
from functools import lru_cache

import numpy as np

V_ALVO_MIN = 0.06   # m/s, velocidade-alvo de descida do MVP (C-107)
V_ALVO_MAX = 0.13   # m/s

FAIXAS = {
    "tarifa": (0.0, 2.0),
    "nivel": (0.0, 100.0),
    "demanda": (0.0, 10.0),
    "comando": (-100.0, 100.0),
}

# Conjuntos fuzzy: nome -> pontos da função trapezoidal (triângulo = b igual a c)
CONJUNTOS = {
    "tarifa": {
        "baixa": [0, 0, 0.6, 0.8],
        "media": [0.6, 0.9, 0.9, 1.2],
        "alta": [0.9, 1.2, 2, 2],
    },
    "nivel": {
        "baixo": [0, 0, 20, 45],
        "medio": [20, 50, 50, 95],
        "alto": [60, 95, 100, 100],
    },
    "demanda": {
        "baixa": [0, 0, 0.3, 1],
        "media": [0.3, 1.5, 1.5, 3],
        "alta": [2, 4, 10, 10],
    },
    "comando": {
        "descer": [-100, -100, -80, -50],
        "descer_parcial": [-70, -40, -40, -10],
        "manter": [-25, 0, 0, 25],
        "subir": [40, 70, 100, 100],
    },
}

# (regra, tarifa, nível, demanda, ação). Demanda None = qualquer; tupla = OU.
REGRAS = [
    ("R1", "baixa", "baixo", None, "subir"),
    ("R2", "baixa", "medio", None, "subir"),
    ("R3", "baixa", "alto", None, "manter"),
    ("R4", "media", "baixo", None, "manter"),
    ("R5", "media", "medio", None, "manter"),
    ("R6", "media", "alto", "alta", "descer_parcial"),
    ("R7", "media", "alto", ("baixa", "media"), "manter"),
    ("R8", "alta", "baixo", None, "manter"),
    ("R9", "alta", "medio", ("media", "alta"), "descer_parcial"),
    ("R10", "alta", "alto", ("media", "alta"), "descer"),
    ("R11", "alta", None, "baixa", "manter"),
]

_EIXO_SAIDA = np.arange(-100, 101, 2, dtype=float)


def trap(x, a, b, c, d):
    """Função trapezoidal igual à `trap()` do firmware (aceita escalar ou array)."""
    x = np.asarray(x, dtype=float)
    subida = np.where(x <= a, 0.0, (x - a) / max(b - a, 1e-9))
    descida = np.where(x >= d, 0.0, (d - x) / max(d - c, 1e-9))
    return np.where((x >= b) & (x <= c), 1.0, np.where(x < b, subida, descida))


def pertinencias(variavel, valor):
    """Grau de pertinência de `valor` em cada conjunto da variável."""
    return {nome: float(trap(valor, *pontos)) for nome, pontos in CONJUNTOS[variavel].items()}


def _centroide(ativacoes):
    mu = np.zeros_like(_EIXO_SAIDA)
    for nome, alfa in ativacoes.items():
        mu = np.maximum(mu, np.minimum(alfa, trap(_EIXO_SAIDA, *CONJUNTOS["comando"][nome])))
    peso = mu.sum()
    return float((mu * _EIXO_SAIDA).sum() / peso) if peso > 0 else 0.0


@lru_cache(maxsize=1)
def _normalizacao():
    vazio = dict.fromkeys(CONJUNTOS["comando"], 0.0)
    max_subir = _centroide({**vazio, "subir": 1.0})
    max_descer = -_centroide({**vazio, "descer": 1.0})
    return max_subir, max_descer


def ativar_regras(tarifa, nivel, demanda):
    """Grau de disparo de cada regra: lista de (regra, ação, grau)."""
    t = pertinencias("tarifa", np.clip(tarifa, *FAIXAS["tarifa"]))
    n = pertinencias("nivel", np.clip(nivel, *FAIXAS["nivel"]))
    d = pertinencias("demanda", np.clip(demanda, *FAIXAS["demanda"]))

    disparos = []
    for regra, tt, nn, dd, acao in REGRAS:
        grau = t[tt]
        if nn is not None:
            grau = min(grau, n[nn])
        if dd is not None:
            grau = min(grau, max(d[x] for x in ((dd,) if isinstance(dd, str) else dd)))
        disparos.append((regra, acao, grau))
    return disparos


def calcular_comando(tarifa, nivel, demanda):
    """Comando fuzzy normalizado, de −100 (descer) a +100 (subir)."""
    ativacoes = dict.fromkeys(CONJUNTOS["comando"], 0.0)
    for _, acao, grau in ativar_regras(tarifa, nivel, demanda):
        ativacoes[acao] = max(ativacoes[acao], grau)

    c = _centroide(ativacoes)
    max_subir, max_descer = _normalizacao()
    if c >= 0:
        return float(np.clip(c / max_subir * 100, 0, 100))
    return float(np.clip(c / max_descer * 100, -100, 0))


def classificar_comando(comando):
    """Ação que o firmware tomaria partindo de MANTER: (chave, rótulo)."""
    if comando > 30:
        return "medium", "⬆️ Subir — armazenar energia"
    if comando < -30:
        return "high", "⬇️ Descer — gerar energia"
    return "low", "⏸️ Manter — motor desligado e trava engatada"


def velocidade_alvo(comando):
    """Velocidade-alvo de descida (m/s) para um comando, como no firmware do MVP."""
    if comando >= -10:
        return 0.0
    return V_ALVO_MIN + max(-comando - 30, 0.0) / 70.0 * (V_ALVO_MAX - V_ALVO_MIN)


def curvas_pertinencia(variavel, pontos=201):
    """Pontos (x, conjunto, pertinência) para desenhar as funções de pertinência."""
    x = np.linspace(*FAIXAS[variavel], pontos)
    linhas = []
    for nome, pts in CONJUNTOS[variavel].items():
        for xi, yi in zip(x, trap(x, *pts)):
            linhas.append({"x": float(xi), "conjunto": nome, "pertinencia": float(yi)})
    return linhas


def superficie(demanda, tarifas=None, niveis=None):
    """Comando para uma grade tarifa × nível, com a demanda fixa."""
    tarifas = np.round(np.arange(0.0, 2.01, 0.1), 2) if tarifas is None else tarifas
    niveis = np.arange(0, 101, 5) if niveis is None else niveis
    return [
        {"tarifa": float(t), "nivel": float(n), "comando": calcular_comando(t, n, demanda)}
        for t in tarifas for n in niveis
    ]
