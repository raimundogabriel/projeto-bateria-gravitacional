# MVP FABLAB — releitura enxuta da bateria gravitacional

**Status:** porte revisto em 2026-10-29: **parafusadeira Bosch GSR 1440-LI
inteira e 6 kg**, 1,70 m, só LEDs (DEC-026). Nada aqui altera o projeto
principal (pastas `00_MASTER/` a `05_DOC_ORIGINAL/` na raiz). Esta pasta é uma
variante menor, para montar num fablab com corte a laser, impressão 3D e
ferramentas de bancada, sem serralheria nem solda.

## A ideia em uma frase
**6 kg** de anilhas sobem **1,70 m** numa torre de perfil de
alumínio 20 × 20, puxados por uma **parafusadeira de 14,4 V** (sem a trava
do mandril), e na descida o mesmo motor gera energia que acende LEDs. O ESP32
continua decidindo por fuzzy quando subir, manter ou descer, e manda os dados
ao painel Streamlit.

## O que o MVP precisa provar
1. O ciclo completo funciona: subir, manter travado, descer gerando, parar.
2. A descida é controlada pela carga elétrica do gerador (malha fechada pelo
   encoder), sem freio de atrito.
3. O fuzzy de 3 entradas decide sozinho com a tarifa do horário.
4. O painel mostra posição, potência de subida, potência gerada e energia por
   ciclo, com dados reais.

O que **não** precisa provar: carregar celular por USB. Com a parafusadeira
sobram ~2,7 W a ~3,9 V por ~9 s na descida, abaixo dos 5 V de uma USB
(DEC-022); fica para o projeto principal.

## Números principais

| Grandeza | Projeto principal | MVP fablab |
|----------|-------------------|------------|
| Massa / curso | 20 kg / 1,70 m | **6 kg de anilhas / 1,70 m** |
| Altura da torre | 2,10 m | ~2,05 m, topo preso à parede |
| Energia por ciclo (E_teo) | 333,5 J | **100 J** (~25 J gerados, estimado) |
| Motor | 24 V ~50 W, planetário 1:50 (~R$ 450) | **parafusadeira Bosch GSR 1440-LI** (14,4 V, planetário ~1:42 na 1ª marcha; o grupo já tem), na fonte de 12 V com PWM ≤ 50 %; encoder LPD3806 no tambor |
| Transmissão | talha 2:1 + tambor Ø 60 mm usinado | cordão direto, sem talha, tambor Ø 30 mm impresso em 3D |
| Trava | catraca + solenoide 24 V (hit-and-hold) | **catraca impressa + micro servo MG90S + mola** |
| Troca subir/gerar | relés K1, K2 (DPDT) e K4 | **nenhum relé**: meia-ponte do IBT-2 desligada vira caminho de geração |
| Medição | 3× INA226 com shunt 10 mΩ | **2× INA219** (12 V, < 3,2 A) |
| Hora | RTC DS3231 | NTP pelo Wi-Fi do ESP32 |
| Interface local | LCD 20×4 + buzzer | nenhuma (painel + Monitor Serial) |
| Saída útil | USB 4–5 W para celular | 3 LEDs de nível de geração (~2,7 W gerados a 0,18 m/s) |
| Estrutura | metalon soldado 30 × 30 | perfil 2020 + compensado/MDF cortado a laser, sem solda |
| Custo estimado | ≈ R$ 3.100 sem a massa | **≈ R$ 870** tudo comprado, ≈ R$ 475 reaproveitando (não cotado) |

## Organização
Mesmas personas e regras de `00_MASTER/SKILLS.md` da raiz; cada uma escreve na
sua pasta dentro de `MVP_FABLAB/`.

| Pasta | Persona | Conteúdo |
|-------|---------|----------|
| `00_MASTER/` | todas | Estado, decisões (DEC-014 a DEC-026), handoffs (HANDOFF-009 a 013), questões (Q-009 a Q-013) |
| `01_FISICA/` | FÍSICO | Premissas, energia e geração por velocidade, ensaios do MVP |
| `02_ARQUITETO/` | ARQUITETO | Mecânica para fablab, circuito com diagramas, BOM e lista do que sai |
| `03_SOFTWARE/` | DESENVOLVEDOR | Pinagem, firmware e projeto Wokwi do MVP, painel Streamlit adaptado |
| `DIY/` | DESENVOLVEDOR | Passo a passo: gravar o ESP32, ligar ao painel por MQTT, problemas comuns |

## Ordem de leitura
1. `00_MASTER/DECISOES.md` — cada corte e o motivo
2. `02_ARQUITETO/bom_e_cortes.md` — o que comprar e o que sai
3. `01_FISICA/calculos_energia.md` — por que fica só LED
4. `02_ARQUITETO/circuito.md` — como geração funciona sem relé
5. `01_FISICA/validacao_experimental.md` — o ensaio 0 (a parafusadeira desce sozinha com 6 kg?) decide a compra da eletrônica
6. `03_SOFTWARE/firmware/README.md` — como rodar o MVP no Wokwi
7. `03_SOFTWARE/dashboard/README.md` — painel Streamlit do MVP
8. `DIY/README.md` — gravar o ESP32 e ligar ao painel
