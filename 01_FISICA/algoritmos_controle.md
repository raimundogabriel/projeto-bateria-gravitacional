# ALGORITMOS DE CONTROLE

O controle tem duas camadas: a **decisão** (fuzzy, a cada 5 s) escolhe entre
subir, manter e descer; a **regulação** (a cada 50 ms) segura a velocidade e
verifica as proteções. Implementação de referência:
`03_SOFTWARE/firmware/wokwi/sketch.ino`.

## 1. Controlador fuzzy (DEC-007)

Mamdani (ZADEH, 1965; MAMDANI; ASSILIAN, 1975), AND = mín, OR = máx,
defuzzificação por centroide (passo 2 na faixa −100 a +100).

### Entradas e saída

| Variável | Faixa | Conjuntos (pontos da função) |
|----------|-------|------------------------------|
| Tarifa T (entrada) | 0 a 2 R$/kWh | baixa trap(0, 0, 0,6, 0,8); média tri(0,6, 0,9, 1,2); alta trap(0,9, 1,2, 2, 2) |
| Nível de carga N (entrada) | 0 a 100 % | baixo trap(0, 0, 20, 45); médio tri(20, 50, 95); alto trap(60, 95, 100, 100) |
| Demanda D (entrada) | 0 a 10 W | baixa trap(0, 0, 0,3, 1) = nada ligado; média tri(0,3, 1,5, 3) = LEDs; alta trap(2, 4, 10, 10) = celular |
| Comando u (saída) | −100 a +100 | descer trap(−100, −100, −80, −50); descer parcial tri(−70, −40, −10); manter tri(−25, 0, 25); subir trap(40, 70, 100, 100) |

A tarifa vem de uma tabela por posto horário (configurável pelo painel em
`grav/tarifas`); por isso o posto não é entrada separada. A demanda é a
potência pedida pela saída USB, medida pelo INA226 nº 3 (com a massa parada,
pela sondagem do K4, DEC-008).

### Base de regras

| Regra | Condição | Ação | Justificativa |
|-------|----------|------|---------------|
| R1 | T baixa E N baixo | SUBIR | Armazenar com energia barata |
| R2 | T baixa E N médio | SUBIR | Completar a carga |
| R3 | T baixa E N alto | MANTER | Carga completa |
| R4 | T média E N baixo | MANTER | Esperar a tarifa baixa para subir |
| R5 | T média E N médio | MANTER | Guardar para a ponta |
| R6 | T média E N alto E D alta | DESCER PARCIAL | Atender o celular no intermediário |
| R7 | T média E N alto E (D baixa OU média) | MANTER | Guardar para a ponta |
| R8 | T alta E N baixo | MANTER | Pouca energia para gerar |
| R9 | T alta E N médio E (D média OU alta) | DESCER PARCIAL | Gerar sem esvaziar de uma vez |
| R10 | T alta E N alto E (D média OU alta) | DESCER | Gerar na ponta |
| R11 | T alta E D baixa | MANTER | Nada ligado à saída |

As 9 combinações tarifa × nível estão cobertas; a demanda decide se há para
quem gerar (sem aparelho na saída, a massa não desce).

### Normalização
O centroide não alcança ±100. O firmware divide o resultado pelo maior valor
que o centroide produz em cada sentido (`maxSubir`, `maxDescer`, calculados na
partida), para que o comando use a faixa inteira (INC-016).

### Do comando à ação
- Histerese: começa a subir com u > +30 e a descer com u < −30; continua
  enquanto |u| > 10. Isso evita liga/desliga a cada 5 s.
- Velocidade-alvo de descida: v_alvo = 0,03 + max(−u − 30, 0) / 70 ×
  (0,08 − 0,03) m/s. "Descer parcial" = descer mais devagar.
- Subida: velocidade fixa de 0,05 m/s.
- Override manual do painel (`grav/comando`: subir, descer, parar) substitui a
  decisão fuzzy até o comando `auto`.

### Tabela de tarifas (valores de exemplo do firmware)
| Posto | Horário | R$/kWh |
|-------|---------|--------|
| Fora de ponta | demais horas | 0,60 |
| Intermediário | 17 h–18 h e 21 h–22 h | 0,90 |
| Ponta | 18 h–21 h | 1,40 |

Valores reais da concessionária e tratamento de fins de semana/feriados estão
em aberto (Q-003, INC-030).

## 2. Regulação da descida
PI incremental a cada 50 ms sobre o PWM da carga de frenagem:
`frenagem = clamp(frenagem + 2,0 · (|v| − v_alvo), 0, 1)`. Rápido demais →
mais PWM → mais corrente → mais freio. A USB tem prioridade: o resistor só
recebe o excedente.

## 3. Proteções (a cada 50 ms)
| Condição | Ação |
|----------|------|
| Velocidade > 0,10 m/s | solenoide em 0 (trava engata), frenagem 100 %, K1 aberto |
| Tensão no GEN > 28 V | frenagem 100 % |
| Corrente > 3 A com encoder parado por 500 ms | "massa travada" → FALHA |
| Fim de curso inesperado | FALHA |
| Emergência acionada | FALHA (e corte por hardware, DEC-009) |
| Trava não solta em 3 s | FALHA "trava presa" |

Na FALHA: solenoide em 0, frenagem 100 %, EN em baixo, K2 e K1 soltos,
buzzer. Só o comando de rearme sai da falha.

## 4. Máquina de estados
`REARME` (posição desconhecida: desce com frenagem 100 % até o fim de curso
inferior e zera o encoder) → `MANTER` ⇄ `SUBINDO` / `PREP_DESCIDA` →
`DESCENDO` → `PARANDO` → `MANTER`; qualquer estado → `FALHA` → `REARME`.

Sequências detalhadas (ordem dos relés, alívio de 3 mm da lingueta, tempos)
em `02_ARQUITETO/circuitos/esquema_potencia.md`.

## 5. Ritmos
| Laço | Período |
|------|---------|
| Proteção e malha de velocidade | 50 ms |
| Decisão fuzzy | 5 s |
| LCD | 1 s |
| Sondagem USB em MANTER | 1 s a cada 30 s |
| Publicação MQTT de estado/energia | 30 s (a implementar) |
