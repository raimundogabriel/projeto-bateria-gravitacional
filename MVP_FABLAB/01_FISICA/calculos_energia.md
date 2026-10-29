# CÁLCULOS DE ENERGIA — MVP FABLAB

Premissas em `premissas.md`: **2 kg, 1,70 m, motor de 6 V, sem talha,
tambor de Ø 30 mm** (DEC-024, DEC-025). Numeração C-101 em diante para não
confundir com os cálculos C-001 a C-010 do projeto principal. "estim." =
depende de rendimentos estimados.

Versão anterior (6 kg, 12 V, talha 2:1, Ø 20 mm): no histórico do git,
commit `7e96f4c`.

## C-101 — Energia potencial teórica
E_teo = m·g·h = 2 × 9,81 × 1,70 = **33,4 J (0,0093 Wh)**

Sanity check: ~0,06 % de uma bateria de celular de 15 Wh. É uma prova de
conceito: o que importa é ver o ciclo completo e medir o rendimento.

## C-102 — Energia nos terminais do gerador (estim.)
E_gen = E_teo · η_cordão · η_redutor,descida · η_gerador
= 33,4 × 0,90 × 0,55 × 0,60 = 33,4 × 0,297 ≈ **9,9 J**

## C-103 — Energia de subida e eficiência de ida e volta (estim.)
Com a subida a 0,08 m/s (C-108): E_subida ≈ **~110 J** (o motor de 6 V tem
corrente em vazio maior, ~0,3 A, e ela pesa numa massa tão leve).

η_ciclo = E_gen / E_subida ≈ **0,09**. Igual em ordem de grandeza ao porte
anterior (~0,10): é o que o painel mede e mostra.

## C-104 — Tração no cordão e torque no tambor
Sem talha: T_cordão = m·g = 19,6 N; τ_tambor = 19,6 × 0,015 = **0,294 N·m**

O mesmo torque do porte anterior (6 kg com talha 2:1 no tambor de Ø 20 mm),
de propósito: o torque é o que faz o redutor retroacionar. Com 2 kg, a talha
e o tambor de Ø 20 mm dariam só 0,098 N·m, e a massa quase certamente não
desceria sozinha (DEC-025).

Motorredutor com torque nominal ≥ 0,6 N·m dá fator 2. Cordão de 2 mm com
ruptura ≥ 100 kg: fator de segurança ~50.

## C-105 — Relação de transmissão
- Sem talha: o cordão corre na mesma velocidade da massa.
- Tambor Ø 30 mm: 1 volta = 94,2 mm de cordão = 94,2 mm de massa.
- Redutor 1:90.

ω_motor = (v / r) · i = 6.000 · v (rad/s). 1 cm de massa ≈ 9,5 voltas do
motor.

Cordão no tambor: 1,70 m / 94,2 mm ≈ 18 voltas + 3 mortas = 21 voltas ×
passo 2,5 mm ≈ **53 mm de largura útil do tambor** (imprimir com 60 mm). O
mancal 608 do lado oposto ao motor continua, para tirar do redutor a carga
radial.

## C-106 — Resolução do encoder
11 pulsos × 4 (quadratura) × 90 = 3.960 contagens por volta do tambor =
94,2 mm de massa → **0,0238 mm por contagem** (`MM_POR_PULSO`). O curso de
1,70 m soma ~71.400 contagens: acima dos 16 bits do PCNT, então continua
valendo a ESP32Encoder. A 0,13 m/s chegam ~5.500 contagens/s, folgado.

## C-107 — Tensão e potência geradas por velocidade (estim.)
E_fcem = K_e · ω_motor = 0,006 × 6.000 · v = **36 · v** (V) → `KE_MASSA = 36`

P_el ≈ m·g·v · 0,297

