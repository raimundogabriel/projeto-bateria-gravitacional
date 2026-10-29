# HANDOFFS — MVP FABLAB

Continua a numeração de `00_MASTER/HANDOFF.md` da raiz (até HANDOFF-008).

## 🔴 ABERTOS

### HANDOFF-009
- **De:** FÍSICO
- **Para:** ARQUITETO
- **O quê:** Preparar a parafusadeira GSR 1440-LI (DEC-026: sem bateria,
  sem gatilho, sem a trava Auto-Lock, 1ª marcha), imprimir o tambor de
  Ø 30 mm e fazer o ensaio 0 de `../01_FISICA/validacao_experimental.md`:
  desce sozinha com 6 kg direto no tambor? Redução i? K_e? R_a? I_0?
- **Critério de pronto:** linhas "i", "K_e", "R_a", "I_0" e "Retroaciona"
  preenchidas; DEC-025 e DEC-026 confirmadas, ou tambor Ø 35 mm / mais
  massa escolhidos. Com os números medidos, o DESENVOLVEDOR troca
  `KE_MASSA`, `PWM_SUBIDA` e as constantes da planta virtual.
- **Criado em:** 2026-10-28

### HANDOFF-010
- **De:** ARQUITETO
- **Para:** ARQUITETO (após Q-010)
- **O quê:** Desenho cotado da torre e arquivos de fabricação: DXF da base,
  topo, carrinho e caixa; STL do tambor com catraca, polia, lingueta,
  mancal e suportes dos fins de curso.
- **Critério de pronto:** arquivos em `../02_ARQUITETO/fabricacao/`
  referenciados em `mecanica.md`.
- **Criado em:** 2026-10-28

### HANDOFF-011
- **De:** ARQUITETO
- **Para:** DESENVOLVEDOR
- **O quê:** Firmware do MVP conforme `../03_SOFTWARE/adaptacao_firmware.md`
  (constantes, ponte de 4 modos, servo, NTP), com projeto Wokwi próprio.
- **Critério de pronto:** subir, descer, manter, falha e automático
  conferidos no Wokwi; código em `../03_SOFTWARE/firmware/`.
- **Andamento:** código e `diagram.json` prontos em 2026-10-28, testados fora
  do Wokwi com pinos simulados; falta rodar dentro do Wokwi.
- **Criado em:** 2026-10-28

### HANDOFF-013
- **De:** DESENVOLVEDOR
- **Para:** DESENVOLVEDOR
- **O quê:** MQTT no firmware do MVP (`grav/estado`, `grav/energia`,
  `grav/comando` com `w` de demanda) e coletor em `ler_esp32()` do painel.
  Depende de Q-006 (onde roda o broker).
- **Critério de pronto:** o painel mostra o Wokwi ou o protótipo ao vivo.
- **Andamento:** código pronto em 2026-10-29 (DEC-023): o firmware publica
  `grav/estado` a cada 1 s e recebe `grav/comando` e `grav/tarifas`; com
  `SIMULACAO 0` lê os 2 INA219 e o encoder pelo PCNT. O painel ganhou a fonte
  “ESP32 (MQTT)” (`src/mqtt_esp32.py`) e comandos de verdade. Passo a passo
  em `../DIY/`. Testado fora do hardware (firmware com MQTT simulado; painel
  contra broker local com mensagens do firmware). Falta ver ao vivo num
  ESP32 ou no Wokwi.
- **Criado em:** 2026-10-28

## 🟢 FECHADOS

### HANDOFF-012 — fechado em 2026-10-28
- **De:** FÍSICO → **Para:** DESENVOLVEDOR
- Painel Streamlit com os parâmetros do MVP.
- Entrega: `../03_SOFTWARE/dashboard/`, cópia adaptada do painel principal
  (49 J por ciclo na época, 100 J com o porte de 2026-10-29; rendimento
  ~10 %, LEDs no lugar da USB). Em vez de um
  seletor no painel principal, ficou uma cópia para não alterar o projeto
  principal.
