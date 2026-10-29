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
| 32 | Encoder A | LPD3806 no eixo do tambor (pull-up 4,7 kΩ a 3,3 V) | IN | — | = |
| 33 | Encoder B | LPD3806 no eixo do tambor (pull-up 4,7 kΩ a 3,3 V) | IN | — | = |
| 34 | Estado da emergência | Divisor 10 k / 3,3 k do 12V_POT | IN | Baixo = acionada | Divisor diferente (12 V) |

Saem: GPIO 14 (buzzer), 23 (K2) e o LCD/DS3231 do I²C.

## Endereços I²C
| Endereço | Dispositivo |
|----------|-------------|
| 0x40 | INA219 nº 1, subida |
| 0x41 | INA219 nº 2, barramento gerado (jumper A0) |

## Simulação no Wokwi
Projeto em `firmware/wokwi/`. O Wokwi tem servo, potenciômetros e chaves,
então o MVP simula melhor que o projeto principal (sem relés para inventar).
Pinos usados só na simulação:

| GPIO | Função no Wokwi | No protótipo real |
|------|-----------------|-------------------|
| 35 | Potenciômetro da corrente de subida (0 a 5 A) | INA219 nº 1 pelo I²C |
| 23 | LED verde do gerador (GEN > 2 V) | LED com 220 Ω direto no GEN, sem software |
| 14 | LED amarelo do gerador (GEN > 2,6 V) | 1× 1N4148 + LED + 220 Ω no GEN |
| 2 | LED vermelho do gerador (GEN > 3,8 V) | 3× 1N4148 + LED + 220 Ω no GEN |
