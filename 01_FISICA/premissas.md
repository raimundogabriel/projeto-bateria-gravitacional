# PREMISSAS FÍSICAS

| Variável | Valor | Unidade | Fonte | Validado? |
|----------|-------|---------|-------|-----------|
| g | 9,81 | m/s² | SI (DEC-002) | ✅ |
| m_c | 20 | kg | DEC-001 | ⏳ pesar a massa montada |
| h (curso útil) | 1,70 | m | DEC-001 | ⏳ medir na torre |
| Raio do tambor r | 0,030 | m | DEC-003 (Ø 60 mm, camada única) | ⏳ |
| Talha | 2:1 | — | DEC-003 | ✅ projeto |
| Redução do motorredutor i | 50 | — | DEC-003 | ⏳ folha de dados |
| Relação total massa → motor | 100:1 | — | talha × redutor | ✅ projeto |
| K_e = K_t | 0,076 | V·s/rad | motor 24 V 3.000 rpm (típico) | ⏳ ensaio de bancada |
| Corrente em vazio I_0 | ~0,5 | A | típico | ⏳ |
| η polias | 0,92 | — | estimativa | ⏳ |
| η redutor | 0,75 | — | estimativa (planetário pequeno) | ⏳ |
| η motor e η gerador | 0,75 | — | estimativa | ⏳ |
| η buck USB | 0,85 | — | estimativa | ⏳ |
| Consumo da eletrônica | ~1 | W | estimativa (ESP32 + LCD + sensores) | ⏳ medir |
| Encoder | 600 | pulsos/volta | LPD3806-600BM, no tambor | ✅ |
| Velocidade de subida | 0,05 | m/s | firmware (`V_SUBIDA`) | ⏳ |
| Velocidade-alvo de descida | 0,03 a 0,08 | m/s | DEC-004 | ⏳ |
| Limite de velocidade | 0,10 | m/s | proteção | ✅ projeto |
| Descida com frenagem a 100 % (11 Ω) | ~0,025 | m/s | DEC-010 | ⏳ ensaio com 5 kg |
| Entrada mínima do buck USB | ~8 | V | XL4015 | ⏳ |

> A versão inicial deste arquivo trazia m_c = 500 kg e h = 3 m (exemplo do
> modelo). Esses valores foram substituídos pela DEC-001.

## PREMISSAS DE MODELO
- **Rendimento constante:** os rendimentos acima são tratados como constantes.
  Em baixa rotação o rendimento real cai, então as linhas de 0,01 e 0,02 m/s
  do Quadro 5 são otimistas. Erro esperado: grande abaixo de 0,03 m/s,
  moderado no ponto de projeto. Só o ensaio resolve.
- **Tensão em vazio:** a tensão gerada é E = K_e · ω. Com carga, a tensão cai
  pela resistência do enrolamento, que só a folha de dados ou o ensaio
  informam.
- **Regime quasi-estático:** a massa sobe e desce a 0,03–0,09 m/s; a energia
  cinética a 0,10 m/s é ½ · 20 · 0,10² = 0,1 J, desprezível frente aos 333,5 J.
- **Raio constante do tambor:** o cabo enrola em camada única (canal
  helicoidal), então r não muda com a altura.
- **Atrito do carrinho nas guias:** desprezado separadamente; fica embutido no
  η das polias. Os 8 rolamentos 608 tornam esse termo pequeno, mas não foi
  medido.
- **Consumo auxiliar:** a eletrônica (~1 W) consome em ~6 minutos o que um
  ciclo armazena. Por isso a eficiência é medida só no ramo de potência e o
  consumo auxiliar é mostrado à parte no painel (INC-002).
- **Massa conhecida:** a massa é uma constante de 20 kg no firmware; não há
  célula de carga (INC-013, parcial).
