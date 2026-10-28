// Bateria gravitacional - ESP32 (Wokwi e prototipo real)
//
// Mesma pinagem do circuito real. Com SIMULACAO 1 (Wokwi), a massa e o
// gerador viram uma "planta virtual" calculada no codigo, os INA226 sao
// trocados por potenciometros e os sinais de potencia acendem LEDs.
// Com SIMULACAO 0, o codigo le encoder, INA226 e DS3231 de verdade.
//
// Comandos pelo Monitor Serial (115200):
//   a = automatico (fuzzy)   s = subir   d = descer   p = parar   r = rearme
//   h19 = forca a hora em 19 h (teste do fuzzy)   hx = volta a hora do RTC

#define SIMULACAO 1

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <RTClib.h>

// ---------- pinos (iguais ao circuito real) ----------
const uint8_t PIN_TRAVA = 4;      // solenoide (PWM hit-and-hold)
const uint8_t PIN_K4 = 13;        // rele de sondagem da USB
const uint8_t PIN_BUZZER = 14;
const uint8_t PIN_RPWM = 16;      // BTS7960: subir
const uint8_t PIN_LPWM = 17;      // BTS7960: descer (so rearme e teste)
const uint8_t PIN_EN = 18;        // BTS7960: R_EN e L_EN
const uint8_t PIN_FRENAGEM = 19;  // MOSFET da carga de frenagem
const uint8_t PIN_K2 = 23;        // rele de modo (2 canais)
const uint8_t PIN_FC_INF = 25;    // ALTO = acionado
const uint8_t PIN_FC_SUP = 26;    // ALTO = acionado
const uint8_t PIN_K1 = 27;        // rele de corte
const uint8_t PIN_ENC_A = 32;
const uint8_t PIN_ENC_B = 33;
const uint8_t PIN_EMERG = 34;     // ALTO = emergencia solta
#if SIMULACAO
const uint8_t PIN_POT_CORRENTE = 35;  // no lugar do INA226 n. 1 (0 a 5 A)
const uint8_t PIN_POT_DEMANDA = 39;   // no lugar do INA226 n. 3 (0 a 10 W)
#endif

// Modulo de 4 reles do prototipo: ativo em BAIXO. Rele do Wokwi: ativo em ALTO.
#if SIMULACAO
const uint8_t RELE_LIGA = HIGH;
#else
const uint8_t RELE_LIGA = LOW;
#endif

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
const float MM_POR_PULSO = 0.0393; // encoder 600 pulsos x4, tambor 60 mm, talha 2:1
const int TRAVA_PUXA = 255;        // PWM do solenoide nos primeiros 300 ms
const int TRAVA_SEGURA = 77;       // 30 %
const unsigned long T_PUXA = 300;  // ms

// Tarifa por posto horario (R$/kWh). Valores de exemplo: no prototipo
// real vem do painel (topico grav/tarifas).
const float TARIFA_FORA = 0.60;
const float TARIFA_INTER = 0.90;
const float TARIFA_PONTA = 1.40;

const unsigned long T_CONTROLE = 50;   // ms
const unsigned long T_FUZZY = 5000;    // ms
const unsigned long T_TELA = 1000;     // ms

LiquidCrystal_I2C lcd(0x27, 20, 4);
#if SIMULACAO
RTC_DS1307 rtc;   // o Wokwi tem DS1307; no prototipo e DS3231
#else
RTC_DS3231 rtc;
#endif

enum Estado { MANTER, SUBINDO, PREP_DESCIDA, DESCENDO, PARANDO, FALHA, REARME };
const char *NOME_ESTADO[] = {"MANTER", "SUBINDO", "PREP_DESCIDA", "DESCENDO", "PARANDO", "FALHA", "REARME"};

enum Modo { AUTOMATICO, MANUAL };

Estado estado = REARME;
Modo modo = AUTOMATICO;
uint8_t etapa = 0;              // passo dentro de PREP_DESCIDA e REARME
unsigned long inicioEtapa = 0;
const char *motivoFalha = "";

float h = 0.80;                 // altura da massa (m), desconhecida no boot
float v = 0.0;                  // velocidade (m/s), positiva para cima
bool posicaoConhecida = false;

// atuadores
bool k1 = false, k2 = false, k4 = false, travaLiberada = false;
unsigned long ultSonda = 0;
unsigned long inicioTrava = 0;
int pwmMotor = 0;               // 0 a 255, so na subida
float frenagem = 0.0;           // 0 a 1
float alvoDescida = V_ALVO_MIN; // m/s
float hInicioAlivio = 0.0;
int ticksTravado = 0;

