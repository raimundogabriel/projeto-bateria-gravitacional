// Bateria gravitacional - MVP fablab - ESP32 (Wokwi e prototipo real)
//
// Mesma estrutura do firmware do projeto principal
// (03_SOFTWARE/firmware/wokwi/sketch.ino), adaptada ao MVP:
// 5 kg, 1,00 m, motorredutor 12 V 1:90, sem reles (o IBT-2 com R_EN e L_EN
// separados faz a troca subir/gerar, DEC-017), trava por servo (DEC-019),
// 2x INA219 (DEC-018), hora por NTP e sem LCD (DEC-021).
//
// Com SIMULACAO 1 (Wokwi), a massa e o gerador viram uma "planta virtual"
// calculada no codigo, o INA219 da subida vira um potenciometro e os LEDs de
// nivel do barramento gerado sao acesos pelo codigo.
//
// Comandos pelo Monitor Serial (115200):
//   a = automatico (fuzzy)   s = subir   d = descer   p = parar   r = rearme
//   h19 = forca a hora em 19 h (teste do fuzzy)   hx = volta a hora do NTP
//   w3 = demanda de 3 W vinda do painel (no real, grav/comando)

#define SIMULACAO 1

#include <Wire.h>
#include <WiFi.h>
#include <time.h>

// ---------- pinos (iguais ao circuito real, MVP_FABLAB/03_SOFTWARE/pinagem_mvp.md) ----------
const uint8_t PIN_SERVO = 4;      // servo da lingueta (50 Hz)
const uint8_t PIN_L_EN = 13;      // BTS7960: meia-ponte do M-
const uint8_t PIN_RPWM = 16;      // BTS7960: subir
const uint8_t PIN_LPWM = 17;      // BTS7960: descer motorizado (so teste)
const uint8_t PIN_R_EN = 18;      // BTS7960: meia-ponte do M+
const uint8_t PIN_FRENAGEM = 19;  // MOSFET da carga de frenagem
const uint8_t PIN_FC_INF = 25;    // ALTO = acionado
const uint8_t PIN_FC_SUP = 26;    // ALTO = acionado
const uint8_t PIN_DEMANDA = 27;   // chave de demanda: BAIXO = ha demanda
const uint8_t PIN_ENC_A = 32;
const uint8_t PIN_ENC_B = 33;
const uint8_t PIN_EMERG = 34;     // ALTO = emergencia solta (12V_POT presente)
#if SIMULACAO
const uint8_t PIN_POT_CORRENTE = 35;  // no lugar do INA219 n. 1 (0 a 3 A)
const uint8_t PIN_LED_VERDE = 23;     // so Wokwi: no real os LEDs ficam direto no GEN
const uint8_t PIN_LED_AMARELO = 14;
const uint8_t PIN_LED_VERMELHO = 2;
#endif

// ---------- rede (hora por NTP, DEC-021) ----------
#if SIMULACAO
const char *WIFI_SSID = "Wokwi-GUEST";
const char *WIFI_SENHA = "";
#else
const char *WIFI_SSID = "fablab";      // trocar pela rede do fablab
const char *WIFI_SENHA = "senha";
#endif
const long FUSO_S = -3 * 3600;         // horario de Brasilia

// ---------- parametros do MVP (MVP_FABLAB/01_FISICA) ----------
const float MASSA = 5.0;           // kg (DEC-014)
const float G = 9.81;
const float CURSO = 1.00;          // m, posicao do fim de curso superior
const float FOLGA_TOPO = 0.01;     // m de folga mecanica acima dele (alivio da trava)
const float V_SUBIDA = 0.03;       // m/s (C-108)
const float V_LIMITE = 0.07;       // m/s, acima disso e falha
const float V_ALVO_MIN = 0.02;     // m/s (C-107)
const float V_ALVO_MAX = 0.05;     // m/s
const float KE_MASSA = 214.0;      // V por m/s de massa (Ke 0,0119 x 2 x 90 / 0,010)
const float V_GEN_MAX = 14.0;      // V (TVS de 15 V)
const float I_TRAVADO = 1.5;       // A
const float ALIVIO_TRAVA = 0.003;  // m que a massa sobe para soltar a lingueta
const float MM_POR_PULSO = 0.00793;// Hall 11 pulsos x4 x 90, tambor 20 mm, talha 2:1
const float DEMANDA_CHAVE = 5.0;   // W quando a chave de demanda esta ligada
const int PWM_SUBIDA = 184;        // ~72 %: 0,03 m/s com 12 V (C-108)
const int PWM_ALIVIO = 140;        // ~55 %: sobe os 3 mm devagar
const int SERVO_ENGATADA = 20;     // graus; calibrar no ensaio 3
const int SERVO_SOLTA = 80;        // graus
const unsigned long T_SERVO = 300; // ms para o servo puxar a lingueta

