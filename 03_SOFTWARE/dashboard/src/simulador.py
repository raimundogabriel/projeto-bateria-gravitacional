"""
Simulador de leituras do ESP32.

Enquanto o hardware não está pronto, este módulo gera leituras "falsas" mas
realistas. As leituras são uma função determinística do horário: chamar o
simulador duas vezes para o mesmo instante devolve o mesmo valor, então o
histórico não "pula" a cada atualização do dashboard.
"""
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

COLUNAS = [
    "timestamp", "temperatura", "umidade", "luminosidade",
    "rssi", "heap_livre", "uptime_s",
]


def _ruido(t, semente):
    """Ruído pseudoaleatório em [-1, 1], determinístico para cada instante."""
    x = np.sin((t % 604800) * 12.9898 + semente * 78.233) * 43758.5453
    return (x - np.floor(x)) * 2 - 1


def _deriva(t, semente):
    """Variação lenta e suave (soma de ondas com períodos diferentes)."""
    p = 1 + 0.11 * semente  # cada grandeza oscila em um ritmo próprio
    return (
        np.sin(2 * np.pi * t / (420 * p) + semente)
        + 0.6 * np.sin(2 * np.pi * t / (1380 * p) + 2 * semente)
        + 0.4 * np.sin(2 * np.pi * t / (3660 * p) + 3 * semente)
    ) / 2


def gerar_leituras(minutos=60, intervalo_s=5, fim=None):
    """
    Gera um DataFrame de leituras simuladas.

    Parameters:
        minutos (int): Tamanho da janela de tempo.
        intervalo_s (int): Intervalo entre leituras, em segundos.
        fim (datetime): Instante da última leitura (padrão: agora).

    Returns:
        DataFrame: Uma linha por leitura, com as colunas de COLUNAS.
    """
    fim = fim or datetime.now()
    fim_epoch = int(fim.timestamp()) // intervalo_s * intervalo_s
    n = int(minutos * 60 / intervalo_s) + 1
    t = fim_epoch - np.arange(n - 1, -1, -1) * intervalo_s

    inicio = datetime.fromtimestamp(fim_epoch) - timedelta(seconds=(n - 1) * intervalo_s)
    timestamps = pd.date_range(inicio, periods=n, freq=f"{intervalo_s}s")
    hora = (timestamps.hour + timestamps.minute / 60 + timestamps.second / 3600).to_numpy()

    # Temperatura: ciclo diário (pico no meio da tarde) + deriva + ruído do sensor
    temperatura = (
        26 + 4.5 * np.sin(2 * np.pi * (hora - 9) / 24)
        + 1.2 * _deriva(t, 1.0) + 0.15 * _ruido(t, 1)
    )

    # Umidade: cai quando a temperatura sobe
    umidade = 62 - 2.4 * (temperatura - 26) + 4 * _deriva(t, 2.3) + 0.6 * _ruido(t, 2)
    umidade = np.clip(umidade, 20, 98)

    # Luminosidade: curva do sol entre 6h e 18h, com "nuvens"
    sol = np.clip(np.sin(np.pi * (hora - 6) / 12), 0, None)
    nuvens = 0.8 + 0.2 * _deriva(t, 4.1)
    luminosidade = np.clip(900 * sol * nuvens + 12 + 3 * _deriva(t, 3.4) + (0.3 + 8 * sol) * _ruido(t, 3), 0, None)

    # Saúde do dispositivo
    rssi = -58 + 6 * _deriva(t, 5.7) + 1.5 * _ruido(t, 4)
    uptime_s = t % (3 * 86400) + 600
    heap_livre = 184 - 8 * ((uptime_s % 3600) / 3600) + 1.5 * _ruido(t, 5)

    return pd.DataFrame({
        "timestamp": timestamps,
        "temperatura": np.round(temperatura, 1),
        "umidade": np.round(umidade, 1),
        "luminosidade": np.round(luminosidade, 1),
        "rssi": np.round(rssi, 0).astype(int),
        "heap_livre": np.round(heap_livre, 1),
        "uptime_s": uptime_s.astype(int),
    })[COLUNAS]
