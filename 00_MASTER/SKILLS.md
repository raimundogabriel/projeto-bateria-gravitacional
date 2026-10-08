# COMO INVOCAR AS SKILLS

Cole no início da mensagem a persona desejada. Exemplos:

## FÍSICO
> "Ative o FÍSICO. Leia `00_MASTER/ESTADO_ATUAL.md` e 
> `00_MASTER/HANDOFF.md`. Preciso que você [tarefa]."

## ARQUITETO
> "Ative o ARQUITETO. Leia `00_MASTER/ESTADO_ATUAL.md`, 
> `00_MASTER/DECISOES.md` e `01_FISICA/premissas.md`. 
> Preciso que você [tarefa]."

## DESENVOLVEDOR
> "Ative o DESENVOLVEDOR. Leia `00_MASTER/ESTADO_ATUAL.md`, 
> `03_SOFTWARE/contrato_dados.md` e `02_ARQUITETURA/circuitos/`. 
> Preciso que você [tarefa]."

## REGRA UNIVERSAL
Ao terminar qualquer tarefa, a skill DEVE:
1. Atualizar `00_MASTER/ESTADO_ATUAL.md`
2. Registrar decisões em `00_MASTER/DECISOES.md`
3. Criar/atualizar handoffs em `00_MASTER/HANDOFF.md`
4. Escrever sua entrega na pasta própria (01_, 02_ ou 03_)