// Tarifa por posto horario (R$/kWh). Valores de exemplo: no prototipo
// real vem do painel (topico grav/tarifas).
const float TARIFA_FORA = 0.60;
const float TARIFA_INTER = 0.90;
const float TARIFA_PONTA = 1.40;

const unsigned long T_CONTROLE = 50;   // ms
const unsigned long T_FUZZY = 5000;    // ms
const unsigned long T_TELA = 1000;     // ms

#if SIMULACAO
// planta virtual (MVP_FABLAB/01_FISICA/calculos_energia.md)
const float V_MAX_SUBIDA = 0.0458;   // m/s com PWM 100 % ((12 - 2,2) / 214)
const float I_GEN = 0.09;            // A, imposta pelo torque da massa (C-109)
const float R_FIXA = 120.0;          // ohm, carga fixa sempre ligada
const float R_FRENAGEM = 22.0;       // ohm, chaveada pelo MOSFET
const float R_A = 4.0;               // ohm, enrolamento
const float ETA_SUBIDA = 0.33;       // polias x redutor x motor, com I0 (C-103)
const float ETA_DESCIDA = 0.297;     // polias x redutor x gerador (C-102)
#endif

enum Estado { MANTER, SUBINDO, PREP_DESCIDA, DESCENDO, PARANDO, FALHA, REARME };
const char *NOME_ESTADO[] = {"MANTER", "SUBINDO", "PREP_DESCIDA", "DESCENDO", "PARANDO", "FALHA", "REARME"};

// Os quatro modos do IBT-2 (MVP_FABLAB/02_ARQUITETO/circuito.md)
enum Ponte { LIVRE, SUBIR, GERAR, CURTO };
const char *NOME_PONTE[] = {"LIVRE", "SUBIR", "GERAR", "CURTO"};

enum Modo { AUTOMATICO, MANUAL };

Estado estado = REARME;
Modo modo = AUTOMATICO;
uint8_t etapa = 0;              // passo dentro de PREP_DESCIDA e REARME
unsigned long inicioEtapa = 0;
const char *motivoFalha = "";

float h = 0.40;                 // altura da massa (m), desconhecida no boot
float v = 0.0;                  // velocidade (m/s), positiva para cima
bool posicaoConhecida = false;

// atuadores
Ponte ponte = LIVRE;
bool travaLiberada = false;
int pwmMotor = 0;               // 0 a 255, so em SUBIR
float frenagem = 0.0;           // 0 a 1
float alvoDescida = V_ALVO_MIN; // m/s
float hInicioAlivio = 0.0;
int ticksTravado = 0;

// leituras
float corrente = 0, hora = 0, demanda = 0, tarifa = 0, vGen = 0;
float pSubida = 0, pGerada = 0, eSubida = 0, eGerada = 0;
float horaForcada = -1, demandaPainel = 0;
bool horaValida = false;
float comandoFuzzy = 0;
long ciclos = 0;

volatile long pulsos = 0;

unsigned long ultControle = 0, ultFuzzy = 0, ultTela = 0;

// =====================================================================
// PWM (LEDC), compativel com o core 2.x e 3.x do ESP32
// =====================================================================
void pwmIniciar(uint8_t pino, uint8_t canal, uint32_t freq, uint8_t bits = 8) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  (void)canal;
  ledcAttach(pino, freq, bits);
