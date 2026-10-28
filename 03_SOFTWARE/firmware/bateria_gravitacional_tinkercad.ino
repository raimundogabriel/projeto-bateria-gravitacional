// Bateria gravitacional - versao para Tinkercad (Arduino Uno)
//
// Simula no Uno a mesma logica que vai rodar no ESP32: sequencias de subida e
// descida, protecoes e controlador fuzzy (Mamdani, 3 entradas, 11 regras).
// O Tinkercad nao tem gerador nem massa, entao a fisica e uma "planta virtual"
// calculada no codigo (altura h e velocidade v). O motor do Tinkercad gira
// para mostrar o movimento.
//
// Comandos pelo Monitor Serial (9600):
//   a = automatico (fuzzy)   s = subir   d = descer   p = parar   r = rearme
//
// Correspondencia com o circuito real (ESP32):
//   L293D (EN, IN1, IN2)  -> BTS7960 (R_EN/L_EN, RPWM, LPWM)
//   LED do modo (pino 4)  -> rele de modo K2
//   nMOS + LED (pino 5)   -> MOSFET + resistor de frenagem 11 ohm
//   Servo (pino 9)        -> solenoide da trava (hit-and-hold)
//   Rele do pino 12       -> rele de corte K1
//   Pot A0 / A1 / A2      -> INA226 da subida / DS3231 (hora) / INA226 da USB

#include <Adafruit_LiquidCrystal.h>
#include <Servo.h>

// ---------- pinos ----------
const uint8_t PIN_ENC_A = 2;
const uint8_t PIN_ENC_B = 3;
const uint8_t PIN_LED_MODO = 4;   // aceso = motor no driver (subida)
const uint8_t PIN_FRENAGEM = 5;   // PWM da carga de frenagem
const uint8_t PIN_EMERG = 6;      // ALTO = emergencia solta
const uint8_t PIN_IN1 = 7;
const uint8_t PIN_IN2 = 8;
const uint8_t PIN_TRAVA = 9;      // servo no lugar do solenoide
const uint8_t PIN_FC_INF = 10;    // NF para GND: ALTO = acionado
const uint8_t PIN_EN = 11;        // PWM do L293D
const uint8_t PIN_K1 = 12;        // rele de corte (ALTO = fechado)
const uint8_t PIN_BUZZER = 13;
const uint8_t PIN_CORRENTE = A0;  // 0 a 5 A
const uint8_t PIN_HORA = A1;      // 0 a 24 h
const uint8_t PIN_DEMANDA = A2;   // 0 a 10 W
const uint8_t PIN_FC_SUP = A3;    // NF para GND: ALTO = acionado

// ---------- parametros do prototipo ----------
const float CURSO = 1.70;          // m, posicao do fim de curso superior
const float FOLGA_TOPO = 0.02;     // m de folga mecanica acima dele (alivio da trava)
const float V_SUBIDA = 0.05;       // m/s
const float V_MAX_SUBIDA = 0.09;   // m/s com PWM 100 %
const float V_LIMITE = 0.10;       // m/s, acima disso e falha
const float V_ALVO_MIN = 0.03;     // m/s
const float V_ALVO_MAX = 0.08;     // m/s
const float V_FREIO_TOTAL = 0.025; // m/s com frenagem em 100 % (11 ohm)
const float KE_MASSA = 253.0;      // V por m/s de massa (Ke 0,076 x 100:1 / r)
const float V_GEN_MAX = 28.0;      // V
const float I_TRAVADO = 3.0;       // A
const float ALIVIO_TRAVA = 0.003;  // m que a massa sobe para soltar a lingueta
const int TRAVA_ENGATADA = 0;      // graus do servo
const int TRAVA_LIBERADA = 90;

// Tarifa por posto horario (R$/kWh). Valores de exemplo: no prototipo
// real vem do painel (topico grav/tarifas).
const float TARIFA_FORA = 0.60;
const float TARIFA_INTER = 0.90;
const float TARIFA_PONTA = 1.40;

const unsigned long T_CONTROLE = 50;   // ms
const unsigned long T_FUZZY = 5000;    // ms
const unsigned long T_TELA = 1000;     // ms

Adafruit_LiquidCrystal lcd(0);
Servo trava;

enum Estado { MANTER, SUBINDO, PREP_DESCIDA, DESCENDO, PARANDO, FALHA, REARME };
const char *NOME_ESTADO[] = {"MANTER", "SUBINDO", "PREP_DESCIDA", "DESCENDO", "PARANDO", "FALHA", "REARME"};
const char *CURTO_ESTADO[] = {"MANT", "SUB", "PREP", "DESC", "PARA", "FALH", "REAR"};

