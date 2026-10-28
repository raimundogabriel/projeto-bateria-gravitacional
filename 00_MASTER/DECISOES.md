# REGISTRO DE DECISÕES

Modelo de entrada:

```
## DEC-XXX — [Título curto]
- **Data:** AAAA-MM-DD
- **Skill:** FÍSICO / ARQUITETO / DESENVOLVEDOR
- **Contexto:** [por que precisou decidir]
- **Decisão:** [o que foi decidido]
- **Alternativas descartadas:** [lista + motivo]
- **Consequências:** [o que muda nas outras skills]
- **Revisável em:** [condição para reabrir]
```

> A versão inicial deste arquivo trazia um exemplo com 500 kg e 3 m. Ele não
> vale para o projeto e foi substituído pela DEC-001.

---

## DEC-001 — Massa de 20 kg e curso útil de 1,70 m
- **Data:** 2026-10-07
- **Skill:** FÍSICO
- **Contexto:** O relatório original misturava 20 a 100 kg e alturas de
  1,70 m e 3 m (INC-003, INC-005). A auditoria deu NO-GO para 20–100 kg e GO
  condicional para um protótipo reduzido.
- **Decisão:** m_c = 20 kg, h = 1,70 m (fim de curso inferior em h = 0,
  superior em h = 1,70 m). E_teo = 333,5 J (0,093 Wh) por ciclo.
- **Alternativas descartadas:** 50 kg nominal / 100 kg máximo (estrutura,
  custo e risco de carga suspensa sem necessidade para a demonstração);
  3 m de altura (não cabe na torre de 2,10 m).
- **Consequências:** ARQUITETO dimensiona para 20 kg com margem até 50 kg;
  DESENVOLVEDOR usa `CURSO = 1.70` no firmware.
- **Revisável em:** se o grupo quiser ensaiar mais massa (até 50 kg sem
  mudar a mecânica).

## DEC-002 — g = 9,81 m/s² e unidades SI
- **Data:** 2026-10-07
- **Skill:** FÍSICO
- **Contexto:** Evitar valores diferentes de g e conversões espalhadas.
- **Decisão:** g = 9,81 m/s² fixo; todos os cálculos em SI; conversões (Wh,
  rpm, R$) só na interface do painel.
- **Alternativas descartadas:** g = 9,8 ou 10 (diferenças pequenas, mas geram
  números que não batem entre documentos).
- **Consequências:** ver `00_MASTER/GLOSSARIO.md`.
- **Revisável em:** não se aplica.

## DEC-003 — Um único motorredutor como motor e gerador (opção A)
- **Data:** 2026-10-07
- **Skill:** ARQUITETO
- **Contexto:** O relatório não definia o gerador (INC-001, INC-008), e o
  tambor sozinho giraria a ~16 rpm.
- **Decisão:** Motorredutor DC escovado 24 V ~50 W, 3.000 rpm, redutor
  planetário 1:50 (aceita 1:40 a 1:60), torque nominal ≥ 6 N·m, eixo 12 mm.
  Talha 2:1 + tambor Ø 60 mm → relação total massa → motor de 100:1 (1 cm de
  descida ≈ 5,3 voltas do motor). Ke = Kt ≈ 0,076 V·s/rad (a confirmar em
  ensaio). Na descida, o relé de modo liga o motor ao barramento gerado.
- **Alternativas descartadas:** NEMA 23 como gerador com corrente de bicicleta
  1:9,4 (B); dínamo de cubo 1:8 (C, não segura 20 kg rápido); motor de esteira
  (D, pesado, sobretensão); motor 12 V pequeno (E, perdas); redutor sem-fim
  (autotravante, impede a descida).
- **Consequências:** Não existe gerador separado; o estágio de engrenagens é
  o redutor planetário + talha. ARQUITETO especifica o barramento gerado;
  DESENVOLVEDOR controla a descida pela frenagem.
- **Revisável em:** se o ensaio de bancada mostrar tensão < 8 V a 0,05 m/s.

