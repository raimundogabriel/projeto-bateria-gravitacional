# O QUE MUDA NO FIRMWARE E NO PAINEL — MVP FABLAB

**Implementado em 2026-10-28** em `firmware/wokwi/` (HANDOFF-011), menos o
MQTT (item 8) e as leituras reais de `SIMULACAO 0`. O painel está em
`dashboard/` (HANDOFF-012). O firmware partiu de
`03_SOFTWARE/firmware/wokwi/sketch.ino` da raiz e mudou só o que está abaixo. A máquina de
estados (`MANTER`, `SUBINDO`, `PREP_DESCIDA`, `DESCENDO`, `PARANDO`, `FALHA`,
`REARME`), o fuzzy e as proteções continuam.

## Constantes

| Constante | Projeto principal | MVP | Origem |
|-----------|-------------------|-----|--------|
| `CURSO` | 1.70 | 1.70 | DEC-014 (mesmo curso) |
| `FOLGA_TOPO` | 0.02 | 0.01 | `02_ARQUITETO/mecanica.md` |
| `V_SUBIDA` | 0.05 | 0.03 | C-108 |
| `V_MAX_SUBIDA` | 0.09 | 0.045 | C-108 |
| `V_LIMITE` | 0.10 | 0.07 | C-107 |
| `V_ALVO_MIN` / `V_ALVO_MAX` | 0.03 / 0.08 | 0.02 / 0.05 | C-107 |
| `V_FREIO_TOTAL` | 0.025 | 0.01 | C-109 |
| `KE_MASSA` | 253 | 214 | C-107 |
| `V_GEN_MAX` | 28 | 14 | TVS 15 V |
| `I_TRAVADO` | 3.0 | 1.5 | C-108 (2,4× a corrente de regime) |
| `MM_POR_PULSO` | 0.0393 | 0.00793 | C-106 |
| `ALIVIO_TRAVA` | 0.003 | 0.003 | = |
| `MASSA` (planta virtual e painel) | 20 kg | 6 kg | DEC-014 |

## Mudanças de lógica

1. **Relés → enables do IBT-2.** Trocar `PIN_EN` por `PIN_R_EN` (18) e
   `PIN_L_EN` (13). Criar uma função `modoPonte(LIVRE | SUBIR | GERAR | CURTO)`
   que é o único lugar que mexe nesses pinos (tabela em
   `../02_ARQUITETO/circuito.md`). Remover K1, K2, K4 e `RELE_LIGA`.
2. **Solenoide → servo.** Trocar o hit-and-hold do GPIO 4 por
   `servoTrava(ENGATADA | SOLTA)` com LEDC a 50 Hz. Os ângulos saem do
   ensaio 3.
3. **Sequências** (mesma ideia do projeto principal, sem relés):
   - Subir: frenagem 0 % → `SUBIR` com rampa 0 → ~72 % em 1 s → PI em
     `V_SUBIDA` → parar com rampa, `CURTO` 200 ms (massa assenta na lingueta)
     → `LIVRE`.
   - Descer: `SUBIR` até +3 mm → `CURTO` segurando → servo `SOLTA`, esperar
     300 ms → frenagem 100 % → `GERAR` → PI na frenagem com alvo de 0,02 a
     0,05 m/s → parar com frenagem 100 %, `CURTO` até v ≈ 0, servo
     `ENGATADA`, 500 ms → `LIVRE`, frenagem 0 %.
   - Falha: servo `ENGATADA`, frenagem 100 %, `CURTO`. Só o rearme sai.
4. **Sondagem da USB → chave de demanda.** Sem K4: a demanda D vem da chave
   no GPIO 27 (ligada = 5 W) ou do painel por `grav/comando`, o que for
   maior. As 11 regras do fuzzy não mudam; a faixa de D continua 0–10 W.
5. **Sensores.** 2× INA219 (biblioteca Adafruit INA219) no lugar dos 3×
   INA226. Energia gerada = integral de V × I do INA219 nº 2; subida = nº 1.
6. **Hora.** Sem DS3231: `configTime()` com NTP ao conectar no Wi-Fi; sem
   Wi-Fi, o painel manda a hora em `grav/comando`. Sem nenhum dos dois, o
   fuzzy fica em MANTER e o modo manual continua funcionando.
7. **Sem LCD e buzzer.** Remover `linhaLcd()` e o buzzer; o estado vai ao
   Monitor Serial a cada 1 s e ao MQTT.
8. **MQTT é obrigatório no MVP.** Sem LCD, o painel é a única tela. Implementar
   `grav/estado`, `grav/energia` e `grav/comando` de
   `03_SOFTWARE/contrato_dados.md` (o mesmo trabalho do HANDOFF-004 do
   projeto principal, que aproveita).

## Painel Streamlit
Cópia do painel de `03_SOFTWARE/dashboard/` em `dashboard/`, com a mesma
estrutura e as mesmas abas. Mudam os parâmetros do simulador (6 kg, 1,70 m,
`KE_MASSA` 214, rendimentos do MVP), a velocidade-alvo do fuzzy (0,02 a
0,05 m/s) e a saída útil: as colunas `p_usb_w` e `e_usb_j` viram `p_leds_w` e
`e_leds_j` (potência e energia nos 3 LEDs de nível). Ver `dashboard/README.md`.