enum Modo { AUTOMATICO, MANUAL };

Estado estado = REARME;
Modo modo = AUTOMATICO;
uint8_t etapa = 0;              // passo dentro de PREP_DESCIDA e PARANDO
unsigned long inicioEtapa = 0;
const char *motivoFalha = "";

// planta virtual
float h = 0.80;                 // altura da massa (m), desconhecida no boot
float v = 0.0;                  // velocidade (m/s), positiva para cima
bool posicaoConhecida = false;

// atuadores
bool k1 = false, k2 = false, travaLiberada = false;
int pwmMotor = 0;               // 0 a 255, so na subida
float frenagem = 0.0;           // 0 a 1
float alvoDescida = V_ALVO_MIN; // m/s
float hInicioAlivio = 0.0;
int ticksTravado = 0;

// leituras
float corrente = 0, hora = 0, demanda = 0, tarifa = 0, vGen = 0;
float comandoFuzzy = 0;

volatile long pulsos = 0;

unsigned long ultControle = 0, ultFuzzy = 0, ultTela = 0;

// =====================================================================
// Fuzzy (Mamdani, AND = min, OR = max, centroide)
// =====================================================================
float trap(float x, float a, float b, float c, float d) {
  if (x >= b && x <= c) return 1.0;
  if (x < b) return (x <= a) ? 0.0 : (x - a) / (b - a);
  return (x >= d) ? 0.0 : (d - x) / (d - c);
}
float tri(float x, float a, float b, float c) { return trap(x, a, b, b, c); }

float saidaDescer(float y)  { return trap(y, -100, -100, -80, -50); }
float saidaParcial(float y) { return tri(y, -70, -40, -10); }
float saidaManter(float y)  { return tri(y, -25, 0, 25); }
float saidaSubir(float y)   { return trap(y, 40, 70, 100, 100); }

float centroide(float aDescer, float aParcial, float aManter, float aSubir) {
  float soma = 0, somaPeso = 0;
  for (int y = -100; y <= 100; y += 2) {
    float mu = max(max(min(aDescer, saidaDescer(y)), min(aParcial, saidaParcial(y))),
                   max(min(aManter, saidaManter(y)), min(aSubir, saidaSubir(y))));
    soma += mu * y;
    somaPeso += mu;
  }
  return somaPeso > 0 ? soma / somaPeso : 0;
}

float maxSubir = 1, maxDescer = 1;  // normalizacao do centroide

float fuzzy(float tar, float nivel, float dem) {
  tar = constrain(tar, 0, 2);
  nivel = constrain(nivel, 0, 100);
  dem = constrain(dem, 0, 10);

  float tb = trap(tar, 0, 0, 0.6, 0.8);
  float tm = tri(tar, 0.6, 0.9, 1.2);
  float ta = trap(tar, 0.9, 1.2, 2, 2);
  float nb = trap(nivel, 0, 0, 20, 45);
  float nm = tri(nivel, 20, 50, 95);
  float na = trap(nivel, 60, 95, 100, 100);
  float db = trap(dem, 0, 0, 0.3, 1);
  float dm = tri(dem, 0.3, 1.5, 3);
  float da = trap(dem, 2, 4, 10, 10);

  float aSubir = 0, aManter = 0, aParcial = 0, aDescer = 0;
  aSubir = max(aSubir, min(tb, nb));                       // R1
  aSubir = max(aSubir, min(tb, nm));                       // R2
  aManter = max(aManter, min(tb, na));                     // R3
  aManter = max(aManter, min(tm, nb));                     // R4
  aManter = max(aManter, min(tm, nm));                     // R5
  aParcial = max(aParcial, min(min(tm, na), da));          // R6
  aManter = max(aManter, min(min(tm, na), max(db, dm)));   // R7
  aManter = max(aManter, min(ta, nb));                     // R8
  aParcial = max(aParcial, min(min(ta, nm), max(dm, da))); // R9
  aDescer = max(aDescer, min(min(ta, na), max(dm, da)));   // R10
  aManter = max(aManter, min(ta, db));                     // R11

  float c = centroide(aDescer, aParcial, aManter, aSubir);
  return c >= 0 ? constrain(c / maxSubir * 100, 0, 100)
                : constrain(c / maxDescer * 100, -100, 0);
}

float tarifaDaHora(float hr) {
  if (hr >= 18 && hr < 21) return TARIFA_PONTA;
  if ((hr >= 17 && hr < 18) || (hr >= 21 && hr < 22)) return TARIFA_INTER;
  return TARIFA_FORA;
}

