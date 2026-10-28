# ESTADO ATUAL DO PROJETO
Última atualização: 2026-10-28
Atualizado por: FÍSICO / ARQUITETO / DESENVOLVEDOR (consolidação do trabalho
feito fora do repositório entre 2026-10-07 e 2026-10-22)

## ✅ CONCLUÍDO
- [x] Auditoria do relatório original: 24 inconsistências, 5 críticas →
  `04_AUDITORIA/inconsistencias.md`
- [x] Premissas físicas travadas (20 kg, 1,70 m) → `01_FISICA/premissas.md`
- [x] Cálculos de energia e geração por velocidade → `01_FISICA/calculos_energia.md`
- [x] Lógica fuzzy (3 entradas, 11 regras) → `01_FISICA/algoritmos_controle.md`
- [x] Dimensionamento mecânico e escolha do motorredutor/gerador →
  `02_ARQUITETO/mecanica/dimensionamento.md`
- [x] Esquema elétrico de potência v2 (relés, frenagem, USB, trava) →
  `02_ARQUITETO/circuitos/esquema_potencia.md`
- [x] Diagrama de blocos → `02_ARQUITETO/circuitos/diagrama_blocos.md`
- [x] Pinagem do ESP32 → `03_SOFTWARE/pinagem_esp32.md`
- [x] Firmware com máquina de estados, fuzzy, proteções e planta virtual →
  `03_SOFTWARE/firmware/wokwi/sketch.ino` (testado fora do Wokwi com pinos
  simulados)
- [x] Texto do relatório revisado →
  `05_DOC_ORIGINAL/Documentacao_1_Integracao_Bateria_Gravitacional_v2.docx`
- [x] Mock do dashboard em Streamlit (ainda com grandezas de ventilador) →
  `03_SOFTWARE/dashboard/`

## 🔄 EM ANDAMENTO
- Rodar o firmware dentro do Wokwi e conferir o `diagram.json` — responsável:
  DESENVOLVEDOR — prazo: [a definir]
- Contrato de dados MQTT (`grav/*`) → `03_SOFTWARE/contrato_dados.md` —
  definido no papel, ainda não implementado no firmware — DESENVOLVEDOR

## ⏸️ BLOQUEADO
- Adaptar o dashboard às grandezas da bateria (HANDOFF-005) — bloqueado por:
  escolha entre Streamlit e Node-RED — depende de: grupo (Q-001)
- Validação experimental (HANDOFF-006) — bloqueado por: compra e montagem —
  depende de: ARQUITETO (compras) e DESENVOLVEDOR (leituras reais)

## ❌ NÃO INICIADO
- MQTT no firmware (hoje só Monitor Serial e LCD)
- Leituras reais em `lerSensores()` com `SIMULACAO 0` (HANDOFF-003)
- Desenho técnico cotado da torre (HANDOFF-007)
- Cotação e compra: motorredutor planetário 24 V 1:50, eletrônica (~R$ 670),
  estrutura e tambor na serralheria, 20 kg de anilhas ou areia
- Ensaios em 7 etapas (`01_FISICA/validacao_experimental.md`)

## ⚠️ ALERTAS
- O relatório v2 está atrás da eletrônica v2 (fala em 2 INA226, 22 Ω, eFLL,
  relé que "só comuta com corrente nula") — INC-026 e INC-027
- O relatório cita Node-RED; o repositório tem Streamlit — INC-028 / Q-001
- A tabela de tarifas do firmware não trata fins de semana, que o relatório
  diz tratar — INC-030
- O `diagram.json` foi montado sem abrir o Wokwi; fios podem aparecer soltos
  — INC-031
- Toda a eficiência (~27 %) e o Ke (0,076 V·s/rad) são estimativas até o
  ensaio

## PRÓXIMA AÇÃO RECOMENDADA
1. Decidir Q-001 (painel em Streamlit ou Node-RED) e adaptar o painel
2. Rodar o roteiro de teste no Wokwi (`03_SOFTWARE/firmware/README.md`) e
   corrigir o `diagram.json` se preciso
3. Cotar e comprar o motorredutor; fazer o ensaio de bancada do gerador
   (tensão × rotação) antes de montar a torre
