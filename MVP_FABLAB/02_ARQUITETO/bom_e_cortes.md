# BOM E LISTA DE CORTES — MVP FABLAB

Preços aproximados, de memória, **não cotados** (mesmo critério do projeto
principal). ML = Mercado Livre. "Fablab" = material que costuma existir no
fablab; se tiver, custa zero.

## Eletrônica

Lista de compras detalhada, com os passivos um a um, a alimentação e o
que faltava aqui (cabo de força, cabo USB de dados, chave de demanda), em
`../DIY/05_lista_compras_eletronica.md` (≈ R$ 520).

| Item | Especificação | Qtd | R$ | Observação |
|------|---------------|-----|-----|------------|
| ESP32 DevKit V1 | WROOM-32 | 1 | 45 | Reaproveita do projeto principal |
| Driver de motor | BTS7960 (IBT-2) | 1 | 60 | Reaproveita; precisa de R_EN e L_EN separados (DEC-017) |
| **Motor e redutor** | **Parafusadeira Bosch GSR 1440-LI inteira** (motor 14,4 V + redutor planetário 2 marchas + mandril), sem a trava Auto-Lock e sem o gatilho | 1 | 0 | DEC-026: o Gabriel já tem. Fazer o ensaio 0 antes de comprar o resto |
| Encoder | LPD3806-600BM (600 pulsos/volta, A/B, eixo Ø 6 mm) | 1 | 90 | O motor da parafusadeira não tem encoder; vai no eixo do tambor |
| Acoplamento | Flexível 6 × 8 mm | 1 | 15 | Liga o encoder ao eixo de Ø 8 mm |
| Sensor de corrente | Módulo INA219 (shunt 0,1 Ω) | 2 | 30 | DEC-018 |
| Servo | MG90S (engrenagem metálica) | 1 | 25 | DEC-019 |
| MOSFET | Módulo D4184 | 1 | 12 | Reaproveita |
| Fins de curso | Micro switch com rolete | 2 | 10 | Reaproveita |
| Emergência | Cogumelo NF 22 mm com trava | 1 | 25 | Reaproveita |
| Buck | LM2596 | 2 | 24 | |
| Fonte | Chaveada 12 V 5 A | 1 | 55 | Motor de 14,4 V a ~5 A na subida (~1,3 A da fonte com PWM); folga para a partida |
| Resistores de potência | 5,6 Ω 10 W (carga fixa) e 2,2 Ω 10 W (frenagem), cerâmicos | 2 | 12 | |
| Diodos | 1N5822 (3), 1N4148 (4), TVS P6KE8.2A | — | 12 | |
| Capacitores | 1.000 µF 25 V (B+), 470 µF 25 V (GEN), 100 nF | — | 4 | |
| Fusível | 5 A retardado + porta-fusível | 1 | 8 | |
| Diversos | 3 LEDs, resistores 220 Ω, 10 kΩ, 4,7 kΩ, 3,3 kΩ | — | 8 | |
| Montagem | Bornes, fios 1 mm² e 0,2 mm², jumpers, placa perfurada | — | 40 | |
| **Subtotal eletrônica** | | | **≈ 475** | ~R$ 325 se reaproveitar ESP32, IBT-2, MOSFET, fins de curso e emergência |

## Mecânica

