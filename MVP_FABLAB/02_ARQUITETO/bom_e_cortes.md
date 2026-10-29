# BOM E LISTA DE CORTES — MVP FABLAB

Preços aproximados, de memória, **não cotados** (mesmo critério do projeto
principal). ML = Mercado Livre. "Fablab" = material que costuma existir no
fablab; se tiver, custa zero.

## Eletrônica

Lista de compras detalhada, com os passivos um a um, a alimentação e o
que faltava aqui (cabo de força, cabo USB de dados, chave de demanda), em
`../DIY/05_lista_compras_eletronica.md` (≈ R$ 480).

| Item | Especificação | Qtd | R$ | Observação |
|------|---------------|-----|-----|------------|
| ESP32 DevKit V1 | WROOM-32 | 1 | 45 | Reaproveita do projeto principal |
| Driver de motor | BTS7960 (IBT-2) | 1 | 60 | Reaproveita; precisa de R_EN e L_EN separados (DEC-017) |
| **Motorredutor** | **6 V, Ø 37 mm, engrenagens retas 1:90 (~107 rpm), torque nominal ≥ 0,6 N·m, encoder Hall 11 PPR, tipo JGB37-520. Nunca sem-fim** | 1 | 80 | DEC-024: o Gabriel achou um motor de 6 V (modelo a confirmar). Comprar primeiro e fazer o ensaio 0 |
| Suporte do motor | Suporte em L para motor 37 mm | 1 | 10 | Às vezes vem junto |
| Sensor de corrente | Módulo INA219 (shunt 0,1 Ω) | 2 | 30 | DEC-018 |
| Servo | MG90S (engrenagem metálica) | 1 | 25 | DEC-019 |
| MOSFET | Módulo D4184 | 1 | 12 | Reaproveita |
| Fins de curso | Micro switch com rolete | 2 | 10 | Reaproveita |
| Emergência | Cogumelo NF 22 mm com trava | 1 | 25 | Reaproveita |
| Buck | LM2596 | 2 | 24 | |
| Fonte | Chaveada 12 V 3 A | 1 | 40 | Continua 12 V mesmo com o motor de 6 V: os LM2596 precisam de > 6,5 V na entrada; o motor recebe PWM ≤ 50 % |
| Resistores de potência | 22 Ω 5 W (carga fixa) e 6,8 Ω 5 W (frenagem), cerâmicos | 2 | 8 | |
| Diodos | 1N5822 (2), 1N5819, 1N4148 (2), Zener 2,4 V, TVS P6KE8.2A | — | 12 | |
| Capacitores | 470 µF 25 V, 100 nF | — | 4 | |
| Fusível | 3 A retardado + porta-fusível | 1 | 8 | |
| Diversos | 3 LEDs, resistores 220 Ω, 10 kΩ, 4,7 kΩ, 3,3 kΩ | — | 8 | |
| Montagem | Bornes, fios 1 mm² e 0,2 mm², jumpers, placa perfurada | — | 40 | |
| **Subtotal eletrônica** | | | **≈ 441** | ~R$ 290 se reaproveitar ESP32, IBT-2, MOSFET, fins de curso e emergência |

## Mecânica

| Item | Especificação | Qtd | R$ | Observação |
|------|---------------|-----|-----|------------|
| Perfil V-slot 2020 | 2 × 2.050 mm + 3 × 260 mm | 1 conj. | 150 | Fablab costuma ter sobras; 2,05 m pede barra de 3 m |
| Cantoneiras e porcas T M5 | Kit, mais 2 cantoneiras para prender o topo à parede | 1 | 35 | |
| Rodas V-slot com rolamento + espaçador excêntrico | | 4 | 40 | Alternativa: patins impressos em PETG (R$ 0, mais atrito) |
| Compensado 15 e 18 mm, MDF 3 e 6 mm, acrílico 3 mm | Base 500 × 600, topo, carrinho, caixa | 1 conj. | 70 | Fablab |
| Filamento PETG | ~250 g (tambor de 60 mm, catraca, lingueta, suportes) | 1 | 25 | Fablab |
| Rolamento 608 | Mancal do tambor | 1 | 5 | Sem talha, sem polia móvel (DEC-025) |
| Pino de aço Ø 8 mm, pino das anilhas com trava, parafusos M3/M4/M5/M8, mola de tração | | 1 conj. | 40 | |
| Cordão Dyneema ou poliéster trançado 2 mm (≥ 100 kg) | 3 m | 1 | 15 | |
| Massa | Uma anilha de 2 kg | 1 | 0 | Já disponível |
| EVA 20 mm | Batente | 1 | 5 | |
| **Subtotal mecânica** | | | **≈ 385** | ~R$ 140 se o fablab tiver perfil, chapas e filamento |

