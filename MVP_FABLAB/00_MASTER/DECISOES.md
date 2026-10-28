# DECISÕES — MVP FABLAB

Continua a numeração de `00_MASTER/DECISOES.md` da raiz (DEC-001 a DEC-013
valem para o projeto principal). Todas abaixo são **propostas** de
2026-10-28; viram decididas quando o Gabriel aprovar o PR ou escolher a
variante (Q-009). As decisões do projeto principal que não aparecem aqui
continuam valendo no MVP (DEC-002 unidades, DEC-004 controle pela
frenagem, DEC-007 fuzzy, DEC-011 Wokwi, DEC-013 Streamlit).

## DEC-014 — Massa de 5 kg e curso de 1,00 m (variante A)
- **Data:** 2026-10-28
- **Skill:** FÍSICO
- **Status:** proposta, aguarda o Gabriel (Q-009)
- **Contexto:** Pedido de uma releitura menor, montável num fablab, com motor
  mais simples. Com 20 kg a estrutura pede metalon soldado e o motor pede um
  planetário de ~R$ 450.
- **Decisão:** m_c = 5 kg (galão de 5 L), h = 1,00 m, torre de ~1,5 m.
  E_teo = 49 J por ciclo. Meta de geração: 3 LEDs de nível; a USB sai.
- **Alternativas descartadas:** variante B, 10 kg e 1,2 m com planetário
  1:71 (~R$ 200 a mais, USB de ~1,5 W só para power bank); manter 20 kg
  (não cabe em fablab sem serralheria).
- **Consequências:** `CURSO = 1.00`; FÍSICO refaz energia (C-101 a C-109);
  ARQUITETO dimensiona tudo para 5 kg com margem até 10 kg.
- **Revisável em:** se o ensaio 0 mostrar que o redutor não retroaciona com
  5 kg, ou se o grupo quiser a variante B.

## DEC-015 — Motorredutor 12 V Ø 37 mm 1:90 com encoder Hall
- **Data:** 2026-10-28
- **Skill:** ARQUITETO
- **Status:** proposta; compra depende do ensaio 0
- **Contexto:** O motor precisa subir 5 kg, retroacionar na descida e gerar
  tensão para os LEDs, com peça de prateleira barata.
- **Decisão:** Motorredutor DC 12 V, Ø 37 mm, engrenagens retas 1:90
  (~107 rpm em vazio), torque nominal ≥ 0,5 N·m, encoder Hall de 11 PPR no
  motor (família JGB37-520). K_e estimado 0,0119 V·s/rad; `KE_MASSA = 214`.
  O encoder do motor substitui o LPD3806.
- **Alternativas descartadas:** sem-fim (JGY-370, vidro elétrico, limpador:
  autotravantes, não descem); 1:30 (tensão baixa, ~3 V a 0,05 m/s); motor de
  passo como gerador (sai CA, exige retificador e outra lógica de controle).
- **Plano B:** se não retroacionar, 1:50 da mesma família (menos tensão: só
  verde e amarelo) ou planetário 37 mm 1:71 (variante B).
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
  sem o ESP32, a carga fixa de 120 Ω limita a descida a ~0,05 m/s.

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
