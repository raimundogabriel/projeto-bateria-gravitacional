# BOM E LISTA DE CORTES — MVP FABLAB

Preços aproximados, de memória, **não cotados** (mesmo critério do projeto
principal). ML = Mercado Livre. "Fablab" = material que costuma existir no
fablab; se tiver, custa zero.

## Eletrônica

| Item | Especificação | Qtd | R$ | Observação |
|------|---------------|-----|-----|------------|
| ESP32 DevKit V1 | WROOM-32 | 1 | 45 | Reaproveita do projeto principal |
| Driver de motor | BTS7960 (IBT-2) | 1 | 60 | Reaproveita; precisa de R_EN e L_EN separados (DEC-017) |
| **Motorredutor** | **12 V, Ø 37 mm, engrenagens retas 1:90 (~107 rpm), torque nominal ≥ 0,5 N·m, encoder Hall 11 PPR, tipo JGB37-520. Nunca sem-fim** | 1 | 80 | DEC-015. Comprar primeiro e fazer o ensaio 0 |
| Suporte do motor | Suporte em L para motor 37 mm | 1 | 10 | Às vezes vem junto |
| Sensor de corrente | Módulo INA219 (shunt 0,1 Ω) | 2 | 30 | DEC-018 |
| Servo | MG90S (engrenagem metálica) | 1 | 25 | DEC-019 |
| MOSFET | Módulo D4184 | 1 | 12 | Reaproveita |
| Fins de curso | Micro switch com rolete | 2 | 10 | Reaproveita |
| Emergência | Cogumelo NF 22 mm com trava | 1 | 25 | Reaproveita |
| Buck | LM2596 | 2 | 24 | |
| Fonte | Chaveada 12 V 3 A | 1 | 40 | Substitui a de 24 V 5 A |
| Resistores de potência | 22 Ω 5 W e 120 Ω 2 W (cerâmicos) | 2 | 8 | |
| Diodos | 1N5822 (2), 1N5819, Zener 4,7 V e 8,2 V, TVS SMBJ15A | — | 12 | |
| Capacitores | 470 µF 25 V, 100 nF | — | 4 | |
| Fusível | 3 A retardado + porta-fusível | 1 | 8 | |
| Diversos | 3 LEDs, resistores 1 kΩ, 10 kΩ, 4,7 kΩ, 3,3 kΩ | — | 8 | |
| Montagem | Bornes, fios 1 mm² e 0,2 mm², jumpers, placa perfurada | — | 40 | |
| **Subtotal eletrônica** | | | **≈ 441** | ~R$ 290 se reaproveitar ESP32, IBT-2, MOSFET, fins de curso e emergência |

## Mecânica

| Item | Especificação | Qtd | R$ | Observação |
|------|---------------|-----|-----|------------|
| Perfil V-slot 2020 | 2 × 1.500 mm + 2 × 260 mm | 1 conj. | 110 | Fablab costuma ter sobras |
| Cantoneiras e porcas T M5 | Kit | 1 | 30 | |
| Rodas V-slot com rolamento + espaçador excêntrico | | 4 | 40 | Alternativa: patins impressos em PETG (R$ 0, mais atrito) |
| Compensado 15 e 18 mm, MDF 3 e 6 mm, acrílico 3 mm | Base, topo, carrinho, caixa | 1 conj. | 60 | Fablab |
| Filamento PETG | ~300 g (tambor, catraca, polia, lingueta, suportes) | 1 | 30 | Fablab |
| Rolamentos 608 | Polia móvel e mancal do tambor | 2 | 10 | |
| Pino de aço Ø 8 mm, parafusos M3/M4/M5/M8, mola de tração | | 1 conj. | 30 | |
| Cordão Dyneema ou poliéster trançado 2 mm (≥ 100 kg) | 5 m | 1 | 25 | |
| Cinta com catraca pequena | Prender o galão | 1 | 15 | |
| Massa | Galão de 5 L com água (ou areia) | 1 | 0 | |
| EVA 20 mm | Batente | 1 | 5 | |
| **Subtotal mecânica** | | | **≈ 355** | ~R$ 200 se o fablab tiver perfil, chapas e filamento |

**Total MVP ≈ R$ 800** com tudo comprado; **≈ R$ 500** reaproveitando a
eletrônica do projeto principal e o material do fablab. O projeto principal
fica em ≈ R$ 3.100 sem a massa.

## O que sai em relação ao projeto principal

| Sai | Entra no lugar | Economia | O que se perde |
|-----|----------------|----------|----------------|
| Torre de metalon 2,10 m soldada (R$ 910) | Perfil 2020 1,5 m + compensado | ~R$ 700 e a serralheria | Nada para 5 kg; não aguenta 20 kg |
| Motorredutor 24 V planetário 1:50 (R$ 450) | 12 V 37 mm 1:90 com encoder (R$ 80) | ~R$ 370 | Eficiência (η_ciclo ~0,10 contra ~0,27) e torque |
| Eixo 1045, 2 UCP204, acoplamento, tambor usinado (R$ 310) | Tambor impresso no eixo do motor + 608 | ~R$ 300 e o torno | Vida útil do tambor |
| Cabo de aço, clipes, sapatilhas, polias de cabo (R$ 120) | Cordão 2 mm + polia impressa | ~R$ 80 | — |
| Solenoide 24 V + catraca cortada + MOSFET da trava (R$ 205) | Catraca impressa + servo MG90S | ~R$ 180 | Força de retenção (só serve para 5 a 10 kg) |
| Relés K1, K2, K4 e módulo de 4 relés (R$ 30) | Enables separados do IBT-2 (DEC-017) | ~R$ 30 e 3 GPIOs | O corte por relé do 24V_POT (a emergência corta direto) |
| Sondagem da USB e buck XL4015 + USB (R$ 25) | Chave "demanda" ou slider do painel | ~R$ 25 | A demonstração de carga de celular |
| LPD3806 (R$ 90) | Encoder Hall do próprio motor | R$ 90 | Medida direta no tambor |
| 3× INA226 com shunt trocado (R$ 85) | 2× INA219 de prateleira (R$ 30) | ~R$ 55 | A medida separada da USB |
| DS3231 (R$ 20) | Hora por NTP | R$ 20 | Hora sem Wi-Fi |
| LCD 20×4 + BSS138 + buzzer (R$ 60) | Painel + Monitor Serial | ~R$ 60 | Interface local sem notebook |
| Carga de frenagem 2 × 22 Ω 25 W, SR560, 2.200 µF, TVS 28 V | 22 Ω 5 W + 120 Ω 2 W, 1N5822, 470 µF, TVS 15 V | ~R$ 30 | — |
| Fonte 24 V 5 A (R$ 80) | 12 V 3 A (R$ 40) | R$ 40 | — |
| 20 kg de anilhas (R$ 250 a 350) | Galão de 5 L | até R$ 350 | Energia por ciclo (49 J contra 333,5 J) |

## O que fica
ESP32, IBT-2, encoder em quadratura com ESP32Encoder, fins de curso NF,
emergência por hardware, trava de catraca com falha segura, talha 2:1,
frenagem por PWM em malha fechada, fuzzy de 3 entradas e 11 regras, painel
Streamlit, MQTT.