#else
  ledcSetup(canal, freq, bits);
  ledcAttachPin(pino, canal);
#endif
}

void pwmEscrever(uint8_t pino, uint8_t canal, uint32_t duty) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  (void)canal;
  ledcWrite(pino, duty);
#else
  (void)pino;
  ledcWrite(canal, duty);
#endif
}

const uint8_t CANAL_RPWM = 0, CANAL_LPWM = 1, CANAL_FRENAGEM = 2, CANAL_SERVO = 3;

// Servo a 50 Hz com 16 bits: 0 graus = 500 us, 180 graus = 2.500 us
void servoAngulo(int graus) {
  uint32_t us = 500 + (uint32_t)constrain(graus, 0, 180) * 2000 / 180;
  pwmEscrever(PIN_SERVO, CANAL_SERVO, us * 65535UL / 20000UL);
}

// =====================================================================
// Fuzzy (Mamdani, AND = min, OR = max, centroide) - igual ao principal
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
// Atuadores: o unico lugar que mexe nos pinos do IBT-2 e do servo
// =====================================================================
void aplicarAtuadores() {
  bool rEn = ponte != LIVRE;
  bool lEn = ponte == SUBIR || ponte == CURTO;  // em GERAR o M- fica solto
  digitalWrite(PIN_R_EN, rEn ? HIGH : LOW);
  digitalWrite(PIN_L_EN, lEn ? HIGH : LOW);
  pwmEscrever(PIN_RPWM, CANAL_RPWM, ponte == SUBIR ? pwmMotor : 0);
  pwmEscrever(PIN_LPWM, CANAL_LPWM, 0);
  pwmEscrever(PIN_FRENAGEM, CANAL_FRENAGEM, (int)(frenagem * 255));
  servoAngulo(travaLiberada ? SERVO_SOLTA : SERVO_ENGATADA);
}

void estadoSeguro() {
  pwmMotor = 0;
  travaLiberada = false;
  frenagem = 1.0;
  ponte = CURTO;
}

