# VALIDAÇÃO EXPERIMENTAL — MVP FABLAB

Nenhum ensaio feito. Cada etapa só começa quando a anterior passou. A massa
de 6 kg entra por último, com corda de segurança e nada embaixo do carrinho.

| # | Etapa | O que medir | Critério de aprovação |
|---|-------|-------------|-----------------------|
| **0** | **Parafusadeira na bancada, antes de comprar o resto** | (a) tirar a trava Auto-Lock; com o motor desligado, girar o mandril à mão: gira e leva o motor junto? (b) 1ª marcha, embreagem na posição de furar; tambor de Ø 30 mm no mandril e 6 kg pendurados direto no cordão: desce sozinho? (c) contar as voltas do motor por volta do mandril (redução i); (d) girar o mandril com outra furadeira a ~100 rpm e medir a tensão no motor; (e) corrente em vazio com 12 V | (a) gira sem travar; (b) desce sem empurrão; (c) i entre 35 e 50; (d) K_e entre 0,005 e 0,010 V·s/rad; (e) I_0 abaixo de ~1,3 A. Se (b) falhar: tambor Ø 35 mm, ou mais massa |
| 1 | Só lógica, USB do notebook | Varredura I²C; contagens por volta do tambor; fins de curso; emergência | Acha 0x40 e 0x41; ~2.400 contagens/volta; leituras mudam |
| 2 | Motor sem cordão, 12 V com PWM até 50 % | Corrente no INA219 nº 1 com PWM 15 a 50 %; curto pelo IBT-2 para o motor | Corrente coerente com C-108; nenhum movimento no boot; o firmware nunca passa de 50 % |
| 3 | Trava | Servo solta a lingueta com a mola montada; sem 5 V no servo a lingueta cai | Solta e engata 20 vezes seguidas |
| 4 | Gerador sem massa, girando o mandril com outra furadeira | Polaridade no GEN; LEDs por limiar; tensão com 5,6 Ω e com 5,6 ∥ 2,2 Ω | LEDs acendem perto de 2; 2,6 e 3,8 V |
| 5 | Só o carrinho, depois uma anilha de 2 kg e depois 6 kg, com corda de segurança | Ciclo manual; velocidade sem ESP32 (só carga fixa) e com frenagem 100 % | Com 6 kg e sem ESP32 desce abaixo de 0,30 m/s; com frenagem 100 % abaixo de 0,08 m/s |
| 6 | 6 kg, ciclos completos | Ciclos manuais e automáticos; tensão × velocidade; energia de subida e de descida | Preencher a tabela abaixo; η_ciclo medido |

## Tabela de resultados (a preencher)

| Grandeza | Previsto | Medido | Erro | Arquivo de dados |
|----------|----------|--------|------|------------------|
| Redução da 1ª marcha i | ~42 | | | |
| K_e (V·s/rad) | ~0,0078 | | | |
| R_a (Ω) | ~0,2 | | | |
| I_0 com 12 V (A) | ~1,0 | | | |
| Retroaciona com 6 kg no tambor de Ø 30 mm? | sim (margem ~1,7×) | | | |
| Tensão gerada a 0,18 m/s (V) | 3,9 | | | |
| Potência gerada a 0,18 m/s (W) | ~2,7 | | | |
| v sem ESP32, carga fixa 5,6 Ω (m/s) | 0,11 a 0,27 | | | |
| v com frenagem 100 % (m/s) | ~0,06 | | | |
| Corrente de subida a 0,10 m/s, no motor / na fonte (A) | 5,0 / 1,3 | | | |
| Energia consumida na subida (J) | ~270 | | | |
| Energia gerada na descida (J) | ~25 (11 a 37) | | | |
| η_ciclo | ~0,09 | | | |
| Consumo da eletrônica (W) | ~0,8 | | | |

Erro acima de 20 %: o FÍSICO revisa `premissas.md` e registra decisão em
`../00_MASTER/DECISOES.md`.