| v (m/s) | Duração da descida (s) | Tambor / motor (rpm) | Tensão em vazio (V) | P gerada (W) | O que acende |
|---------|------------------------|----------------------|---------------------|--------------|--------------|
| 0,04 | 42 | 25 / 2.292 | 1,4 | ~0,23 | nada |
| 0,06 | 28 | 38 / 3.438 | 2,2 | ~0,35 | LED verde |
| 0,08 | 21 | 51 / 4.584 | 2,9 | ~0,47 | verde |
| 0,10 | 17 | 64 / 5.730 | 3,6 | ~0,58 | verde + amarelo |
| 0,12 | 14 | 76 / 6.875 | 4,3 | ~0,70 | verde + amarelo (vermelho no limiar, 4,4 V) |
| **0,13** | **13** | **83 / 7.448** | **4,7** | **~0,76** | **os 3 LEDs (ponto de projeto)** |
| 0,20 | 8,5 | 127 / 11.459 | 7,2 | ~1,17 | limite de falha |

A tensão gerada fica sempre abaixo dos 12 V da fonte, então o diodo de corpo
do IBT-2 nunca devolve corrente para ela (no porte anterior isso limitava a
descida a 0,05 m/s). O limite agora é o da massa: 0,20 m/s, e o motor a
~11.500 rpm, ~20 % acima da rotação em vazio, por poucos segundos.

## Por que só LEDs, sem USB (DEC-022)
Continua valendo, com mais razão: a descida gera ~0,76 W a ~4,7 V, abaixo
dos 5 V de uma USB. Os LEDs acendem a partir de ~2 V, não têm conversor nem
firmware, e mostram a geração ao vivo durante os ~13 s da descida.

## C-108 — Subida
Torque no motor: 0,294 / (0,90 × 0,65 × 90) ≈ 5,6 mN·m → I ≈ 5,6 / 6,0 +
I_0 ≈ **1,23 A** no motor.

A 0,08 m/s: E_fcem = 2,9 V; V_motor ≈ 2,9 + 1,23 × 1 ≈ 4,1 V → **PWM ~34 %**
em 12 V (`PWM_SUBIDA = 88`), ~5,1 W, 21 s → **~110 J** por subida. Do lado
da fonte (onde fica o INA219 nº 1) a corrente é ~0,42 A.

Velocidade máxima de subida com o PWM limitado a 50 % (6 V em média):
(6 − 1,23) / 36 ≈ **0,13 m/s**.

Motor travado com 6 V: ~6 A no motor, ~3 A na fonte. A proteção de massa
travada corta acima de **1,0 A medido na fonte** por 0,5 s (`I_TRAVADO`,
~2,4× a corrente de regime, a mesma folga do porte anterior). A fonte de
12 V 3 A continua servindo.

## C-109 — Cargas do gerador
Na descida a corrente do gerador é quase fixa, porque é o torque da massa
que a impõe: τ_motor ≈ 0,294 × 0,90 × 0,55 / 90 ≈ 1,6 mN·m → I_gen ≈
τ_motor / K_t ≈ **0,16 a 0,28 A** (o intervalo cobre o atrito desconhecido;
o simulador usa 0,216 A). A velocidade sai da resistência que o gerador
enxerga: v ≈ I_gen · (R_carga + R_a) / 36.

| Carga ligada | R vista | v estimada | Uso |
|--------------|---------|------------|-----|
| Carga fixa 22 Ω (sempre ligada) | ~23 Ω | 0,10 a 0,18 m/s (0,14 no valor central) | descida sem controle: ESP32 desligado ou travado. Fica abaixo do limite de 0,20 m/s |
| 22 Ω ∥ 6,8 Ω (MOSFET 100 %) | ~6,2 Ω | ~0,037 m/s | frenagem máxima controlada |
| Curto pelo IBT-2 (dois lados baixos) | ~1 Ω | ~0,006 m/s | parada e falha (a massa escorrega ~3 mm nos 0,5 s até a lingueta pegar) |

O PWM do MOSFET varia entre as duas primeiras linhas; a malha PI escolhe o
ponto. Potência na carga fixa: ~1,0 W; no 6,8 Ω: < 0,35 W. Os dois de 5 W
(cerâmicos) dão folga. Os valores finais saem dos ensaios 4 e 5.

**Atenção ao risco do motor de 6 V:** a corrente em vazio (I_0 ≈ 0,3 A)
equivale a um torque de atrito de ~1,8 mN·m no motor, parecido com o
torque que a massa aplica (1,6 mN·m). Por isso o ensaio 0 continua sendo a
primeira coisa a fazer: se a massa não descer sozinha, ver as saídas em
`validacao_experimental.md`.
