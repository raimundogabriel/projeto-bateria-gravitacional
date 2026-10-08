"""
Sistema fuzzy de controle do ventilador.

Entradas: temperatura (°C) e umidade (%)
Saída:    velocidade do ventilador (0 a 100 % de PWM)
"""
from functools import lru_cache

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

FAIXA_TEMPERATURA = (10, 45)
FAIXA_UMIDADE = (0, 100)

# Conjuntos fuzzy: nome -> pontos da função trapezoidal
CONJUNTOS = {
    "temperatura": {
        "fria": [10, 10, 18, 24],
        "agradavel": [20, 25, 25, 30],
        "quente": [27, 33, 45, 45],
    },
    "umidade": {
        "seca": [0, 0, 30, 45],
        "ideal": [35, 52, 52, 70],
        "umida": [60, 75, 100, 100],
    },
    "ventilador": {
        "baixa": [0, 0, 0, 35],
        "media": [25, 50, 50, 75],
        "alta": [65, 100, 100, 100],
    },
}

# (temperatura, umidade) -> ventilador
REGRAS = [
    ("fria", "seca", "baixa"),
    ("fria", "ideal", "baixa"),
    ("fria", "umida", "baixa"),
    ("agradavel", "seca", "baixa"),
    ("agradavel", "ideal", "baixa"),
    ("agradavel", "umida", "media"),
    ("quente", "seca", "media"),
    ("quente", "ideal", "alta"),
    ("quente", "umida", "alta"),
]


@lru_cache(maxsize=1)
def criar_sistema_fuzzy():
    # Entradas
    temperatura = ctrl.Antecedent(np.arange(10, 45.1, 0.5), "temperatura")
    umidade = ctrl.Antecedent(np.arange(0, 101, 1), "umidade")

    # Saída
    ventilador = ctrl.Consequent(np.arange(0, 101, 1), "ventilador")

    # Funções de pertinência
    for variavel in (temperatura, umidade, ventilador):
        for nome, pontos in CONJUNTOS[variavel.label].items():
            variavel[nome] = fuzz.trapmf(variavel.universe, pontos)

    # Regras fuzzy
    regras = [
        ctrl.Rule(temperatura[t] & umidade[u], ventilador[v])
        for t, u, v in REGRAS
    ]

    return ctrl.ControlSystem(regras)


def calcular_ventilador_fuzzy(temperatura_val, umidade_val):
    """Devolve a velocidade do ventilador (0 a 100) para uma leitura."""
    sistema = ctrl.ControlSystemSimulation(criar_sistema_fuzzy())

    sistema.input["temperatura"] = float(np.clip(temperatura_val, *FAIXA_TEMPERATURA))
    sistema.input["umidade"] = float(np.clip(umidade_val, *FAIXA_UMIDADE))

    sistema.compute()

    return float(sistema.output["ventilador"])


def classificar_ventilador(velocidade):
    """Classifica a velocidade em três níveis: (chave, rótulo)."""
    if velocidade < 30:
        return "low", "🟢 Ventilação baixa"
    if velocidade < 60:
        return "medium", "🟡 Ventilação moderada"
    return "high", "🔴 Ventilação alta"


def curvas_pertinencia(variavel):
    """Pontos (x, conjunto, pertinência) para desenhar as funções de pertinência."""
    limites = {"temperatura": FAIXA_TEMPERATURA, "umidade": FAIXA_UMIDADE, "ventilador": (0, 100)}
    x = np.linspace(*limites[variavel], 141)
    linhas = []
    for nome, pontos in CONJUNTOS[variavel].items():
        for xi, yi in zip(x, fuzz.trapmf(x, pontos)):
            linhas.append({"x": float(xi), "conjunto": nome, "pertinencia": float(yi)})
    return linhas
