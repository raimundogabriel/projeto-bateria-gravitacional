# VALIDAÇÃO EXPERIMENTAL — MVP FABLAB

Nenhum ensaio feito. Cada etapa só começa quando a anterior passou. A massa
de 5 kg entra por último, com corda de segurança e nada embaixo do carrinho.

| # | Etapa | O que medir | Critério de aprovação |
|---|-------|-------------|-----------------------|
| **0** | **Motor na bancada, antes de comprar o resto** | (a) com o tambor impresso no eixo e 2,5 kg pendurados direto no cordão (sem talha, mesmo torque que 5 kg com talha), soltar à mão: desce sozinho? (b) girar o eixo de saída com furadeira a ~100 rpm e medir a tensão em vazio; (c) resistência do enrolamento | (a) desce sem empurrão com 2,5 kg pendurados direto (= 5 kg com talha); (b) K_e entre 0,009 e 0,015 V·s/rad; se (a) falhar, trocar por 1:50 ou planetário (DEC-015) |
| 1 | Só lógica, USB do notebook | Varredura I²C; contagens por volta do tambor; fins de curso; emergência | Acha 0x40 e 0x41; ~3.960 contagens/volta; leituras mudam |
| 2 | Motor sem cordão, 12 V | Corrente no INA219 nº 1 com PWM 30 a 80 %; curto pelo IBT-2 para o motor | Corrente coerente com C-108; nenhum movimento no boot |
| 3 | Trava | Servo solta a lingueta com a mola montada; sem 5 V no servo a lingueta cai | Solta e engata 20 vezes seguidas |
| 4 | Gerador sem massa, girando à mão ou com furadeira | Polaridade no GEN; LEDs por limiar; tensão com 120 Ω e com 120 ∥ 22 Ω | LEDs acendem perto de 2, 6 e 10 V; nada vai à fonte de 12 V abaixo de 12 V |
| 5 | 2,5 kg com corda | Ciclo manual; velocidade sem ESP32 (só carga fixa) e com frenagem 100 % | Sem ESP32 desce abaixo de 0,07 m/s; com frenagem 100 % abaixo de 0,02 m/s |
| 6 | 5 kg com corda | Ciclos manuais e automáticos; tensão × velocidade; energia de subida e de descida | Preencher a tabela abaixo; η_ciclo medido |

## Tabela de resultados (a preencher)

| Grandeza | Previsto | Medido | Erro | Arquivo de dados |
|----------|----------|--------|------|------------------|
| K_e (V·s/rad) | 0,0119 | | | |
| Retroaciona com 5 kg? | sim | | | |
| Tensão em vazio a 0,05 m/s (V) | 10,7 | | | |
| Potência gerada a 0,05 m/s (W) | ~0,7 | | | |
| v sem ESP32, carga fixa 120 Ω (m/s) | 0,04 a 0,06 | | | |
| v com frenagem 100 % (m/s) | ~0,01 | | | |
| Corrente de subida a 0,03 m/s (A) | 0,54 | | | |
| Energia consumida na subida (J) | 140 a 155 | | | |
| Energia gerada na descida (J) | ~14,6 | | | |
| η_ciclo | ~0,10 | | | |
| Consumo da eletrônica (W) | ~0,8 | | | |

Erro acima de 20 %: o FÍSICO revisa `premissas.md` e registra decisão em
`../00_MASTER/DECISOES.md`.
