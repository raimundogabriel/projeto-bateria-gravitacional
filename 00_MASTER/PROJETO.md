# PROJETO: Bateria Gravitacional + ESP32

## OBJETIVO
Protótipo didático de uma bateria gravitacional de baixo custo. O sistema
eleva uma massa de 20 kg por 1,70 m quando a tarifa de energia está baixa e
a desce quando a tarifa está alta, com o mesmo motorredutor funcionando como
gerador. Na descida, a energia gerada acende LEDs e alimenta uma porta USB
de 5 V, o bastante para um celular indicar carga enquanto a massa desce.
A decisão de subir, manter ou descer é tomada por um controlador de lógica
fuzzy no ESP32, e os dados vão a um painel remoto por MQTT.

O objetivo é demonstrar o conceito e a estratégia de decisão, não obter
economia: um ciclo armazena 333,5 J (0,093 Wh), e a eletrônica de controle
(~1 W) gasta isso em cerca de 6 minutos.

Trabalho da disciplina Sistemas Embarcados, Ciência da Computação,
Universidade Veiga de Almeida (Rio de Janeiro, 2026). Orientador: Prof.
Thiago Gabriel. Grupo: Gabriel dos Santos Raimundo, Jorge Rodrigues da Silva,
Cauã Felipe Batista Tito e Iasmim Kamilly A. Silva.

## ESCOPO
- ENTRA: protótipo funcional com massa de 20 kg e curso de 1,70 m (estrutura
  aguenta até 50 kg em ensaios futuros), um motorredutor 24 V como motor e
  gerador, saída USB + LEDs, controle fuzzy, proteções de carga suspensa,
  medição de energia real (INA226) e painel remoto
- ENTRA: simulação completa no Wokwi antes da montagem
- NÃO ENTRA: produção em escala industrial, certificação, comercialização,
  devolver energia à rede ou a uma bateria (a energia gerada é usada na USB e
  o excedente é dissipado no resistor de frenagem)

## MÉTRICAS DE SUCESSO
- Celular indica carga pela USB durante a descida no ponto de projeto
  (0,05 m/s, ~34 s, 4 a 5 W na porta)
- LED de geração acende em qualquer descida acima de ~0,01 m/s
- Eficiência de ida e volta medida no ramo de potência (estimativa: ~27 %;
  ver `01_FISICA/calculos_energia.md`)
- Velocidade de descida nunca passa de 0,10 m/s (proteção dispara antes)
- Painel recebe estado e energia a cada 30 s e cada decisão fuzzy no
  momento em que ocorre
- Custo do protótipo ≈ R$ 3.100 sem a massa (estimativa, não cotada)

## RESTRIÇÕES
- Orçamento: ≈ R$ 3.100 sem a massa (estimativa do dimensionamento; a
  eletrônica revisada sai por ≈ R$ 670 sem fonte e motorredutor)
- Espaço físico: torre de ~2,10 m de altura, base 0,80 × 0,80 m, parafusada
  ao piso ou lastreada
- Prazo: [a definir com o grupo]
- Componentes: preferência por disponíveis no Brasil (Mercado Livre,
  AliExpress)
- Segurança: montagem e testes supervisionados, em área isolada, fonte 24 V
  isolada da rede e, nos primeiros ciclos, massa presa por corda

## STACK TÉCNICA
- MCU: ESP32-WROOM-32 (DevKit V1), firmware C++ no ambiente Arduino
- Simulação: Wokwi (ESP32), em `03_SOFTWARE/firmware/wokwi/`
- Acionamento: motorredutor DC 24 V ~50 W, planetário 1:50 + driver BTS7960
- Dashboard: Python + Streamlit em `03_SOFTWARE/dashboard/` (DEC-013), hoje
  alimentado por um simulador da planta
- Comunicação: MQTT (broker Mosquitto), tópicos `grav/*`
- Sensores: encoder LPD3806-600BM no tambor, 3× INA226 (shunt 10 mΩ),
  2 fins de curso NF, RTC DS3231, sondagem de demanda USB
- Interface local: LCD 20×4 I²C, buzzer

## DOCUMENTOS DE REFERÊNCIA
- Original: `05_DOC_ORIGINAL/Documentacao_1_Integracao_Bateria_Gravitacional.pdf`
- Revisado (texto corrigido após a auditoria):
  `05_DOC_ORIGINAL/Documentacao_1_Integracao_Bateria_Gravitacional_v2.docx`
- Fontes de cada pasta: 01_FISICA (física e controle), 02_ARQUITETO
  (mecânica e circuitos), 03_SOFTWARE (firmware, dados e painel),
  04_AUDITORIA (inconsistências e questões abertas)
