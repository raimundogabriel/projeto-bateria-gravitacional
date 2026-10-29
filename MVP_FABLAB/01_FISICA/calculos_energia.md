# CÁLCULOS DE ENERGIA — MVP FABLAB

Premissas em `premissas.md`: **parafusadeira Bosch GSR 1440-LI** (motor
550 de 14,4 V + redutor planetário ~1:42 na 1ª marcha), **6 kg, 1,70 m,
sem talha, tambor de Ø 30 mm** (DEC-025, DEC-026). Numeração C-101 em diante
para não confundir com os cálculos C-001 a C-010 do projeto principal.
"estim." = depende de dados estimados do motor; o ensaio 0 confirma.

Versões anteriores no histórico do git: 6 kg com motorredutor 12 V e talha
(commit `7e96f4c`); 2 kg com motorredutor 6 V (commit `428b3cc`).

## C-101 — Energia potencial teórica
E_teo = m·g·h = 6 × 9,81 × 1,70 = **100,1 J (0,0278 Wh)**

Sanity check: ~0,2 % de uma bateria de celular de 15 Wh. É uma prova de
conceito: o que importa é ver o ciclo completo e medir o rendimento.

## C-102 — Energia nos terminais do gerador (estim.)
Na descida, a massa aplica no motor τ_massa = m·g·r·η_cordão·η_redutor / i
= 6 × 9,81 × 0,015 × 0,90 × 0,70 / 42 ≈ 13,2 mN·m. O atrito interno do motor
come τ_atrito = K_t·I_0 ≈ 7,8 mN·m. Sobra ~5,4 mN·m para gerar.

E_gen ≈ (τ_massa − τ_atrito) × ângulo do motor = 5,4 mN·m × 4.760 rad −
perdas no cobre ≈ **~25 J** (η_descida ≈ 0,25).

A faixa é larga: com I_0 = 0,7 A seriam ~37 J; com I_0 = 1,3 A, ~11 J.

## C-103 — Energia de subida e eficiência de ida e volta (estim.)
Com a subida a 0,10 m/s (C-108): E_subida ≈ **~270 J**.

η_ciclo = E_gen / E_subida ≈ **0,09**. Mesma ordem de grandeza das versões
anteriores (~0,10). É o que o painel mede e mostra.

## C-104 — Tração no cordão, torque e margem para retroacionar
Sem talha: T_cordão = m·g = 58,9 N; τ_tambor = 58,9 × 0,015 = **0,88 N·m** no
mandril. A parafusadeira chega a 30 N·m: folga enorme para subir.

**Margem para a massa descer sozinha** = τ_massa / τ_atrito ≈ 13,2 / 7,8 ≈
**1,7×** (1,3× a 2,4× conforme o I_0 real).

| Massa | Tambor | Margem | `KE_MASSA` (V por m/s) | Desce sozinha? |
|-------|--------|--------|------------------------|----------------|
| 2 kg | Ø 30 mm | ~0,6× | 21,8 | não |
| 6 kg | Ø 26 mm | ~1,5× | 25,2 | provável |
| **6 kg** | **Ø 30 mm** | **~1,7×** | **21,8** | **sim (escolha)** |
| 6 kg | Ø 35 mm | ~2,0× | 18,7 | sim, mas o LED vermelho só a 0,20 m/s |

Cordão de 2 mm com ruptura ≥ 100 kg: fator de segurança ~17.

## C-105 — Relação de transmissão
- Sem talha: o cordão corre na mesma velocidade da massa.
- Tambor Ø 30 mm: 1 volta = 94,2 mm de massa.
- Redutor da parafusadeira na 1ª marcha: ~1:42.

ω_motor = (v / r) · i = 2.800 · v (rad/s). 1 cm de massa ≈ 4,5 voltas do
motor.

Cordão no tambor: 1,70 m / 94,2 mm ≈ 18 voltas + 3 mortas = 21 voltas ×
passo 2,5 mm ≈ **53 mm de largura útil** (imprimir com 60 mm).

## C-106 — Resolução do encoder
O motor da parafusadeira não tem encoder. Entra um LPD3806-600BM no eixo do
tambor: 600 pulsos × 4 (quadratura) = 2.400 contagens por volta = 94,2 mm
→ **0,0393 mm por contagem** (`MM_POR_PULSO`). O curso soma ~43.300
contagens (ESP32Encoder acumula os estouros do PCNT). A 0,30 m/s chegam
~7.600 contagens/s, folgado.