| Item | Especificação | Qtd | R$ | Observação |
|------|---------------|-----|-----|------------|
| Perfil V-slot 2020 | 2 × 2.050 mm + 3 × 260 mm | 1 conj. | 150 | Fablab costuma ter sobras; 2,05 m pede barra de 3 m |
| Cantoneiras e porcas T M5 | Kit, mais 2 cantoneiras para prender o topo à parede | 1 | 35 | |
| Rodas V-slot com rolamento + espaçador excêntrico | | 4 | 40 | Alternativa: patins impressos em PETG (R$ 0, mais atrito) |
| Compensado 15 e 18 mm, MDF 3 e 6 mm, acrílico 3 mm | Base 500 × 600, topo, carrinho, caixa | 1 conj. | 70 | Fablab |
| Filamento PETG | ~300 g (tambor de 60 mm, catraca, lingueta, berço da parafusadeira, suportes) | 1 | 25 | Fablab |
| Abraçadeiras metálicas | Para prender a parafusadeira no berço | 2 | 10 | |
| Rolamento 608 | Mancal do tambor | 1 | 5 | Sem talha, sem polia móvel (DEC-025) |
| Barra de aço Ø 8 mm × 200 mm (eixo do tambor, preso no mandril), pino das anilhas com trava, parafusos M3/M4/M5/M8, mola de tração | | 1 conj. | 40 | |
| Cordão Dyneema ou poliéster trançado 2 mm (≥ 100 kg) | 3 m | 1 | 15 | |
| Massa | Anilhas totalizando 6 kg | 1 conj. | 0 | Já disponíveis |
| EVA 20 mm | Batente | 1 | 5 | |
| **Subtotal mecânica** | | | **≈ 395** | ~R$ 150 se o fablab tiver perfil, chapas e filamento |

**Total MVP ≈ R$ 870** com tudo comprado; **≈ R$ 475** reaproveitando a
eletrônica do projeto principal e o material do fablab. O projeto principal
fica em ≈ R$ 3.100 sem a massa.

## O que sai em relação ao projeto principal

| Sai | Entra no lugar | Economia | O que se perde |
|-----|----------------|----------|----------------|
| Torre de metalon 2,10 m soldada (R$ 910) | Perfil 2020 2,05 m + compensado, topo preso à parede | ~R$ 650 e a serralheria | Nada para 6 kg; não aguenta 20 kg |
| Motorredutor 24 V planetário 1:50 (R$ 450) | Parafusadeira GSR 1440-LI que o grupo já tem (R$ 0) | ~R$ 450 | Eficiência (η_ciclo ~0,09 contra ~0,27; o motor de parafusadeira tem muito atrito) e tensão gerada (~4 V) |
| Eixo 1045, 2 UCP204, acoplamento, tambor usinado (R$ 310) | Barra Ø 8 mm no mandril + tambor impresso + 608 | ~R$ 290 e o torno | Vida útil do tambor |
| Cabo de aço, clipes, sapatilhas, polias de cabo (R$ 120) | Cordão 2 mm direto, sem talha | ~R$ 105 | — |
| Solenoide 24 V + catraca cortada + MOSFET da trava (R$ 205) | Catraca impressa + servo MG90S | ~R$ 180 | Força de retenção (só serve até ~10 kg) |
| Relés K1, K2, K4 e módulo de 4 relés (R$ 30) | Enables separados do IBT-2 (DEC-017) | ~R$ 30 e 3 GPIOs | O corte por relé do 24V_POT (a emergência corta direto) |
| Sondagem da USB e buck XL4015 + USB (R$ 25) | Chave "demanda" ou slider do painel | ~R$ 25 | A demonstração de carga de celular |
| 3× INA226 com shunt trocado (R$ 85) | 2× INA219 de prateleira (R$ 30) | ~R$ 55 | A medida separada da USB |
| DS3231 (R$ 20) | Hora por NTP | R$ 20 | Hora sem Wi-Fi |
| LCD 20×4 + BSS138 + buzzer (R$ 60) | Painel + Monitor Serial | ~R$ 60 | Interface local sem notebook |
| Carga de frenagem 2 × 22 Ω 25 W, SR560, 2.200 µF, TVS 28 V | 2,2 Ω 10 W + 5,6 Ω 10 W, 1N5822, 470 µF, TVS 8,2 V | ~R$ 25 | — |
| Fonte 24 V 5 A (R$ 80) | 12 V 5 A (R$ 55) | R$ 25 | — |
| 20 kg de anilhas (R$ 250 a 350) | 6 kg de anilhas já disponíveis | até R$ 350 | Energia por ciclo (100 J contra 333,5 J) |

## O que fica
ESP32, IBT-2, encoder LPD3806 em quadratura com ESP32Encoder, fins de curso NF,
emergência por hardware, trava de catraca com falha segura,
frenagem por PWM em malha fechada, fuzzy de 3 entradas e 11 regras, painel
Streamlit, MQTT.
