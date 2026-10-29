# MECÂNICA PARA FABLAB — MVP

Base: m_c = 2 kg (uma anilha), h = 1,70 m, motor de 6 V (DEC-024), sem talha
(DEC-025), cálculos em
`../01_FISICA/calculos_energia.md`. Nenhuma peça pede solda, torno ou
serralheria: tudo sai de corte a laser, impressão 3D, CNC router (opcional),
serra e furadeira.

## Arranjo
Mesmo princípio do projeto principal, em escala menor: duas colunas-guia, um
carrinho que corre entre elas e o motorredutor no topo enrolando o cordão,
que desce direto do tambor ao carrinho (sem talha, DEC-025).
A catraca é parte da mesma peça impressa do tambor.

```mermaid
flowchart TB
    subgraph TOPO["Placa do topo (compensado 15 mm)"]
        M["Motorredutor 6 V Ø 37 mm 1:90<br/>com encoder Hall"] --- T["Tambor Ø 30 mm + catraca Ø 50 mm<br/>(uma peça PETG)"]
        T --- R["Mancal com rolamento 608"]
        L["Lingueta + mola<br/>puxada pelo servo MG90S"] -.trava.- T
    end
    T -->|"cordão 2 mm, direto"| C["Carrinho com 4 rodas V<br/>+ anilha de 2 kg no pino central"]
    C -.corre entre.- G["2 colunas de perfil 2020 × 2,05 m"]
    G --- B["Base de compensado 18 mm 500 × 600 mm<br/>com lastro, topo preso à parede"]
```

## Peças e processo

| Peça | Especificação | Processo |
|------|---------------|----------|
| Colunas-guia | 2 × perfil de alumínio V-slot 20 × 20 × 2.050 mm | Serra; comprar barras de 3 m ou já cortadas |
| Travessas | 3 × perfil 2020 × 260 mm (topo, ~0,70 m e ~1,40 m), cantoneiras e porcas T M5 | Serra |
| Base | Compensado 18 mm, 500 × 600 mm | CNC router ou serra circular |
| Placa do topo | Compensado 15 mm, 300 × 150 mm, furos do motor, do mancal e da passagem do cordão | CNC router ou laser (se cortar 15 mm) |
| Mãos-francesas | 4 triângulos de MDF 6 mm unindo colunas e base | Laser |
| Carrinho | Compensado 15 mm, 260 × 220 mm, 4 rodas V-slot com espaçador excêntrico, pino central do diâmetro do furo da anilha (28 mm ou 25 mm) com trava e olhal no topo para amarrar o cordão | CNC ou serra + furadeira |
| Tambor + catraca | PETG 100 % de preenchimento nos dentes, Ø 28 mm no fundo do canal helicoidal (passo 2,5 mm, 60 mm úteis), catraca Ø 50 mm com 24 dentes, furo D 6 mm com parafuso M3 e porca embutida, pino de aço Ø 8 mm na outra ponta | Impressão 3D |
| Mancal do tambor | Rolamento 608 num suporte impresso parafusado à placa do topo | Impressão 3D |
| Suporte do motor | Suporte em L para motor de 37 mm (vem com o motor ou impresso), 6 × M3 | Comprado ou impresso |
| Lingueta | PETG, pivô em parafuso M4, mola de tração pequena puxando para a catraca; o servo puxa por um elo de arame 1 mm | Impressão 3D |
| Suportes dos fins de curso | PETG, presos no canal do perfil com porca T: a posição se ajusta deslizando | Impressão 3D |
| Caixa da eletrônica | MDF 3 mm com tampa de acrílico 3 mm | Laser |
| Cordão | Dyneema ou poliéster trançado 2 mm, ruptura ≥ 100 kg, ~3 m | Comprado |
| Massa | Uma anilha de 2 kg (já disponível) | — |
| Batente | EVA 20 mm na base, sob o carrinho | Estilete |

## Por que estas escolhas
- **Perfil 2020 em vez de metalon:** é guia e estrutura ao mesmo tempo, as
  rodas V correm direto nele, e os fins de curso deslizam no canal. Muitos
  fablabs têm sobras de impressoras 3D e CNCs.
- **Tambor no eixo do motor com mancal do outro lado:** dispensa eixo de aço,
  mancais UCP e acoplamento. O mancal 608 tira do redutor a carga radial do
  cordão (19,6 N).
- **Sem talha, tambor de Ø 30 mm:** com só 2 kg, o que falta é torque para
  o redutor retroacionar. Cordão direto e tambor de Ø 30 mm dão 0,294 N·m no
  tambor, o mesmo do porte anterior de 6 kg; com talha seriam 0,098 N·m e a
  massa provavelmente não desceria (C-104). Ainda tira uma polia e um
  rolamento da montagem.
- **Servo + mola no lugar do solenoide:** o servo de 5 V não precisa de
  MOSFET nem de hit-and-hold. A falha continua segura: sem energia no servo,
  a mola encosta a lingueta e a catraca segura a massa.

## Estrutura
- Carga no topo: ~20 N com 2 kg, ~40 N num tranco. Perfil 2020 de 2,05 m com
  as mãos-francesas e três travessas tem folga grande para isso; o que
  preocupa é tombar e flexionar, não quebrar.
- Tombamento: com a anilha no alto, o centro de massa passa de 1,8 m. Base
  de 500 × 600 mm com ~10 kg de lastro **e** a travessa do topo presa à
  parede por duas cantoneiras (a torre fica encostada numa parede do
  fablab). Sem parede, usar base de 800 × 800 mm como no projeto principal.

## Folgas obrigatórias
- **~1 cm acima do fim de curso superior.** A descida começa subindo 3 mm
  para aliviar a lingueta (mesma lógica da DEC-005 do projeto principal).
- Alturas: base 18 mm + batente 20 mm + carrinho com a anilha ~120 mm (olhal
  no topo do pino) na posição inferior; 1.700 mm de curso; 10 mm de folga;
  do olhal ao tambor ~180 mm. Fecha em ~2.050 mm, a altura das colunas.
- Conferir que a torre de ~2,1 m com o motor no topo passa no pé-direito e
  na porta do fablab.
- O desenho cotado sai do ARQUITETO (HANDOFF-010).

## Segurança
- Primeiros ciclos só com o carrinho, depois com uma anilha de 2 kg e corda de segurança.
- Ninguém com mão ou pé embaixo do carrinho; a área sob a torre fica livre.
- Conferir o cordão e os nós (tambor e olhal do carrinho) antes de cada sessão.
