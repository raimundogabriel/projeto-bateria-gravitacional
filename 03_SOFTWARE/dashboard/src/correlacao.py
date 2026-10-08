import pandas as pd

VARIAVEIS = ["temperatura", "umidade", "luminosidade", "rssi"]
NOMES = {"temperatura": "Temperatura", "umidade": "Umidade", "luminosidade": "Luminosidade", "rssi": "Wi-Fi"}


def calcular_correlacao(df):
    """
    Calcula a matriz de correlação entre as variáveis medidas.

    Parameters:
        df (DataFrame): Leituras do ESP32.

    Returns:
        DataFrame: Matriz de correlação.
    """
    return df[VARIAVEIS].corr().rename(index=NOMES, columns=NOMES)


def descrever_correlacao(valor):
    """Traduz um coeficiente de correlação em palavras."""
    if pd.isna(valor):
        return "indefinida"
    forca = abs(valor)
    if forca >= 0.7:
        intensidade = "forte"
    elif forca >= 0.4:
        intensidade = "moderada"
    elif forca >= 0.2:
        intensidade = "fraca"
    else:
        return "praticamente nula"
    sentido = "positiva" if valor > 0 else "negativa"
    return f"{sentido} {intensidade}"
