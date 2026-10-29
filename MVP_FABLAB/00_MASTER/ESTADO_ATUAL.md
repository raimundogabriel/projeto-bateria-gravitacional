# ESTADO ATUAL — MVP FABLAB
Última atualização: 2026-10-29
Atualizado por: DESENVOLVEDOR (MQTT e passo a passo DIY)

## ✅ CONCLUÍDO
- [x] Avaliação e proposta da releitura (variantes A e B) → `../README.md`
- [x] Premissas e energia do MVP → `../01_FISICA/`
- [x] Mecânica para fablab, circuito sem relés com diagramas, BOM e lista do
  que sai → `../02_ARQUITETO/`
- [x] Pinagem e plano de mudanças do firmware e do painel → `../03_SOFTWARE/`
- [x] Porte decidido: 6 kg de anilhas, 1,70 m, só LEDs (DEC-014, DEC-022);
  física, mecânica, BOM, firmware e painel refeitos para ele
- [x] Firmware do MVP e projeto Wokwi (planta virtual de 6 kg, ponte sem
  relés, servo, NTP), testado fora do Wokwi com pinos simulados →
  `../03_SOFTWARE/firmware/` (HANDOFF-011, menos MQTT)
- [x] Painel Streamlit do MVP → `../03_SOFTWARE/dashboard/` (HANDOFF-012)
- [x] MQTT no firmware e fonte “ESP32 (MQTT)” no painel, com comandos e
  tarifas; leituras reais do INA219 e do encoder com `SIMULACAO 0`
  (DEC-023, HANDOFF-013). Testado fora do hardware
- [x] Passo a passo para gravar o ESP32 e ligar ao painel → `../DIY/`

## 🔄 EM ANDAMENTO
- Escolha do motor pelo custo — Gabriel (Q-012). Tudo está calculado para o
  12 V 1:90 de referência.
- Rodar o firmware dentro do Wokwi ou num ESP32 solto (`../DIY/`, parte A)
  e ver o painel ao vivo — Gabriel / DESENVOLVEDOR (HANDOFF-011 e 013)

## ❌ NÃO INICIADO
- Ensaio 0 do motor (HANDOFF-009) — decide a compra do resto
- Desenho cotado e arquivos de corte/impressão (HANDOFF-010)

## ⚠️ ALERTAS
- O maior risco é o redutor de engrenagens retas não retroacionar com 6 kg.
  Comprar um motor e fazer o ensaio 0 antes do resto.
- A troca subir/gerar sem relé (DEC-017) é nova: provar com o motor girando
  à mão (ensaio 4) antes de pendurar massa.
- Todos os números (K_e, rendimentos, preços) são estimativas.

## PRÓXIMA AÇÃO RECOMENDADA
1. Gabriel escolhe o motor (Q-012) e diz que máquinas o fablab tem (Q-010)
2. Comprar 1 motorredutor e fazer o ensaio 0
3. ARQUITETO gera o desenho cotado e os arquivos de corte
