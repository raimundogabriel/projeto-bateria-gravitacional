# CÁLCULOS DE ENERGIA — MVP FABLAB

Premissas em `premissas.md`. Numeração C-101 em diante para não confundir com
os cálculos C-001 a C-010 do projeto principal. "estim." = depende de
rendimentos estimados.

## C-101 — Energia potencial teórica
E_teo = m·g·h = 5 × 9,81 × 1,00 = **49,05 J (0,0136 Wh)**

Sanity check: ~0,1 % de uma bateria de celular de 15 Wh. Serve para mostrar
o princípio, não para guardar energia útil (o projeto principal guarda 333,5 J,
também didático).

## C-102 — Energia nos terminais do gerador (estim.)
E_gen = E_teo · η_polias · η_redutor,descida · η_gerador
= 49,05 × 0,90 × 0,55 × 0,60 = 49,05 × 0,297 ≈ **14,6 J**

## C-103 — Energia de subida e eficiência de ida e volta (estim.)
E_subida ≈ E_teo / (η_polias · η_redutor,subida · η_motor) = 49,05 / 0,351
≈ **140 a 155 J** (o valor maior inclui a corrente em vazio, ver C-108).

η_ciclo = E_gen / E_subida ≈ **0,10**. É baixo porque o redutor de
engrenagens retas e o motor pequeno perdem mais que o planetário do projeto
principal (~0,27). Para o MVP isso é aceitável: o que se mede e se mostra no
painel é justamente essa eficiência.

## C-104 — Tração no cordão e torque no tambor
T_cordão = m·g / 2 = 24,5 N (talha 2:1); τ_tambor = 24,5 × 0,010 = **0,245 N·m**

Motorredutor com torque nominal ≥ 0,5 N·m (≈ 5 kg·cm) dá fator 2. Cordão de
2 mm com ruptura ≥ 100 kg: fator de segurança ~40.

## C-105 — Relação de transmissão
- Talha 2:1: o cordão corre o dobro da velocidade da massa.
- Tambor Ø 20 mm: 1 volta = 62,8 mm de cordão = 31,4 mm de massa.
- Redutor 1:90.

ω_motor = (2·v / r) · i = 18.000 · v (rad/s). 1 cm de massa ≈ 29 voltas do
motor.

Cordão no tambor: 2 m de cordão (talha) / 62,8 mm ≈ 32 voltas + 3 mortas =
35 voltas × passo 2,5 mm ≈ **88 mm de largura útil do tambor**.

## C-106 — Resolução do encoder
11 pulsos × 4 (quadratura) × 90 = 3.960 contagens por volta do tambor =
31,4 mm de massa → **0,00793 mm por contagem** (`MM_POR_PULSO`). O curso de
1 m soma ~126.000 contagens: acima dos 16 bits do PCNT, então continua
valendo a ESP32Encoder (acumula estouros). A 0,05 m/s chegam ~6.300
contagens/s, folgado para o PCNT.

## C-107 — Tensão e potência geradas por velocidade (estim.)
E_fcem = K_e · ω_motor = 0,0119 × 18.000 · v ≈ **214 · v** (V) → `KE_MASSA = 214`

P_el ≈ m·g·v · 0,297

| v (m/s) | Duração da descida (s) | Tambor / motor (rpm) | Tensão em vazio (V) | P gerada (W) | O que acende |
|---------|------------------------|----------------------|---------------------|--------------|--------------|
| 0,01 | 100 | 19 / 1.719 | 2,1 | ~0,15 | nada útil |
| 0,02 | 50 | 38 / 3.438 | 4,3 | ~0,29 | LED verde |
| 0,03 | 33 | 57 / 5.157 | 6,4 | ~0,44 | verde + amarelo (limiar) |
| 0,04 | 25 | 76 / 6.875 | 8,6 | ~0,58 | verde + amarelo |
| **0,05** | **20** | **95 / 8.594** | **10,7** | **~0,73** | **os 3 LEDs (ponto de projeto)** |

Acima de ~0,055 m/s a tensão passa dos 12 V da fonte e o diodo de corpo do
IBT-2 começa a devolver corrente à fonte (ver `02_ARQUITETO/circuito.md`).
Por isso o alvo máximo é 0,05 m/s e o limite de falha é 0,07 m/s.

**Por que não USB:** a 0,05 m/s sobram ~0,7 W a ~10 V. Um buck para 5 V
entregaria ~0,6 W (~120 mA). O celular tenta puxar 500 mA ou mais, a tensão
desaba, o buck desliga e o celular entra e sai de carga. Não é uma
demonstração confiável.

## C-108 — Subida
Torque no motor: 0,245 / (0,90 × 0,65 × 90) ≈ 4,7 mN·m → I ≈ 4,7 / 11,9 +
I_0 ≈ **0,54 A**.

A 0,03 m/s: E_fcem = 6,4 V; V_motor ≈ 6,4 + 0,54 × 4 ≈ 8,6 V → **PWM ~72 %**
em 12 V, ~4,6 W, 33 s → ~155 J por subida.

Velocidade máxima de subida com 12 V: (12 − 2,2) / 214 ≈ **0,045 m/s**.
Fonte de 12 V 3 A dá folga para a partida (até ~2× a corrente de regime).

## C-109 — Carga de frenagem
Na descida a corrente do gerador é quase fixa, porque é o torque da massa que
a impõe: I_gen ≈ τ_motor / K_t ≈ 0,07 a 0,11 A (o intervalo cobre o atrito
desconhecido). A velocidade sai da resistência que o gerador enxerga:
v ≈ I_gen · (R_carga + R_a) / 214.

| Carga ligada | R vista | v estimada | Uso |
|--------------|---------|------------|-----|
| Carga fixa 120 Ω (sempre ligada) | ~124 Ω | 0,04 a 0,06 m/s | descida sem controle: ESP32 desligado ou travado |
| 120 Ω ∥ 22 Ω (MOSFET 100 %) | ~23 Ω | ~0,01 m/s | frenagem máxima controlada |
| Curto pelo IBT-2 (dois lados baixos) | ~4 Ω | < 0,002 m/s | parada e falha |

O PWM do MOSFET varia entre as duas primeiras linhas; a malha PI escolhe o
ponto. Potência no 22 Ω: < 0,3 W; na carga fixa: < 1,5 W. Resistores de 5 W
(22 Ω) e 2 W (120 Ω) bastam. Os valores finais saem do ensaio 4.

## Variante B — 10 kg, 1,2 m, tentativa de USB
Só se o Gabriel escolher a variante B (DEC-014). Muda o motor para um
**planetário de 37 mm, 12 V, 1:71, com encoder, torque nominal ≥ 1 N·m**
(η_redutor ~0,70 nos dois sentidos).

| Grandeza | Variante A | Variante B |
|----------|------------|------------|
| E_teo | 49 J | 117,7 J |
| Torque no tambor | 0,245 N·m | 0,49 N·m |
| KE_MASSA | 214 V/(m/s) | ~169 V/(m/s) |
| Ponto de projeto | 0,05 m/s, 10,7 V, ~0,7 W | 0,06 m/s, ~10,1 V, ~2,2 W |
| E_gen por ciclo | ~14,6 J | ~44 J |
| Saída útil | 3 LEDs | LEDs + USB ~1,5 W por ~20 s (power bank ou luminária USB, não celular) |
| Torre | ~1,50 m | ~1,75 m |
| Custo | ≈ R$ 800 | ≈ R$ 1.000 |
