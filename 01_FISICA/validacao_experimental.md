# VALIDAÇÃO EXPERIMENTAL

Nenhum ensaio foi feito ainda: o protótipo não está montado. Este arquivo é o
plano e a tabela a preencher (HANDOFF-006).

## Ordem dos ensaios
Cada etapa só começa quando a anterior passou. A massa de 20 kg entra por
último, sempre com corda de segurança.

| # | Etapa | O que medir | Critério de aprovação |
|---|-------|-------------|-----------------------|
| 1 | Só lógica, sem 24 V | Varredura I²C; pulsos por volta; fins de curso e emergência | Acha 0x40, 0x41, 0x44, 0x68, 0x27; ~2.400 pulsos/volta; leituras mudam |
| 2 | Relés sem carga | Pulso no boot; emergência | Nenhum relé pulsa no boot; todos caem com a emergência |
| 3 | Motor sem cabo | Corrente no INA226 nº 1 com PWM 20 a 60 % | Corrente coerente com C-008, sem disparo de travamento |
| 4 | Gerador sem massa | Polaridade no GEN; tensão × rotação (150, 300, 450 rpm no tambor ou equivalente); frenagem; celular na USB | K_e ≈ 0,076 V·s/rad (±20 %); celular aceita a USB |
| 5 | Trava | Corrente do solenoide a 100 % e 30 %; puxa a lingueta com a mola | Solta a lingueta; corrente de retenção ~10 % da nominal |
| 6 | Massa de 5 kg, com corda | Ciclo manual; velocidade com frenagem 100 % | Escolher entre 22 Ω e 11 Ω (DEC-010) |
| 7 | Massa de 20 kg, com corda | Ciclos manuais e automáticos; tensão × velocidade; energia de subida e de descida | Refazer o Quadro 5 com dados medidos; medir η_ciclo |

## Tabela de resultados (a preencher)

| Grandeza | Previsto | Medido | Erro | Arquivo de dados |
|----------|----------|--------|------|------------------|
| K_e (V·s/rad) | 0,076 | | | |
| Tensão em vazio a 0,05 m/s (V) | 12,7 | | | |
| Potência gerada a 0,05 m/s (W) | 5,1 | | | |
| Potência na USB a 0,05 m/s (W) | 4 a 5 | | | |
| Velocidade com frenagem 100 %, 11 Ω (m/s) | 0,025 | | | |
| Corrente de subida a 0,05 m/s (A) | 0,8 | | | |
| Energia consumida na subida (J) | ~640 (333,5 / 0,52) | | | |
| Energia gerada na descida (J) | ~173 | | | |
| η_ciclo | 0,27 | | | |
| Consumo da eletrônica (W) | ~1 | | | |
| Corrente do solenoide 100 % / 30 % (A) | — / ~10 % da potência | | | |

Critério de revisão: se um valor medido divergir mais de 20 % do previsto,
o FÍSICO revisa as premissas e registra uma decisão em
`00_MASTER/DECISOES.md`.