// leituras
float corrente = 0, hora = 0, demanda = 0, tarifa = 0, vGen = 0;
float horaForcada = -1;
float comandoFuzzy = 0;

volatile long pulsos = 0;

unsigned long ultControle = 0, ultFuzzy = 0, ultTela = 0;

// =====================================================================
// PWM (LEDC), compativel com o core 2.x e 3.x do ESP32
// =====================================================================
void pwmIniciar(uint8_t pino, uint8_t canal, uint32_t freq) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  (void)canal;
  ledcAttach(pino, freq, 8);
#else
  ledcSetup(canal, freq, 8);
  ledcAttachPin(pino, canal);
#endif
}

void pwmEscrever(uint8_t pino, uint8_t canal, int duty) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  (void)canal;
  ledcWrite(pino, duty);
#else
  (void)pino;
  ledcWrite(canal, duty);
#endif
}

const uint8_t CANAL_RPWM = 0, CANAL_LPWM = 1, CANAL_FRENAGEM = 2, CANAL_TRAVA = 3;

void rele(uint8_t pino, bool ligado) {
  digitalWrite(pino, ligado ? RELE_LIGA : !RELE_LIGA);
}

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
  tar = constrain(tar, 0.0f, 2.0f);
  nivel = constrain(nivel, 0.0f, 100.0f);
  dem = constrain(dem, 0.0f, 10.0f);

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
  return c >= 0 ? constrain(c / maxSubir * 100, 0.0f, 100.0f)
                : constrain(c / maxDescer * 100, -100.0f, 0.0f);
}

float tarifaDaHora(float hr) {
  if (hr >= 18 && hr < 21) return TARIFA_PONTA;
  if ((hr >= 17 && hr < 18) || (hr >= 21 && hr < 22)) return TARIFA_INTER;
  return TARIFA_FORA;
}

// =====================================================================
// Atuadores
// =====================================================================
void aplicarAtuadores() {
  rele(PIN_K1, k1);
  rele(PIN_K2, k2);
  rele(PIN_K4, k4);

  int dutyTrava = 0;
  if (travaLiberada) dutyTrava = (millis() - inicioTrava < T_PUXA) ? TRAVA_PUXA : TRAVA_SEGURA;
  pwmEscrever(PIN_TRAVA, CANAL_TRAVA, dutyTrava);
  pwmEscrever(PIN_FRENAGEM, CANAL_FRENAGEM, (int)(frenagem * 255));

  bool subir = k2 && pwmMotor > 0;
  digitalWrite(PIN_EN, subir ? HIGH : LOW);
  pwmEscrever(PIN_RPWM, CANAL_RPWM, subir ? pwmMotor : 0);
  pwmEscrever(PIN_LPWM, CANAL_LPWM, 0);
}

void liberarTrava() {
  if (!travaLiberada) inicioTrava = millis();
  travaLiberada = true;
}

void estadoSeguro() {
  pwmMotor = 0;
  travaLiberada = false;
  frenagem = 1.0;
  k2 = false;
  k1 = false;
  k4 = false;
}

void entrar(Estado novo) {
  estado = novo;
  etapa = 0;
  inicioEtapa = millis();
  Serial.print("-> ");
  Serial.println(NOME_ESTADO[novo]);
}

void falha(const char *motivo) {
  if (estado == FALHA) return;
  motivoFalha = motivo;
  estadoSeguro();
  entrar(FALHA);
  Serial.print("FALHA: ");
  Serial.println(motivo);
}

// =====================================================================
// Medicoes
// =====================================================================
#if SIMULACAO
// Planta virtual: substitui a massa, o gerador e o encoder
void atualizarPlanta(float dt) {
  float vDesejada = 0;
  bool energia = k1 && digitalRead(PIN_EMERG) == HIGH;

  if (k2 && energia && pwmMotor > 0) {
    vDesejada = V_MAX_SUBIDA * pwmMotor / 255.0;
  } else if (!k2 && travaLiberada) {
    // Motor como gerador: mais frenagem e mais carga na USB = mais freio
    float freio = constrain(frenagem + demanda / 20.0f, 0.2f, 1.0f);
    vDesejada = -V_FREIO_TOTAL / freio;
  }

  v += (vDesejada - v) * 0.3;  // inercia
  if (v < 0 && !travaLiberada) v = 0;  // a lingueta segura a descida
  h += v * dt;
  if (h < 0) { h = 0; if (v < 0) v = 0; }
  if (h > CURSO + FOLGA_TOPO) { h = CURSO + FOLGA_TOPO; if (v > 0) v = 0; }

  vGen = (!k2 && v < 0) ? -v * KE_MASSA : 0;
}

