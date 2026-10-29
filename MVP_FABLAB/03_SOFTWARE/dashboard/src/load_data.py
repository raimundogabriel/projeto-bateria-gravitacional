"""
Camada de dados do dashboard.

O dashboard só conversa com `obter_leituras()`. Ela devolve dados
simulados, um CSV de exemplo ou as leituras que o ESP32 publica por MQTT em
`<base>/estado` (coletor em `src/mqtt_esp32.py`, passo a passo em
`MVP_FABLAB/DIY/`). As três fontes têm as mesmas colunas, então o resto do
dashboard não muda.
"""
import pandas as pd

from src.simulador import COLUNAS, gerar_leituras

FONTE_SIMULADOR = "Simulador (tempo real)"
FONTE_ESP32 = "ESP32 (MQTT)"
FONTE_CSV = "CSV de exemplo"
FONTES = [FONTE_SIMULADOR, FONTE_ESP32, FONTE_CSV]

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


def ler_esp32(minutos, coletor):
    """
    Leituras do ESP32 recebidas pelo coletor MQTT na janela pedida.

    Parameters:
        minutos (int): Tamanho da janela de tempo.
        coletor (ColetorESP32): Coletor conectado ao broker.

    Returns:
        DataFrame: Leituras com as colunas de COLUNAS (vazio até o ESP32 publicar).
    """
    if coletor is None:
        return pd.DataFrame(columns=COLUNAS)
    return coletor.dataframe(minutos)


def obter_leituras(fonte=FONTE_SIMULADOR, janela="1 hora", tarifas=None, coletor=None):
    """
    Devolve as leituras da janela escolhida, da mais antiga para a mais nova.

    Parameters:
        fonte (str): Uma das opções de FONTES.
        janela (str): Uma das chaves de JANELAS.
        tarifas (dict): R$/kWh por posto, usado pelo simulador.
        coletor (ColetorESP32): Usado só com a fonte FONTE_ESP32.

    Returns:
        DataFrame: Leituras com as colunas de COLUNAS.
    """
    minutos, intervalo_s = JANELAS[janela]

    if fonte == FONTE_ESP32:
        return ler_esp32(minutos, coletor)

    if fonte == FONTE_CSV:
        df = carregar_csv()
        inicio = df["timestamp"].max() - pd.Timedelta(minutes=minutos)
        return df[df["timestamp"] >= inicio].reset_index(drop=True)

    return gerar_leituras(minutos=minutos, intervalo_s=intervalo_s, tarifas=tarifas)
