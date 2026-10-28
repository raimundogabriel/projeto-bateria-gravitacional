"""
Simulador da bateria gravitacional.

Enquanto o ESP32 não publica por MQTT, este módulo gera as leituras de
`grav/estado` (ver `03_SOFTWARE/contrato_dados.md`) a partir de uma planta
virtual igual à do firmware: massa de 20 kg, curso de 1,70 m, subida a
0,05 m/s, descida entre 0,03 e 0,08 m/s e decisão fuzzy a cada 5 s.

O dia de tarifas é **acelerado**: um dia inteiro (fora de ponta,
intermediário e ponta) passa a cada `DIA_SIMULADO_S` segundos. Num dia real a
massa faz um único ciclo, e o painel ficaria parado quase o tempo todo.

As leituras são uma função determinística do horário: a simulação sempre
recomeça de um instante fixo da grade e roda até o fim da janela, então
chamar o simulador duas vezes para o mesmo instante devolve o mesmo valor.
"""
from datetime import datetime
from functools import lru_cache

import numpy as np
import pandas as pd

from src.fuzzy_bateria import calcular_comando, velocidade_alvo

# ---------- parâmetros do protótipo (iguais ao firmware) ----------
MASSA = 20.0              # kg
G = 9.81                  # m/s²
CURSO = 1.70              # m
V_SUBIDA = 0.05           # m/s
V_FREIO_TOTAL = 0.025     # m/s com frenagem em 100 % (11 Ω)
V_MAX_DESCIDA = 0.09      # m/s com frenagem em 0 %
KE_MASSA = 253.0          # V por m/s de massa
ETA_IDA = 0.92 * 0.75 * 0.75   # polias × redutor × motor (≈ 0,52)
ETA_BUCK = 0.85
V_MIN_BUCK = 8.0          # V, entrada mínima do conversor USB
CONSUMO_AUX_W = 1.0       # eletrônica de controle
T_FUZZY = 5               # s

DIA_SIMULADO_S = 20 * 60  # um dia de tarifas a cada 20 minutos

TARIFAS_PADRAO = {"fora_ponta": 0.60, "intermediario": 0.90, "ponta": 1.40}
POSTOS = {"fora_ponta": "Fora de ponta", "intermediario": "Intermediário", "ponta": "Ponta"}

COLUNAS = [
    "timestamp", "estado", "h_m", "nivel_pct", "v_ms",
    "p_subida_w", "p_gerada_w", "p_usb_w", "v_gen_v", "frenagem_pct",
    "tarifa_rs_kwh", "posto", "demanda_w", "comando", "hora_sim",
    "ciclo", "e_subida_j", "e_gerada_j", "e_usb_j", "e_aux_j",
]


def posto_da_hora(hora):
    """Posto tarifário da hora do dia, como `tarifaDaHora()` do firmware."""
    if 18 <= hora < 21:
        return "ponta"
    if 17 <= hora < 18 or 21 <= hora < 22:
        return "intermediario"
    return "fora_ponta"


def _ruido(t, semente):
    """Ruído pseudoaleatório em [-1, 1], determinístico para cada instante."""
    x = np.sin((t % 604800) * 12.9898 + semente * 78.233) * 43758.5453
    return (x - np.floor(x)) * 2 - 1


def _demanda(t):
    """
    Potência pedida pela saída USB (W). O celular fica ligado em boa parte do
    dia simulado e às vezes só uma luminária de LED; varia de um dia para outro.
    """
    dia = t // DIA_SIMULADO_S
    fase = (t % DIA_SIMULADO_S) / DIA_SIMULADO_S
    sorteio = (_ruido(dia, 7) + 1) / 2
    if sorteio < 0.15:                       # dia sem nada ligado
        return 0.0
    if 0.70 <= fase < 0.95:                  # noite: celular na tomada
        return 4.5 if sorteio > 0.4 else 1.5
    if 0.35 <= fase < 0.45:                  # meio do dia: luminária de LED
        return 1.5
    return 0.0


@lru_cache(maxsize=20000)
def _comando(tarifa, nivel, demanda):
    return calcular_comando(tarifa, nivel, demanda)


def _frenagem(v):
    """PWM de frenagem (0 a 1) que segura a massa na velocidade v (m/s)."""
    return float(np.clip((V_MAX_DESCIDA - v) / (V_MAX_DESCIDA - V_FREIO_TOTAL), 0, 1))