// =====================================================================
// Atuadores
// =====================================================================
void motorSubir(int pwm) {
  digitalWrite(PIN_IN1, HIGH);
  digitalWrite(PIN_IN2, LOW);
  analogWrite(PIN_EN, pwm);
}

// So na simulacao: gira o motor para tras para mostrar a descida.
// No circuito real o motor esta no barramento gerado e o driver fica desligado.
void motorMostrarDescida(int pwm) {
  digitalWrite(PIN_IN1, LOW);
  digitalWrite(PIN_IN2, HIGH);
  analogWrite(PIN_EN, pwm);
}

void motorParar() {
  analogWrite(PIN_EN, 0);
  digitalWrite(PIN_IN1, LOW);
  digitalWrite(PIN_IN2, LOW);
}

void aplicarAtuadores() {
  digitalWrite(PIN_K1, k1 ? HIGH : LOW);
  digitalWrite(PIN_LED_MODO, k2 ? HIGH : LOW);
  trava.write(travaLiberada ? TRAVA_LIBERADA : TRAVA_ENGATADA);
  analogWrite(PIN_FRENAGEM, (int)(frenagem * 255));
  if (k2 && pwmMotor > 0) {
    motorSubir(pwmMotor);
  } else if (!k2 && v < -0.001) {
    motorMostrarDescida((int)constrain(-v / 0.12 * 255, 60, 255));
  } else {
    motorParar();
  }
}

void estadoSeguro() {
  pwmMotor = 0;
  travaLiberada = false;
  frenagem = 1.0;
  k2 = false;
  k1 = false;
}

void entrar(Estado novo) {
  estado = novo;
  etapa = 0;
  inicioEtapa = millis();
  Serial.print(F("-> "));
  Serial.println(NOME_ESTADO[novo]);
}

void falha(const char *motivo) {
  if (estado == FALHA) return;
  motivoFalha = motivo;
  estadoSeguro();
  entrar(FALHA);
  Serial.print(F("FALHA: "));
  Serial.println(motivo);
}

// =====================================================================
// Planta virtual: substitui a massa, o gerador e o encoder do prototipo
// =====================================================================
void atualizarPlanta(float dt) {
  float vDesejada = 0;
  bool energia = k1 && digitalRead(PIN_EMERG) == HIGH;

  if (k2 && energia && pwmMotor > 0) {
    vDesejada = V_MAX_SUBIDA * pwmMotor / 255.0;
  } else if (!k2 && travaLiberada) {
    // Motor como gerador: mais frenagem e mais carga na USB = mais freio
    float freio = constrain(frenagem + demanda / 20.0, 0.2, 1.0);
    vDesejada = -V_FREIO_TOTAL / freio;
  }

  v += (vDesejada - v) * 0.3;  // inercia
  if (v < 0 && !travaLiberada) v = 0;  // a lingueta segura a descida
  h += v * dt;
  if (h < 0) { h = 0; if (v < 0) v = 0; }
  if (h > CURSO + FOLGA_TOPO) { h = CURSO + FOLGA_TOPO; if (v > 0) v = 0; }

  vGen = (!k2 && v < 0) ? -v * KE_MASSA : 0;
}

bool fimInferior() { return digitalRead(PIN_FC_INF) == HIGH || h <= 0.0005; }
bool fimSuperior() { return digitalRead(PIN_FC_SUP) == HIGH || h >= CURSO; }