## C-107 — Tensão e potência geradas por velocidade (estim.)
E_fcem = K_e · ω_motor = 0,0078 × 2.800 · v ≈ **21,8 · v** (V) →
`KE_MASSA = 21.8`

| v (m/s) | Duração da descida (s) | Tambor / motor (rpm) | Tensão (V) | P gerada (W) | O que acende |
|---------|------------------------|----------------------|------------|--------------|--------------|
| 0,06 | 28 | 38 / 1.604 | 1,3 | ~0,8 | nada (frenagem máxima) |
| 0,10 | 17 | 64 / 2.674 | 2,2 | ~1,4 | LED verde |
| 0,12 | 14 | 76 / 3.209 | 2,6 | ~1,7 | verde + amarelo (limiar) |
| 0,15 | 11 | 95 / 4.011 | 3,3 | ~2,2 | verde + amarelo |
| **0,18** | **9,4** | **115 / 4.813** | **3,9** | **~2,7** | **os 3 LEDs (ponto de projeto)** |
| 0,30 | 5,7 | 191 / 8.021 | 6,6 | ~4,5 | limite de falha |

A potência é maior que nas versões anteriores (a massa é de 6 kg e desce
mais rápido), mas a tensão é baixa: o motor 550 gera pouca tensão por
rotação e o redutor tem só ~1:42. Por isso os LEDs têm limiares baixos
(2 / 2,6 / 3,8 V, ver `../02_ARQUITETO/circuito.md`).

## Por que só LEDs, sem USB (DEC-022)
Continua valendo: ~2,7 W a ~3,9 V, abaixo dos 5 V de uma USB, durante ~9 s.
Um conversor elevador daria 5 V, mas por poucos segundos; não vale para o
MVP.

## C-108 — Subida
Torque no motor: 0,883 / (0,90 × 0,75 × 42) ≈ 31 mN·m → I ≈ 31 / 7,8 + I_0
≈ **5,0 A** no motor.

A 0,10 m/s: E_fcem = 2,2 V; V_motor ≈ 2,2 + 5,0 × 0,2 ≈ 3,2 V → **PWM
~27 %** em 12 V (`PWM_SUBIDA = 68`), ~16 W, 17 s → **~270 J** por subida.
Do lado da fonte (onde fica o INA219 nº 1) a corrente é ~1,3 A.

Velocidade máxima de subida com o PWM limitado a 50 %: (6 − 1,0) / 21,8 ≈
**0,23 m/s**.

Motor travado: com 50 % de PWM, ~30 A no motor e ~15 A na fonte. A proteção
de massa travada corta acima de **3,0 A medidos na fonte** por 0,5 s
(`I_TRAVADO`); o PI sobe o PWM aos poucos, então ela age antes de o motor
passar de ~15 A. Fonte de **12 V 5 A** e fusível de 5 A.

## C-109 — Cargas do gerador
Na descida a corrente do gerador é quase fixa, porque é o torque que sobra
da massa que a impõe: I_gen ≈ (τ_massa − τ_atrito) / K_t ≈ **0,70 A**
(0,40 a 1,00 A conforme o I_0 real). A velocidade sai da resistência que o
gerador enxerga: v ≈ I_gen · (R_carga + R_a) / 21,8.

| Carga ligada | R vista | v estimada | Uso |
|--------------|---------|------------|-----|
| Carga fixa 5,6 Ω (sempre ligada) | ~5,8 Ω | 0,19 m/s (0,11 a 0,27) | descida sem controle: ESP32 desligado ou travado. Fica abaixo do limite de 0,30 m/s |
| 5,6 Ω ∥ 2,2 Ω (MOSFET 100 %) | ~1,8 Ω | ~0,057 m/s | frenagem máxima controlada |
| Curto pelo IBT-2 (dois lados baixos) | ~0,2 Ω | ~0,006 m/s | parada e falha (a massa escorrega ~3 mm até a lingueta pegar) |

O PWM do MOSFET varia entre as duas primeiras linhas; a malha PI escolhe o
ponto. Potência na carga fixa: até ~5,6 W; no 2,2 Ω: até ~2,2 W. Os dois de
10 W (cerâmicos). Os valores finais saem dos ensaios 4 e 5: se o I_0 real
for alto e a massa descer devagar demais, trocar a carga fixa por 8,2 Ω.