void entrar(Estado novo) {
  if (estado == DESCENDO && novo != DESCENDO) ciclos++;
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
// Planta virtual: substitui a massa, o gerador, o encoder e o INA219 n. 2
void atualizarPlanta(float dt) {
  bool energia = digitalRead(PIN_EMERG) == HIGH;  // sem 12V_POT: sem motor e sem servo
  bool travaSolta = travaLiberada && energia;     // sem 5V_SERVO a mola engata
  Ponte efetiva = energia ? ponte : LIVRE;        // sem B+ o IBT-2 nao conduz
  float vDesejada = 0;

  if (efetiva == SUBIR && pwmMotor > 0) {
    vDesejada = max(0.0f, (12.0f * pwmMotor / 255.0f - 2.2f) / KE_MASSA);
  } else if (efetiva == CURTO) {
    vDesejada = 0;                                // motor em curto: quase parado
  } else if (travaSolta) {
    // Motor como gerador contra a carga fixa e a frenagem (C-109)
    float condutancia = 1.0f / R_FIXA + frenagem / R_FRENAGEM;
    vDesejada = -I_GEN * (1.0f / condutancia + R_A) / KE_MASSA;
  }

  v += (vDesejada - v) * 0.3;          // inercia
  if (v < 0 && !travaSolta) v = 0;     // a lingueta segura a descida
  h += v * dt;
  if (h < 0) { h = 0; if (v < 0) v = 0; }
  if (h > CURSO + FOLGA_TOPO) { h = CURSO + FOLGA_TOPO; if (v > 0) v = 0; }
  pulsos = lround(h * 1000.0 / MM_POR_PULSO);

  bool gerando = v < 0 && (efetiva == GERAR || efetiva == LIVRE);
  vGen = gerando ? -v * KE_MASSA : 0;
  pGerada = gerando ? MASSA * G * -v * ETA_DESCIDA : 0;
  pSubida = (efetiva == SUBIR && v > 0) ? MASSA * G * v / ETA_SUBIDA : 0;

  // LEDs de nivel do GEN (no real: Zener + resistor, sem software)
  digitalWrite(PIN_LED_VERDE, vGen > 2.0 ? HIGH : LOW);
  digitalWrite(PIN_LED_AMARELO, vGen > 6.5 ? HIGH : LOW);
  digitalWrite(PIN_LED_VERMELHO, vGen > 10.0 ? HIGH : LOW);
}

void lerSensores(float dt) {
  corrente = analogRead(PIN_POT_CORRENTE) * 3.0 / 4095.0;
  atualizarPlanta(dt);
}
#else
// Prototipo real: altura pelo encoder Hall do motor (troque por ESP32Encoder
// para usar o PCNT: o curso soma ~126.000 contagens), corrente de subida pelo
// INA219 0x40, tensao e potencia geradas pelo INA219 0x41.
float hAnterior = 0;
void lerSensores(float dt) {
  noInterrupts();
  long p = pulsos;
  interrupts();
  h = p * MM_POR_PULSO / 1000.0;
  v = (h - hAnterior) / dt;
  hAnterior = h;
  // corrente = ina1.getCurrent_mA() / 1000; pSubida = ina1.getPower_mW() / 1000;
  // vGen = ina2.getBusVoltage_V(); pGerada = ina2.getPower_mW() / 1000;
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

  switch (estado) {
    case MANTER:
      pwmMotor = 0;
      travaLiberada = false;
      ponte = LIVRE;
      if (naEtapa > 500) frenagem = 0;
      break;

    case SUBINDO:
      if (fimSuperior()) {
        entrar(PARANDO);
        break;
      }
      ponte = SUBIR;           // a catraca estala e deixa subir
      frenagem = 0;
      {
        int alvo = PWM_SUBIDA + (int)(3000 * (V_SUBIDA - v));
        alvo = constrain(alvo, 0, 255);
        pwmMotor += constrain(alvo - pwmMotor, -7, 7);  // rampa de ~1,3 s
      }
      break;

    case PREP_DESCIDA:
    case REARME:
      if (estado == REARME && etapa == 0 && fimInferior()) {
        zerarPosicao();
        estadoSeguro();
        entrar(PARANDO);
        break;
      }
      if (estado == PREP_DESCIDA && fimInferior()) {
        entrar(PARANDO);
        break;
      }
      if (etapa == 0) {        // sobe 3 mm para aliviar a lingueta
        ponte = SUBIR;
        frenagem = 0;
        hInicioAlivio = h;
        etapa = 1;
        inicioEtapa = agora;
      } else if (etapa == 1) {
        pwmMotor = PWM_ALIVIO;
        if (h >= hInicioAlivio + ALIVIO_TRAVA) {
          pwmMotor = 0;
          ponte = CURTO;       // o motor em curto segura enquanto o servo puxa
          travaLiberada = true;
          etapa = 2;
          inicioEtapa = agora;
        } else if (naEtapa > 3000) {
          falha("trava presa");
        }
      } else if (etapa == 2 && naEtapa >= T_SERVO) {
        frenagem = 1.0;        // freio maximo antes de soltar o M-
        ponte = GERAR;
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
      ponte = CURTO;           // freio forte: a massa para em poucos ms
      travaLiberada = false;   // a mola leva a lingueta ao proximo dente
      if (naEtapa > 500) entrar(MANTER);
      break;

    case FALHA:
      estadoSeguro();
      break;
  }
}

// =====================================================================
// Decisao (a cada 5 s no automatico)
// =====================================================================
float nivel() { return constrain(h / CURSO * 100, 0.0f, 100.0f); }

void decidir() {
  comandoFuzzy = fuzzy(tarifa, nivel(), demanda);
  if (modo != AUTOMATICO || !posicaoConhecida || !horaValida) return;
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
  if (c[0] == 'w') {
    demandaPainel = constrain(c.substring(1).toFloat(), 0.0f, 10.0f);
    Serial.print("demanda do painel: ");
    Serial.println(demandaPainel);
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
      alvoDescida = V_ALVO_MAX;
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
// Hora (NTP) e Monitor Serial
// =====================================================================
void atualizarHora() {
  if (horaForcada >= 0) {
    hora = horaForcada;
    horaValida = true;
    return;
  }
  struct tm t;
  horaValida = getLocalTime(&t, 0);   // 0 ms: nao trava o loop esperando o NTP
  if (horaValida) hora = t.tm_hour + t.tm_min / 60.0;
}

void mostrar() {
  Serial.printf("%s %s ponte=%s h=%.3f nivel=%d%% v=%.3f fuzzy=%.0f hora=%s tarifa=%.2f dem=%.1fW "
                "gen=%.1fV freio=%d%% Psub=%.2fW Pgen=%.2fW Esub=%.1fJ Egen=%.1fJ ciclos=%ld I=%.2fA",
                NOME_ESTADO[estado], modo == AUTOMATICO ? "AUTO" : "MAN", NOME_PONTE[ponte],
                h, (int)nivel(), v, comandoFuzzy, horaValida ? String(hora, 2).c_str() : "--",
                tarifa, demanda, vGen, (int)(frenagem * 100), pSubida, pGerada, eSubida, eGerada,
                ciclos, corrente);
  if (estado == FALHA) Serial.printf(" motivo=%s (r = rearme)", motivoFalha);
  Serial.println();
}

void IRAM_ATTR contarPulso() {
  pulsos += (digitalRead(PIN_ENC_A) == digitalRead(PIN_ENC_B)) ? 1 : -1;
}

// =====================================================================
void setup() {
  // EN em baixo antes de virar saida: ponte LIVRE no boot (pull-down 10 kOhm no real)
  for (uint8_t p : {PIN_R_EN, PIN_L_EN}) {
    digitalWrite(p, LOW);
    pinMode(p, OUTPUT);
  }
  pinMode(PIN_EMERG, INPUT);          // GPIO 34 nao tem pull-up interno
  pinMode(PIN_FC_INF, INPUT_PULLUP);
  pinMode(PIN_FC_SUP, INPUT_PULLUP);
  pinMode(PIN_DEMANDA, INPUT_PULLUP);
  pinMode(PIN_ENC_A, INPUT_PULLUP);
  pinMode(PIN_ENC_B, INPUT_PULLUP);
#if SIMULACAO
  for (uint8_t p : {PIN_LED_VERDE, PIN_LED_AMARELO, PIN_LED_VERMELHO}) pinMode(p, OUTPUT);
#else
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_A), contarPulso, CHANGE);
#endif

  pwmIniciar(PIN_RPWM, CANAL_RPWM, 20000);
  pwmIniciar(PIN_LPWM, CANAL_LPWM, 20000);
  pwmIniciar(PIN_FRENAGEM, CANAL_FRENAGEM, 5000);
  pwmIniciar(PIN_SERVO, CANAL_SERVO, 50, 16);

  estadoSeguro();
  aplicarAtuadores();

  Serial.begin(115200);
  Wire.begin(21, 22);
  WiFi.begin(WIFI_SSID, WIFI_SENHA);   // conecta em segundo plano
  configTime(FUSO_S, 0, "pool.ntp.org", "a.st1.ntp.br");

  maxSubir = centroide(0, 0, 0, 1);
  maxDescer = -centroide(1, 0, 0, 0);

  Serial.println("Bateria gravitacional - MVP fablab - ESP32");
  Serial.println("a=auto s=subir d=descer p=parar r=rearme h19=hora hx=hora do NTP w3=demanda do painel");
  entrar(REARME);  // posicao desconhecida: desce ate o fim de curso inferior
}

void loop() {
  unsigned long agora = millis();
  lerComando();

  if (agora - ultControle >= T_CONTROLE) {
    float dt = (agora - ultControle) / 1000.0;
    ultControle = agora;

    atualizarHora();
    tarifa = tarifaDaHora(hora);
    demanda = max(digitalRead(PIN_DEMANDA) == LOW ? DEMANDA_CHAVE : 0.0f, demandaPainel);

    lerSensores(dt);
    eSubida += pSubida * dt;
    eGerada += pGerada * dt;
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
