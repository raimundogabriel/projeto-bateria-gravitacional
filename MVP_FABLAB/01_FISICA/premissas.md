# PREMISSAS FÍSICAS — MVP FABLAB

Porte decidido pelo Gabriel em 2026-10-29 (DEC-026): **parafusadeira Bosch
GSR 1440-LI inteira** (motor de 14,4 V + redutor planetário + mandril), sem
a trava Auto-Lock, com **6 kg de anilhas** e 1,70 m de curso. Sem talha,
tambor de Ø 30 mm (DEC-025). Saída útil: só LEDs (DEC-022). Mesmas regras de
unidades do projeto principal (DEC-002: g = 9,81 m/s², SI).

Os dados do motor não vêm de uma folha de dados da Bosch (não foi achada):
são de um motor 550 equivalente da Mabuchi (RS-550VC-7525, 12 V) escalado
para 14,4 V, e da rotação em vazio da parafusadeira no manual. Todos saem do
ensaio 0.

| Variável | Valor | Unidade | Fonte | Validado? |
|----------|-------|---------|-------|-----------|
| g | 9,81 | m/s² | DEC-002 | ✅ |
| m_c | 6 | kg | DEC-026 (anilhas que o grupo já tem) | ⏳ pesar com o carrinho |
| h (curso útil) | 1,70 | m | DEC-014 | ⏳ medir na torre |
| Talha | nenhuma (cordão direto do tambor ao carrinho) | — | DEC-025 | ✅ projeto |
| Diâmetro efetivo do tambor | 30 | mm | DEC-025 (canal Ø 28 + cordão 2 mm) | ⏳ medir 10 voltas |
| Raio efetivo r | 0,015 | m | idem | ⏳ |
| Rotação em vazio no mandril, 1ª marcha | 0–420 | rpm | manual Bosch GSR 1440-LI (14,4 V) | ✅ catálogo |
| Rotação em vazio do motor (14,4 V) | ~17.600 | rpm | Mabuchi RS-550VC-7525 escalado | ⏳ ensaio 0 |
| Redução da 1ª marcha i | ~42 | — | 17.600 / 420 | ⏳ contar voltas do motor por volta do mandril |
| K_e = K_t | ~0,0078 | V·s/rad | 14,4 V / (17.600 rpm em rad/s) | ⏳ ensaio 0 |
| Resistência do motor R_a | ~0,2 | Ω | Mabuchi 12 V (0,14 Ω) escalado | ⏳ medir (baixa: usar 4 fios ou fonte limitada) |
| Corrente em vazio I_0 | ~1,0 (0,7 a 1,3) | A | Mabuchi 12 V (1,2 A) escalado | ⏳ ensaio 0 |
| Encoder | LPD3806-600BM no eixo do tambor, 600 pulsos/volta | — | DEC-026 (o motor da parafusadeira não tem encoder) | ⏳ ensaio 1 |
| η do cordão no tambor e no mancal 608 | 0,90 | — | estimativa | ⏳ |
| η redutor planetário, subida | 0,75 | — | estimativa | ⏳ |
| η redutor planetário, descida | 0,70 | — | estimativa | ⏳ ensaio 0 |
| Velocidade de subida | 0,10 | m/s | C-108 | ⏳ |
| Velocidade-alvo de descida | 0,10 a 0,18 | m/s | C-107 | ⏳ |
| Limite de velocidade | 0,30 | m/s | proteção | ✅ projeto |
| Consumo da eletrônica | ~0,8 | W | ESP32 com Wi-Fi + INA219 + servo parado | ⏳ |

## Premissas de modelo
Iguais às do projeto principal (`01_FISICA/premissas.md` na raiz), com estas
diferenças:

- **Atrito interno do motor.** O motor de parafusadeira gasta ~1 A só para
  girar em vazio (escovas e ventoinha), equivalente a ~7,8 mN·m de atrito.
  A massa precisa vencer esse atrito para descer e gerar. Com 6 kg no tambor
  de Ø 30 mm, ela aplica ~13,2 mN·m no motor: margem de ~1,7× (C-104). Com
  2 kg a margem seria ~0,6× e a massa não desceria; por isso a massa voltou
  a 6 kg.
- **Regra de projeto.** margem × `KE_MASSA` ≈ m·g·η_descida / I_0. Para o
  mesmo motor, mais massa dá mais margem ou mais tensão; o tambor escolhe
  entre as duas (tambor maior: mais margem, menos tensão).
- **Trava Auto-Lock removida.** A linha GSR da Bosch trava o mandril
  quando o gatilho está solto. Sem tirar a trava, a massa nunca gira o
  redutor (ensaio 0).
- **Motor de 14,4 V na fonte de 12 V.** O motor gira a ~83 % da rotação
  nominal com 12 V. O firmware limita o PWM a 50 % (`PWM_MAX = 128`), não
  pelo motor, mas para a subida nunca passar de ~0,23 m/s.
- **Cordão no lugar do cabo de aço.** Dyneema ou poliéster trançado de 2 mm
  estica um pouco sob carga; isso só aparece como erro de posição de poucos
  milímetros, corrigido no fim de curso inferior a cada ciclo.
- **Encoder no eixo do tambor.** Mede a posição direto no tambor, sem a
  folga do redutor. Não vê escorregamento do cordão; os fins de curso zeram
  a posição.

## Se o motor ou o redutor mudarem
Tudo depende de quatro números: i, K_e, R_a e I_0. Refazer
`KE_MASSA = K_e × i / r` (C-107), a margem de retroação (C-104), a corrente
de subida (C-108) e as cargas (C-109), e trocar as constantes do firmware
(`../03_SOFTWARE/adaptacao_firmware.md`). Se o ensaio 0 medir I_0 bem acima
de 1,3 A, a massa pode não descer: aumentar o tambor (Ø 35 mm) ou a massa.