// =====================================================================
// Maquina de estados (a cada 50 ms)
// =====================================================================
void controlar() {
  unsigned long agora = millis();
  unsigned long naEtapa = agora - inicioEtapa;

  // ---- protecoes ----
  if (digitalRead(PIN_EMERG) == LOW) falha("emergencia");
  if (fabs(v) > V_LIMITE) falha("velocidade alta");
  if (vGen > V_GEN_MAX) falha("tensao alta");
  if (estado == SUBINDO && corrente > I_TRAVADO) {
    if (++ticksTravado >= 10) falha("massa travada");
  } else {
    ticksTravado = 0;
  }

  switch (estado) {
    case MANTER:
      pwmMotor = 0;
      travaLiberada = false;
      k2 = false;
      k1 = false;
      if (naEtapa > 500) frenagem = 0;
      break;

    case SUBINDO:
      if (fimSuperior()) {
        entrar(PARANDO);
        break;
      }
      k1 = true;
      frenagem = 0;
      if (!k2) {               // passo 2: motor no driver, espera 50 ms
        k2 = true;
        inicioEtapa = agora;
        break;
      }
      if (naEtapa < 50) break;
      {
        int alvo = 142 + (int)(2000 * (V_SUBIDA - v));  // ~55 % + correcao
        alvo = constrain(alvo, 0, 255);
        pwmMotor += constrain(alvo - pwmMotor, -7, 7);  // rampa de ~1 s
      }
      break;

    case PREP_DESCIDA:
      if (fimInferior()) {
        entrar(PARANDO);
        break;
      }
      k1 = true;
      if (etapa == 0) {        // sobe 3 mm para aliviar a lingueta
        k2 = true;
        frenagem = 0;
        hInicioAlivio = h;
        etapa = 1;
        inicioEtapa = agora;
      } else if (etapa == 1) {
        pwmMotor = 100;
        if (h >= hInicioAlivio + ALIVIO_TRAVA) {
          pwmMotor = 0;        // no real: o motor segura a posicao
          travaLiberada = true;  // solenoide 100 %
          etapa = 2;
          inicioEtapa = agora;
        } else if (naEtapa > 3000) {
          falha("trava presa");
        }
      } else if (etapa == 2 && naEtapa >= 300) {
        frenagem = 1.0;        // freio ligado antes de trocar o rele
        k2 = false;            // motor no barramento gerado
        entrar(DESCENDO);
      }
      break;

    case DESCENDO:
    case REARME:
      if (estado == REARME && etapa == 0) {
        // rearme usa a mesma preparacao da descida
        if (fimInferior()) {
          h = 0;
          posicaoConhecida = true;
          pulsos = 0;
          estadoSeguro();
          entrar(MANTER);
          break;
        }
        k1 = true;
        k2 = true;
        hInicioAlivio = h;
        etapa = 1;
        inicioEtapa = agora;
        break;
      }
      if (estado == REARME && etapa == 1) {
        pwmMotor = 100;
        if (h >= hInicioAlivio + ALIVIO_TRAVA) {
          pwmMotor = 0;
          travaLiberada = true;
          etapa = 2;
          inicioEtapa = agora;
        }
        break;
      }
      if (estado == REARME && etapa == 2) {
        if (naEtapa < 300) break;
        frenagem = 1.0;
        k2 = false;
        etapa = 3;
        break;
      }
      if (fimInferior()) {
        if (estado == REARME) {
          h = 0;
          posicaoConhecida = true;
          pulsos = 0;
        }
        entrar(PARANDO);
        break;
      }
      if (estado == REARME) {
        frenagem = 1.0;        // descida mais lenta possivel
      } else {
        // PI incremental: rapido demais -> mais frenagem
        float erro = -v - alvoDescida;
        frenagem = constrain(frenagem + 2.0 * erro, 0.0, 1.0);
      }
      break;

    case PARANDO:
      pwmMotor = 0;
      frenagem = 1.0;
      travaLiberada = false;   // lingueta pega o proximo dente
      if (naEtapa > 200) k2 = false;  // massa ja assentou na lingueta
      if (naEtapa > 500) entrar(MANTER);
      break;

    case FALHA:
      estadoSeguro();
      digitalWrite(PIN_BUZZER, (agora / 250) % 2);
      break;
  }

  if (estado != FALHA) digitalWrite(PIN_BUZZER, LOW);
}

// =====================================================================
// Decisao (a cada 5 s no automatico)
// =====================================================================
float nivel() { return constrain(h / CURSO * 100, 0, 100); }

void decidir() {
  comandoFuzzy = fuzzy(tarifa, nivel(), demanda);
  if (modo != AUTOMATICO || !posicaoConhecida) return;
  if (estado == FALHA || estado == REARME || estado == PREP_DESCIDA || estado == PARANDO) return;

  // Histerese: comeca com |comando| > 30 e continua enquanto |comando| > 10
  if (comandoFuzzy < -10) {
    alvoDescida = V_ALVO_MIN + max(-comandoFuzzy - 30, 0) / 70.0 * (V_ALVO_MAX - V_ALVO_MIN);
  }
  if (estado == SUBINDO && comandoFuzzy <= 10) entrar(PARANDO);
  else if (estado == DESCENDO && comandoFuzzy >= -10) entrar(PARANDO);
  else if (estado == MANTER && comandoFuzzy > 30 && !fimSuperior()) entrar(SUBINDO);
  else if (estado == MANTER && comandoFuzzy < -30 && !fimInferior()) entrar(PREP_DESCIDA);
}

