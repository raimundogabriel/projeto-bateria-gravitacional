# ESQUEMA DE POTÊNCIA (eletrônica v2, 2026-10-22)

Diagramas em `02_ARQUITETO/circuitos/diagrama_blocos.md`; pinagem em
`03_SOFTWARE/pinagem_esp32.md`. Esta versão corrige sete problemas do
relatório revisado (ver INC-027).

## TENSÕES ENVOLVIDAS
- Fonte: 24 V 5 A chaveada, isolada da rede
- 24V_POT: 24 V depois do relé de corte K1 (motor e solenoide)
- Barramento gerado (GEN): 0 a ~23 V na descida (253 V por m/s de massa),
  limitado por firmware a 28 V
- Lógica: 5 V (LM2596, sempre ligado, antes do K1) e 3,3 V (regulador do
  ESP32)
- Motor: subir a 0,05 m/s pede ~13 V (PWM 55 %) e ~0,8 A; máximo ~0,09 m/s

## BLOCOS

### 1. Entrada e corte
Fonte 24 V → fusível 5 A retardado → contato NA do K1 (GPIO 27) → 24V_POT.
O 24V_POT alimenta o BTS7960 (via INA226 nº 1) e o solenoide.
O LM2596 (ajustado em 5,0 V) fica antes do K1: com o corte aberto, o ESP32
continua ligado para alertar e receber o rearme (INC-021).
5 V → VIN do ESP32, LCD, encoder e JD-VCC dos relés (passando pela
emergência). 3,3 V do ESP32 → INA226, DS3231 e VCC do módulo de relés.

### 2. Acionamento (subida)
BTS7960 (IBT-2): RPWM GPIO 16, LPWM GPIO 17 (só rearme e teste), R_EN + L_EN
no GPIO 18 com 10 kΩ ao GND (motor desligado no boot). VCC lógico do IBT-2 em
**3,3 V** (com 5 V o 74HC244 do módulo não garante ler 3,3 V como alto).
PWM 20 kHz. M+ e M− vão aos contatos NA do K2.

### 3. Relé de modo, geração e frenagem (descida)
K2 = dois canais do módulo de relés no mesmo GPIO 23, formando um DPDT. Os
comuns vão aos fios do motor.
- Energizado (NA): motor no BTS7960. Só na subida.
- Repouso (NF): o terminal positivo na descida vai ao D1; o outro, ao GND.
  Confirmar a polaridade girando o eixo à mão com multímetro.

Barramento gerado: D1 (Schottky SR560, 5 A 60 V) → fusível 3 A → 2.200 µF
50 V + 100 nF + TVS SMBJ28A → INA226 nº 2 → nó GEN, que alimenta em paralelo:
- **Frenagem:** 2 × 22 Ω 25 W em paralelo (11 Ω, DEC-010) em série com módulo
  MOSFET D4184 no GPIO 19 (PWM 5 kHz), 1N5822 em antiparalelo com os
  resistores. Mais PWM = mais freio = descida mais lenta.
- **USB:** buck XL4015 (entrada 8–35 V, saída 5,3 V) → 1N5819 → INA226 nº 3 →
  USB-A fêmea. Unir D+ e D− da porta (sem isso o celular puxa só 500 mA).
- **LEDs de geração (sem software):** verde com 2,2 kΩ ½ W (acima de ~3 V);
  amarelo com Zener 6,8 V + 2,2 kΩ (acima de ~9 V, USB já funciona);
  vermelho com Zener 18 V + 2,2 kΩ (acima de ~20 V, sobra para o freio).
- **Sondagem da demanda (DEC-008):** 5 V da lógica → NA do K4 (GPIO 13) →
  4,7 Ω 1 W → 1N5819 → mesmo nó da USB (~100 mA no máximo).

### 4. Trava de catraca
Solenoide 24 V no 24V_POT, módulo MOSFET D4184 no GPIO 4 (PWM 20 kHz), 1N5822
em antiparalelo com a bobina. Hit-and-hold: 100 % por 300 ms, depois 30 %.

