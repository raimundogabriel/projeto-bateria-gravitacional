# Firmware ESP32 — MVP fablab

Mesma estrutura do firmware do projeto principal
(`03_SOFTWARE/firmware/wokwi/sketch.ino`): mesma máquina de estados, mesmo
fuzzy (3 entradas, 11 regras), mesmas proteções, mesma flag `SIMULACAO` e os
mesmos comandos pelo Monitor Serial. Muda o que o MVP muda (ver
`../adaptacao_firmware.md`).

| Arquivo | O que é |
|---------|---------|
| `wokwi/sketch.ino` | Firmware do MVP (ESP32). Mesma pinagem do circuito real (`../pinagem_mvp.md`) |
| `wokwi/diagram.json` | Circuito do Wokwi: ESP32 DevKit V1, servo, LEDs do IBT-2 e do barramento gerado, chaves, potenciômetro, KY-040 |
| `wokwi/libraries.txt` | Nenhuma biblioteca externa no Wokwi (Wi-Fi, Wire e NTP vêm com o core do ESP32) |

## O que mudou em relação ao firmware principal
| Principal | MVP |
|-----------|-----|
| Relés K1, K2 e K4 | `Ponte` com 4 modos (`LIVRE`, `SUBIR`, `GERAR`, `CURTO`) nos pinos R_EN (18) e L_EN (13) do IBT-2 |
| Solenoide com hit-and-hold (GPIO 4) | Servo a 50 Hz no GPIO 4: `ENGATADA` 20°, `SOLTA` 80° (calibrar no ensaio 3) |
| RTC DS1307/DS3231 | Hora por NTP no Wi-Fi (`Wokwi-GUEST` na simulação) |
| LCD 20×4 e buzzer | Uma linha por segundo no Monitor Serial |
| Potenciômetro da demanda USB e sondagem K4 | Chave de demanda no GPIO 27 (5 W) e comando `w` (demanda vinda do painel) |
| 20 kg, 1,70 m, 0,05 m/s, `KE_MASSA` 253 | 5 kg, 1,00 m, 0,03 m/s, `KE_MASSA` 214 |
| Parar com frenagem e relé | Parar com a ponte em `CURTO` (motor em curto freia a massa) |

## Flag `SIMULACAO`
- `1` (Wokwi): massa, gerador e encoder viram uma planta virtual calculada no
  código, com a física de `MVP_FABLAB/01_FISICA/calculos_energia.md` (C-107 a
  C-109). O INA219 da subida vira o potenciômetro do GPIO 35 (0 a 3 A). Os 3
  LEDs de nível do gerador, que no real ficam direto no barramento com Zener,
  são acesos pelo código nos GPIOs 23, 14 e 2 (só no Wokwi).
- `0` (protótipo): falta completar `lerSensores()` com os 2 INA219 e a
  ESP32Encoder, e trocar `WIFI_SSID`/`WIFI_SENHA` pela rede do fablab.

## Comandos pelo Monitor Serial (115200)
`a` automático · `s` subir · `d` descer · `p` parar · `r` rearme ·
`h19` força a hora em 19 h · `hx` volta à hora do NTP · `w3` demanda de 3 W
vinda do painel (`w0` zera)

Sem hora (NTP ainda não respondeu e sem `h`), o automático fica parado em
`MANTER`; os comandos manuais funcionam.

## Como rodar no Wokwi
1. Crie um projeto ESP32 em wokwi.com.
2. Cole `sketch.ino`, `diagram.json` e `libraries.txt` nas abas de mesmo nome.
3. Se algum fio aparecer solto, refaça pela tabela de `../pinagem_mvp.md` (o
   `diagram.json` foi montado sem abrir o simulador, como o do principal,
   INC-031).

## Roteiro de teste
Os tempos abaixo saíram do teste fora do Wokwi.

1. Ao iniciar: `REARME`. A massa começa em h = 0,40 m e desce com frenagem a
   100 % (~0,01 m/s, ~40 s; o LED verde do gerador acende fraco). Para
   encurtar, mude a chave "FC inferior" e volte. Fica em `MANTER`.
2. `h3` (fora de ponta, nível 0): `SUBINDO`. Acendem R_EN, L_EN e RPWM; a
   massa sobe a 0,03 m/s e chega ao topo em ~34 s, gastando ~150 J (`Esub`).
3. `h19` (ponta) com a chave de demanda desligada: fica em `MANTER` (R11).
4. Ligue a chave de demanda (5 W): `PREP_DESCIDA` (RPWM pisca, o servo vai a
   80°), depois `DESCENDO`: L_EN apaga, LED vermelho da frenagem varia, e os
   LEDs do gerador acendem conforme a velocidade (os 3 perto de 0,05 m/s,
   ~10,7 V). Cada descida inteira soma ~14,6 J em `Egen`.
5. Mude a chave da emergência: `FALHA`, ponte em `CURTO`, servo volta a 20°.
   Volte a chave e digite `r`.
6. Durante uma subida (`s`), gire a corrente acima de 1,5 A: em 0,5 s aparece
   "massa travada".
7. `hx`: volta à hora do NTP (no Wokwi, a hora real de Brasília).

O código foi compilado e testado fora do Wokwi, com pinos simulados, nesses
cenários. **Dentro do Wokwi ainda não rodou.**