void lerSensores(float dt) {
  corrente = analogRead(PIN_POT_CORRENTE) * 5.0 / 4095.0;
  demanda = analogRead(PIN_POT_DEMANDA) * 10.0 / 4095.0;
  atualizarPlanta(dt);
}
#else
// Prototipo real: ver a secao "Circuito real" do documento.
// Altura pelo encoder (troque por ESP32Encoder para usar o PCNT),
// corrente e demanda pelos INA226 (0x40 e 0x44), tensao gerada pelo 0x41.
float hAnterior = 0;
void lerSensores(float dt) {
  noInterrupts();
  long p = pulsos;
  interrupts();
  h = p * MM_POR_PULSO / 1000.0;
  v = (h - hAnterior) / dt;
  hAnterior = h;
  // corrente = ina1.readCurrent(); vGen = ina2.readBusVoltage(); demanda = ina3.readPower();
}
#endif

bool fimInferior() { return digitalRead(PIN_FC_INF) == HIGH || (SIMULACAO && h <= 0.0005); }
bool fimSuperior() { return digitalRead(PIN_FC_SUP) == HIGH || (SIMULACAO && h >= CURSO); }

// =====================================================================
// Maquina de estados (a cada 50 ms)
// =====================================================================
void zerarPosicao() {
  h = 0;
  pulsos = 0;
  posicaoConhecida = true;
}

