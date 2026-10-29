# VALIDAÇÃO EXPERIMENTAL — MVP FABLAB

Nenhum ensaio feito. Cada etapa só começa quando a anterior passou. A massa
de 2 kg entra por último, com corda de segurança e nada embaixo do carrinho.

| # | Etapa | O que medir | Critério de aprovação |
|---|-------|-------------|-----------------------|
| **0** | **Motor na bancada, antes de comprar o resto** | (a) com o tambor de Ø 30 mm impresso no eixo e a anilha de 2 kg pendurada direto no cordão (a mesma montagem final, sem talha), soltar à mão: desce sozinho? (b) girar o eixo de saída com furadeira a ~100 rpm e medir a tensão em vazio; (c) resistência do enrolamento | (a) desce sem empurrão; (b) K_e entre 0,004 e 0,008 V·s/rad; se (a) falhar: tambor maior (Ø 40 mm), ou redução menor com o tambor pela regra Ø ≈ i/3, ou planetário 37 mm (DEC-024) |
| 1 | Só lógica, USB do notebook | Varredura I²C; contagens por volta do tambor; fins de curso; emergência | Acha 0x40 e 0x41; ~3.960 contagens/volta; leituras mudam |
| 2 | Motor sem cordão, 12 V com PWM limitado a 50 % | Corrente no INA219 nº 1 com PWM 20 a 50 %; curto pelo IBT-2 para o motor | Corrente coerente com C-108; nenhum movimento no boot; o firmware nunca passa de 50 % |
| 3 | Trava | Servo solta a lingueta com a mola montada; sem 5 V no servo a lingueta cai | Solta e engata 20 vezes seguidas |
| 4 | Gerador sem massa, girando à mão ou com furadeira | Polaridade no GEN; LEDs por limiar; tensão com 22 Ω e com 22 ∥ 6,8 Ω | LEDs acendem perto de 2; 3,3 e 4,4 V |
| 5 | Só o carrinho, depois a anilha de 2 kg, com corda de segurança | Ciclo manual; velocidade sem ESP32 (só carga fixa) e com frenagem 100 % | Sem ESP32 desce abaixo de 0,20 m/s; com frenagem 100 % abaixo de 0,05 m/s |
| 6 | 2 kg, ciclos completos | Ciclos manuais e automáticos; tensão × velocidade; energia de subida e de descida | Preencher a tabela abaixo; η_ciclo medido |

## Tabela de resultados (a preencher)

| Grandeza | Previsto | Medido | Erro | Arquivo de dados |
|----------|----------|--------|------|------------------|
| K_e (V·s/rad) | 0,006 | | | |
| Retroaciona com 2 kg no tambor de Ø 30 mm? | sim | | | |
| Tensão em vazio a 0,13 m/s (V) | 4,7 | | | |
| Potência gerada a 0,13 m/s (W) | ~0,76 | | | |
| v sem ESP32, carga fixa 22 Ω (m/s) | 0,10 a 0,18 | | | |
| v com frenagem 100 % (m/s) | ~0,04 | | | |
| Corrente de subida a 0,08 m/s, no motor / na fonte (A) | 1,23 / 0,42 | | | |
| Energia consumida na subida (J) | ~110 | | | |
| Energia gerada na descida (J) | ~9,9 | | | |
| η_ciclo | ~0,09 | | | |
| Consumo da eletrônica (W) | ~0,8 | | | |

Erro acima de 20 %: o FÍSICO revisa `premissas.md` e registra decisão em
`../00_MASTER/DECISOES.md`.
