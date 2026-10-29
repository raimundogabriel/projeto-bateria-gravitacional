# 🔋 Painel Remoto — Bateria Gravitacional (MVP fablab)

Cópia do painel do projeto principal (`03_SOFTWARE/dashboard/`) adaptada ao
MVP: 6 kg de anilhas, 1,70 m, motorredutor 12 V 1:90 e LEDs de nível no lugar da saída
USB. A estrutura, as abas e o fuzzy são os mesmos.

Painel da bateria gravitacional em **Python + Streamlit** (DEC-013). Segue a
mesma organização do projeto
[Cardik](https://github.com/raimundogabriel/cardik): `dashboard.py` na raiz,
funções em `src/`, dados em `data/`, abas, cards e um sistema de lógica fuzzy.

Três fontes de dados na barra lateral: **Simulador**, **ESP32 (MQTT)** e
**CSV de exemplo**. Para ligar o ESP32, siga `MVP_FABLAB/DIY/`.

> ℹ️ No **Simulador**, as leituras vêm de `src/simulador.py`,
> uma planta virtual igual à do firmware do MVP (6 kg, 1,70 m, subida a
> 0,03 m/s, descida a 0,02–0,05 m/s, decisão fuzzy a cada 5 s). O **dia de
> tarifas é acelerado**: um dia inteiro passa a cada 20 minutos, porque num
> dia real a massa faz um único ciclo de cerca de 1,5 minuto.

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
│ ├── load_data.py          # Fonte de dados (simulador, ESP32 por MQTT ou CSV)
│ ├── mqtt_esp32.py         # Coletor MQTT: assina grav/estado, publica grav/comando e grav/tarifas
│ ├── fuzzy_bateria.py      # Fuzzy de 3 entradas e 11 regras, idêntico ao firmware (alvo 0,02–0,05 m/s)
│ ├── energia.py            # Energia por descida e economia simulada
│ ├── visualizacao.py       # Funções gráficas (Altair)
│
└── dashboard.py            # Dashboard principal
```

---

## 📊 Abas do Dashboard

| Aba | O que mostra |
| --- | --- |
| **Tempo Real** | Cards de nível, velocidade, potência, LEDs de nível e tarifa; estado da máquina de estados; gráficos de nível, potências, tarifa e comando fuzzy |
| **Histórico** | Trocas de estado com as entradas do fuzzy, tempo em cada estado, tabela das leituras e download em CSV |
| **Energia** | Descidas na janela, rendimento do ramo de potência (~10 %), energia nos LEDs, economia **simulada**, consumo da eletrônica à parte, energia por descida e tensão gerada × velocidade |
| **Lógica Fuzzy** | Sliders de tarifa, nível e demanda; comando resultante; funções de pertinência; regras com grau de disparo; mapa do comando tarifa × nível |
| **Controle** | Comandos `auto`, `subir`, `descer`, `parar`, `rearmar`, demanda e hora de teste (`grav/comando`; simulados nas outras fontes), tarifas (`grav/tarifas`), JSON de `grav/estado` e proteções do firmware |
| **Mini Relatório** | Texto gerado a partir das leituras da janela escolhida |

Na barra lateral: fonte de dados, janela de tempo, atualização automática e
tarifas por posto horário.

---

## 🧠 Lógica Fuzzy — Bateria

### **Entradas**
- Tarifa atual (0 a 2 R$/kWh)
- Nível de carga (0 a 100 %)
- Demanda da saída (0 a 10 W): chave de demanda (5 W) ou pedido do painel

### **Saída**
- Comando de −100 (descer) a +100 (subir)

### **Exemplos de Regras Fuzzy**
- Se **tarifa** é BAIXA e **nível** é BAIXO → SUBIR
- Se **tarifa** é ALTA e **nível** é ALTO e há **demanda** → DESCER
- Se **tarifa** é ALTA e **demanda** é BAIXA → MANTER

No MVP muda só a velocidade-alvo da descida: 0,02 a 0,05 m/s.

As 11 regras e as funções de pertinência estão em
`01_FISICA/algoritmos_controle.md`. `src/fuzzy_bateria.py` é escrito em NumPy,
sem `scikit-fuzzy`, para reproduzir o firmware ponto a ponto. O fuzzy do MVP
é o mesmo do principal, que coincide com o de `sketch.ino` (diferença máxima
de 0,0001 numa grade de 2.646 combinações).

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

Passo a passo completo (Mosquitto, firewall, IP, sketch) em
`MVP_FABLAB/DIY/03_painel_mqtt.md`. Resumo: com o Mosquitto rodando no mesmo
computador, escolha a fonte **ESP32 (MQTT)**, endereço `localhost`, porta
`1883` e tópico base `grav` (igual a `TOPICO_BASE` no sketch).

`src/mqtt_esp32.py` guarda as leituras em memória enquanto o painel está
aberto (até 24 h). As três fontes devolvem as colunas de `COLUNAS` em
`src/simulador.py`, então o resto do painel não muda:

| coluna | unidade | exemplo |
| --- | --- | --- |
| timestamp | data e hora | 2026-10-28 18:00:00 |
| estado | — | DESCENDO |
| h_m / nivel_pct | m / % | 1.234 / 72.6 |
| v_ms | m/s (positivo para cima) | -0.050 |
| p_subida_w / p_gerada_w / p_leds_w | W | 0.0 / 0.87 / 0.15 |
| v_gen_v | V | 10.7 |
| frenagem_pct | % | 18 |
| tarifa_rs_kwh / posto | R$/kWh / — | 1.40 / Ponta |
| demanda_w | W | 5.0 |
| comando | −100 a +100 | -64 |
| hora_sim | h (hora simulada; no ESP32, a hora do NTP ou forçada) | 19.2 |
| ciclo | contagem de descidas | 12 |
| e_subida_j / e_gerada_j / e_leds_j / e_aux_j | J acumulados | 300 / 29.7 / 2.2 / 2880 |

`p_leds_w` e `e_leds_j` substituem `p_usb_w` e `e_usb_j` do projeto principal:
o MVP não tem saída USB (DEC-014).

---

✨ Autor: Gabriel Raimundo
