# GLOSSÁRIO E NOMENCLATURA ÚNICA

## GRANDEZAS

| Termo oficial | Símbolo | Unidade SI | Valor no projeto | Sinônimos PROIBIDOS |
|---------------|---------|------------|------------------|---------------------|
| Massa do contrapeso | m_c | kg | 20 | peso, carga, lastro |
| Curso útil | h | m | 1,70 | altura, distância |
| Altura instantânea da massa | h(t) | m | 0 a 1,70 | posição do peso |
| Nível de carga gravitacional | N | % | 0 a 100 | carga, SOC |
| Energia potencial teórica | E_teo | J | 333,5 | energia bruta |
| Energia nos terminais do gerador | E_gen | J | ~173 (estim.) | energia gerada bruta |
| Energia útil entregue | E_util | J | ~147 na USB (estim.) | energia líquida |
| Eficiência ciclo ida/volta | η_ciclo | adimensional (0-1) | ~0,27 (estim.) | rendimento |
| Velocidade da massa | v | m/s | 0,03 a 0,08 na descida | velocidade do peso |
| Velocidade angular do tambor | ω | rad/s | — | RPM (usar só na UI) |
| Constante do motor | K_e = K_t | V·s/rad = N·m/A | 0,076 (a medir) | — |
| Tarifa atual | T | R$/kWh | 0 a 2 | preço |
| Demanda da saída | D | W | 0 a 10 | demanda da casa |
| Comando fuzzy | u | adimensional | −100 a +100 | saída do fuzzy |

N = (h − h_min) / (h_max − h_min) × 100 %, com h_min = 0 e h_max = 1,70 m.

## COMPONENTES (um nome por peça)

| Nome oficial | O que é | Não chamar de |
|--------------|---------|---------------|
| Motorredutor | Motor DC 24 V + redutor planetário 1:50; sobe e gera | gerador DC, alternador, guincho |
| Tambor | Cilindro Ø 60 mm no topo que enrola o cabo | polia, guincho |
| Talha 2:1 | Polia fixa no topo + polia móvel no carrinho | — |
| Carrinho | Bandeja que leva a massa entre as colunas-guia | plataforma |
| Trava de catraca | Roda dentada + lingueta + solenoide | freio, freio eletromagnético |
| Carga de frenagem | 2 × 22 Ω 25 W (11 Ω) + MOSFET em PWM | dump, freio |
| Barramento gerado (GEN) | Nó alimentado pelo motor na descida | — |
| 24V_POT | 24 V depois do relé de corte K1 | — |
| K1 | Relé de corte (GPIO 27) | — |
| K2 | Relé de modo, 2 canais = DPDT (GPIO 23) | — |
| K4 | Relé de sondagem da USB (GPIO 13) | — |
| Saída USB | Buck 8–35 V → 5,3 V + porta USB-A | carga |

## ESTADOS DO FIRMWARE
`MANTER`, `SUBINDO`, `PREP_DESCIDA`, `DESCENDO`, `PARANDO`, `FALHA`,
`REARME`. "Manter" = motor desligado e trava engatada (não usar "standby").

## REGRAS
- Sempre SI em cálculos; converter só na interface do dashboard (ver DEC-002)
- g = 9,81 m/s² fixado (ver DEC-002)
- "energia" sem qualificador = E_util (a que chega na carga)
- "carga" sozinho é ambíguo: usar "nível de carga" (energia armazenada) ou
  "saída USB" / "carga de frenagem" (carga elétrica)
- Valores marcados "estim." vêm de rendimentos estimados e precisam de ensaio
  (`01_FISICA/validacao_experimental.md`)