## DEC-004 — Demonstração: LED (mínimo) e celular via USB (máximo)
- **Data:** 2026-10-07
- **Skill:** FÍSICO
- **Contexto:** Pedido do Gabriel: o gerador deve no mínimo acender um LED e,
  no máximo, carregar um celular por USB enquanto o peso desce.
- **Decisão:** Ponto de projeto 0,05 m/s (~34 s de descida, ~12,7 V em
  vazio, ~5 W gerados, 4 a 5 W na porta USB). Abaixo de 0,04 m/s só os LEDs
  funcionam (o buck USB pede ≥ 8 V).
- **Alternativas descartadas:** descida lenta de horas (potência de ~0,07 W,
  não acende nada útil; INC-012).
- **Consequências:** O fuzzy só manda descer se houver demanda na saída
  (R11); a velocidade-alvo fica entre 0,03 e 0,08 m/s.
- **Revisável em:** após medir tensão × velocidade com 20 kg.

## DEC-005 — Trava de catraca com solenoide + frenagem elétrica
- **Data:** 2026-10-07
- **Skill:** ARQUITETO
- **Contexto:** O freio eletromagnético "liberado quando energizado" gastava
  mais do que o ciclo gera e estava no GPIO 14, que pulsa no boot (INC-002,
  INC-015).
- **Decisão:** Roda de catraca no eixo do tambor com lingueta puxada por
  solenoide 24 V (GPIO 4), ligada só na descida com hit-and-hold (100 % por
  300 ms, depois 30 %). A velocidade de descida é controlada pelo próprio
  gerador contra um resistor de frenagem com MOSFET em PWM (GPIO 19), em
  malha fechada pelo encoder.
- **Alternativas descartadas:** freio eletromagnético (consumo); freio por
  atrito para controlar velocidade (dissipa a energia que se quer gerar).
- **Consequências:** Sem energia, a lingueta cai e a massa fica presa (falha
  segura). A descida começa subindo 3 mm para aliviar a lingueta, o que exige
  ~2 cm de folga mecânica acima do fim de curso superior.
- **Revisável em:** se o solenoide não soltar a lingueta com a mola montada.

## DEC-006 — Três INA226 com shunt de 10 mΩ no lugar do INA219
- **Data:** 2026-10-22
- **Skill:** ARQUITETO
- **Contexto:** INA219 vai só a 26 V e ~3,2 A; o módulo INA226 comum (shunt
  0,1 Ω) satura em 0,82 A (INC-007).
- **Decisão:** 3× INA226 com shunt R010: nº 1 subida (0x40, high-side no
  24V_POT), nº 2 barramento gerado (0x41), nº 3 saída USB (0x44).
- **Alternativas descartadas:** 2 INA226 (versão do relatório v2: sem medir a
  USB separada da frenagem); PZEM-004T (mede rede CA, fora do escopo).
- **Consequências:** Endereços I²C fixos; o painel recebe potência de subida,
  gerada e entregue à USB.
- **Revisável em:** não se aplica.

## DEC-007 — Fuzzy Mamdani com 3 entradas e 11 regras
- **Data:** 2026-10-07
- **Skill:** FÍSICO
- **Contexto:** A base de regras original tinha buracos, demanda em escala de
  kW e entradas redundantes (INC-009, INC-010, INC-011).
- **Decisão:** Entradas: tarifa (0–2 R$/kWh), nível de carga (0–100 %),
  demanda da saída (0–10 W). Saída: comando −100 (descer) a +100 (subir).
  Regras R1–R11 (ver `01_FISICA/algoritmos_controle.md`). Defuzzificação por
  centroide, normalizada pelo máximo que o centroide alcança. Tarifa vem de
  tabela por posto horário; o posto não é entrada separada.
- **Alternativas descartadas:** demanda da casa em W via PZEM (não muda o que
  a bateria consegue entregar); posto horário como entrada (redundante com a
  tarifa).
- **Consequências:** DESENVOLVEDOR implementa no ESP32 e no painel com as
  mesmas funções de pertinência.
- **Revisável em:** após ensaios, para ajustar as funções de pertinência.

