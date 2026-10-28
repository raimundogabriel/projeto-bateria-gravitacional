# 🔋 Painel Remoto — Bateria Gravitacional

Painel da bateria gravitacional em **Python + Streamlit** (DEC-013). Segue a
mesma organização do projeto
[Cardik](https://github.com/raimundogabriel/cardik): `dashboard.py` na raiz,
funções em `src/`, dados em `data/`, abas, cards e um sistema de lógica fuzzy.

> ⚠️ **Nenhum ESP32 está conectado.** As leituras vêm de `src/simulador.py`,
> uma planta virtual igual à do firmware (20 kg, 1,70 m, subida a 0,05 m/s,
> descida a 0,03–0,08 m/s, decisão fuzzy a cada 5 s). O **dia de tarifas é
> acelerado**: um dia inteiro passa a cada 20 minutos, porque num dia real a
> massa faz um único ciclo de cerca de 1 minuto.

---

## 📁 Estrutura do Projeto

```
dashboard/
│
├── data/
│ └── leituras_esp32.csv    # 6 horas de leituras simuladas (formato grav/estado)
│
├── src/
│ ├── simulador.py          # Planta virtual da bateria (mesma lógica do firmware)
│ ├── load_data.py          # Fonte de dados (simulador, CSV e, depois, o ESP32)
│ ├── fuzzy_bateria.py      # Fuzzy de 3 entradas e 11 regras, idêntico ao firmware
│ ├── energia.py            # Energia por descida e economia simulada
│ ├── visualizacao.py       # Funções gráficas (Altair)
│
└── dashboard.py            # Dashboard principal
```

---

## 📊 Abas do Dashboard

| Aba | O que mostra |
| --- | --- |
| **Tempo Real** | Cards de nível, velocidade, potência, saída USB e tarifa; estado da máquina de estados; gráficos de nível, potências, tarifa e comando fuzzy |
| **Histórico** | Trocas de estado com as entradas do fuzzy, tempo em cada estado, tabela das leituras e download em CSV |
| **Energia** | Descidas na janela, rendimento do ramo de potência, energia entregue à USB, economia **simulada**, consumo da eletrônica à parte, energia por descida e tensão gerada × velocidade |
| **Lógica Fuzzy** | Sliders de tarifa, nível e demanda; comando resultante; funções de pertinência; regras com grau de disparo; mapa do comando tarifa × nível |
| **Controle** | Comandos `auto`, `subir`, `descer`, `parar`, `rearmar` (simulados, `grav/comando`), tarifas (`grav/tarifas`), JSON de `grav/estado` e proteções do firmware |
| **Mini Relatório** | Texto gerado a partir das leituras da janela escolhida |

Na barra lateral: fonte de dados, janela de tempo, atualização automática e
tarifas por posto horário.

---

## 🧠 Lógica Fuzzy — Bateria

### **Entradas**
- Tarifa atual (0 a 2 R$/kWh)
- Nível de carga (0 a 100 %)
- Demanda da saída USB (0 a 10 W)

### **Saída**
- Comando de −100 (descer) a +100 (subir)

### **Exemplos de Regras Fuzzy**
- Se **tarifa** é BAIXA e **nível** é BAIXO → SUBIR
- Se **tarifa** é ALTA e **nível** é ALTO e há **demanda** → DESCER
- Se **tarifa** é ALTA e **demanda** é BAIXA → MANTER

As 11 regras e as funções de pertinência estão em
`01_FISICA/algoritmos_controle.md`. `src/fuzzy_bateria.py` é escrito em NumPy,
sem `scikit-fuzzy`, para reproduzir o firmware ponto a ponto: o comando
coincide com o de `sketch.ino` (diferença máxima de 0,0001 numa grade de
2.646 combinações).

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

O dashboard só conversa com `obter_leituras()` em `src/load_data.py`. Quando o
firmware publicar por MQTT (`03_SOFTWARE/contrato_dados.md`), implemente
`ler_esp32()` nesse arquivo devolvendo um DataFrame com as colunas de
`COLUNAS` em `src/simulador.py`:

| coluna | unidade | exemplo |
| --- | --- | --- |
| timestamp | data e hora | 2026-10-28 18:00:00 |
| estado | — | DESCENDO |
| h_m / nivel_pct | m / % | 1.234 / 72.6 |
| v_ms | m/s (positivo para cima) | -0.050 |
| p_subida_w / p_gerada_w / p_usb_w | W | 0.0 / 5.1 / 4.3 |
| v_gen_v | V | 12.4 |
| frenagem_pct | % | 18 |
| tarifa_rs_kwh / posto | R$/kWh / — | 1.40 / Ponta |
| demanda_w | W | 4.3 |
| comando | −100 a +100 | -64 |
| hora_sim | h (só no simulador) | 19.2 |
| ciclo | contagem de descidas | 12 |
| e_subida_j / e_gerada_j / e_usb_j / e_aux_j | J acumulados | 640 / 173 / 147 / 3600 |

---

✨ Autor: Gabriel Raimundo
