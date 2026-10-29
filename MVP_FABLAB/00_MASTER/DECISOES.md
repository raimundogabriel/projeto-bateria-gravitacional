# DECISÕES — MVP FABLAB

Continua a numeração de `00_MASTER/DECISOES.md` da raiz (DEC-001 a DEC-013
valem para o projeto principal). Propostas em 2026-10-28; o PR #4 foi
aprovado e o porte (DEC-014) e a saída (DEC-022) foram decididos em
2026-10-29. No fim do mesmo dia o Gabriel trocou para motor de 6 V e 2 kg
(DEC-024), o que substituiu DEC-014, DEC-015 e DEC-016 (DEC-025). As decisões do projeto principal que não aparecem aqui
continuam valendo no MVP (DEC-002 unidades, DEC-004 controle pela
frenagem, DEC-007 fuzzy, DEC-011 Wokwi, DEC-013 Streamlit).

## DEC-014 — Massa de 6 kg de anilhas e curso de 1,70 m
- **Data:** 2026-10-28 (proposta), 2026-10-29 (decidida)
- **Skill:** FÍSICO
- **Status:** substituída por DEC-024 em 2026-10-29 (a massa passou a 2 kg; o curso de 1,70 m continua)
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
- **Status:** substituída por DEC-024 em 2026-10-29 (motor de 6 V)
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
- **Status:** substituída por DEC-025 em 2026-10-29 (sem talha, tambor Ø 30 mm)
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
  sem o ESP32, a carga fixa limita a descida (com a parafusadeira: 5,6 Ω,
  ~0,19 m/s, DEC-026).

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

## DEC-023 — MQTT do MVP: broker no notebook, estado completo a cada 1 s
- **Data:** 2026-10-29
- **Skill:** DESENVOLVEDOR
- **Status:** proposta
- **Contexto:** Sem LCD (DEC-021), o painel é a única tela. O contrato da
  raiz (`03_SOFTWARE/contrato_dados.md`) separa `grav/estado` (30 s),
  `grav/acao`, `grav/energia` e `grav/alerta`. Q-006 (onde roda o broker)
  segue aberta no projeto principal.
- **Decisão:** No MVP o broker é o Mosquitto no notebook que roda o painel,
  na mesma rede do ESP32. O ESP32 publica um único `grav/estado` a cada
  1 s e a cada troca de estado, com todas as colunas do painel (energias,
  ciclo, motivo da falha), e `grav/online` retido com testamento. O painel
  publica `grav/comando` (`acao`, `demanda_w`, `hora`) e `grav/tarifas`
  retido. JSON montado e lido sem biblioteca. O ESP32 só tenta conectar
  no broker com a massa parada (`MANTER` ou `FALHA`), porque a conexão
  pode bloquear o loop por segundos. Broker público só com `SIMULACAO 1`
  (Wokwi).
- **Alternativas descartadas:** os 4 tópicos do contrato (mais código para
  ~400 bytes por segundo numa rede local); ArduinoJson (mais uma biblioteca
  para mensagens planas); broker público com o protótipo real (qualquer um
  que saiba o tópico manda descer).
- **Consequências:** O painel só guarda dados enquanto está aberto (até
  24 h em memória, CSV pela aba Histórico). Passo a passo em `../DIY/`.

## DEC-024 — Motor de 6 V e massa de 2 kg
- **Data:** 2026-10-29
- **Skill:** FÍSICO
- **Status:** substituída por DEC-026 em 2026-10-29 (o motor era o de 14,4 V
  de uma parafusadeira, não um motorredutor de 6 V)
- **Contexto:** O MVP é só prova de conceito. Um motor de 6 V gera metade da
  tensão por rotação que o de 12 V, e 2 kg dão um terço da energia de 6 kg.
- **Decisão:** m_c = 2 kg (uma anilha), h = 1,70 m. Motorredutor de 6 V,
  Ø 37 mm, engrenagens retas 1:90, encoder Hall (referência JGB37-520 6 V;
  K_e ≈ 0,006 V·s/rad, R_a ≈ 1 Ω, I_0 ≈ 0,3 A, estimados). A fonte continua
  12 V 3 A (os LM2596 precisam de > 6,5 V na entrada) e o firmware limita o
  PWM do motor a 50 % (`PWM_MAX = 128`, 6 V em média). E_teo = 33,4 J;
  ~9,9 J gerados; η_ciclo ~0,09.
- **Alternativas descartadas:** fonte de 6 V (os reguladores de 5 V não
  funcionariam); manter 6 kg com o motor de 6 V (corrente de subida ~3,7 A
  no motor, perto do limite do motor pequeno).
