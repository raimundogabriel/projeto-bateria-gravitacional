# 01 — Gravar o firmware no ESP32

Você vai precisar de: ESP32 DevKit V1, **cabo USB de dados** (muitos cabos
de carregador só têm os fios de energia e o computador não enxerga a placa)
e um computador com Windows, Linux ou macOS.

## 1. Instalar a Arduino IDE
Baixe a Arduino IDE 2 em <https://www.arduino.cc/en/software> e instale.

## 2. Instalar o suporte ao ESP32
1. **File → Preferences** (Arquivo → Preferências).
2. Em **Additional boards manager URLs**, cole:
   ```
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```
3. **Tools → Board → Boards Manager**, procure `esp32` e instale
   **esp32 by Espressif Systems**. O firmware funciona com as versões 2.x e
   3.x.

## 3. Driver USB (só se a porta não aparecer)
Ligue o ESP32 no USB. Se nenhuma porta nova aparecer em **Tools → Port**,
olhe o chip ao lado do conector USB da placa:

| Chip | Driver |
|------|--------|
| CP2102 / CP2104 (quadrado, “SILABS”) | <https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers> |
| CH340 / CH9102 (retangular) | <https://www.wch-ic.com/downloads/CH341SER_ZIP.html> (Windows) |

No Linux a porta aparece como `/dev/ttyUSB0`; se der “permission denied”,
rode `sudo usermod -aG dialout $USER` e entre de novo na sessão.

## 4. Instalar as bibliotecas
**Tools → Manage Libraries** (Ferramentas → Gerenciar Bibliotecas):

| Procure | Instale | Para quê |
|---------|---------|----------|
| `PubSubClient` | **PubSubClient** by Nick O'Leary | MQTT (painel). Sempre |
| `Adafruit INA219` | **Adafruit INA219** (aceite “Install all” para levar a Adafruit BusIO) | Só com `SIMULACAO 0` |
| `ESP32Encoder` | **ESP32Encoder** by Kevin Harrington | Só com `SIMULACAO 0` |

Wi-Fi, Wire (I²C) e o NTP já vêm com o pacote do ESP32.

## 5. Abrir o sketch
A Arduino IDE exige que o `.ino` esteja numa pasta com o mesmo nome. Para
não mexer no repositório:

1. Crie a pasta `Documentos/Arduino/bateria_mvp/`.
2. Copie `MVP_FABLAB/03_SOFTWARE/firmware/wokwi/sketch.ino` para dentro dela
   com o nome `bateria_mvp.ino`.
3. Abra `bateria_mvp.ino` na IDE.

Quando o arquivo do repositório mudar, copie de novo.

## 6. Ajustar as linhas do topo
Tudo o que muda entre Wokwi, bancada e protótipo está no começo do arquivo:

```cpp
#define SIMULACAO 1          // 1 = planta virtual (sem hardware); 0 = protótipo real

const char *WIFI_SSID = "Wokwi-GUEST";            // nome da rede Wi-Fi
const char *WIFI_SENHA = "";                      // senha
const char *MQTT_BROKER = "broker.hivemq.com";    // IP do notebook com o Mosquitto
const uint16_t MQTT_PORTA = 1883;
const char *TOPICO_BASE = "grav-mvp-fablab";      // "grav" no Mosquitto do notebook
```

| Onde vai rodar | `SIMULACAO` | `WIFI_SSID` / `WIFI_SENHA` | `MQTT_BROKER` | `TOPICO_BASE` |
|----------------|-------------|----------------------------|---------------|---------------|
| Wokwi | 1 | `Wokwi-GUEST` / vazio | `broker.hivemq.com` | um nome só seu, ex. `grav-gabriel-7731` |
| ESP32 solto na bancada | 1 | sua rede (2,4 GHz) | IP do notebook, ex. `192.168.0.42` | `grav` |
| Protótipo montado | 0 | sua rede (2,4 GHz) | IP do notebook | `grav` |

Como achar o IP do notebook está em [03_painel_mqtt.md](03_painel_mqtt.md).
O ESP32 só conecta em Wi-Fi **2,4 GHz** com senha comum (WPA2 pessoal).
Rede de faculdade com login e senha pessoais (tipo eduroam) não funciona:
use o roteador do celular.

## 7. Gravar
1. **Tools → Board → esp32 → ESP32 Dev Module** (serve para o DevKit V1;
   “DOIT ESP32 DEVKIT V1” também serve).
2. **Tools → Port**: a porta que apareceu ao ligar a placa (`COM3`, `COM4`…
   no Windows; `/dev/ttyUSB0` no Linux; `/dev/cu.usbserial-…` no macOS).
3. Clique em **Upload** (seta para a direita). A primeira compilação demora
   1 a 2 minutos.
4. Se parar em `Connecting........_____`, **segure o botão BOOT** da placa
   até aparecer `Writing at 0x…`, e solte.
5. Termina com `Hard resetting via RTS pin...`.

## 8. Ver se está vivo
**Tools → Serial Monitor**, velocidade **115200**. Aperte o botão **EN**
(reset) da placa. Com `SIMULACAO 1` e os jumpers de
[02_teste_bancada.md](02_teste_bancada.md) você deve ver:

```
Bateria gravitacional - MVP fablab - ESP32
MQTT: 192.168.0.42 topicos grav/estado, /comando, /tarifas
a=auto s=subir d=descer p=parar r=rearme h19=hora hx=hora do NTP w3=demanda do painel
-> REARME
REARME AUTO ponte=GERAR h=0.398 nivel=23% v=-0.004 ...
```

Depois de ~40 s o rearme termina (`-> PARANDO`, `-> MANTER`) e aparece
`MQTT: conectado` (se o broker já estiver rodando) ou `MQTT: falhou, rc=-2`
(broker ainda não ligado; ele tenta de novo a cada 10 s). O ESP32 só tenta
o broker com a massa parada (`MANTER` ou `FALHA`), para a conexão nunca
travar o controle no meio de uma descida.

Digite comandos na caixa do Monitor Serial e aperte Enter: `h3` (força 3 h
da manhã: o fuzzy manda subir), `s`, `p`, `h19`, `w5`… A lista completa
está em `../03_SOFTWARE/firmware/README.md`.

Próximo: [02_teste_bancada.md](02_teste_bancada.md).
