# 05 — Lista de compras da eletrônica

Preços aproximados, **não cotados** (mesma base de
`../02_ARQUITETO/bom_e_cortes.md`). "Reaproveita" = peça que também serve no
projeto principal; quem já tem não compra.

## Alimentação: como o MVP é ligado

Tudo sai de **uma fonte chaveada 12 V 5 A ligada na tomada** (110/220 V).
Não há bateria (nem a da parafusadeira). Depois da fonte:

```mermaid
flowchart LR
    T["Tomada<br/>110/220 V"] --> PSU["Fonte 12 V 5 A"]
    PSU --> F["Fusível 5 A"]
    F --> B1["LM2596 nº 1<br/>ajustado em 5 V"]
    B1 --> ESP["ESP32 (pino VIN)<br/>5V_LOG"]
    F --> EM["Emergência NF"]
    EM --> POT["12V_POT"]
    POT --> IBT["IBT-2 → parafusadeira 14,4 V<br/>(PWM até 50 %)"]
    POT --> B2["LM2596 nº 2<br/>ajustado em 5 V"]
    B2 --> SERVO["Servo MG90S<br/>5V_SERVO"]
```

- O ESP32 fica **antes** da emergência: apertar o botão corta motor e servo,
  mas o ESP32 continua ligado para avisar o painel e aceitar o rearme.
- Os LEDs de nível **não** gastam da fonte: acendem com a energia que o
  próprio motor gera na descida.
- **O motor da parafusadeira é de 14,4 V e a fonte é de 12 V.** Ele
  aguenta os 12 V, mas recebe pelo IBT-2 com PWM limitado a 50 % no
  firmware, para a massa nunca subir a mais de ~0,23 m/s. Os fios do motor
  saem direto dos terminais dele (o gatilho é retirado, ver
  `../02_ARQUITETO/mecanica.md`).
- Consumo na fonte: motor ~1,3 A na subida (~5 A no motor, a 27 % de PWM;
  um capacitor de 1.000 µF no B+ do IBT-2 alisa os pulsos), servo até
  ~0,3 A, ESP32 ~0,1 A. A fonte de 5 A tem folga para a partida do motor; a
  proteção de massa travada corta acima de 3 A medidos na fonte.
- Na bancada (parte A de [02](02_teste_bancada.md)), o ESP32 roda só com o
  USB do notebook. A fonte de 12 V só entra quando o motor entra.

**Ajuste os dois LM2596 para 5,0 V com o multímetro antes de ligar
qualquer coisa neles.** Eles costumam vir de fábrica com a saída perto da
entrada (12 V), e 12 V queima o ESP32 e o servo.

## Ordem de compra
1. **Primeiro, nada de eletrônica.** O ensaio 0 usa só a parafusadeira
   (sem a trava Auto-Lock), o tambor impresso, o cordão e os 6 kg
   (`../01_FISICA/validacao_experimental.md`). Ele diz se a massa desce
   sozinha. Se não descer, muda o tambor antes de gastar com o resto.
2. **Depois, o resto da lista.**

## Lista

### Motor e encoder
| ☐ | Item | Especificação | Qtd | R$ |
|---|------|---------------|-----|-----|
| ☐ | Parafusadeira | Bosch GSR 1440-LI (artigo 3 601 JA8 4..), a que o grupo já tem. Não precisa da bateria nem do carregador | 1 | 0 |
| ☐ | Encoder rotativo | LPD3806-600BM-G5-24C: 600 pulsos/volta, eixo de 6 mm, 5 a 24 V, saída NPN de coletor aberto | 1 | 90 |
| ☐ | Acoplamento flexível | 6 × 8 mm (eixo do encoder × eixo do tambor) | 1 | 15 |

### Alimentação
| ☐ | Item | Especificação | Qtd | R$ |
|---|------|---------------|-----|-----|
| ☐ | Fonte chaveada | **12 V 5 A** (tipo "colmeia" ou fonte de mesa com plug P4) | 1 | 55 |
| ☐ | Cabo de força | Cabo com plugue de tomada, para a fonte colmeia (a de mesa já vem com cabo) | 1 | 10 |
| ☐ | Regulador | Módulo LM2596 (buck ajustável) | 2 | 24 |
| ☐ | Fusível | 5 A retardado + porta-fusível | 1 | 8 |

### Controle e sensores
| ☐ | Item | Especificação | Qtd | R$ |
|---|------|---------------|-----|-----|
| ☐ | ESP32 | DevKit V1 (ESP32-WROOM-32), 30 pinos. Reaproveita | 1 | 45 |
| ☐ | Cabo USB **de dados** | Micro-USB ou USB-C, conforme a placa (cabo só de carga não grava) | 1 | 15 |
| ☐ | Sensor de corrente | Módulo INA219 (shunt 0,1 Ω, I²C) | 2 | 30 |
| ☐ | Fim de curso | Micro switch com rolete (usar o contato NF). Reaproveita | 2 | 10 |

