# COMO INVOCAR AS SKILLS

Cole no início da mensagem a persona desejada. Cada persona tem uma pasta
própria e lê os arquivos das outras como entrada.

| Persona | Responde por | Escreve em | Lê de |
|---------|--------------|------------|-------|
| FÍSICO | Premissas, equações, energia, eficiência, lógica fuzzy, validação dos ensaios | `01_FISICA/` | `00_MASTER/`, dados medidos |
| ARQUITETO | Mecânica, estrutura, circuitos de potência e lógica, pinagem, BOM, sequências de operação | `02_ARQUITETO/` | `01_FISICA/premissas.md`, `00_MASTER/DECISOES.md` |
| DESENVOLVEDOR | Firmware ESP32, simulação Wokwi, contrato de dados MQTT, dashboard | `03_SOFTWARE/` | `02_ARQUITETO/circuitos/`, `01_FISICA/algoritmos_controle.md` |

Qualquer persona que encontrar uma contradição registra em
`04_AUDITORIA/inconsistencias.md`; dúvidas que só o grupo responde vão para
`04_AUDITORIA/questoes_abertas.md`.

## FÍSICO
> "Ative o FÍSICO. Leia `00_MASTER/ESTADO_ATUAL.md`,
> `00_MASTER/HANDOFF.md` e `01_FISICA/premissas.md`. Preciso que você [tarefa]."

## ARQUITETO
> "Ative o ARQUITETO. Leia `00_MASTER/ESTADO_ATUAL.md`, 
> `00_MASTER/DECISOES.md` e `01_FISICA/premissas.md`. 
> Preciso que você [tarefa]."

## DESENVOLVEDOR
> "Ative o DESENVOLVEDOR. Leia `00_MASTER/ESTADO_ATUAL.md`, 
> `03_SOFTWARE/contrato_dados.md`, `03_SOFTWARE/pinagem_esp32.md` e
> `02_ARQUITETO/circuitos/`. Preciso que você [tarefa]."

## REGRA UNIVERSAL
Ao terminar qualquer tarefa, a skill DEVE:
1. Atualizar `00_MASTER/ESTADO_ATUAL.md`
2. Registrar decisões em `00_MASTER/DECISOES.md`
3. Criar/atualizar handoffs em `00_MASTER/HANDOFF.md`
4. Escrever sua entrega na pasta própria (01_, 02_ ou 03_)
5. Usar os nomes de `00_MASTER/GLOSSARIO.md`
