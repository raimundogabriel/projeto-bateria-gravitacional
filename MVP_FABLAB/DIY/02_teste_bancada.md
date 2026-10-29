# 02 — Teste na bancada

## Parte A — ESP32 sozinho, `SIMULACAO 1` (sem montar nada)

Com `SIMULACAO 1` o ESP32 calcula a massa, o gerador e o encoder dentro do
código, igual ao Wokwi. Só faltam as chaves que o Wokwi tem: sem elas os
pinos ficam soltos e o firmware acha que o fim de curso está acionado ou que
a emergência foi apertada. Ligue **4 jumpers** na placa:

| Jumper | Faz o papel de |
|--------|----------------|
| GPIO **34** → **3V3** | Emergência solta (12 V presente) |
| GPIO **25** → **GND** | Fim de curso inferior livre (NF fechado) |
| GPIO **26** → **GND** | Fim de curso superior livre |
| GPIO **35** → **GND** | Corrente de subida 0 A (no Wokwi é o potenciômetro) |

Opcional: GPIO **27** → **GND** liga a chave de demanda (5 W). Sem jumper,
não há demanda; o painel também pode mandar (`w5` no Serial).

O LED azul da placa é o GPIO 2: na simulação ele faz o papel do LED
vermelho do gerador e acende quando a descida passa de ~3,8 V (0,17 m/s).

### Roteiro (Monitor Serial a 115200)
1. Reset (botão EN): `REARME`, a massa virtual desce de 0,40 m até 0 em
   ~7 s e fica em `MANTER`.
2. `h3` (3 h, tarifa fora de ponta): `SUBINDO` a 0,10 m/s, mais devagar nos
   últimos 5 cm, até o fim de curso (1,70 m, ~20 s). `Esub` chega a ~270 J.
3. `h19` (ponta) e `w5` (demanda de 5 W): `PREP_DESCIDA` e `DESCENDO`;
   `Egen` sobe até ~25 J numa descida inteira (~9,5 s a 0,18 m/s).
4. Tire o jumper do GPIO 34: `FALHA motivo=emergencia`. Recoloque e digite
   `r`: volta ao `REARME`.
5. `hx`: volta à hora real (NTP). Precisa do Wi-Fi conectado.

Se isso funcionou, vá para [03_painel_mqtt.md](03_painel_mqtt.md) e ligue
o painel antes de montar qualquer peça.

## Parte B — protótipo real, `SIMULACAO 0`

Troque para `#define SIMULACAO 0`, instale as bibliotecas Adafruit INA219 e
ESP32Encoder (passo 4 de [01_gravar_firmware.md](01_gravar_firmware.md)) e
grave de novo. **Tire os 4 jumpers da parte A.** A ligação completa está em
`../02_ARQUITETO/circuito.md` e a pinagem em
`../03_SOFTWARE/pinagem_mvp.md`. Siga os ensaios de
`../01_FISICA/validacao_experimental.md` na ordem; abaixo está o que olhar
no firmware em cada um. O **ensaio 0** (parafusadeira sem a trava Auto-Lock,
descendo sozinha com 6 kg) vem antes de tudo e não usa o ESP32: o preparo da
parafusadeira está em `../02_ARQUITETO/mecanica.md`.

### Ensaio 1 — só lógica, ESP32 no USB do notebook
- **INA219:** os dois no I²C (SDA 21, SCL 22, 3,3 V). O segundo precisa do
  jumper **A0** soldado (endereço 0x41). Se faltar algum, o Serial mostra
  `INA219 nao encontrado` e o firmware fica em `FALHA` de propósito: sem
  medir a corrente, a proteção de massa travada não funciona.
- **Emergência:** sem 12 V o GPIO 34 lê baixo e o firmware entra em
  `FALHA motivo=emergencia`. Para testar só a lógica, ponha o jumper
  34 → 3V3 **e tire antes de ligar os 12 V**.
- **Encoder LPD3806** (no eixo do tambor): vermelho no **5 V**, preto no
  GND. As saídas A (verde) e B (branco) são de coletor aberto: cada uma
  precisa de um resistor de **4,7 kΩ para o 3,3 V** (nunca para o 5 V). A →
  GPIO 32, B → GPIO 33. Gire o tambor uma volta no sentido de subir: `h`
  deve aumentar ~0,094 m (2.400 contagens × 39,3 µm). Se **diminuir**,
  troque os fios A e B.
- **Fins de curso NF:** ligados entre o GPIO e o GND. Apertar com a mão
  abre o contato e o firmware vê “acionado”. Fio solto também vira
  “acionado”, o que é o lado seguro.

### Ensaio 2 — motor sem cordão, 12 V com PWM até 50 %
No boot o firmware faz o `REARME`: sobe 3 mm, solta a trava e desce até o
fim de curso inferior. Sem cordão a massa nunca chega lá, então **aperte o
fim de curso inferior com a mão** para terminar o rearme. Depois, em manual:
`s` sobe, `p` para. Olhe `I=` no Serial (ou “Potência” no painel): deve ficar
perto de C-108 (~1,3 A na fonte a 0,10 m/s com a massa; ~0,3 A sem
cordão). O motor é de 14,4 V e aguenta os 12 V, mas o firmware nunca passa
de 50 % de PWM (`PWM_MAX`) para a subida não passar de ~0,23 m/s. **Não
ligue o motor direto nos 12 V com o cordão preso:** a massa subiria a
~0,5 m/s, rápido demais para os fins de curso.

### Ensaio 3 — trava (servo)
Ajuste `SERVO_ENGATADA` (20°) e `SERVO_SOLTA` (80°) no topo do sketch até a
lingueta soltar e engatar 20 vezes seguidas. `T_SERVO` (300 ms) é o tempo
que o firmware espera o servo antes de soltar o motor.

### Ensaios 4 a 6 — gerador e massa
Com o painel aberto (fonte “ESP32 (MQTT)”), cada descida aparece na aba
**Energia** com a energia gerada, e a aba **Histórico** baixa o CSV para
preencher a tabela de `validacao_experimental.md`. Suba primeiro só com o
carrinho e com 2 kg, com corda de segurança; a descida sozinha só acontece
com os 6 kg (com menos, o atrito do motor segura, C-104).