void lerComando() {
  if (!Serial.available()) return;
  char c = Serial.read();
  switch (c) {
    case 'a':
      modo = AUTOMATICO;
      Serial.println(F("modo automatico"));
      break;
    case 's':
      modo = MANUAL;
      if (estado == MANTER && posicaoConhecida) entrar(SUBINDO);
      break;
    case 'd':
      modo = MANUAL;
      alvoDescida = 0.05;
      if (estado == MANTER && posicaoConhecida) entrar(PREP_DESCIDA);
      break;
    case 'p':
      modo = MANUAL;
      if (estado == SUBINDO || estado == DESCENDO || estado == PREP_DESCIDA) entrar(PARANDO);
      break;
    case 'r':
      if (estado == FALHA && digitalRead(PIN_EMERG) == HIGH) {
        posicaoConhecida = false;
        entrar(REARME);
      }
      break;
  }
}

// =====================================================================
// Tela e serial
// =====================================================================
void mostrar() {
  char linha[17], t1[6], t2[6];

  dtostrf(h, 4, 2, t1);
  snprintf(linha, sizeof(linha), "%-4s h%s %3d%%%c", CURTO_ESTADO[estado], t1,
           (int)nivel(), modo == AUTOMATICO ? 'A' : 'M');
  lcd.setCursor(0, 0);
  lcd.print(linha);

  if (estado == FALHA) {
    snprintf(linha, sizeof(linha), "%-16s", motivoFalha);
  } else {
    dtostrf(tarifa, 4, 2, t1);
    dtostrf(vGen, 4, 1, t2);
    snprintf(linha, sizeof(linha), "%s %sV F%3d%%", t1, t2, (int)(frenagem * 100));
  }
  lcd.setCursor(0, 1);
  lcd.print(linha);

  Serial.print(F("h="));       Serial.print(h, 3);
  Serial.print(F(" v="));      Serial.print(v, 3);
  Serial.print(F(" estado=")); Serial.print(NOME_ESTADO[estado]);
  Serial.print(F(" fuzzy="));  Serial.print(comandoFuzzy, 0);
  Serial.print(F(" hora="));   Serial.print(hora, 1);
  Serial.print(F(" tarifa=")); Serial.print(tarifa, 2);
  Serial.print(F(" dem="));    Serial.print(demanda, 1);
  Serial.print(F("W gen="));   Serial.print(vGen, 1);
  Serial.print(F("V freio=")); Serial.print((int)(frenagem * 100));
  Serial.print(F("% pulsos=")); Serial.println(pulsos);
}

void contarPulso() {
  pulsos += (digitalRead(PIN_ENC_A) == digitalRead(PIN_ENC_B)) ? 1 : -1;
}

// =====================================================================
void setup() {
  digitalWrite(PIN_K1, LOW);  // nivel definido antes de virar saida
  pinMode(PIN_K1, OUTPUT);
  pinMode(PIN_LED_MODO, OUTPUT);
  pinMode(PIN_FRENAGEM, OUTPUT);
  pinMode(PIN_IN1, OUTPUT);
  pinMode(PIN_IN2, OUTPUT);
  pinMode(PIN_EN, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_EMERG, INPUT);
  pinMode(PIN_FC_INF, INPUT_PULLUP);
  pinMode(PIN_FC_SUP, INPUT_PULLUP);
  pinMode(PIN_ENC_A, INPUT_PULLUP);
  pinMode(PIN_ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_A), contarPulso, CHANGE);

  trava.attach(PIN_TRAVA);
  estadoSeguro();
  aplicarAtuadores();

  Serial.begin(9600);
  lcd.begin(16, 2);
  lcd.setBacklight(1);

  maxSubir = centroide(0, 0, 0, 1);
  maxDescer = -centroide(1, 0, 0, 0);

  Serial.println(F("Bateria gravitacional - Tinkercad"));
  Serial.println(F("a=auto s=subir d=descer p=parar r=rearme"));
  entrar(REARME);  // posicao desconhecida: desce ate o fim de curso inferior
}

void loop() {
  unsigned long agora = millis();
  lerComando();

  if (agora - ultControle >= T_CONTROLE) {
    float dt = (agora - ultControle) / 1000.0;
    ultControle = agora;
    corrente = analogRead(PIN_CORRENTE) * 5.0 / 1023.0;
    hora = analogRead(PIN_HORA) * 24.0 / 1024.0;
    demanda = analogRead(PIN_DEMANDA) * 10.0 / 1023.0;
    tarifa = tarifaDaHora(hora);
    atualizarPlanta(dt);
    controlar();
    aplicarAtuadores();
  }

  if (agora - ultFuzzy >= T_FUZZY) {
    ultFuzzy = agora;
    decidir();
  }

  if (agora - ultTela >= T_TELA) {
    ultTela = agora;
    mostrar();
  }
}
