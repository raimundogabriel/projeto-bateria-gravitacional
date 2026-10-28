# Bateria Gravitacional de baixo custo com dashboard remoto e lógica fuzzy

Protótipo didático (UVA, Sistemas Embarcados, 2026): uma massa de 20 kg sobe
1,70 m quando a tarifa está baixa e desce quando está alta, com o mesmo
motorredutor 24 V funcionando como gerador. Na descida, a energia acende LEDs
e alimenta uma porta USB que carrega um celular. Um ESP32 decide por lógica
fuzzy quando subir, manter ou descer, e os dados vão a um painel remoto.

## Por onde começar
1. `00_MASTER/PROJETO.md` — objetivo, escopo e stack
2. `00_MASTER/ESTADO_ATUAL.md` — o que está pronto e a próxima ação
3. `00_MASTER/SKILLS.md` — as personas (FÍSICO, ARQUITETO, DESENVOLVEDOR) e
   como invocá-las

## Estrutura
| Pasta | Persona | Conteúdo |
|-------|---------|----------|
| `00_MASTER/` | todas | Projeto, decisões, handoffs, glossário, estado atual |
| `01_FISICA/` | FÍSICO | Premissas, cálculos de energia, controle fuzzy, validação |
| `02_ARQUITETO/` | ARQUITETO | Mecânica, circuitos, BOM |
| `03_SOFTWARE/` | DESENVOLVEDOR | Firmware ESP32 (Wokwi), pinagem, contrato MQTT, dashboard |
| `04_AUDITORIA/` | todas | Inconsistências e questões abertas |
| `05_DOC_ORIGINAL/` | — | Relatório original (PDF) e revisado (v2, DOCX) |
| `logs/` | — | Fluxo de handoffs entre personas |
| `MVP_FABLAB/` | todas | Releitura menor para fablab (5 kg, 1,0 m, motor 12 V), em avaliação |

## Números principais
| Grandeza | Valor |
|----------|-------|
| Massa / curso | 20 kg / 1,70 m |
| Energia por ciclo | 333,5 J (0,093 Wh) |
| Relação massa → motor | 100:1 (talha 2:1 × planetário 1:50) |
| Ponto de projeto da descida | 0,05 m/s, ~34 s, 4–5 W na USB |
| Eficiência de ida e volta | ~27 % (estimada, a medir) |
| Custo estimado | ≈ R$ 3.100 sem a massa (não cotado) |
