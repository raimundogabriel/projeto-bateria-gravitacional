# ESTADO ATUAL — MVP FABLAB
Última atualização: 2026-10-29
Atualizado por: FÍSICO / ARQUITETO / DESENVOLVEDOR (parafusadeira GSR 1440-LI e 6 kg)

## ✅ CONCLUÍDO
- [x] Avaliação e proposta da releitura (variantes A e B) → `../README.md`
- [x] Premissas e energia do MVP → `../01_FISICA/`
- [x] Mecânica para fablab, circuito sem relés com diagramas, BOM e lista do
  que sai → `../02_ARQUITETO/`
- [x] Pinagem e plano de mudanças do firmware e do painel → `../03_SOFTWARE/`
- [x] Porte decidido: 6 kg de anilhas, 1,70 m, só LEDs (DEC-014, DEC-022)
- [x] Porte trocado para motor de 6 V e 2 kg, sem talha, tambor Ø 30 mm
  (DEC-024, DEC-025)
- [x] Motor definido: parafusadeira Bosch GSR 1440-LI inteira, sem a trava
  Auto-Lock, com 6 kg e encoder LPD3806 no tambor (DEC-026, Q-013); física,
  mecânica, circuito, BOM, firmware, painel, guia DIY, lista de compras e
  planilha do comprador refeitos
- [x] Firmware do MVP e projeto Wokwi (planta virtual, ponte sem
  relés, servo, NTP), testado fora do Wokwi com pinos simulados →
  `../03_SOFTWARE/firmware/` (HANDOFF-011, menos MQTT)
- [x] Painel Streamlit do MVP → `../03_SOFTWARE/dashboard/` (HANDOFF-012)
- [x] MQTT no firmware e fonte “ESP32 (MQTT)” no painel, com comandos e
  tarifas; leituras reais do INA219 e do encoder com `SIMULACAO 0`
  (DEC-023, HANDOFF-013). Testado fora do hardware
- [x] Passo a passo para gravar o ESP32 e ligar ao painel → `../DIY/`

## 🔄 EM ANDAMENTO
- Rodar o firmware dentro do Wokwi ou num ESP32 solto (`../DIY/`, parte A)
  e ver o painel ao vivo — Gabriel / DESENVOLVEDOR (HANDOFF-011 e 013)

## ❌ NÃO INICIADO
- Ensaio 0 da parafusadeira (HANDOFF-009) — não precisa de eletrônica e
  decide a compra do resto
- Desenho cotado e arquivos de corte/impressão (HANDOFF-010)

## ⚠️ ALERTAS
- O maior risco é a massa não descer sozinha: a margem estimada é ~1,7×
  (1,3 a 2,4) sobre o atrito do motor (I_0 ~1 A) e do redutor. Sem tirar a
  trava Auto-Lock ela não desce de jeito nenhum. Fazer o ensaio 0 antes de
  comprar a eletrônica.
- Os dados do motor (K_e, R_a, I_0, redução) são de um motor 550
  equivalente, não da Bosch. O ensaio 0 mede os quatro.
- O motor de 14,4 V roda na fonte de 12 V com o PWM limitado a 50 % pelo
  firmware. Ligado direto nos 12 V com a massa, ela subiria a ~0,5 m/s.
- A troca subir/gerar sem relé (DEC-017) é nova: provar com o motor girando
  à mão (ensaio 4) antes de pendurar massa.
- Todos os números (K_e, rendimentos, preços) são estimativas.

## PRÓXIMA AÇÃO RECOMENDADA
1. Preparar a parafusadeira (`../02_ARQUITETO/mecanica.md`), imprimir o
   tambor e fazer o ensaio 0 com 6 kg
2. Se descer: mandar a planilha ao comprador (eletrônica ≈ R$ 520)
3. Gabriel diz que máquinas o fablab tem (Q-010); ARQUITETO gera o desenho
   cotado e os arquivos de corte
