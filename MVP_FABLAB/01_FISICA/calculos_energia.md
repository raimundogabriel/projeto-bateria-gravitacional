# CÁLCULOS DE ENERGIA — MVP FABLAB

Premissas em `premissas.md` (6 kg, 1,70 m, DEC-014). Numeração C-101 em
diante para não confundir com os cálculos C-001 a C-010 do projeto principal.
"estim." = depende de rendimentos estimados.

## C-101 — Energia potencial teórica
E_teo = m·g·h = 6 × 9,81 × 1,70 = **100,1 J (0,0278 Wh)**

Sanity check: ~0,2 % de uma bateria de celular de 15 Wh. Serve para mostrar
o princípio, não para guardar energia útil (o projeto principal guarda 333,5 J,
também didático).

## C-102 — Energia nos terminais do gerador (estim.)
E_gen = E_teo · η_polias · η_redutor,descida · η_gerador
= 100,1 × 0,90 × 0,55 × 0,60 = 100,1 × 0,297 ≈ **29,7 J**

## C-103 — Energia de subida e eficiência de ida e volta (estim.)
E_subida ≈ E_teo / (η_polias · η_redutor,subida · η_motor) = 100,1 / 0,351
≈ **285 a 315 J** (o valor maior inclui a corrente em vazio, ver C-108).

η_ciclo = E_gen / E_subida ≈ **0,10**. É baixo porque o redutor de
engrenagens retas e o motor pequeno perdem mais que o planetário do projeto
principal (~0,27). Para o MVP isso é aceitável: o que se mede e se mostra no
painel é justamente essa eficiência.

## C-104 — Tração no cordão e torque no tambor
T_cordão = m·g / 2 = 29,4 N (talha 2:1); τ_tambor = 29,4 × 0,010 = **0,294 N·m**

Motorredutor com torque nominal ≥ 0,6 N·m (≈ 6 kg·cm) dá fator 2. Cordão de
2 mm com ruptura ≥ 100 kg: fator de segurança ~33.

## C-105 — Relação de transmissão
- Talha 2:1: o cordão corre o dobro da velocidade da massa.
- Tambor Ø 20 mm: 1 volta = 62,8 mm de cordão = 31,4 mm de massa.
- Redutor 1:90.

ω_motor = (2·v / r) · i = 18.000 · v (rad/s). 1 cm de massa ≈ 29 voltas do
motor.

Cordão no tambor: 3,40 m de cordão (talha) / 62,8 mm ≈ 54 voltas + 3 mortas =
57 voltas × passo 2,5 mm ≈ **143 mm de largura útil do tambor** (imprimir com
150 mm). Com esse comprimento, o mancal 608 do lado oposto ao motor é
obrigatório.

## C-106 — Resolução do encoder
11 pulsos × 4 (quadratura) × 90 = 3.960 contagens por volta do tambor =
31,4 mm de massa → **0,00793 mm por contagem** (`MM_POR_PULSO`). O curso de
1,70 m soma ~214.000 contagens: acima dos 16 bits do PCNT, então continua
valendo a ESP32Encoder (acumula estouros). A 0,05 m/s chegam ~6.300
contagens/s, folgado para o PCNT.

## C-107 — Tensão e potência geradas por velocidade (estim.)
E_fcem = K_e · ω_motor = 0,0119 × 18.000 · v ≈ **214 · v** (V) → `KE_MASSA = 214`

P_el ≈ m·g·v · 0,297

| v (m/s) | Duração da descida (s) | Tambor / motor (rpm) | Tensão em vazio (V) | P gerada (W) | O que acende |
|---------|------------------------|----------------------|---------------------|--------------|--------------|
| 0,01 | 170 | 19 / 1.719 | 2,1 | ~0,17 | nada útil |
| 0,02 | 85 | 38 / 3.438 | 4,3 | ~0,35 | LED verde |
| 0,03 | 57 | 57 / 5.157 | 6,4 | ~0,52 | verde + amarelo (limiar) |
| 0,04 | 42 | 76 / 6.876 | 8,6 | ~0,70 | verde + amarelo |
| **0,05** | **34** | **95 / 8.595** | **10,7** | **~0,87** | **os 3 LEDs (ponto de projeto)** |

Acima de ~0,055 m/s a tensão passa dos 12 V da fonte e o diodo de corpo do
IBT-2 começa a devolver corrente à fonte (ver `02_ARQUITETO/circuito.md`).
Por isso o alvo máximo é 0,05 m/s e o limite de falha é 0,07 m/s.

## Por que só LEDs, sem USB (DEC-022)
A 0,05 m/s sobram ~0,87 W a ~10 V. Um buck para 5 V entregaria ~0,74 W
(~150 mA). O celular tenta puxar 500 mA ou mais, a tensão desaba, o buck
desliga e o celular entra e sai de carga. Para a USB funcionar seria preciso
descer mais rápido (acima do limite de 0,055 m/s deste motor) ou trocar o
motor e o redutor, o que custa mais e atrasa. Os LEDs funcionam com qualquer
tensão acima de ~2 V, não têm conversor nem firmware, e mostram a geração ao
vivo durante os 34 s da descida.

## C-108 — Subida
Torque no motor: 0,294 / (0,90 × 0,65 × 90) ≈ 5,6 mN·m → I ≈ 5,6 / 11,9 +
I_0 ≈ **0,62 A**.

A 0,03 m/s: E_fcem = 6,4 V; V_motor ≈ 6,4 + 0,62 × 4 ≈ 8,9 V → **PWM ~74 %**
em 12 V, ~5,5 W, 57 s → ~300 J por subida.

Velocidade máxima de subida com 12 V: (12 − 2,5) / 214 ≈ **0,044 m/s**.
Fonte de 12 V 3 A dá folga para a partida (até ~2× a corrente de regime).

## C-109 — Carga de frenagem
Na descida a corrente do gerador é quase fixa, porque é o torque da massa que
a impõe: I_gen ≈ τ_motor / K_t ≈ 0,08 a 0,14 A (o intervalo cobre o atrito
desconhecido; o simulador usa 0,108 A). A velocidade sai da resistência que o
gerador enxerga: v ≈ I_gen · (R_carga + R_a) / 214.

| Carga ligada | R vista | v estimada | Uso |
|--------------|---------|------------|-----|
| Carga fixa 100 Ω (sempre ligada) | ~104 Ω | 0,04 a 0,06 m/s | descida sem controle: ESP32 desligado ou travado |
| 100 Ω ∥ 22 Ω (MOSFET 100 %) | ~22 Ω | ~0,011 m/s | frenagem máxima controlada |
| Curto pelo IBT-2 (dois lados baixos) | ~4 Ω | < 0,002 m/s | parada e falha |

O PWM do MOSFET varia entre as duas primeiras linhas; a malha PI escolhe o
ponto. Potência no 22 Ω: < 0,4 W; na carga fixa: < 1,5 W. Resistores de 5 W
(22 Ω) e 2 W (100 Ω) bastam. Os valores finais saem do ensaio 4.