### Potência: motor, gerador e trava
| ☐ | Item | Especificação | Qtd | R$ |
|---|------|---------------|-----|-----|
| ☐ | Driver de motor | Módulo BTS7960 (IBT-2), 43 A. Reaproveita | 1 | 60 |
| ☐ | MOSFET da frenagem | Módulo D4184 (ou outro módulo MOSFET acionado por 3,3 V). Reaproveita | 1 | 12 |
| ☐ | Servo | MG90S (engrenagem metálica) | 1 | 25 |
| ☐ | Resistor de frenagem | 2,2 Ω 10 W, cerâmico (de fio) | 1 | 6 |
| ☐ | Carga fixa | 5,6 Ω 10 W, cerâmico | 1 | 6 |

### Segurança e interface
| ☐ | Item | Especificação | Qtd | R$ |
|---|------|---------------|-----|-----|
| ☐ | Botão de emergência | Cogumelo 22 mm com trava, contato **NF**. Reaproveita | 1 | 25 |
| ☐ | Chave de demanda | Chave alavanca liga/desliga (1 polo) | 1 | 5 |

### Semicondutores e passivos
| ☐ | Item | Para quê | Qtd | R$ |
|---|------|----------|-----|-----|
| ☐ | Diodo Schottky 1N5822 (3 A) | Saída do gerador (M− → GEN), série no B+ do IBT-2 e antiparalelo no resistor de frenagem | 3 | 5 |
| ☐ | Diodo 1N4148 | 1 em série com o LED amarelo (acende em ~2,6 V) e 3 com o vermelho (~3,8 V) | 4 | 1 |
| ☐ | TVS P6KE8.2A (com fios) ou SMBJ7.0A (SMD) | Proteção do barramento gerado (a descida normal gera até ~4 V; acima de 7 V é falha) | 1 | 3 |
| ☐ | LED 5 mm | Verde, amarelo e vermelho (nível de geração) | 3 | 2 |
| ☐ | Capacitor eletrolítico 1.000 µF 25 V | B+ do IBT-2, depois do diodo: o INA219 nº 1 lê a média do PWM | 1 | 3 |
| ☐ | Capacitor eletrolítico 470 µF 25 V | Barramento gerado | 1 | 2 |
| ☐ | Capacitor cerâmico 100 nF | Barramento gerado e fins de curso (1 de sobra) | 4 | 1 |
| ☐ | Resistor 220 Ω ¼ W | Série dos 3 LEDs | 3 | 1 |
| ☐ | Resistor 10 kΩ ¼ W | Pull-down de R_EN e L_EN (2), pull-up dos fins de curso (2), divisor da emergência (1) | 5 | 1 |
| ☐ | Resistor 3,3 kΩ ¼ W | Divisor da emergência (12 V → 3,0 V no GPIO 34) | 1 | 1 |
| ☐ | Resistor 4,7 kΩ ¼ W | Pull-up do encoder (A e B) para o 3,3 V | 2 | 1 |

Kits de resistores e de capacitores sortidos costumam sair mais baratos que
peças avulsas, e muitos fablabs têm.

### Montagem
| ☐ | Item | Especificação | Qtd | R$ |
|---|------|---------------|-----|-----|
| ☐ | Placa perfurada | 7 × 9 cm ou maior | 1 | 8 |
| ☐ | Bornes | Borne KF301 de 2 e 3 vias, para os fios de potência | ~10 | 10 |
| ☐ | Fio de potência | 1 mm² (18 AWG), vermelho e preto, ~3 m de cada | — | 12 |
| ☐ | Fio de sinal | 0,2 mm² (24 AWG) ou cabo flat; ~6 m até os fins de curso no alto da torre | — | 8 |
| ☐ | Jumpers e protoboard | Macho-fêmea e macho-macho; protoboard para a bancada | — | 15 |
| ☐ | Barra de pinos fêmea | Para o ESP32 não ficar soldado na placa | 2 | 3 |

**Total ≈ R$ 520** com tudo comprado; **≈ R$ 365** reaproveitando ESP32,
IBT-2, MOSFET, fins de curso e emergência do projeto principal. A
parafusadeira entra com R$ 0 porque o grupo já tem.

## Ferramentas que precisam existir no fablab
Multímetro (obrigatório, para ajustar os LM2596), ferro de solda e estanho,
alicate de corte e desencapador, chaves de fenda pequenas.

## Onde cada peça liga
- Circuito completo: `../02_ARQUITETO/circuito.md`
- Pinos do ESP32: `../03_SOFTWARE/pinagem_mvp.md`
- Mecânica (perfil, chapas, filamento, cordão): `../02_ARQUITETO/bom_e_cortes.md`