- **Consequências:** Tudo refeito em C-101 a C-109. Descida a 0,06–0,13 m/s,
  limite 0,20 m/s, tensão gerada até ~5 V (LEDs em 2 / 3,3 / 4,4 V), carga
  fixa 22 Ω, frenagem 6,8 Ω, TVS 8,2 V, `I_TRAVADO = 1,0 A` na fonte.
- **Revisável em:** ensaio 0, ou quando o Gabriel informar o modelo do
  motor (Q-013).

## DEC-025 — Sem talha, tambor de Ø 30 mm
- **Data:** 2026-10-29
- **Skill:** ARQUITETO
- **Status:** proposta; continua com a parafusadeira (DEC-026), com outros
  números
- **Contexto:** Com 2 kg, a talha 2:1 e o tambor de Ø 20 mm dariam só
  0,098 N·m no tambor. É pouco para o redutor 1:90 retroacionar: a massa
  provavelmente não desceria sozinha.
- **Decisão:** Cordão direto do tambor ao carrinho, tambor de Ø 30 mm
  efetivo (60 mm de largura). Dá 0,294 N·m no tambor, o mesmo do porte de
  6 kg, e `KE_MASSA = 36` V por m/s. Regra para outro motor: Ø do tambor
  (mm) ≈ redução / 3.
- **Alternativas descartadas:** manter a talha (torque baixo demais); tambor
  maior que Ø 30 mm com 1:90 (mais torque, mas menos tensão: o LED vermelho
  só acenderia acima do limite de velocidade).
- **Consequências:** Sai a polia móvel e um rolamento 608; o cordão cai de
  7 m para 3 m; a subida desacelera nos últimos 5 cm (a 0,08 m/s passaria da
  folga do topo). Com a parafusadeira (DEC-026) o tambor continua Ø 30 mm,
  mas a regra "Ø ≈ redução / 3" não vale mais: `KE_MASSA = 21,8` e
  `MM_POR_PULSO = 0.0393` (encoder no tambor).
- **Revisável em:** ensaio 0.

## DEC-026 — Parafusadeira Bosch GSR 1440-LI inteira, 6 kg
- **Data:** 2026-10-29
- **Skill:** FÍSICO + ARQUITETO
- **Status:** decidida pelo Gabriel em 2026-10-29 (respondeu Q-013 e
  escolheu "parafusadeira inteira" entre as opções)
- **Contexto:** O motor que o grupo tem é o de 14,4 V da parafusadeira Bosch
  GSR 1440-LI (artigo 3 601 JA8 4..), não um motorredutor de 6 V. Sozinho,
  é um motor 550 de ~17.600 rpm em vazio, ~1 A em vazio e dezenas de ampères
  travado: precisaria de redução ~250:1 e, com 2 kg, o atrito interno não
  deixaria a massa descer.
- **Decisão:** Usar a parafusadeira inteira (motor + redutor planetário
  ~1:42 na 1ª marcha + mandril), sem bateria, sem gatilho e **sem a trava
  Auto-Lock**. O mandril aperta um eixo Ø 8 mm com o tambor de Ø 30 mm;
  mancal 608 do outro lado; encoder LPD3806-600BM no eixo do tambor
  (acoplamento 6 × 8 mm). Massa volta a **6 kg**. Fonte 12 V **5 A**,
  fusível 5 A, PWM ≤ 50 %. Dados do motor estimados (Mabuchi RS-550VC-7525
  escalado para 14,4 V): K_e ≈ 0,0078 V·s/rad, R_a ≈ 0,2 Ω, I_0 ≈ 1,0 A.
- **Números:** margem para descer ~1,7× (1,3 a 2,4); `KE_MASSA = 21,8`;
  subida a 0,10 m/s com ~5 A no motor e ~1,3 A na fonte (~270 J); descida a
  0,10–0,18 m/s, ~25 J (11 a 37); η_ciclo ~0,09; limite 0,30 m/s; LEDs em
  2 / 2,6 / 3,8 V; carga fixa 5,6 Ω 10 W (descida sem ESP32 a ~0,19 m/s);
  frenagem 2,2 Ω 10 W; `I_TRAVADO = 3,0 A` na fonte; capacitor de
  1.000 µF no B+ do IBT-2.
- **Alternativas descartadas:** só o motor da parafusadeira com outro
  redutor (precisa de ~250:1 e o atrito segura a massa); comprar um
  motorredutor de 6 V (o Gabriel preferiu usar o que o grupo já tem); 2 kg
  com a parafusadeira (margem ~0,6×: não desce).
- **Consequências:** Tudo refeito em C-101 a C-109, firmware, painel, DIY e
  lista de compras (≈ R$ 520 de eletrônica). O motor deixa de ser compra; o
  ensaio 0 não precisa de eletrônica nenhuma. As peças retiradas da
  parafusadeira são guardadas.
- **Revisável em:** ensaio 0 (i, K_e, R_a, I_0 e se desce com 6 kg).
