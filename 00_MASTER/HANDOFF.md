# FILA DE HANDOFFS

> A versão inicial trazia HANDOFF-007 (estrutura para 500 kg e 3 m) e
> HANDOFF-008 (encoder 1024 pulsos no GPIO 34/35). Os dois eram exemplos do
> modelo e não valem: a massa é 20 kg (DEC-001) e o encoder tem 600 pulsos no
> GPIO 32/33 (`03_SOFTWARE/pinagem_esp32.md`).

## 🔴 ABERTOS (aguardando ação de outra skill)

> HANDOFF-009 a HANDOFF-013 são da variante MVP para fablab:
> `MVP_FABLAB/00_MASTER/HANDOFF.md`.

### HANDOFF-003
- **De:** ARQUITETO
- **Para:** DESENVOLVEDOR
- **O quê:** Completar `lerSensores()` do firmware para o hardware real
  (`SIMULACAO 0`): 3× INA226 (0x40 subida, 0x41 gerado, 0x44 USB, shunt
  10 mΩ), encoder com a biblioteca ESP32Encoder (o curso dá ~43.300 contagens,
  acima dos 16 bits do PCNT) e DS3231. Ver
  `02_ARQUITETO/circuitos/esquema_potencia.md`.
- **Critério de pronto:** varredura I²C acha 0x40, 0x41, 0x44, 0x68 e 0x27;
  ~2.400 pulsos por volta do tambor; etapa 1 de
  `01_FISICA/validacao_experimental.md` aprovada.
- **Criado em:** 2026-10-28

### HANDOFF-004
- **De:** FÍSICO
- **Para:** DESENVOLVEDOR
- **O quê:** Publicar e mostrar no painel a energia por ciclo separada em:
  consumida na subida, gerada, entregue à USB e consumo auxiliar da
  eletrônica (à parte). Economia simulada = E_gerada × tarifa da descida −
  E_consumida × tarifa da subida, rotulada "simulada". Ver
  `03_SOFTWARE/contrato_dados.md`.
- **Critério de pronto:** firmware publica `grav/energia` e o painel mostra os
  quatro valores e a economia simulada.
- **Andamento:** lado do painel pronto em 2026-10-28 (aba Energia, com dados
  do simulador); falta o firmware publicar.
- **Criado em:** 2026-10-28

### HANDOFF-006
- **De:** DESENVOLVEDOR
- **Para:** FÍSICO
- **O quê:** Entregar os dados dos ensaios (tensão gerada × velocidade, energia
  de subida e de descida, corrente do solenoide em 100 % e 30 %, velocidade
  com frenagem a 100 %) para validar Ke, η_ciclo e refazer o Quadro 5 com
  valores medidos.
- **Critério de pronto:** CSV dos ensaios em `01_FISICA/` e tabela
  preenchida em `01_FISICA/validacao_experimental.md`.
- **Criado em:** 2026-10-28 (bloqueado: protótipo ainda não montado)

### HANDOFF-007
- **De:** AUDITORIA (INC-017, INC-023)
- **Para:** ARQUITETO
- **O quê:** Desenho técnico cotado da torre: posição real dos fins de curso,
  ~2 cm de folga acima do superior, altura do carrinho, tambor e polias dentro
  dos 2,10 m (INC-017, INC-023).
- **Critério de pronto:** desenho em `02_ARQUITETO/mecanica/` referenciado em
  `dimensionamento.md`.
- **Criado em:** 2026-10-28

### HANDOFF-008
- **De:** ARQUITETO
- **Para:** DESENVOLVEDOR
- **O quê:** Ao rodar o firmware no Wokwi, conferir se cada sequência acende
  os LEDs como descrito em `02_ARQUITETO/circuitos/simulacao_wokwi.md` (seção
  5) e corrigir os nomes de pinos do `diagram.json` (INC-031).
- **Critério de pronto:** subir, descer, manter, falha e automático conferidos
  no Wokwi; INC-031 fechada.
- **Criado em:** 2026-10-28

## 🟢 FECHADOS (histórico)

### HANDOFF-005 — fechado em 2026-10-28
- **De:** FÍSICO → **Para:** DESENVOLVEDOR
- Trocar o mock de ventilador do painel pelas grandezas da bateria e pelo fuzzy
  de 3 entradas (DEC-013).
- Entrega: `03_SOFTWARE/dashboard/` com simulador no formato de
  `grav/estado`; o envio real de `grav/comando` depende do MQTT (HANDOFF-004).

### HANDOFF-001 — fechado em 2026-10-07
- **De:** FÍSICO → **Para:** ARQUITETO
- Dimensionar estrutura, motor e trava para 20 kg e 1,70 m.
- Entrega: `02_ARQUITETO/mecanica/dimensionamento.md` (DEC-003, DEC-005,
  DEC-012).

### HANDOFF-002 — fechado em 2026-10-22
- **De:** ARQUITETO → **Para:** DESENVOLVEDOR
- Pinagem, sequências de operação e proteções para o firmware.
- Entrega: `03_SOFTWARE/pinagem_esp32.md` e
  `03_SOFTWARE/firmware/wokwi/sketch.ino`.
