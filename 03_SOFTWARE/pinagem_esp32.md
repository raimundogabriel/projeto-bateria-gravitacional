# PINAGEM ESP32

| GPIO | Função | Periférico | Direção | Notas |
|------|--------|------------|---------|-------|
| 34 | Encoder A | Encoder | IN | input-only, sem pull-up |
| 35 | Encoder B | Encoder | IN | input-only |
| 25 | PWM motor | Driver | OUT | LEDC ch 0 |
| 26 | Direção motor | Driver | OUT | HIGH=sobe |
| 21 | SDA INA219 | I²C | I/O | 4,7k pull-up |
| 22 | SCL INA219 | I²C | I/O | 4,7k pull-up |