void controlar() {
  unsigned long agora = millis();
  unsigned long naEtapa = agora - inicioEtapa;

  // ---- protecoes ----
  if (digitalRead(PIN_EMERG) == LOW) falha("emergencia");
  if (fabs(v) > V_LIMITE) falha("velocidade alta");
  if (vGen > V_GEN_MAX) falha("tensao gerada alta");
  if (estado == SUBINDO && corrente > I_TRAVADO) {
    if (++ticksTravado >= 10) falha("massa travada");
  } else {
    ticksTravado = 0;
  }

  if (estado != MANTER) k4 = false;

  switch (estado) {
    case MANTER:
      // Sondagem: 1 s de 5 V na USB a cada 30 s para ver se ha aparelho
      if (agora - ultSonda >= 30000) ultSonda = agora;
      k4 = agora - ultSonda < 1000;
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
      if (!k2) {               // motor no driver, espera 50 ms
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
    case REARME:
      if (estado == REARME && etapa == 0 && fimInferior()) {
        zerarPosicao();
        estadoSeguro();
        entrar(MANTER);
        break;
      }
      if (estado == PREP_DESCIDA && fimInferior()) {
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
          liberarTrava();
          etapa = 2;
          inicioEtapa = agora;
        } else if (naEtapa > 3000) {
          falha("trava presa");
        }
      } else if (etapa == 2 && naEtapa >= T_PUXA) {
        frenagem = 1.0;        // freio ligado antes de trocar o rele
        k2 = false;            // motor no barramento gerado
        if (estado == PREP_DESCIDA) entrar(DESCENDO);
        else etapa = 3;        // rearme: desce com frenagem em 100 %
      } else if (etapa == 3) {
        frenagem = 1.0;
        if (fimInferior()) {
          zerarPosicao();
          entrar(PARANDO);
        }
      }
      break;

    case DESCENDO:
      if (fimInferior()) {
        entrar(PARANDO);
        break;
      }
      {
        // PI incremental: rapido demais -> mais frenagem
        float erro = -v - alvoDescida;
        frenagem = constrain(frenagem + 2.0f * erro, 0.0f, 1.0f);
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
float nivel() { return constrain(h / CURSO * 100, 0.0f, 100.0f); }

void decidir() {
  comandoFuzzy = fuzzy(tarifa, nivel(), demanda);
  if (modo != AUTOMATICO || !posicaoConhecida) return;
  if (estado == FALHA || estado == REARME || estado == PREP_DESCIDA || estado == PARANDO) return;

  // Histerese: comeca com |comando| > 30 e continua enquanto |comando| > 10
  if (comandoFuzzy < -10) {
    alvoDescida = V_ALVO_MIN + max(-comandoFuzzy - 30, 0.0f) / 70.0f * (V_ALVO_MAX - V_ALVO_MIN);
  }
  if (estado == SUBINDO && comandoFuzzy <= 10) entrar(PARANDO);
  else if (estado == DESCENDO && comandoFuzzy >= -10) entrar(PARANDO);
  else if (estado == MANTER && comandoFuzzy > 30 && !fimSuperior()) entrar(SUBINDO);
  else if (estado == MANTER && comandoFuzzy < -30 && !fimInferior()) entrar(PREP_DESCIDA);
}

void lerComando() {
  if (!Serial.available()) return;
  String c = Serial.readStringUntil('\n');
  c.trim();
  if (c.length() == 0) return;

  if (c[0] == 'h') {
    if (c == "hx") horaForcada = -1;
    else horaForcada = constrain(c.substring(1).toFloat(), 0.0f, 23.99f);
    Serial.print("hora forcada: ");
    Serial.println(horaForcada);
    return;
  }
  switch (c[0]) {
    case 'a':
      modo = AUTOMATICO;
      Serial.println("modo automatico");
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
void linhaLcd(uint8_t n, const char *texto) {
  char linha[21];
  snprintf(linha, sizeof(linha), "%-20s", texto);
  lcd.setCursor(0, n);
  lcd.print(linha);
}

void mostrar() {
  char b[32];
  snprintf(b, sizeof(b), "%-12s %s", NOME_ESTADO[estado], modo == AUTOMATICO ? "AUTO" : "MAN");
  linhaLcd(0, b);
  snprintf(b, sizeof(b), "h %.2f m  nivel %3d%%", h, (int)nivel());
  linhaLcd(1, b);
  if (estado == FALHA) {
    linhaLcd(2, motivoFalha);
    linhaLcd(3, "r = rearme");
  } else {
    snprintf(b, sizeof(b), "%02d:%02d R$%.2f %.1fW", (int)hora, (int)((hora - (int)hora) * 60), tarifa, demanda);
    linhaLcd(2, b);
    snprintf(b, sizeof(b), "Gen %4.1fV Freio %3d%%", vGen, (int)(frenagem * 100));
    linhaLcd(3, b);
  }

  Serial.printf("h=%.3f v=%.3f estado=%s fuzzy=%.0f hora=%.1f tarifa=%.2f dem=%.1fW gen=%.1fV freio=%d%% I=%.1fA pulsos=%ld\n",
                h, v, NOME_ESTADO[estado], comandoFuzzy, hora, tarifa, demanda, vGen,
                (int)(frenagem * 100), corrente, (long)pulsos);
}

void IRAM_ATTR contarPulso() {
  pulsos += (digitalRead(PIN_ENC_A) == digitalRead(PIN_ENC_B)) ? 1 : -1;
}

// =====================================================================
void setup() {
  // reles: nivel de desligado antes de virar saida, para nao pulsar no boot
  for (uint8_t p : {PIN_K1, PIN_K2, PIN_K4}) {
    digitalWrite(p, !RELE_LIGA);
    pinMode(p, OUTPUT);
  }
  digitalWrite(PIN_EN, LOW);
  pinMode(PIN_EN, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_EMERG, INPUT);          // GPIO 34 nao tem pull-up interno
  pinMode(PIN_FC_INF, INPUT_PULLUP);
  pinMode(PIN_FC_SUP, INPUT_PULLUP);
  pinMode(PIN_ENC_A, INPUT_PULLUP);
  pinMode(PIN_ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_A), contarPulso, CHANGE);

  pwmIniciar(PIN_RPWM, CANAL_RPWM, 20000);
  pwmIniciar(PIN_LPWM, CANAL_LPWM, 20000);
  pwmIniciar(PIN_FRENAGEM, CANAL_FRENAGEM, 5000);
  pwmIniciar(PIN_TRAVA, CANAL_TRAVA, 20000);

  estadoSeguro();
  aplicarAtuadores();

  Serial.begin(115200);
  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  if (!rtc.begin()) Serial.println("RTC nao encontrado");

  maxSubir = centroide(0, 0, 0, 1);
  maxDescer = -centroide(1, 0, 0, 0);

  Serial.println("Bateria gravitacional - ESP32");
  Serial.println("a=auto s=subir d=descer p=parar r=rearme h19=hora hx=hora do RTC");
  entrar(REARME);  // posicao desconhecida: desce ate o fim de curso inferior
}

void loop() {
  unsigned long agora = millis();
  lerComando();

  if (agora - ultControle >= T_CONTROLE) {
    float dt = (agora - ultControle) / 1000.0;
    ultControle = agora;

    if (horaForcada >= 0) {
      hora = horaForcada;
    } else {
      DateTime t = rtc.now();
      hora = t.hour() + t.minute() / 60.0;
    }
    tarifa = tarifaDaHora(hora);

    lerSensores(dt);
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
