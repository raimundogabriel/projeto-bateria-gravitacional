# HANDOFFS — MVP FABLAB

Continua a numeração de `00_MASTER/HANDOFF.md` da raiz (até HANDOFF-008).

## 🔴 ABERTOS

### HANDOFF-009
- **De:** FÍSICO
- **Para:** ARQUITETO
- **O quê:** Comprar um motorredutor 12 V 37 mm 1:90 com encoder (DEC-015),
  imprimir o tambor e fazer o ensaio 0 de
  `../01_FISICA/validacao_experimental.md`: retroaciona com 2,5 kg direto no
  tambor? K_e? R_a?
- **Critério de pronto:** linha "K_e" e "Retroaciona" preenchidas; DEC-015
  confirmada ou plano B escolhido.
- **Criado em:** 2026-10-28

### HANDOFF-010
- **De:** ARQUITETO
- **Para:** ARQUITETO (após Q-009 e Q-010)
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
- **Criado em:** 2026-10-28

## 🟢 FECHADOS

### HANDOFF-012 — fechado em 2026-10-28
- **De:** FÍSICO → **Para:** DESENVOLVEDOR
- Painel Streamlit com os parâmetros do MVP.
- Entrega: `../03_SOFTWARE/dashboard/`, cópia adaptada do painel principal
  (49 J por ciclo, rendimento ~10 %, LEDs no lugar da USB). Em vez de um
  seletor no painel principal, ficou uma cópia para não alterar o projeto
  principal.