## DEC-008 — Sondagem da demanda USB pelo relé K4
- **Data:** 2026-10-22
- **Skill:** ARQUITETO
- **Contexto:** Com a massa parada não há geração, a porta USB fica sem
  energia, o INA226 lê 0 W e a regra R11 manteria a massa parada para sempre.
- **Decisão:** A cada 30 s em MANTER, o K4 (GPIO 13) liga a USB ao 5 V da
  lógica por 1 s via 4,7 Ω 1 W + 1N5819. Acima de 30 mA, há aparelho ligado.
- **Alternativas descartadas:** botão manual "tem celular" (depende de
  pessoa); deixar a USB sempre alimentada pela lógica (descaracteriza a
  demonstração).
- **Consequências:** DESENVOLVEDOR implementa a sondagem; o painel mostra a
  demanda.
- **Revisável em:** não se aplica.

## DEC-009 — Estado seguro por hardware: K2 em geração com frenagem a 100 %
- **Data:** 2026-10-22
- **Skill:** ARQUITETO
- **Contexto:** O relatório pedia que o relé de modo "só comute com corrente
  nula", o que é impossível com a massa pendurada e a trava solta.
- **Decisão:** K2 (dois canais no GPIO 23, formando um DPDT) em repouso deixa
  o motor no barramento gerado com a frenagem a 100 %. O botão de emergência
  NF corta o JD-VCC do módulo de relés: K1 abre (sem 24 V no motor e no
  solenoide, a trava engata), K2 cai para geração, K4 abre. O LM2596 fica
  antes do K1, então o ESP32 continua ligado para alertar e receber o rearme.
- **Alternativas descartadas:** relé de corte desligando também o ESP32
  (impede alerta e rearme remoto, INC-021).
- **Consequências:** Com o ESP32 travado ou em emergência, a massa fica na
  lingueta ou cai lentamente no freio elétrico.
- **Revisável em:** não se aplica.

## DEC-010 — Resistor de frenagem de 11 Ω (2 × 22 Ω 25 W em paralelo)
- **Data:** 2026-10-22
- **Skill:** ARQUITETO
- **Contexto:** Com 22 Ω a 100 % a massa desce a ~0,05 m/s, rápido demais
  para o rearme e para parar.
- **Decisão:** 2 × 22 Ω 25 W em paralelo (11 Ω), descida mínima ~0,025 m/s.
- **Alternativas descartadas:** 22 Ω único (velocidade mínima alta).
- **Consequências:** `V_FREIO_TOTAL = 0.025` no firmware.
- **Revisável em:** ensaio com 5 kg (escolher entre 22 Ω e 11 Ω).

## DEC-011 — Simulação no Wokwi com ESP32 (em vez de Tinkercad/Uno)
- **Data:** 2026-10-22
- **Skill:** DESENVOLVEDOR
- **Contexto:** O Tinkercad não tem ESP32; a versão para Uno exigia outra
  pinagem.
- **Decisão:** Projeto Wokwi com ESP32 DevKit V1, mesma pinagem do circuito
  real, flag `SIMULACAO` (1 = planta virtual, 0 = hardware real).
- **Alternativas descartadas:** Tinkercad com Arduino Uno (mantido só como
  histórico em `03_SOFTWARE/firmware/bateria_gravitacional_tinkercad.ino`).
- **Consequências:** O mesmo código vai ao protótipo trocando a flag e
  completando `lerSensores()`.
- **Revisável em:** não se aplica.

## DEC-012 — Estrutura em metalon 30 × 30 × 1,2 mm
- **Data:** 2026-10-07
- **Skill:** ARQUITETO
- **Contexto:** A estrutura não tinha dimensionamento (INC-005).
- **Decisão:** Metalon 30 × 30 × 1,2 mm soldado em toda a estrutura (2
  colunas-guia de 2,10 m, base 0,80 × 0,80 m, travamento diagonal). Com
  20 kg a travessa superior chega a 61 MPa (≈ 4× abaixo do escoamento).
- **Alternativas descartadas:** perfis maiores (desnecessários para 20 kg).
- **Consequências:** Acima de 50 kg, a travessa superior passa a 50 × 50 ×
  2 mm.
- **Revisável em:** se a massa aumentar.