### 5. Segurança
- Módulo de 4 relés 5 V com optoacoplador: K1 (GPIO 27), K2 (2 canais, GPIO
  23), K4 (GPIO 13). Retirar o jumper JD-VCC: VCC em 3,3 V, JD-VCC em 5 V
  passando pelo botão de emergência NF (cogumelo, com trava).
- Emergência apertada: bobinas sem energia → K1 abre (sem 24 V no motor e no
  solenoide, a trava engata), K2 cai para geração, K4 abre. Funciona com o
  ESP32 travado (DEC-009).
- Divisor 10 kΩ / 20 kΩ do JD-VCC ao GPIO 34 informa a emergência.
- Fins de curso NF entre GPIO e GND, pull-up 10 kΩ a 3,3 V + 100 nF. Fio
  rompido = acionado.
- Watchdog do ESP32 ligado.
- Relés ativos em baixo: `digitalWrite(pino, HIGH)` antes de
  `pinMode(pino, OUTPUT)`, senão o relé pulsa no boot.

### 6. Sensores e interface
| Peça | Ligação | Observação |
|------|---------|------------|
| Encoder LPD3806-600BM | 5 V; A/B no GPIO 32/33 com pull-up 4,7 kΩ a 3,3 V | Coletor aberto; 25,5 pulsos por mm de massa |
| INA226 nº 1 (subida) | I²C 0x40, high-side no 24V_POT | Shunt trocado por 10 mΩ (R010) |
| INA226 nº 2 (gerado) | I²C 0x41 (A0 em VS), high-side no GEN | Shunt 10 mΩ |
| INA226 nº 3 (USB) | I²C 0x44 (A1 em VS), high-side no 5 V da USB | Shunt 10 mΩ |
| RTC DS3231 | I²C 0x68 | Pilha CR2032; retirar o diodo de carga do módulo |
| LCD 20×4 PCF8574 | I²C 0x27 via conversor BSS138 | Pull-ups do módulo retirados |
| Buzzer ativo | GPIO 14 | |

**Aterramento:** GND de potência e GND lógico se encontram num único ponto, no
negativo da fonte. Fios: potência 1,5 mm², barramento gerado 0,75 mm²,
sinais 0,2 mm².

## SEQUÊNCIAS DE OPERAÇÃO
A ordem dos passos mantém a massa sempre presa por algo: lingueta, motor ou
freio elétrico.

**Subir:** conferir emergência solta, fim de curso superior livre, solenoide
desligado → fechar K1, frenagem 0 %, energizar K2, esperar 50 ms → EN alto e
rampa RPWM 0 → 55 % em 1 s (a catraca estala e deixa subir) → PWM em malha
para 0,05 m/s → para parar: rampa a 0, EN baixo, esperar 200 ms (massa assenta
na lingueta), soltar K2.

**Descer (gerar):** conferir fim de curso inferior livre e comando de descida
→ fechar K1, energizar K2 e subir 3 mm (~77 pulsos) para aliviar a lingueta →
solenoide 100 % por 300 ms com o motor segurando, depois 30 % → frenagem
100 % → EN baixo, RPWM 0, soltar K2 (troca ~10 ms; a massa desce < 1 mm) →
malha PI a cada 50 ms com alvo 0,03–0,08 m/s → para parar: frenagem 100 %
(~0,025 m/s), desligar o solenoide, esperar a lingueta pegar o dente; após
500 ms parada, frenagem 0 %.

**Manter:** solenoide, motor, K1 e K2 desligados. A cada 30 s, K4 liga 1 s e
lê o INA226 nº 3; acima de 30 mA há aparelho na USB.

**Falha** (fim de curso inesperado, > 0,10 m/s, > 28 V no GEN, > 3 A com
encoder parado por 500 ms, emergência): solenoide 0, frenagem 100 %, EN
baixo, K2 e K1 soltos, buzzer. Só o rearme sai.

