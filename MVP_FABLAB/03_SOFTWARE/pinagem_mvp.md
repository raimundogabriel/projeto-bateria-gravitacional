# PINAGEM ESP32 — MVP FABLAB

ESP32-WROOM-32 (DevKit V1). Nenhum pino de boot (0, 2, 5, 12, 15) comanda
potência. Onde a função existe no projeto principal, o GPIO foi mantido.

| GPIO | Função | Periférico | Direção | Estado seguro | Mudou? |
|------|--------|------------|---------|---------------|--------|
| 4 | Servo da lingueta | MG90S | OUT 50 Hz (LEDC canal 3) | Ângulo ENGATADA | Era o solenoide |
| 13 | L_EN (meia-ponte do M−) | BTS7960 | OUT | Baixo (pull-down 10 kΩ) | Era K4 |
| 16 | RPWM (subir) | BTS7960 | OUT PWM 20 kHz | Baixo | = |
| 17 | LPWM (descer motorizado) | BTS7960 | OUT PWM | Baixo | = (só rearme e teste) |
| 18 | R_EN (meia-ponte do M+) | BTS7960 | OUT | Baixo (pull-down 10 kΩ) | Era R_EN + L_EN juntos |
| 19 | Carga de frenagem | MOSFET D4184 | OUT PWM 5 kHz | Alto (100 %) em falha | = |
| 21 | SDA | I²C | I/O | — | Só 2× INA219 |
| 22 | SCL | I²C | I/O | — | = |
| 25 | Fim de curso inferior (NF) | Micro switch | IN | Alto = acionado | = |
| 26 | Fim de curso superior (NF) | Micro switch | IN | Alto = acionado | = |
| 27 | Chave de demanda | Chave alavanca ao GND | IN_PULLUP | Baixo = há demanda | Era K1 |
| 32 | Encoder A | Hall do motor | IN | — | = |
| 33 | Encoder B | Hall do motor | IN | — | = |
| 34 | Estado da emergência | Divisor 10 k / 3,3 k do 12V_POT | IN | Baixo = acionada | Divisor diferente (12 V) |

Saem: GPIO 14 (buzzer), 23 (K2) e o LCD/DS3231 do I²C.

## Endereços I²C
| Endereço | Dispositivo |
|----------|-------------|
| 0x40 | INA219 nº 1, subida |
| 0x41 | INA219 nº 2, barramento gerado (jumper A0) |

## Simulação no Wokwi
O Wokwi tem servo, potenciômetros e chaves, então o MVP simula melhor que o
projeto principal (sem relés para inventar). INA219 continua sendo trocado
por potenciômetros, como hoje.
