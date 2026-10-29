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
| `wokwi/libraries.txt` | Só a PubSubClient (MQTT) no Wokwi; Wi-Fi, Wire e NTP vêm com o core do ESP32 |

Para gravar num ESP32 de verdade e ligar ao painel, siga `../../DIY/`.

## O que mudou em relação ao firmware principal
| Principal | MVP |
|-----------|-----|
| Relés K1, K2 e K4 | `Ponte` com 4 modos (`LIVRE`, `SUBIR`, `GERAR`, `CURTO`) nos pinos R_EN (18) e L_EN (13) do IBT-2 |
| Solenoide com hit-and-hold (GPIO 4) | Servo a 50 Hz no GPIO 4: `ENGATADA` 20°, `SOLTA` 80° (calibrar no ensaio 3) |
| RTC DS1307/DS3231 | Hora por NTP no Wi-Fi (`Wokwi-GUEST` na simulação) |
| LCD 20×4 e buzzer | Uma linha por segundo no Monitor Serial |
| Potenciômetro da demanda USB e sondagem K4 | Chave de demanda no GPIO 27 (5 W) e comando `w` (demanda vinda do painel) |
| 20 kg, 1,70 m, 0,05 m/s, `KE_MASSA` 253 | 6 kg, 1,70 m, 0,10 m/s, `KE_MASSA` 21,8 (parafusadeira GSR 1440-LI na 1ª marcha, sem talha, tambor Ø 30 mm) |
| Motor na tensão da fonte | Motor de 14,4 V na fonte de 12 V: PWM nunca passa de 50 % (`PWM_MAX`), para a subida não passar de ~0,23 m/s |
| Parar com frenagem e relé | Parar com a ponte em `CURTO` (motor em curto freia a massa) |
| MQTT ainda não implementado | `grav/estado` a cada 1 s, `grav/comando` e `grav/tarifas` (DEC-023) |

## Flag `SIMULACAO`
- `1` (Wokwi): massa, gerador e encoder viram uma planta virtual calculada no
  código, com a física de `MVP_FABLAB/01_FISICA/calculos_energia.md` (C-107 a
  C-109). O INA219 da subida vira o potenciômetro do GPIO 35 (0 a 5 A). Os 3
  LEDs de nível do gerador, que no real ficam direto no barramento com diodos
  em série, são acesos pelo código nos GPIOs 23, 14 e 2 (só no Wokwi).
- `0` (protótipo): altura pelo encoder LPD3806 do tambor, contado no PCNT (ESP32Encoder),
  corrente e potência de subida pelo INA219 0x40, tensão e potência geradas
  pelo 0x41 (biblioteca Adafruit INA219). Sem os dois INA219 o firmware fica
  em `FALHA`.

## Rede e MQTT
No topo do sketch: `WIFI_SSID`, `WIFI_SENHA`, `MQTT_BROKER`, `MQTT_PORTA` e
`TOPICO_BASE`. O padrão é o do Wokwi (`Wokwi-GUEST` e `broker.hivemq.com`).
No fablab, a rede local e o IP do notebook com o Mosquitto
(`../../DIY/03_painel_mqtt.md`).

| Tópico | Sentido | Conteúdo |
|--------|---------|----------|
| `<base>/estado` | ESP32 → painel | JSON com estado, modo, ponte, altura, velocidade, potências, tensão gerada, frenagem, tarifa, posto, demanda, comando fuzzy, hora, ciclos, energias, corrente e motivo da falha; a cada 1 s e a cada troca de estado |
| `<base>/online` | ESP32 → painel | `1` ao conectar; `0` pelo testamento se cair (retido) |
| `<base>/comando` | painel → ESP32 | `{"acao": "auto|subir|descer|parar|rearmar"}`, `{"demanda_w": 3}`, `{"hora": 19}` (−1 volta ao NTP) |
| `<base>/tarifas` | painel → ESP32 | `{"fora_ponta": 0.6, "intermediario": 0.9, "ponta": 1.4}` (retido) |

O ESP32 só tenta conectar no broker com a massa parada (`MANTER` ou
`FALHA`): a conexão pode travar o loop por alguns segundos, e no meio de uma
descida isso deixaria a frenagem sem controle.

## Comandos pelo Monitor Serial (115200)
`a` automático · `s` subir · `d` descer · `p` parar · `r` rearme ·
`h19` força a hora em 19 h · `hx` volta à hora do NTP · `w3` demanda de 3 W
vinda do painel (`w0` zera). O painel manda os mesmos comandos por MQTT.

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
   100 % (~0,057 m/s, ~7 s; ~1,2 V, baixo demais para os LEDs). Para
   encurtar, mude a chave "FC inferior" e volte. Fica em `MANTER`.
2. `h3` (fora de ponta, nível 0): `SUBINDO`. Acendem R_EN, L_EN e RPWM; a
   massa sobe a 0,10 m/s e desacelera para 0,03 m/s nos últimos 5 cm. Como
   o fuzzy decide a cada 5 s, ela normalmente chega ao fim de curso (1,70 m,
   ~20 s); uma subida inteira gasta ~270 J (`Esub`).
3. `h19` (ponta) com a chave de demanda desligada: fica em `MANTER` (R11).
4. Ligue a chave de demanda (5 W): `PREP_DESCIDA` (RPWM pisca, o servo vai a
   80°), depois `DESCENDO`: L_EN apaga, LED vermelho da frenagem varia, e os
   LEDs do gerador acendem conforme a velocidade (os 3 perto de 0,18 m/s,
   ~3,9 V). Uma descida inteira soma ~25 J em `Egen`; o fuzzy pode
   parar antes (descida parcial, R9). Em manual (`d`) a descida vai a
   0,18 m/s e leva ~9,5 s.
5. Mude a chave da emergência: `FALHA`, ponte em `CURTO`, servo volta a 20°.
   Volte a chave e digite `r`.
6. Durante uma subida (`s`), gire a corrente acima de 3,0 A: em 0,5 s aparece
   "massa travada".
7. `hx`: volta à hora do NTP (no Wokwi, a hora real de Brasília).

O código foi compilado e testado fora do Wokwi, com pinos, Wi-Fi, MQTT,
INA219 e encoder simulados, nesses cenários e com comandos chegando por
MQTT. **Dentro do Wokwi e num ESP32 de verdade ainda não rodou.**
