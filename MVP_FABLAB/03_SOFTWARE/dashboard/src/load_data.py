"""
Camada de dados do dashboard.

O dashboard só conversa com `obter_leituras()`. Hoje ela devolve dados
simulados ou um CSV de exemplo; quando o ESP32 publicar em `grav/estado`
(ver `03_SOFTWARE/contrato_dados.md`), basta implementar `ler_esp32()` — o
resto do dashboard não muda.
"""
import pandas as pd

from src.simulador import COLUNAS, gerar_leituras

FONTE_SIMULADOR = "Simulador (tempo real)"
FONTE_CSV = "CSV de exemplo"
FONTES = [FONTE_SIMULADOR, FONTE_CSV]

# janela -> (minutos, intervalo entre leituras em segundos)
JANELAS = {
    "15 minutos": (15, 2),
    "1 hora": (60, 5),
    "6 horas": (360, 30),
    "24 horas": (1440, 120),
}


def carregar_csv(path="data/leituras_esp32.csv"):
    """
    Carrega um arquivo CSV com leituras do ESP32.

    Parameters:
        path (str): Caminho do arquivo CSV.

    Returns:
        DataFrame: Leituras carregadas em um Pandas DataFrame.
    """
    try:
        df = pd.read_csv(path, parse_dates=["timestamp"])
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado no caminho: {path}")
    return df[COLUNAS]


def ler_esp32(minutos):
    """
    TODO: ler as leituras reais do ESP32.

    O ESP32 publica `grav/estado` (30 s e a cada troca de estado) e
    `grav/energia` por MQTT. Um coletor (por exemplo, paho-mqtt) assina os
    tópicos e grava cada mensagem em CSV ou SQLite; aqui lemos a janela pedida.

    Deve devolver um DataFrame com as mesmas colunas de `COLUNAS`.
    """
    raise NotImplementedError("Conexão com o ESP32 ainda não implementada.")


def obter_leituras(fonte=FONTE_SIMULADOR, janela="1 hora", tarifas=None):
    """
    Devolve as leituras da janela escolhida, da mais antiga para a mais nova.

    Parameters:
        fonte (str): Uma das opções de FONTES.
        janela (str): Uma das chaves de JANELAS.
        tarifas (dict): R$/kWh por posto, usado pelo simulador.

    Returns:
        DataFrame: Leituras com as colunas de COLUNAS.
    """
    minutos, intervalo_s = JANELAS[janela]

    if fonte == FONTE_CSV:
        df = carregar_csv()
        inicio = df["timestamp"].max() - pd.Timedelta(minutes=minutos)
        return df[df["timestamp"] >= inicio].reset_index(drop=True)

    return gerar_leituras(minutos=minutos, intervalo_s=intervalo_s, tarifas=tarifas)