def simular(inicio, fim, tarifas=None):
    """
    Roda a planta virtual segundo a segundo, de `inicio` a `fim` (epoch, s).

    Returns:
        DataFrame: uma linha por segundo, com as colunas de COLUNAS (sem timestamp).
    """
    tarifas = tarifas or TARIFAS_PADRAO
    n = fim - inicio + 1
    saida = {c: np.empty(n, dtype=object if c in ("estado", "posto") else float) for c in COLUNAS[1:]}

    estado, h, comando, alvo = "MANTER", 0.0, 0.0, 0.0
    ciclo, e_sub, e_gen, e_usb, e_aux = 0, 0.0, 0.0, 0.0, 0.0

    for i, t in enumerate(range(inicio, fim + 1)):
        hora = 24 * (t % DIA_SIMULADO_S) / DIA_SIMULADO_S
        posto = posto_da_hora(hora)
        tarifa = tarifas[posto]
        demanda = _demanda(t)
        nivel = 100 * h / CURSO

        # decisão fuzzy a cada 5 s, com a histerese do firmware
        if t % T_FUZZY == 0:
            comando = _comando(tarifa, round(nivel, 1), demanda)
            if comando < -10:
                alvo = velocidade_alvo(comando)
            if estado == "SUBINDO" and comando <= 10:
                estado = "PARANDO"
            elif estado == "DESCENDO" and comando >= -10:
                estado = "PARANDO"
            elif estado == "MANTER" and comando > 30 and h < CURSO:
                estado = "SUBINDO"
            elif estado == "MANTER" and comando < -30 and h > 0:
                estado = "PREP_DESCIDA"

        v = p_sub = p_gen = p_usb = v_gen = freio = 0.0
        registro = estado
        if estado == "SUBINDO":
            v = V_SUBIDA
            p_sub = MASSA * G * v / ETA_IDA * (1 + 0.03 * _ruido(t, 1))
            h = min(h + v, CURSO)
            if h >= CURSO:
                estado = "PARANDO"
        elif estado == "PREP_DESCIDA":       # alivia a lingueta antes de soltar
            h = min(h + 0.003, CURSO)
            estado = "DESCENDO"
        elif estado == "DESCENDO":
            v = -alvo * (1 + 0.04 * _ruido(t, 2))
            v_gen = -v * KE_MASSA
            p_gen = MASSA * G * -v * ETA_IDA * (1 + 0.03 * _ruido(t, 3))
            if v_gen >= V_MIN_BUCK and demanda > 0:
                p_usb = min(demanda, p_gen * ETA_BUCK)
            freio = _frenagem(-v)
            h = max(h + v, 0.0)
            if h <= 0:
                estado = "PARANDO"
        elif estado == "PARANDO":         # frenagem a 100 % até a lingueta pegar
            estado = "MANTER"
            freio = 1.0

        # energia acumulada: o ciclo conta ao fim de cada descida
        e_sub += p_sub
        e_gen += p_gen
        e_usb += p_usb
        e_aux += CONSUMO_AUX_W
        if i and saida["estado"][i - 1] == "DESCENDO" and registro != "DESCENDO":
            ciclo += 1

        saida["estado"][i] = registro
        saida["h_m"][i] = h
        saida["nivel_pct"][i] = 100 * h / CURSO
        saida["v_ms"][i] = v
        saida["p_subida_w"][i] = p_sub
        saida["p_gerada_w"][i] = p_gen
        saida["p_usb_w"][i] = p_usb
        saida["v_gen_v"][i] = v_gen
        saida["frenagem_pct"][i] = 100 * freio
        saida["tarifa_rs_kwh"][i] = tarifa
        saida["posto"][i] = POSTOS[posto]
        saida["demanda_w"][i] = demanda
        saida["comando"][i] = comando
        saida["hora_sim"][i] = hora
        saida["ciclo"][i] = ciclo
        saida["e_subida_j"][i] = e_sub
        saida["e_gerada_j"][i] = e_gen
        saida["e_usb_j"][i] = e_usb
        saida["e_aux_j"][i] = e_aux

    return pd.DataFrame(saida)


def gerar_leituras(minutos=60, intervalo_s=5, fim=None, tarifas=None):
    """
    Gera um DataFrame de leituras simuladas.

    Parameters:
        minutos (int): Tamanho da janela de tempo.
        intervalo_s (int): Intervalo entre leituras, em segundos.
        fim (datetime): Instante da última leitura (padrão: agora).
        tarifas (dict): R$/kWh por posto (chaves de TARIFAS_PADRAO).

    Returns:
        DataFrame: Uma linha por leitura, com as colunas de COLUNAS.
    """
    fim = fim or datetime.now()
    fim_epoch = int(fim.timestamp()) // intervalo_s * intervalo_s
    inicio_janela = fim_epoch - minutos * 60

    # Recomeça sempre do início de um dia simulado, um dia antes da janela:
    # nesse dia a massa sobe até o topo, e a trajetória fica igual em toda chamada.
    inicio = (inicio_janela // DIA_SIMULADO_S - 1) * DIA_SIMULADO_S
    df = simular(inicio, fim_epoch, tarifas)
    df.insert(0, "timestamp", pd.to_datetime(np.arange(inicio, fim_epoch + 1), unit="s"))

    # potências: média do intervalo, para uma descida de 34 s não sumir entre duas leituras
    for c in ("p_subida_w", "p_gerada_w", "p_usb_w"):
        df[c] = df[c].rolling(intervalo_s, min_periods=1).mean()
    df = df.iloc[inicio_janela - inicio::intervalo_s].reset_index(drop=True)
    df["timestamp"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(_fuso_local()).dt.tz_localize(None)

    # energia relativa ao início da janela, como um contador zerado ao abrir o painel
    for c in ("e_subida_j", "e_gerada_j", "e_usb_j", "e_aux_j", "ciclo"):
        df[c] = df[c] - df[c].iloc[0]
    df["ciclo"] = df["ciclo"].astype(int)
    for c, casas in (("h_m", 3), ("nivel_pct", 1), ("v_ms", 3), ("p_subida_w", 2), ("p_gerada_w", 2),
                     ("p_usb_w", 2), ("v_gen_v", 1), ("frenagem_pct", 0), ("comando", 1), ("hora_sim", 2),
                     ("e_subida_j", 1), ("e_gerada_j", 1), ("e_usb_j", 1), ("e_aux_j", 0)):
        df[c] = df[c].astype(float).round(casas)
    return df[COLUNAS]


def _fuso_local():
    return datetime.now().astimezone().tzinfo