**Rearme com posição desconhecida:** sequência de descida com frenagem fixa
em 100 % até o fim de curso inferior; ali o encoder é zerado.

## CÁLCULO DE COMPONENTES
### Fusível principal
Fonte de 5 A; subida em regime ~1,5 A no máximo, partida até ~3 A →
fusível 5 A retardado.
### Fusível do barramento gerado
Corrente gerada ~0,6 A com 20 kg (até ~2,9 A com 100 kg) → 3 A.
### Diodos de roda livre
Vrrm ≥ 2 × 24 = 48 V. 1N5822 (40 V, 3 A) nas cargas indutivas e resistivas
do GEN (máx. 28 V); SR560 (60 V, 5 A) em série com o motor no GEN.
### TVS do GEN
SMBJ28A: conduz acima de ~31 V, abaixo dos 35 V do buck e dos 50 V dos
capacitores.

## PROTEÇÕES OBRIGATÓRIAS
- [x] Fusível geral (5 A retardado) e do GEN (3 A)
- [x] Diodos de roda livre no solenoide e na frenagem
- [x] TVS SMBJ28A no barramento gerado
- [x] Optoacoplador entre lógica e relés (módulo de 4 relés, JD-VCC separado)
- [x] Pull-down de 10 kΩ no EN do BTS7960
- [x] Emergência NF cortando as bobinas de todos os relés por hardware
- [x] Fins de curso NF (fio rompido = acionado)
- [x] Watchdog do ESP32

## BOM (eletrônica, preços aproximados, de memória, não cotados)
Total ≈ R$ 670 sem a fonte de 24 V e o motorredutor.

| Item | Espec | Qtd | Preço (R$) | Fornecedor |
|------|-------|-----|------------|------------|
| ESP32 DevKit V1 | WROOM-32 | 1 | 45 | ML / AliExpress |
| Driver de motor | BTS7960 (IBT-2) | 1 | 60 | ML / AliExpress |
| Sensor de corrente | INA226 + shunt R010 (2512) | 3 | 85 | ML / AliExpress |
| RTC | DS3231 | 1 | 20 | ML / AliExpress |
| LCD | 20×4 com I²C + conversor BSS138 | 1 | 53 | ML / AliExpress |
| Relés | Módulo 4 relés 5 V com opto | 1 | 30 | ML / AliExpress |
| MOSFET | Módulo D4184 (aceita 3,3 V) | 2 | 24 | ML / AliExpress |
| Encoder | LPD3806-600BM | 1 | 90 | ML / AliExpress |
| Fins de curso | Micro switch com rolete (1 opcional) | 3 | 15 | ML / AliExpress |
| Emergência | Cogumelo NF 22 mm | 1 | 25 | ML / AliExpress |
| Solenoide | Push-pull 24 V, curso 10 mm | 1 | 45 | ML / AliExpress |
| Frenagem | Resistor de fio 22 Ω 25 W, carcaça de alumínio | 2 | 30 | ML / AliExpress |
| USB | Buck XL4015 + USB-A fêmea | 1 | 25 | ML / AliExpress |
| Lógica | Buck LM2596 | 1 | 12 | ML / AliExpress |
| Diodos | SR560, 3× 1N5822, 3× 1N5819, Zener 6,8 V e 18 V, SMBJ28A | — | 15 | ML / AliExpress |
| Capacitores | 2.200 µF 50 V e 100 nF | — | 8 | ML / AliExpress |
| Fusíveis | 5 A e 3 A com porta-fusível | 2 | 15 | ML / AliExpress |
| Diversos | LEDs, resistores, buzzer ativo, 4,7 Ω 1 W | — | 15 | ML / AliExpress |
| Montagem | Bornes, fios 1,5 e 0,75 mm², jumpers, placa perfurada | — | 60 | ML / AliExpress |
| Fonte (fora do total) | Chaveada 24 V 5 A | 1 | ~80 | ML / AliExpress |

ML = Mercado Livre. Fornecedor indica onde procurar, não uma cotação feita.
