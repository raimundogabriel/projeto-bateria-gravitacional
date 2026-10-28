# Firmware ESP32 — Bateria Gravitacional

| Arquivo | O que é |
|---------|---------|
| `wokwi/sketch.ino` | Firmware principal (ESP32). Mesma pinagem do circuito real |
| `wokwi/diagram.json` | Circuito do Wokwi (ESP32 DevKit V1, relés, LEDs, potenciômetros, DS1307, LCD 2004, KY-040) |
| `wokwi/libraries.txt` | Bibliotecas que o Wokwi instala sozinho |
| `bateria_gravitacional_tinkercad.ino` | Versão antiga para Arduino Uno no Tinkercad (só histórico, DEC-011) |

## Flag `SIMULACAO`
- `1` (Wokwi): massa e gerador viram uma planta virtual calculada no código;
  os INA226 viram potenciômetros (GPIO 35 corrente, GPIO 39 demanda); os
  sinais de potência acendem LEDs.
- `0` (protótipo): lê encoder, INA226 e DS3231 de verdade. **Falta
  completar `lerSensores()`** com os três INA226 e a biblioteca ESP32Encoder
  (HANDOFF-003).

## O que o firmware faz
- Máquina de estados: `REARME`, `MANTER`, `SUBINDO`, `PREP_DESCIDA`,
  `DESCENDO`, `PARANDO`, `FALHA`
- Fuzzy Mamdani escrito à mão (3 entradas, 11 regras, centroide normalizado),
  a cada 5 s — ver `01_FISICA/algoritmos_controle.md`
- Malha PI da frenagem e proteções a cada 50 ms
- Sondagem da USB a cada 30 s em MANTER
- LCD a cada 1 s; log no Monitor Serial
- **Ainda não tem MQTT** (ver `03_SOFTWARE/contrato_dados.md`)

## Comandos pelo Monitor Serial (115200)
`a` automático · `s` subir · `d` descer · `p` parar · `r` rearme ·
`h19` força a hora em 19 h · `hx` volta à hora do RTC

## Como rodar no Wokwi
1. Crie um projeto ESP32 em wokwi.com.
2. Cole `sketch.ino`, `diagram.json` e `libraries.txt` nas abas de mesmo nome.
3. Se algum fio aparecer solto, refaça pela tabela de
   `03_SOFTWARE/pinagem_esp32.md` (o `diagram.json` foi montado sem abrir o
   simulador, INC-031). Se começar em FALHA por emergência ou parar num fim de
   curso, mude a posição da chave.

## Roteiro de teste
1. Ao iniciar, o estado é `REARME` e a massa desce até h = 0, passando a
   `MANTER`.
2. `h3`: o fuzzy manda subir; LEDs amarelo (K1), verde (K2), RPWM e EN acendem
   e a massa vai ao topo.
3. `h19` (ponta) com demanda em 0: fica em `MANTER` pela R11 e o LED branco
   (K4) pisca 1 s a cada 30 s.
4. Gire a demanda acima de 4 W: `PREP_DESCIDA` (LED roxo forte e depois
   fraco), o verde apaga, o laranja acende, entra `DESCENDO` com o LED
   vermelho variando conforme a frenagem.
5. Mude a chave da emergência: `FALHA`, relés soltam, buzzer toca. Volte a
   chave e digite `r`.
6. Durante uma subida, gire a corrente acima de 3 A: em 0,5 s aparece "massa
   travada".
7. `hx` volta à hora do RTC.

O código foi compilado e testado fora do Wokwi, com pinos simulados, nesses
cenários. **Dentro do Wokwi ainda não rodou.**
