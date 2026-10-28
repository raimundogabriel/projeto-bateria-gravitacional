# CÁLCULOS DE ENERGIA

Premissas em `01_FISICA/premissas.md`. Valores "estim." dependem de
rendimentos estimados e serão conferidos em `validacao_experimental.md`.

> A versão inicial trazia C-001 com 500 kg e 3 m (14,7 kJ). Esse cálculo foi
> substituído pelo abaixo (DEC-001).

## C-001 — Energia potencial teórica
**Premissas:** m = 20 kg, h = 1,70 m, g = 9,81 m/s²
**Equação:** E_teo = m·g·h
**Substituição:** E_teo = 20 × 9,81 × 1,70 = 333,5 J
**Resultado:** 333,5 J = 0,093 Wh
**Sanity check:** ≈ 0,6 % de uma bateria de celular de 15 Wh ✓ (ordem de
grandeza de um protótipo didático)
**Sensibilidade:** ±1 kg em m → ±16,7 J; ±5 cm em h → ±9,8 J

## C-002 — Energia nos terminais do gerador (estim.)
**Equação:** E_gen = E_teo · η_polias · η_redutor · η_gerador
**Substituição:** 333,5 × 0,92 × 0,75 × 0,75 = 333,5 × 0,5175
**Resultado:** ≈ 173 J (0,048 Wh)

## C-003 — Energia entregue na porta USB (estim.)
**Equação:** E_util = E_gen · η_buck
**Substituição:** 173 × 0,85
**Resultado:** ≈ 147 J (0,041 Wh), cerca de 0,3 % de uma bateria de 15 Wh

## C-004 — Eficiência de ida e volta (estim.)
**Equação:** η_ciclo = (η_polias·η_redutor·η_motor)_subida ×
(η_polias·η_redutor·η_gerador)_descida
**Substituição:** 0,52 × 0,52
**Resultado:** η_ciclo ≈ 0,27 → ≈ 90 J (0,025 Wh) devolvidos por ciclo
**Observação:** o relatório original citava 40 % a 60 % sem fonte (INC-018).

## C-005 — Tração no cabo e torque no tambor
**Equações:** T_cabo = m·g / 2 (talha 2:1); τ_tambor = T_cabo · r
**Substituição:** T_cabo = 20 × 9,81 / 2 = 98 N; τ = 98 × 0,030 = 2,9 N·m
**Resultado:** 98 N no cabo, 2,9 N·m no tambor. Motorredutor com ≥ 6 N·m
nominal dá fator 2.
**Sanity check:** cabo de 3 mm 7×19 rompe com ~5 kN → fator de segurança ~50.

## C-006 — Relação de transmissão
- Talha 2:1: o cabo corre o dobro da velocidade da massa.
- Tambor Ø 60 mm: 1 volta = 188 mm de cabo = 94 mm de massa.
- Redutor 1:50.
**Resultado:** relação total 100:1; 1 cm de descida ≈ 5,3 voltas do motor.
**Rotação do motor:** n_motor = (2·v / (π·D)) · 60 · 50 → a 0,05 m/s,
tambor a 32 rpm e motor a 1.592 rpm.

## C-007 — Tensão e potência geradas por velocidade (Quadro 5)
**Equações:** ω_motor = 2·v / r · 50 = 3.333·v (rad/s);
E_fcem = K_e · ω_motor = 0,076 × 3.333 · v ≈ 253 · v (V);
P_el ≈ m·g·v · 0,92 · 0,75 · 0,75

| v (m/s) | Duração da descida (s) | Tambor / motor (rpm) | Tensão em vazio (V) | P gerada (W) | Uso |
|---------|------------------------|----------------------|---------------------|--------------|-----|
| 0,01 | 170 | 6 / 318 | 2,5 | ~1,0 | só LED direto |
| 0,03 | 57 | 19 / 955 | 7,6 | ~3,0 | LEDs; abaixo da entrada do buck USB |
| 0,05 | 34 | 32 / 1.592 | 12,7 | ~5,1 | **celular via USB (ponto de projeto)** |
| 0,07 | 24 | 45 / 2.228 | 17,7 | ~7,1 | celular + LEDs |
| 0,09 | 19 | 57 / 2.865 | 22,8 | ~9,1 | excedente vai à frenagem |

**Conclusão:** para a USB, a descida precisa ficar acima de ~0,04 m/s
(~10 V em vazio), porque o buck pede ≥ 8 V. A constante `KE_MASSA = 253` do
firmware vem daqui.

## C-008 — Subida
**Equação:** P_mec = m·g·v; I ≈ P_mec / (24 V · η_motor · η_redutor · η_polias) + I_0
**Ponto de operação do firmware:** 0,05 m/s pede ~13 V no motor (PWM ~55 %) e
~0,8 A. Com 24 V, o máximo fica perto de 0,09 m/s (~18 W mecânicos, ~1,5 A).
**Observação:** a partida pode pedir o dobro da corrente de regime; o
firmware faz rampa de PWM de 1 s.

## C-009 — Consumo da trava na descida (estim.)
Hit-and-hold (100 % por 300 ms, depois 30 %): a potência cai para ~10 % da
nominal (P ∝ I²). Com solenoide de ~15 W: ~1,5 W × 34 s ≈ 50 J por descida,
contra ~173 J gerados. Medir a corrente real nas duas fases.

## C-010 — Resolução do encoder
600 pulsos × 4 (quadratura) = 2.400 contagens por volta do tambor = 94,25 mm
de massa → 0,0393 mm por contagem (`MM_POR_PULSO`). O curso de 1,70 m soma
~43.300 contagens, acima dos 32.767 do PCNT de 16 bits → acumular estouros em
software (ESP32Encoder).
