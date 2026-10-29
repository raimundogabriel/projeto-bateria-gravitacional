# 04 — Problemas comuns

## Gravar

| Sintoma | Causa provável | O que fazer |
|---------|----------------|-------------|
| Nenhuma porta em Tools → Port | Cabo só de carga ou falta driver | Troque o cabo; instale o driver CP210x ou CH340 ([01](01_gravar_firmware.md), passo 3) |
| `Connecting........_____` e falha | Placa não entrou em modo de gravação | Segure **BOOT** durante o `Connecting…`; se ainda falhar, Tools → Upload Speed → 115200 |
| `PubSubClient.h: No such file` | Biblioteca não instalada | Instale PubSubClient (Nick O'Leary) |
| `Adafruit_INA219.h` ou `ESP32Encoder.h: No such file` | `SIMULACAO 0` sem as bibliotecas do protótipo | Instale as duas, ou volte para `SIMULACAO 1` |
| `'ledcSetup' was not declared` ou parecido | — | Não deveria acontecer: o sketch trata as versões 2.x e 3.x do pacote ESP32. Anote a versão em HANDOFF |
| Monitor Serial com caracteres estranhos | Velocidade errada | 115200 no canto do Monitor |
| `Brownout detector was triggered`, reinicia sozinho | USB fraco (hub, cabo longo) com Wi-Fi ligado | Porta USB direto no notebook; no protótipo, alimente pelo regulador de 5 V |

## Wi-Fi e broker

O Serial mostra o motivo. `MQTT: falhou, rc=…`:

| rc | Significa | O que fazer |
|----|-----------|-------------|
| −2 | Não chegou no broker | IP errado em `MQTT_BROKER`, Mosquitto desligado, firewall bloqueando a porta 1883, ou ESP32 e notebook em redes diferentes |
| −4 | Broker não respondeu a tempo | Rede ruim; aproxime o ESP32 do roteador |
| 5 | Broker recusou (não autorizado) | Faltou `allow_anonymous true` no `.conf` ou o Mosquitto foi iniciado sem `-c` |

| Sintoma | Causa provável | O que fazer |
|---------|----------------|-------------|
| Nunca aparece `MQTT: conectando` | Wi-Fi não conectou, ou a massa não está parada | Confira SSID e senha (maiúsculas contam), rede 2,4 GHz, sem login pessoal. O ESP32 só tenta o broker em `MANTER` ou `FALHA`: espere o rearme terminar |
| `hora=--` no Serial e o automático não faz nada | NTP sem resposta (Wi-Fi sem internet, como o roteador do celular sem dados) | Mande a hora pelo painel (“Enviar hora”) ou `h19` no Serial; os comandos manuais funcionam sem hora |
| `mosquitto_sub` em `localhost` não mostra nada | O ESP32 não está publicando nesse broker | Veja `MQTT:` no Serial do ESP32. Teste o broker sozinho: `mosquitto_pub -h localhost -t grav/teste -m oi` em outro terminal |
| Funciona em casa e não no fablab | Rede do fablab isola os aparelhos ou exige login | Use o roteador do celular |
| Conectava ontem, hoje não | IP do notebook mudou | `ipconfig` de novo e regrave o ESP32 |

## Painel

| Sintoma | Causa provável | O que fazer |
|---------|----------------|-------------|
| 🔴 “Sem broker: não conectou em …” | Mosquitto desligado ou endereço errado no painel | O painel e o Mosquitto no mesmo notebook: use `localhost` |
| 🟠 “Broker ok; esperando o ESP32 em `grav/estado`” | Tópico base diferente no painel e no sketch, ou o ESP32 está em outro broker | `TOPICO_BASE` no sketch = “Tópico base” no painel |
| 🟠 “ESP32 sem publicar há N s” | ESP32 reiniciou, saiu do Wi-Fi ou travou | Olhe o Serial; com a massa em movimento ele não reconecta até parar |
| “Sem conexão com o broker: nada foi enviado” ao clicar | Broker caiu | Espere o 🟢 voltar e clique de novo; o comando não fica guardado |
| `ModuleNotFoundError: paho` | Faltou instalar os pacotes | `pip install -r requirements.txt` com o `.venv` ativado |
| Gráficos de energia zerados | Janela de tempo curta, ou nenhuma descida terminou | Aumente a janela; a energia por descida só aparece no fim de cada descida |

## Protótipo (`SIMULACAO 0`)

| Sintoma | Causa provável | O que fazer |
|---------|----------------|-------------|
| `FALHA motivo=INA219 nao encontrado` | Fio do I²C, alimentação do INA219 ou os dois no mesmo endereço | SDA 21, SCL 22, 3,3 V; jumper A0 só no segundo (0x41) |
| `FALHA motivo=emergencia` logo no boot | 12V_POT desligado ou divisor do GPIO 34 errado | Com só o USB isso é normal; veja o ensaio 1 em [02](02_teste_bancada.md) |
| `h` diminui (ou fica em 0 %) quando a massa sobe | Fios do encoder invertidos | Troque A (32) e B (33) |
| `REARME` não termina | Fim de curso inferior não abre | Verifique o micro switch NF e o fio até o GPIO 25 |
| `FALHA motivo=trava presa` | A massa não subiu os 3 mm em 3 s para aliviar a lingueta | Motor sem força com `PWM_ALIVIO` 140, lingueta prendendo, ou motor sem 12 V |
| `FALHA motivo=massa travada` | Corrente de subida acima de 1,5 A por 0,5 s | Cordão enroscado, catraca presa ou carrinho travado na guia |
