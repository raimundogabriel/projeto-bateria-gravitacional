# DECISÕES — MVP FABLAB

Continua a numeração de `00_MASTER/DECISOES.md` da raiz (DEC-001 a DEC-013
valem para o projeto principal). Propostas em 2026-10-28; o PR #4 foi
aprovado e o porte (DEC-014) e a saída (DEC-022) foram decididos em
2026-10-29. O motor (DEC-015) continua em escolha. As decisões do projeto principal que não aparecem aqui
continuam valendo no MVP (DEC-002 unidades, DEC-004 controle pela
frenagem, DEC-007 fuzzy, DEC-011 Wokwi, DEC-013 Streamlit).

## DEC-014 — Massa de 6 kg de anilhas e curso de 1,70 m
- **Data:** 2026-10-28 (proposta), 2026-10-29 (decidida)
- **Skill:** FÍSICO
- **Status:** decidida pelo Gabriel em 2026-10-29 (Q-009)
- **Contexto:** Pedido de uma releitura menor, montável num fablab, com motor
  mais simples. A proposta inicial era 5 kg em 1,00 m (variante A) ou 10 kg
  em 1,20 m (variante B).
- **Decisão:** m_c = 6 kg (anilhas que o grupo já tem), h = 1,70 m (o mesmo
  curso do projeto principal), torre de ~2,05 m. E_teo = 100,1 J por ciclo.
- **Alternativas descartadas:** 5 kg em 1,00 m (49 J, torre menor); 10 kg em
  1,20 m (pede motor planetário mais caro); 20 kg (não cabe em fablab sem
  serralheria).
- **Consequências:** `CURSO = 1.70` e `MASSA = 6` no firmware e no painel;
  FÍSICO refaz C-101 a C-109; ARQUITETO passa as colunas a 2,05 m, o tambor
  a 150 mm úteis e prende o topo da torre à parede; carga fixa vai a 100 Ω.
- **Revisável em:** se o ensaio 0 mostrar que o redutor não retroaciona com
  6 kg.

## DEC-015 — Motorredutor 12 V Ø 37 mm 1:90 com encoder Hall
- **Data:** 2026-10-28
- **Skill:** ARQUITETO
- **Status:** referência; em 2026-10-29 o Gabriel ainda está escolhendo o
  motor pelo custo. O ensaio 0 fecha a escolha
- **Contexto:** O motor precisa subir 6 kg, retroacionar na descida e gerar
  tensão para os LEDs, com peça de prateleira barata.
- **Decisão:** Motorredutor DC 12 V, Ø 37 mm, engrenagens retas 1:90
  (~107 rpm em vazio), torque nominal ≥ 0,6 N·m, encoder Hall de 11 PPR no
  motor (família JGB37-520). K_e estimado 0,0119 V·s/rad; `KE_MASSA = 214`.
  O encoder do motor substitui o LPD3806.
- **Alternativas descartadas:** sem-fim (JGY-370, vidro elétrico, limpador:
  autotravantes, não descem); 1:30 (tensão baixa, ~3 V a 0,05 m/s); motor de
  passo como gerador (sai CA, exige retificador e outra lógica de controle).
- **Plano B:** se não retroacionar, 1:50 da mesma família (menos tensão: só
  verde e amarelo) ou planetário 37 mm 1:71 (mais caro, rende ~0,70 nos dois
  sentidos).
- **Consequências:** Fonte passa a 12 V 3 A; `MM_POR_PULSO = 0.00793`.
- **Revisável em:** ensaio 0.

## DEC-016 — Talha 2:1 com tambor impresso no eixo do motor
- **Data:** 2026-10-28
- **Skill:** ARQUITETO
- **Status:** proposta
- **Decisão:** Tambor PETG Ø 20 mm efetivo (canal helicoidal passo 2,5 mm,
  90 mm úteis) e catraca Ø 50 mm na mesma peça, preso no eixo D de 6 mm do
  motor, com pino Ø 8 mm num 608 do outro lado. Talha 2:1 com polia impressa
  e cordão Dyneema/poliéster 2 mm.
- **Alternativas descartadas:** sem talha (dobra o torque no redutor e
  divide a tensão gerada por dois); eixo de aço com mancais UCP (pede torno).
- **Consequências:** 0,245 N·m no tambor; 1 cm de massa ≈ 29 voltas do
  motor.

## DEC-017 — Sem relés: IBT-2 com enables separados faz a troca subir/gerar
- **Data:** 2026-10-28
- **Skill:** ARQUITETO
- **Status:** proposta; provar no ensaio 4
- **Contexto:** No principal, K2 (DPDT) troca o motor entre o BTS7960 e o
  barramento gerado, K1 corta a potência e K4 sonda a USB.
