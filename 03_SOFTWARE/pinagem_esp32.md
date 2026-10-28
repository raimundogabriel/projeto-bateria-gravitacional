# PINAGEM ESP32

ESP32-WROOM-32 (DevKit V1). Fonte da verdade: constantes `PIN_*` em
`03_SOFTWARE/firmware/wokwi/sketch.ino`. Nenhum pino de boot (0, 2, 5, 12, 15)
comanda potência.

> A versão inicial desta tabela (encoder no 34/35, PWM no 25, direção no 26,
> INA219) era um exemplo e não vale.

| GPIO | Função | Periférico | Direção | Estado seguro | Notas |
|------|--------|------------|---------|---------------|-------|
| 4 | Solenoide da trava | MOSFET D4184 | OUT PWM 20 kHz | Baixo: trava engatada | Hit-and-hold 100 % 300 ms → 30 % |
| 13 | K4, sondagem da USB | Módulo de relés | OUT, ativo baixo | Alto: aberto | 1 s a cada 30 s em MANTER |
| 14 | Buzzer | Buzzer ativo | OUT | Baixo | Pulsa no boot; por isso não comanda potência (INC-015) |
| 16 | RPWM (subir) | BTS7960 | OUT PWM 20 kHz | Baixo | LEDC canal 0 |
| 17 | LPWM (descer motorizado) | BTS7960 | OUT PWM | Baixo | Só rearme e teste; LEDC canal 1 |
| 18 | R_EN + L_EN | BTS7960 | OUT | Baixo (pull-down 10 kΩ) | |
| 19 | Carga de frenagem | MOSFET D4184 | OUT PWM 5 kHz | Ver sequências | LEDC canal 2 |
| 21 | SDA | I²C | I/O | — | INA226 ×3, DS3231, LCD (via BSS138) |
| 22 | SCL | I²C | I/O | — | idem |
| 23 | K2, relé de modo (2 canais) | Módulo de relés | OUT, ativo baixo | Alto: geração | DPDT formado por 2 canais |
| 25 | Fim de curso inferior (NF) | Micro switch | IN | Alto = acionado | Pull-up 10 kΩ a 3,3 V + 100 nF |
| 26 | Fim de curso superior (NF) | Micro switch | IN | Alto = acionado | idem |
| 27 | K1, relé de corte | Módulo de relés | OUT, ativo baixo | Alto: corte aberto | |
| 32 | Encoder A | LPD3806-600BM | IN | — | Pull-up 4,7 kΩ a 3,3 V; ESP32Encoder |
| 33 | Encoder B | LPD3806-600BM | IN | — | idem |
| 34 | Estado da emergência | Divisor 10 k / 20 k do JD-VCC | IN (input-only) | Baixo = acionada | |
| 35 | (só Wokwi) potenciômetro da corrente | — | IN analógico | — | Substitui o INA226 nº 1 (0 a 5 A) |
| 39 (VN) | (só Wokwi) potenciômetro da demanda | — | IN analógico | — | Substitui o INA226 nº 3 (0 a 10 W) |

## Endereços I²C
| Endereço | Dispositivo |
|----------|-------------|
| 0x40 | INA226 nº 1, subida |
| 0x41 | INA226 nº 2, barramento gerado (A0 em VS) |
| 0x44 | INA226 nº 3, USB (A1 em VS) |
| 0x68 | DS3231 (no Wokwi: DS1307) |
| 0x27 | LCD 20×4 PCF8574 |

## Regras
- Relés do módulo real são ativos em baixo; os do Wokwi, ativos em alto. O
  firmware troca isso pela constante `RELE_LIGA`.
- Nos relés ativos em baixo, `digitalWrite(pino, HIGH)` antes de
  `pinMode(pino, OUTPUT)`.
- VCC lógico do BTS7960 em 3,3 V.
