# FILA DE HANDOFFS

## 🔴 ABERTOS (aguardando ação de outra skill)

### HANDOFF-007
- **De:** FÍSICO
- **Para:** ARQUITETO
- **O quê:** Dimensionar estrutura para massa de 500 kg, altura 3 m, 
  com fator de segurança 2. Ver `01_FISICA/premissas.md#massa`
- **Critério de pronto:** arquivo `02_ARQUITETURA/mecanica/dimensionamento.md` 
  com seção "Estrutura de sustentação" preenchida
- **Criado em:** 2026-10-07

### HANDOFF-008
- **De:** ARQUITETO
- **Para:** DESENVOLVEDOR
- **O quê:** Encoder fornece 1024 pulsos/volta, ligado nos pinos GPIO34/35.
  Precisa converter para velocidade angular usando constante do FÍSICO.
- **Critério de pronto:** função `rpm_from_encoder()` em firmware + 
  validação em `plano_testes.md`
- **Criado em:** 2026-10-07

## 🟢 FECHADOS (histórico)
### HANDOFF-001 ... [data de fechamento]