- **Decisão:** R_EN (GPIO 18) e L_EN (GPIO 13) separados. Na descida, a
  meia-ponte do M+ fica com o lado baixo ligado e a do M− desligada; o M−,
  positivo na descida, alimenta o GEN por um 1N5822. Diodo em série no B+ do
  IBT-2 impede que a geração volte ao 12 V. Modo CURTO (os dois lados baixos)
  é o freio forte. Emergência corta o 12V_POT direto.
- **Alternativas descartadas:** manter 1 relé DPDT (funciona, mas acrescenta
  peça e tempo de comutação; fica como plano B se o ensaio 4 falhar).
- **Consequências:** Firmware ganha `modoPonte()`; pinos 23 e 27 liberados;
  sem o ESP32, a carga fixa de 100 Ω limita a descida a ~0,05 m/s.

## DEC-018 — 2× INA219 no lugar de 3× INA226
- **Data:** 2026-10-28
- **Skill:** ARQUITETO
- **Status:** proposta
- **Decisão:** INA219 de prateleira (0,1 Ω, até 3,2 A e 26 V, suficiente
  para 12 V e < 1 A): nº 1 subida (0x40), nº 2 gerado (0x41). Sem troca de
  shunt.
- **Alternativas descartadas:** INA226 (o motivo da DEC-006, 24 V e 3 A, não
  existe no MVP); medir a USB (sem USB).

## DEC-019 — Trava com catraca impressa e servo MG90S
- **Data:** 2026-10-28
- **Skill:** ARQUITETO
- **Status:** proposta; provar no ensaio 3
- **Decisão:** Lingueta impressa encostada na catraca por mola; o servo
  (GPIO 4, 5 V depois da emergência) puxa a lingueta para soltar. Sem
  energia no servo, a mola engata (falha segura, como na DEC-005).
- **Alternativas descartadas:** solenoide 24 V (pede MOSFET, hit-and-hold e
  24 V); só freio elétrico em CURTO (não segura parado, a massa escorrega
  devagar).

## DEC-020 — Estrutura de perfil 2020 e compensado, sem solda
- **Data:** 2026-10-28
- **Skill:** ARQUITETO
- **Status:** proposta
- **Decisão:** 2 colunas V-slot 2020 × 1,5 m, travessas 2020, base de
  compensado 18 mm com lastro, placa do topo de compensado 15 mm, carrinho
  com 4 rodas V, peças em PETG e MDF cortado a laser.
- **Alternativas descartadas:** metalon soldado (DEC-012, pede serralheria);
  só madeira (guias de madeira travam com umidade e atrito).

## DEC-021 — Interface enxuta: sem LCD, RTC, buzzer e USB; MQTT obrigatório
- **Data:** 2026-10-28
- **Skill:** DESENVOLVEDOR
- **Status:** proposta
- **Decisão:** Hora por NTP (ou enviada pelo painel); estado no Monitor
  Serial e no MQTT; demanda D por chave no GPIO 27 (5 W) ou pelo painel.
- **Alternativas descartadas:** manter LCD (R$ 53 e 2 dispositivos I²C a
  mais só para repetir o painel).
- **Consequências:** O MVP depende de Wi-Fi para o modo automático; o modo
  manual pelo Monitor Serial funciona sem rede.

## DEC-022 — Saída útil só com LEDs, sem USB
- **Data:** 2026-10-29
- **Skill:** FÍSICO
- **Status:** decidida (o Gabriel pediu para escolher o mais fácil e rápido)
- **Contexto:** Com 6 kg descendo a 0,05 m/s o gerador entrega ~0,87 W a
  ~10,7 V (C-107). Um buck para 5 V daria ~0,74 W (~150 mA).
- **Decisão:** A saída útil são os 3 LEDs de nível no barramento gerado
  (verde ~2 V, amarelo ~6,5 V, vermelho ~10 V), sem conversor nem firmware.
- **Alternativas descartadas:** porta USB para celular (o celular puxa
  ≥ 500 mA, a tensão desaba e a carga liga e desliga); USB para power bank
  (muitos desligam abaixo de ~100 mA, e exige descer acima do limite de
  0,055 m/s deste motor).
- **Consequências:** Sai o buck XL4015 e a porta USB; o painel mostra
  `p_leds_w` e `e_leds_j`.
- **Revisável em:** se o motor escolhido gerar ≥ 2 W na descida.
