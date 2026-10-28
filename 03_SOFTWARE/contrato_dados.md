# CONTRATO DE DADOS — ESP32 ↔ Dashboard

Status: **definido, ainda não implementado**. O firmware atual só escreve no
Monitor Serial e no LCD; MQTT é a próxima entrega do DESENVOLVEDOR. Os tópicos
seguem o relatório revisado (seção 6). A versão inicial deste arquivo usava
`bg/*` e campos de exemplo (`rpm`, 87 W); foi substituída.

Unidades: SI no payload (m, m/s, W, J, V, A); conversões (Wh, R$) só no
painel. Timestamp em segundos Unix, do RTC.

## TÓPICOS MQTT
| Tópico | Direção | Payload | Frequência |
|--------|---------|---------|------------|
| `grav/estado` | ESP32 → Painel | estado completo (abaixo) | 30 s e a cada troca de estado |
| `grav/acao` | ESP32 → Painel | decisão fuzzy ou manual | a cada decisão que muda a ação |
| `grav/energia` | ESP32 → Painel | energia do ciclo | 30 s e ao fim de cada subida/descida |
| `grav/alerta` | ESP32 → Painel | falha ou emergência | evento |
| `grav/comando` | Painel → ESP32 | `auto`, `subir`, `descer`, `parar`, `rearmar` | on-demand |
| `grav/tarifas` | Painel → ESP32 | valores por posto horário | on-demand (retido) |

## SCHEMA JSON

### `grav/estado`
```json
{
  "ts": 1793190000,
  "estado": "DESCENDO",
  "modo": "AUTOMATICO",
  "h_m": 1.234,
  "nivel_pct": 72.6,
  "v_ms": -0.050,
  "p_subida_w": 0.0,
  "p_gerada_w": 5.1,
  "p_usb_w": 4.3,
  "v_gen_v": 12.4,
  "frenagem_pct": 18,
  "tarifa_rs_kwh": 1.40,
  "posto": "ponta",
  "demanda_w": 4.3
}
```
`estado`: `MANTER`, `SUBINDO`, `PREP_DESCIDA`, `DESCENDO`, `PARANDO`, `FALHA`,
`REARME`. `modo`: `AUTOMATICO` ou `MANUAL`. `v_ms` positivo para cima.

### `grav/acao`
```json
{
  "ts": 1793190000,
  "origem": "fuzzy",
  "comando": -64,
  "acao": "descer",
  "v_alvo_ms": 0.058,
  "entradas": { "tarifa_rs_kwh": 1.40, "nivel_pct": 98.0, "demanda_w": 4.3 }
}
```
`origem`: `fuzzy` ou `manual`. `acao`: `subir`, `manter`, `descer`.

### `grav/energia`
```json
{
  "ts": 1793190000,
  "ciclo": 12,
  "e_subida_j": 640.0,
  "e_gerada_j": 173.0,
  "e_usb_j": 147.0,
  "e_aux_j": 3600.0,
  "tarifa_subida_rs_kwh": 0.60,
  "tarifa_descida_rs_kwh": 1.40
}
```
O painel calcula a economia **simulada** (HANDOFF-004):
`economia = e_gerada_j/3,6e6 × tarifa_descida − e_subida_j/3,6e6 × tarifa_subida`.
`e_aux_j` (consumo da eletrônica) é mostrado à parte, nunca somado ao
rendimento do ramo de potência.

### `grav/alerta`
```json
{ "ts": 1793190000, "nivel": "falha", "codigo": "VEL_MAX", "msg": "descida acima de 0,10 m/s" }
```
Códigos: `VEL_MAX`, `GEN_SOBRETENSAO`, `MASSA_TRAVADA`, `FIM_CURSO`,
`EMERGENCIA`, `TRAVA_PRESA`.

### `grav/comando`
```json
{ "acao": "descer" }
```
`acao`: `auto`, `subir`, `descer`, `parar`, `rearmar`. Equivalem aos comandos
seriais `a`, `s`, `d`, `p`, `r` do firmware.

### `grav/tarifas`
```json
{ "fora_ponta": 0.60, "intermediario": 0.90, "ponta": 1.40 }
```
Valores de exemplo; os reais vêm da concessionária (Q-003).

## CSV do simulador do painel
Enquanto o ESP32 não publica, o simulador do painel deve gerar as mesmas
colunas de `grav/estado` (uma linha por leitura), para que trocar a fonte não
mude o resto do painel.
