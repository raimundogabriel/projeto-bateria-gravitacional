# PREMISSAS FÍSICAS — MVP FABLAB

Variante A (recomendada, DEC-014). Valores da variante B (10 kg, 1,2 m) ficam
em `calculos_energia.md`, seção "Variante B". Mesmas regras de unidades do
projeto principal (DEC-002: g = 9,81 m/s², SI).

| Variável | Valor | Unidade | Fonte | Validado? |
|----------|-------|---------|-------|-----------|
| g | 9,81 | m/s² | DEC-002 | ✅ |
| m_c | 5 | kg | DEC-014 (galão de 5 L com água) | ⏳ pesar com o carrinho |
| h (curso útil) | 1,00 | m | DEC-014 | ⏳ medir na torre |
| Talha | 2:1 | — | DEC-016 | ✅ projeto |
| Diâmetro efetivo do tambor | 20 | mm | DEC-016 (canal Ø 18 + cordão 2 mm) | ⏳ medir 10 voltas |
| Raio efetivo r | 0,010 | m | idem | ⏳ |
| Redução do motorredutor i | 90 | — | DEC-015 (JGB37-520 ou equivalente) | ⏳ folha do vendedor |
| Rotação em vazio do motor (12 V) | ~9.600 | rpm | típico da família (≈ 107 rpm na saída 1:90) | ⏳ ensaio 0 |
| K_e = K_t | 0,0119 | V·s/rad | 12 V / (9.600 rpm em rad/s) | ⏳ ensaio 0 |
| Resistência do enrolamento R_a | ~4 | Ω | típico | ⏳ multímetro |
| Corrente em vazio I_0 | ~0,15 | A | típico | ⏳ |
| Encoder Hall do motor | 11 | pulsos/volta do motor | DEC-015 | ⏳ contar no ensaio 1 |
| η polias (impressas, com 608) | 0,90 | — | estimativa | ⏳ |
| η redutor, subida (retas, 1:90) | 0,65 | — | estimativa | ⏳ |
| η redutor, descida (retas, 1:90) | 0,55 | — | estimativa, pior no sentido reverso | ⏳ ensaio 0 |
| η motor e η gerador | 0,60 | — | estimativa (motor pequeno) | ⏳ |
| Velocidade de subida | 0,03 | m/s | C-108 | ⏳ |
| Velocidade-alvo de descida | 0,02 a 0,05 | m/s | C-107 | ⏳ |
| Limite de velocidade | 0,07 | m/s | proteção | ✅ projeto |
| Consumo da eletrônica | ~0,8 | W | ESP32 com Wi-Fi + INA219 + servo parado | ⏳ |

## Premissas de modelo
Iguais às do projeto principal (`01_FISICA/premissas.md` na raiz), com três
diferenças:

- **Redutor de engrenagens retas.** Rende menos que o planetário e rende
  ainda menos no sentido reverso (descida). O risco principal do MVP é o
  redutor não retroacionar com 5 kg: a massa não desce sozinha. Por isso o
  ensaio 0 (`validacao_experimental.md`) vem antes de qualquer outra compra.
- **Cordão no lugar do cabo de aço.** Dyneema ou poliéster trançado de 2 mm
  estica um pouco sob carga; isso só aparece como erro de posição de poucos
  milímetros, corrigido no fim de curso inferior a cada ciclo.
- **Encoder no motor, não no tambor.** Mede bem a velocidade, mas não vê
  escorregamento do cordão. Os fins de curso zeram a posição.
