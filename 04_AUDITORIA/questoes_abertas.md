# QUESTÕES ABERTAS

Perguntas que só o grupo responde. Ao responder, registre a decisão em
`00_MASTER/DECISOES.md` e marque aqui como respondida.

| ID | Pergunta | Por que importa | Quem decide | Status |
|----|----------|-----------------|-------------|--------|
| Q-001 | O painel fica em **Streamlit** (já no repositório) ou em **Node-RED** (citado no relatório)? | Define onde o DESENVOLVEDOR adapta o painel (HANDOFF-005) e qual texto do relatório muda (INC-028) | Grupo | aberta |
| Q-002 | Haverá ensaios com mais de 20 kg? Até quanto? | A mecânica aguenta 50 kg sem mudança; acima disso muda a travessa e o motor | Grupo | aberta |
| Q-003 | Quais tarifas e postos horários reais usar (concessionária, Tarifa Branca), e como tratar fins de semana e feriados? | Hoje o firmware usa valores de exemplo (0,60 / 0,90 / 1,40 R$/kWh, ponta 18–21 h) e ignora o dia da semana (INC-030) | FÍSICO + grupo | aberta |
| Q-004 | Qual motorredutor comprar (modelo, folha de dados)? | K_e, torque e reversibilidade do redutor precisam ser confirmados antes de montar | ARQUITETO | aberta |
| Q-005 | Manter o fuzzy escrito à mão no firmware ou passar para a eFLL, como diz o relatório? | O texto e o código precisam dizer a mesma coisa (INC-026) | DESENVOLVEDOR + grupo | aberta |
| Q-006 | Onde roda o broker MQTT (notebook do grupo ou Raspberry Pi)? | Define o endereço do broker no firmware e se o painel precisa ficar ligado sozinho | Grupo | aberta |
| Q-007 | O celular que será usado na apresentação aceita carga com tensão oscilando? | Alguns celulares cortam a carga; alternativa é luminária USB ou power bank | Grupo (testar com fonte de bancada a 9 V no buck) | aberta |
| Q-008 | Qual o prazo de entrega do protótipo? | `00_MASTER/PROJETO.md` está sem prazo | Grupo | aberta |
