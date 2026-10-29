# PREMISSAS FÍSICAS — MVP FABLAB

Porte decidido pelo Gabriel em 2026-10-29 e revisto no mesmo dia
(DEC-024): **2 kg e motor de 6 V**, 1,70 m de curso. Sem talha, tambor de
Ø 30 mm (DEC-025). Saída útil: só LEDs (DEC-022). Mesmas regras de unidades do
projeto principal (DEC-002: g = 9,81 m/s², SI).

| Variável | Valor | Unidade | Fonte | Validado? |
|----------|-------|---------|-------|-----------|
| g | 9,81 | m/s² | DEC-002 | ✅ |
| m_c | 2 | kg | DEC-024 (uma anilha de 2 kg) | ⏳ pesar com o carrinho |
| h (curso útil) | 1,70 | m | DEC-014 | ⏳ medir na torre |
| Talha | nenhuma (cordão direto do tambor ao carrinho) | — | DEC-025 | ✅ projeto |
| Diâmetro efetivo do tambor | 30 | mm | DEC-025 (canal Ø 28 + cordão 2 mm) | ⏳ medir 10 voltas |
| Raio efetivo r | 0,015 | m | idem | ⏳ |
| Redução do motorredutor i | 90 | — | DEC-024, motor de referência (o modelo encontrado pelo Gabriel ainda não foi informado) | ⏳ folha do vendedor |
| Rotação em vazio do motor (6 V) | ~9.600 | rpm | típico da família JGB37-520 de 6 V (≈ 107 rpm na saída 1:90) | ⏳ ensaio 0 |
| K_e = K_t | 0,006 | V·s/rad | 6 V / (9.600 rpm em rad/s) | ⏳ ensaio 0 |
| Resistência do enrolamento R_a | ~1 | Ω | típico de 6 V (1/4 do motor de 12 V da mesma potência) | ⏳ multímetro |
| Corrente em vazio I_0 | ~0,3 | A | típico de 6 V (o dobro do de 12 V) | ⏳ |
| Encoder Hall do motor | 11 | pulsos/volta do motor | DEC-015 | ⏳ contar no ensaio 1 |
| η do cordão no tambor e no mancal 608 | 0,90 | — | estimativa (mantida, a favor da segurança) | ⏳ |
| η redutor, subida (retas, 1:90) | 0,65 | — | estimativa | ⏳ |
| η redutor, descida (retas, 1:90) | 0,55 | — | estimativa, pior no sentido reverso | ⏳ ensaio 0 |
| η motor e η gerador | 0,60 | — | estimativa (motor pequeno) | ⏳ |
| Velocidade de subida | 0,08 | m/s | C-108 | ⏳ |
| Velocidade-alvo de descida | 0,06 a 0,13 | m/s | C-107 | ⏳ |
| Limite de velocidade | 0,20 | m/s | proteção | ✅ projeto |
| Consumo da eletrônica | ~0,8 | W | ESP32 com Wi-Fi + INA219 + servo parado | ⏳ |

## Premissas de modelo
Iguais às do projeto principal (`01_FISICA/premissas.md` na raiz), com três
diferenças:

- **Redutor de engrenagens retas.** Rende menos que o planetário e rende
  ainda menos no sentido reverso (descida). O risco principal do MVP é o
  redutor não retroacionar com 2 kg: a massa não desce sozinha. Sem a talha
  e com o tambor de Ø 30 mm, o torque no tambor fica igual ao do porte
  anterior de 6 kg (0,294 N·m), então o risco é o mesmo, não maior (C-104). Por isso o
  ensaio 0 (`validacao_experimental.md`) vem antes de qualquer outra compra,
  e é ele que fecha a escolha do motor.
- **Cordão no lugar do cabo de aço.** Dyneema ou poliéster trançado de 2 mm
  estica um pouco sob carga; isso só aparece como erro de posição de poucos
  milímetros, corrigido no fim de curso inferior a cada ciclo.
- **Motor de 6 V alimentado pela fonte de 12 V.** A fonte continua de 12 V
  porque os reguladores de 5 V (ESP32 e servo) precisam de mais de ~6,5 V na
  entrada. O firmware limita o PWM do motor a 50 % (`PWM_MAX = 128`, 6 V em
  média). A tensão gerada fica sempre abaixo dos 12 V da fonte.
- **Encoder no motor, não no tambor.** Mede bem a velocidade, mas não vê
  escorregamento do cordão. Os fins de curso zeram a posição.

## Se o motor mudar
Todo o resto deste arquivo depende do motor só por quatro números: i, K_e,
R_a e I_0. Regra prática para outra redução: manter **Ø do tambor (mm) ≈
i / 3** (1:60 → Ø 20; 1:90 → Ø 30; 1:150 → Ø 50), o que mantém o torque
para retroacionar e a tensão por velocidade. Com outro motor, refazer
`KE_MASSA = K_e × i / r` (C-107), a corrente de subida (C-108) e as cargas
(C-109), e trocar as constantes do firmware
(`../03_SOFTWARE/adaptacao_firmware.md`).
