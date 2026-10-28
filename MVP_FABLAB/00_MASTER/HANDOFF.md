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
  (constantes, `modoPonte()`, servo, 2× INA219, NTP, MQTT), com projeto
  Wokwi próprio.
- **Critério de pronto:** subir, descer, manter, falha e automático
  conferidos no Wokwi; código em `../03_SOFTWARE/firmware/`.
- **Criado em:** 2026-10-28

### HANDOFF-012
- **De:** FÍSICO
- **Para:** DESENVOLVEDOR
- **O quê:** Seletor "Projeto principal / MVP fablab" no painel Streamlit com
  os parâmetros de `../01_FISICA/premissas.md`.
- **Critério de pronto:** simulador do MVP mostra 49 J por ciclo e
  η_ciclo ~0,10.
- **Criado em:** 2026-10-28