**Total MVP ≈ R$ 830** com tudo comprado; **≈ R$ 430** reaproveitando a
eletrônica do projeto principal e o material do fablab. O projeto principal
fica em ≈ R$ 3.100 sem a massa.

## O que sai em relação ao projeto principal

| Sai | Entra no lugar | Economia | O que se perde |
|-----|----------------|----------|----------------|
| Torre de metalon 2,10 m soldada (R$ 910) | Perfil 2020 2,05 m + compensado, topo preso à parede | ~R$ 650 e a serralheria | Nada para 2 kg; não aguenta 20 kg |
| Motorredutor 24 V planetário 1:50 (R$ 450) | 6 V 37 mm 1:90 com encoder (R$ 80) | ~R$ 370 | Eficiência (η_ciclo ~0,09 contra ~0,27), torque e tensão gerada (~5 V) |
| Eixo 1045, 2 UCP204, acoplamento, tambor usinado (R$ 310) | Tambor impresso no eixo do motor + 608 | ~R$ 300 e o torno | Vida útil do tambor |
| Cabo de aço, clipes, sapatilhas, polias de cabo (R$ 120) | Cordão 2 mm direto, sem talha | ~R$ 105 | — |
| Solenoide 24 V + catraca cortada + MOSFET da trava (R$ 205) | Catraca impressa + servo MG90S | ~R$ 180 | Força de retenção (só serve até ~10 kg) |
| Relés K1, K2, K4 e módulo de 4 relés (R$ 30) | Enables separados do IBT-2 (DEC-017) | ~R$ 30 e 3 GPIOs | O corte por relé do 24V_POT (a emergência corta direto) |
| Sondagem da USB e buck XL4015 + USB (R$ 25) | Chave "demanda" ou slider do painel | ~R$ 25 | A demonstração de carga de celular |
| LPD3806 (R$ 90) | Encoder Hall do próprio motor | R$ 90 | Medida direta no tambor |
| 3× INA226 com shunt trocado (R$ 85) | 2× INA219 de prateleira (R$ 30) | ~R$ 55 | A medida separada da USB |
| DS3231 (R$ 20) | Hora por NTP | R$ 20 | Hora sem Wi-Fi |
| LCD 20×4 + BSS138 + buzzer (R$ 60) | Painel + Monitor Serial | ~R$ 60 | Interface local sem notebook |
| Carga de frenagem 2 × 22 Ω 25 W, SR560, 2.200 µF, TVS 28 V | 6,8 Ω 5 W + 22 Ω 5 W, 1N5822, 470 µF, TVS 8,2 V | ~R$ 30 | — |
| Fonte 24 V 5 A (R$ 80) | 12 V 3 A (R$ 40) | R$ 40 | — |
| 20 kg de anilhas (R$ 250 a 350) | Uma anilha de 2 kg já disponível | até R$ 350 | Energia por ciclo (33 J contra 333,5 J) |

## O que fica
ESP32, IBT-2, encoder em quadratura com ESP32Encoder, fins de curso NF,
emergência por hardware, trava de catraca com falha segura,
frenagem por PWM em malha fechada, fuzzy de 3 entradas e 11 regras, painel
Streamlit, MQTT.
