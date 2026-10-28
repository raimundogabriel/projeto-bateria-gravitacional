# INCONSISTÊNCIAS ENCONTRADAS

INC-001 a INC-024: auditoria do relatório original
(`05_DOC_ORIGINAL/Documentacao_1_Integracao_Bateria_Gravitacional.pdf`) em
2026-10-07. Veredito na época: NO-GO para 20–100 kg como descrito; GO
condicional para protótipo reduzido. "Doc v2" = texto revisado em
`05_DOC_ORIGINAL/Documentacao_1_Integracao_Bateria_Gravitacional_v2.docx`.

INC-025 em diante: encontradas ao consolidar o repositório (2026-10-28).

Severidade: 🔴 crítica (impede funcionar ou cria risco físico) · 🟠 alta
(funciona mal) · 🟡 média (definir antes de comprar) · ⚪ baixa (redação).

> A versão inicial trazia INC-001/INC-002 de exemplo (energia 10× maior;
> massa em kg e N). Foram substituídas pelos itens reais abaixo.

| ID | Local | Tipo | Sev. | Descrição | Status |
|----|-------|------|------|-----------|--------|
| INC-001 | Doc §4.2, Quadro 3, §4.5 | Físico | 🔴 | Gerador indefinido; tambor a ~16 rpm não gera nada útil; redutor sem-fim travaria a descida | resolvido DEC-003 (falta ensaio de K_e) |
| INC-002 | Doc §4.2, §6 | Físico | 🔴 | Consumo próprio não contabilizado: bobina do freio ligada a descida toda + eletrônica > energia do ciclo | resolvido DEC-005 + consumo auxiliar à parte (medir) |
| INC-003 | Doc §3, Quadro 1 | Físico | 🔴 | Exemplo diz 1,70 m mas multiplica por 3; Quadro 1 "3 m" com valores de 1,70 m | resolvido no doc v2 (C-001) |
| INC-004 | Doc §4.4, §5 | Segurança | 🔴 | Descida sem controle de velocidade ("soltar a plataforma"); queda livre chegaria a 5,8 m/s | resolvido: frenagem PI, limite 0,10 m/s |
| INC-005 | Doc §4.3, §4.5 | Segurança | 🔴 | Estrutura para 100 kg sem dimensionamento (cabo, tambor, guias, tombamento) | parcial: dimensionado para 20 kg (DEC-012); falta desenho cotado (HANDOFF-007) |
| INC-006 | Doc §4.4 | Interno | 🟠 | Na subida o freio não é liberado; cada subida dispararia "travamento" | resolvido: catraca deixa subir (DEC-005) |
| INC-007 | Doc Quadro 2 | Técnico | 🟠 | INA219 satura (26 V, ~3,2 A) | resolvido DEC-006 |
| INC-008 | Doc §4.2, Quadros 3–4 | Técnico | 🟠 | Motor, redutor e fonte sem especificação | resolvido DEC-003 |
| INC-009 | Doc §5 | Interno | 🟠 | Base de regras com combinações sem regra | resolvido DEC-007 (9 combinações cobertas) |
| INC-010 | Doc §5 | Técnico | 🟠 | Demanda em 0–5.000 W; única regra de descer exigia demanda alta | resolvido: demanda 0–10 W da USB |
| INC-011 | Doc §4.4, §5 | Interno | 🟠 | Tarifa e classe horária redundantes; R4 nunca dispara | resolvido: posto não é entrada |
| INC-012 | Doc §1, §4.4, §7 | Viabilidade | 🟠 | Descida de 17–33 s contra horário de ponta de horas | aceito: demonstração curta (DEC-004) |
| INC-013 | Doc §3, §4.5, §6 | Técnico | 🟠 | Massa variável sem medição; fórmula do nível ausente | parcial: massa fixa 20 kg, fórmula no doc v2; sem campo de massa no painel |
| INC-014 | Doc §2.1, §6 | Viabilidade | 🟠 | "A carga" indefinida; economia sem fórmula | resolvido: USB/LEDs; economia simulada em `contrato_dados.md` |
| INC-015 | Doc Quadro 3 | Segurança | 🟠 | Freio no GPIO 14, que pulsa no boot | resolvido: trava no GPIO 4; GPIO 14 = buzzer |
| INC-016 | Doc §4.4, §5 | Técnico | 🟠 | Comando −100..+100 sem mapeamento para ação; centroide não chega a ±100 | resolvido: normalização + histerese |
| INC-017 | Doc §4.3, §4.5 | Interno | 🟡 | Fins de curso em 0,05 e 1,70 m → curso real 1,65 m | resolvido no doc v2 (h = 0 a 1,70); verificar no desenho cotado |
| INC-018 | Doc §3 | Físico | 🟡 | Eficiência 40–60 % sem fonte | resolvido: ~27 % estimado (C-004), medir |
| INC-019 | Doc Quadro 2, §4.3 | Técnico | 🟡 | Encoder sem homing | resolvido: REARME até o fim de curso inferior |
| INC-020 | Doc §4.4, Quadro 7 | Interno | 🟡 | Tarifa ora do RTC, ora de API; fins de semana não tratados | parcial: tabela local via `grav/tarifas`; fins de semana em INC-030 |
| INC-021 | Doc Quadro 3, §7 | Técnico | 🟡 | Relé de corte poderia desligar o ESP32 e impedir o rearme | resolvido DEC-009 |
| INC-022 | Doc Quadros 2–3 | Técnico | 🟡 | Pinagem incompleta | resolvido: `03_SOFTWARE/pinagem_esp32.md` |
| INC-023 | Doc Figuras 1–2, §4.5 | Interno | ⚪ | Diagramas não batem com o texto; foto sem número; sem desenho técnico | parcial: figuras refeitas no doc v2; falta desenho cotado |
| INC-024 | Doc inteiro | Interno | ⚪ | Vários nomes para a mesma peça | parcial: `00_MASTER/GLOSSARIO.md` |
| INC-025 | Repositório (template) | Interno | 🔴 | Premissas, decisões e handoffs com 500 kg e 3 m, contra a DEC-001 (20 kg, 1,70 m) | resolvido nesta consolidação |
| INC-026 | Doc v2 §4.3, §5 × firmware | Interno | 🟡 | Doc v2 diz eFLL; o firmware usa fuzzy escrito à mão | aberto (Q-005) |
| INC-027 | Doc v2 Quadros 2–3 × eletrônica v2 | Interno | 🟠 | Doc v2 traz 2 INA226, resistor de 22 Ω, relé de modo que "só comuta com corrente nula"; a eletrônica v2 tem 3 INA226, 11 Ω, K2 com repouso em geração, K4 de sondagem | aberto: atualizar o texto do relatório |
| INC-028 | Doc v2 §6 × `03_SOFTWARE/dashboard/` | Interno | 🟡 | Doc v2 diz Node-RED + Mosquitto; repositório tem Streamlit | resolvido DEC-013 (seção 6 do doc v2 corrigida) |
| INC-029 | Doc v2 §4.4, §6 × firmware | Técnico | 🟡 | Doc v2 descreve publicação MQTT; o firmware ainda não tem MQTT | aberto |
| INC-030 | Doc v2 Quadro 2 × firmware | Técnico | 🟡 | Doc v2 diz que o RTC trata fins de semana; `tarifaDaHora()` só olha a hora | aberto (Q-003) |
| INC-031 | `03_SOFTWARE/firmware/wokwi/diagram.json` | Técnico | 🟡 | Nomes de pinos do Wokwi escritos sem abrir o simulador; código não rodou dentro do Wokwi | aberto |
| INC-032 | `03_SOFTWARE/pinagem_esp32.md` (template) | Técnico | 🟠 | Encoder no 34/35, PWM no 25, INA219: conflitava com fins de curso no 25/26 | resolvido nesta consolidação |
