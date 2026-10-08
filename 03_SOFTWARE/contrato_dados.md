# CONTRATO DE DADOS — ESP32 ↔ Dashboard

## TÓPICOS MQTT
| Tópico | Direção | Payload | Frequência |
|--------|---------|---------|------------|
| `bg/telemetria` | ESP32→Dash | `{rpm, potencia_w, energia_j, estado}` | 2 Hz |
| `bg/comando` | Dash→ESP32 | `{acao: "start"/"stop"/"setpoint", valor}` | on-demand |
| `bg/alerta` | ESP32→Dash | `{nivel, codigo, msg}` | evento |

## SCHEMA JSON (telemetria)
```json
{
  "ts": 1730000000,
  "rpm": 145.3,
  "potencia_w": 87.2,
  "energia_j": 12450,
  "estado": "descendo",
  "alertas": []
}