"""
Conexão do painel com o ESP32 por MQTT (passo a passo em `MVP_FABLAB/DIY/`).

Tópicos, todos abaixo de uma base (`grav` no fablab):

| Tópico             | Quem publica | Conteúdo                                         |
|--------------------|--------------|--------------------------------------------------|
| `<base>/estado`    | ESP32        | JSON com as colunas de `COLUNAS`, a cada 1 s     |
| `<base>/online`    | ESP32        | `1` ao conectar, `0` (testamento) se cair; retido |
| `<base>/comando`   | Painel       | `{"acao": "subir"}`, `{"demanda_w": 3}`, `{"hora": 19}` |
| `<base>/tarifas`   | Painel       | `{"fora_ponta": 0.6, "intermediario": 0.9, "ponta": 1.4}`; retido |

O coletor roda numa thread do paho-mqtt e guarda as últimas 24 h em memória;
o painel lê a janela pedida com `dataframe()`.
"""
import json
import threading
import uuid
from collections import deque
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import paho.mqtt.client as mqtt

from src.simulador import COLUNAS

MAX_LEITURAS = 24 * 3600   # 24 h a uma leitura por segundo
ACOES = ("auto", "subir", "descer", "parar", "rearmar")


class ColetorESP32:
    """Assina os tópicos do ESP32 e publica comandos e tarifas."""

    def __init__(self, broker, porta=1883, base="grav"):
        self.broker, self.porta, self.base = broker, int(porta), base.strip("/")
        self.leituras = deque(maxlen=MAX_LEITURAS)
        self.ultimo_json = None
        self.ultima_msg = None
        self.esp32_online = None   # None = sem notícia; senão o valor retido de <base>/online
        self.conectado = False
        self.erro = ""
        self._trava = threading.Lock()

        self.cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"painel-grav-{uuid.uuid4().hex[:8]}")
        self.cliente.on_connect = self._ao_conectar
        self.cliente.on_disconnect = self._ao_desconectar
        self.cliente.on_connect_fail = self._ao_falhar
        self.cliente.on_message = self._ao_receber
        self.cliente.reconnect_delay_set(1, 10)
        try:
            self.cliente.connect_async(self.broker, self.porta, keepalive=30)
            self.cliente.loop_start()
        except Exception as e:   # endereço inválido: o painel mostra o erro
            self.erro = str(e)

    def topico(self, nome):
        return f"{self.base}/{nome}"

    # ---------- callbacks (thread do paho) ----------
    def _ao_conectar(self, cliente, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            self.erro = f"broker recusou: {reason_code}"
            return
        self.conectado, self.erro = True, ""
        cliente.subscribe([(self.topico("estado"), 0), (self.topico("online"), 1)])

    def _ao_desconectar(self, cliente, userdata, flags, reason_code, properties):
        self.conectado = False

    def _ao_falhar(self, cliente, userdata):
        self.erro = f"não conectou em {self.broker}:{self.porta} (endereço certo? Mosquitto ligado? firewall?)"

    def _ao_receber(self, cliente, userdata, msg):
        texto = msg.payload.decode("utf-8", errors="replace")
        if msg.topic == self.topico("online"):
            self.esp32_online = texto.strip() == "1"
            return
        if msg.topic == self.topico("estado"):
            self.registrar(texto)

    def registrar(self, texto, quando=None):
        """Converte um JSON de `<base>/estado` numa linha de leitura."""
        try:
            dados = json.loads(texto)
        except json.JSONDecodeError:
            return
        linha = {c: dados.get(c, np.nan) for c in COLUNAS}
        linha["timestamp"] = quando or datetime.now()
        linha["hora_sim"] = dados.get("hora", np.nan) if dados.get("hora_valida", True) else np.nan
        with self._trava:
            self.leituras.append(linha)
            self.ultimo_json = dados
            self.ultima_msg = linha["timestamp"]
            self.esp32_online = True

    # ---------- leitura pelo painel ----------
    def dataframe(self, minutos):
        with self._trava:
            linhas = list(self.leituras)
        df = pd.DataFrame(linhas, columns=COLUNAS)
        if df.empty:
            return df
        df = df[df["timestamp"] >= datetime.now() - timedelta(minutes=minutos)]
        return df.astype({"estado": str, "posto": str}).reset_index(drop=True)

    def situacao(self):
        """Texto curto para a barra lateral."""
        if self.erro:
            return "🔴", f"Sem broker: {self.erro}"
        if not self.conectado:
            return "🟠", f"Conectando em {self.broker}:{self.porta}…"
        if self.ultima_msg is None:
            return "🟠", f"Broker ok; esperando o ESP32 em `{self.topico('estado')}`"
        atraso = (datetime.now() - self.ultima_msg).total_seconds()
        if self.esp32_online is False or atraso > 10:
            return "🟠", f"ESP32 sem publicar há {atraso:.0f} s"
        return "🟢", f"ESP32 online · última leitura há {atraso:.0f} s"

    # ---------- comandos ----------
    def comandar(self, acao=None, demanda_w=None, hora=None):
        """Publica em `<base>/comando`. Devolve True se o broker aceitou."""
        msg = {}
        if acao is not None:
            if acao not in ACOES:
                raise ValueError(f"ação desconhecida: {acao}")
            msg["acao"] = acao
        if demanda_w is not None:
            msg["demanda_w"] = round(float(demanda_w), 1)
        if hora is not None:
            msg["hora"] = round(float(hora), 2)
        return self._publicar("comando", msg, reter=False)

    def enviar_tarifas(self, tarifas):
        """Publica as tarifas retidas: o ESP32 recebe de novo sempre que reconecta."""
        return self._publicar("tarifas", {k: round(float(v), 2) for k, v in tarifas.items()}, reter=True)

    def _publicar(self, nome, msg, reter):
        if not self.conectado:
            return False
        info = self.cliente.publish(self.topico(nome), json.dumps(msg), qos=1, retain=reter)
        return info.rc == mqtt.MQTT_ERR_SUCCESS

    def parar(self):
        self.cliente.loop_stop()
        self.cliente.disconnect()
