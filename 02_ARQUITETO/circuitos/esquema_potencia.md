# ESQUEMA DE POTÊNCIA

## TENSÕES ENVOLVIDAS
- Barramento: 24 V
- Motor: 24 V / 10 A pico
- Lógica: 5 V e 3,3 V (via buck)

## DIAGRAMA DE BLOCOS
[ASCII ou Mermaid]

## CÁLCULO DE COMPONENTES
### Fusível principal
I_pico = 12 A → fusível 15 A slow-blow
### Diodo de flyback (motor DC)
Vrrm ≥ 2×24 = 48 V → 1N5822 (40V, 3A) ou SS54 (40V, 5A)

## PROTEÇÕES OBRIGATÓRIAS
- [x] Fusível geral
- [x] Diodo flyback no motor
- [x] TVS na entrada do ESP32
- [x] Optoacoplador entre lógica e potência
- [x] Pull-down nos gates de MOSFET

## BOM
| Item | Espec | Qtd | Preço | Fornecedor |
|------|-------|-----|-------|------------|