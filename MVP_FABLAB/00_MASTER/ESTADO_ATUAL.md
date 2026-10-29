# ESTADO ATUAL — MVP FABLAB
Última atualização: 2026-10-28
Atualizado por: DESENVOLVEDOR (firmware, Wokwi e painel do MVP)

## ✅ CONCLUÍDO
- [x] Avaliação e proposta da releitura (variantes A e B) → `../README.md`
- [x] Premissas e energia do MVP → `../01_FISICA/`
- [x] Mecânica para fablab, circuito sem relés com diagramas, BOM e lista do
  que sai → `../02_ARQUITETO/`
- [x] Pinagem e plano de mudanças do firmware e do painel → `../03_SOFTWARE/`
- [x] Firmware do MVP e projeto Wokwi (planta virtual de 5 kg, ponte sem
  relés, servo, NTP), testado fora do Wokwi com pinos simulados →
  `../03_SOFTWARE/firmware/` (HANDOFF-011, menos MQTT)
- [x] Painel Streamlit do MVP → `../03_SOFTWARE/dashboard/` (HANDOFF-012)

## 🔄 EM ANDAMENTO
- Escolha da variante (5 kg / 1,0 m ou 10 kg / 1,2 m) — Gabriel (Q-009).
  O firmware e o painel já seguem a variante A.
- Rodar o firmware dentro do Wokwi e conferir o `diagram.json` — Gabriel /
  DESENVOLVEDOR

## ❌ NÃO INICIADO
- Ensaio 0 do motor (HANDOFF-009) — decide a compra do resto
- Desenho cotado e arquivos de corte/impressão (HANDOFF-010)
- MQTT no firmware do MVP e coletor `ler_esp32()` no painel (HANDOFF-013)

## ⚠️ ALERTAS
- O maior risco é o redutor de engrenagens retas não retroacionar com 5 kg.
  Comprar um motor e fazer o ensaio 0 antes do resto.
- A troca subir/gerar sem relé (DEC-017) é nova: provar com o motor girando
  à mão (ensaio 4) antes de pendurar massa.
- Todos os números (K_e, rendimentos, preços) são estimativas.

## PRÓXIMA AÇÃO RECOMENDADA
1. Gabriel escolhe a variante (Q-009) e diz que máquinas o fablab tem (Q-010)
2. Comprar 1 motorredutor e fazer o ensaio 0
3. ARQUITETO gera o desenho cotado e os arquivos de corte
