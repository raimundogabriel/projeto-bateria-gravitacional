# DIAGRAMA DE BLOCOS

Regra que une os blocos: **sem o ESP32 comandando, todo relé desliga, a trava
engata e o motor fica ligado ao freio elétrico** (DEC-009).

## Integração sensores → ESP32 → atuadores

```mermaid
flowchart LR
  subgraph Sensores
    ENC["Encoder 600 p/v<br/>GPIO 32/33"]
    FC["Fins de curso NF<br/>GPIO 25/26"]
    INA1["INA226 nº1 subida<br/>0x40"]
    INA2["INA226 nº2 gerado<br/>0x41"]
    INA3["INA226 nº3 USB<br/>0x44"]
    RTC["DS3231<br/>0x68"]
    EM["Emergência<br/>GPIO 34"]
  end
  ESP["ESP32-WROOM-32<br/>fuzzy + máquina de estados"]
  subgraph Atuadores
    BTS["BTS7960<br/>GPIO 16/17/18"]
    K1["K1 corte<br/>GPIO 27"]
    K2["K2 modo<br/>GPIO 23"]
    K4["K4 sondagem USB<br/>GPIO 13"]
    FR["Frenagem MOSFET<br/>GPIO 19"]
    TR["Solenoide da trava<br/>GPIO 4"]
  end
  LCD["LCD 20x4<br/>0x27"]
  BZ["Buzzer GPIO 14"]
  MQTT[("Broker MQTT<br/>grav/*")]
  PAINEL["Painel remoto"]

  ENC --> ESP
  FC --> ESP
  INA1 --> ESP
  INA2 --> ESP
  INA3 --> ESP
  RTC --> ESP
  EM --> ESP
  ESP --> BTS
  ESP --> K1
  ESP --> K2
  ESP --> K4
  ESP --> FR
  ESP --> TR
  ESP --> LCD
  ESP --> BZ
  ESP <--> MQTT <--> PAINEL
```

## Potência

```mermaid
flowchart LR
  F["Fonte 24 V 5 A"] --> FUS["Fusível 5 A retardado"]
  FUS --> LM["LM2596 → 5 V<br/>lógica sempre ligada"]
  FUS --> K1c{K1 NA}
  K1c --> POT["24V_POT"]
  POT --> INA1["INA226 nº1"] --> BTS["BTS7960"]
  POT --> SOL["Solenoide da trava"]
  BTS -->|K2 energizado: subida| M((Motorredutor))
  M -->|K2 em repouso: descida| D1["SR560"] --> F3["Fusível 3 A"] --> CAP["2.200 µF + TVS SMBJ28A"] --> INA2["INA226 nº2"] --> GEN["Barramento GEN"]
  GEN --> FRE["Frenagem 11 Ω + MOSFET"]
  GEN --> BUCK["Buck 8–35 V → 5,3 V"] --> INA3["INA226 nº3"] --> USB["Porta USB"]
  GEN --> LEDS["LEDs verde / amarelo / vermelho"]
  LM -. "sondagem: K4 + 4,7 Ω" .-> USB
```

## Fluxo do ciclo de controle

```mermaid
flowchart TD
  A["Medição: RTC → tarifa; encoder → nível; INA226 → potências e demanda"] --> B["Fuzzy: comando −100 a +100"]
  B --> C{Override do painel?}
  C -- sim --> D["Usa o comando manual"]
  C -- não --> E["Usa o fuzzy com histerese ±30/±10"]
  D --> F["Atuação: subir / manter / descer"]
  E --> F
  F --> G["Registro: LCD, grav/acao, grav/estado, grav/energia"]
  P["Proteção a cada 50 ms"] -. falha .-> X["FALHA: trava engata, frenagem 100 %, K1 e K2 soltos, buzzer"]
  X --> R["Aguarda rearme"]
```
