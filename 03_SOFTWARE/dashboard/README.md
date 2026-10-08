# 📡 Dashboard de Monitoramento — ESP32 (mockup)

Mockup de um **dashboard interativo** para um projeto com ESP32, feito em
**Python + Streamlit**. Segue a mesma organização do projeto
[Cardik](https://github.com/raimundogabriel/cardik): `dashboard.py` na raiz,
funções em `src/`, dados em `data/`, abas, cards e um sistema de lógica fuzzy.

> ⚠️ **Nenhum ESP32 está conectado.** Todas as leituras são simuladas em
> `src/simulador.py`. O objetivo é validar o layout antes de ligar o hardware.

---

## 📁 Estrutura do Projeto

```
esp32-dashboard/
│
├── data/
│ └── leituras_esp32.csv    # 6 horas de leituras de exemplo
│
├── src/
│ ├── simulador.py          # Gera leituras falsas do ESP32
│ ├── load_data.py          # Fonte de dados (simulador, CSV e, depois, o ESP32)
│ ├── correlacao.py         # Cálculo de correlação
│ ├── visualizacao.py       # Funções gráficas (Altair)
│ ├── fuzzy_ventilador.py   # Sistema fuzzy completo
│
└── dashboard.py            # Dashboard principal
```

---

## 📊 Abas do Dashboard

| Aba | O que mostra |
| --- | --- |
| **Tempo Real** | Cards com a última leitura, estado do ambiente (🟢 🟡 🔴) e gráficos que se atualizam sozinhos |
| **Histórico** | Resumo estatístico, distribuição das variáveis, tabela das leituras e download em CSV |
| **Correlação** | Mapa de calor e dispersão temperatura × umidade |
| **Lógica Fuzzy** | Sliders para testar o controle fuzzy do ventilador, com as funções de pertinência |
| **Dispositivo** | Wi-Fi, memória livre, uptime, controles simulados e o formato JSON da leitura |
| **Mini Relatório** | Texto gerado a partir das leituras da janela escolhida |

Na barra lateral: fonte de dados, janela de tempo, atualização automática e limites de alerta.

---

## 🧠 Lógica Fuzzy – Ventilador

### **Entradas**
- Temperatura (°C)
- Umidade (%)

### **Saída**
- Velocidade do ventilador (0 a 100 % de PWM)

### **Exemplos de Regras Fuzzy**
- Se **temperatura** é QUENTE e **umidade** é ÚMIDA → ventilação é ALTA
- Se **temperatura** é AGRADÁVEL e **umidade** é ÚMIDA → ventilação é MÉDIA
- Se **temperatura** é FRIA → ventilação é BAIXA

Implementado com `scikit-fuzzy`, em `src/fuzzy_ventilador.py`.

---

## 🚀 Como Executar

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
streamlit run dashboard.py
```

---

## 🔌 Ligando o ESP32 de verdade

O dashboard só conversa com `obter_leituras()` em `src/load_data.py`. Para usar
o hardware, implemente `ler_esp32()` nesse arquivo devolvendo um DataFrame com
estas colunas:

| coluna | unidade | exemplo |
| --- | --- | --- |
| timestamp | data e hora | 2026-10-08 18:00:00 |
| temperatura | °C | 29.3 |
| umidade | % | 57.9 |
| luminosidade | lux | 14.0 |
| rssi | dBm | -60 |
| heap_livre | kB | 183.0 |
| uptime_s | segundos | 162600 |

Para trocar as grandezas (outros sensores), ajuste `COLUNAS` em
`src/simulador.py` e `GRANDEZAS` em `dashboard.py`.

---

✨ Autor: Gabriel Raimundo
