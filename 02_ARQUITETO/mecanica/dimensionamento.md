# DIMENSIONAMENTO MECÂNICO

Base: m_c = 20 kg, h = 1,70 m (DEC-001); cálculos em
`01_FISICA/calculos_energia.md`. A mecânica aguenta até 50 kg sem mudanças.

## Arranjo
Torre de 2 colunas-guia. O carrinho com a massa corre entre elas sobre
rolamentos. No topo, o tambor acoplado ao motorredutor enrola o cabo; a talha
2:1 (uma ponta do cabo fixa no topo, polia móvel no carrinho, outra ponta no
tambor) divide a tração por dois. A roda de catraca fica no eixo do tambor.

## Componentes

| Item | Especificação | Observação |
|------|---------------|------------|
| Motorredutor | DC escovado 24 V, ~50 W, 3.000 rpm, planetário 1:50 (1:40 a 1:60), ≥ 6 N·m nominal, eixo 12 mm | Sobe e gera (DEC-003). **Nunca sem-fim**: é autotravante e impede a descida |
| Talha 2:1 | Ponta fixa no topo + polia móvel no carrinho | Tambor enrola 3,40 m de cabo |
| Tambor | Ø 60 × 80 mm, alumínio ou nylon usinado, canal helicoidal passo 3,5 mm | 18 voltas úteis + 3 mortas, camada única |
| Cabo de aço | 3 mm, 7×19, ruptura ~5 kN | Fator de segurança ~50 com 20 kg; relação tambor/cabo 20 |
| Polias | 2 de cabo com rolamento, Ø ≥ 60 mm | Uma guia no topo, uma móvel no carrinho |
| Eixo do tambor | Aço 1045 Ø 20 × 300 mm, 2 mancais UCP204, acoplamento rígido 12 → 20 mm com chaveta | |
| Trava de catraca | Roda de catraca no eixo do tambor + lingueta puxada por solenoide 24 V push-pull, curso 10 mm, ≥ 10 N | Sem energia, a lingueta cai e segura a massa (DEC-005) |
| Encoder | LPD3806-600BM no eixo do tambor, acoplamento ou correia 1:1 | Mede no tambor, não no motor |
| Carrinho | Bandeja com pino central para anilhas + 8 rolamentos 608 nas faces das colunas | |
| Estrutura | Metalon 30 × 30 × 1,2 mm soldado: 2 colunas de 2,10 m, base 0,80 × 0,80 m, travamento diagonal | DEC-012 |
| Massa | 20 kg em anilhas ou sacos de areia | |
| Fins de curso | 2 microchaves com rolete, NF; inferior em h = 0, superior em h = 1,70 m | Opcional: 3ª chave no topo cortando o EN do BTS7960 |

## Estrutura de sustentação
- Com a talha 2:1, a travessa superior recebe o peso inteiro: 196 N com 20 kg,
  392 N num tranco ou parada brusca.
- Com 392 N no meio do vão de 0,80 m, o metalon 30 × 30 × 1,2 mm chega a
  61 MPa, cerca de 4× abaixo do escoamento do aço (250 MPa).
- Colunas de 2,10 m: carga crítica de flambagem ~8,6 kN cada, muito acima da
  carga.
- Base parafusada ao piso ou lastreada (tombamento).
- Acima de 50 kg: travessa superior em 50 × 50 × 2 mm.

## Folgas obrigatórias
- **~2 cm de folga mecânica acima do fim de curso superior.** A descida
  começa subindo 3 mm para aliviar a lingueta (DEC-005); sem a folga, a massa
  no topo nunca desce.
- Batente de borracha no fundo do curso e área isolada abaixo do carrinho.
- Desenho cotado da torre (posição real dos fins de curso, altura do
  carrinho, tambor e polias dentro dos 2,10 m) ainda falta: HANDOFF-007.

## Segurança e manutenção
- Primeiros ciclos com a massa presa por corda de segurança.
- Inspecionar cabo e clipes antes de cada sessão; trocar o cabo ao primeiro
  fio partido.

## BOM mecânica (preços aproximados, de memória, não cotados)

| Item | Qtd | R$ |
|------|-----|-----|
| Motorredutor 24 V 50 W planetário 1:50, ≥ 6 N·m | 1 | 450 (350 a 600) |
| Metalon 30×30×1,2 (4 barras de 6 m), chapas e solda | 1 conj. | 910 |
| Solenoide push-pull 24 V + catraca e lingueta cortadas | 1 conj. | 180 |
| Eixo 1045 Ø 20 × 300 + 2 UCP204 + acoplamento | 1 conj. | 160 |
| Tambor Ø 60 × 80 usinado | 1 | 150 |
| Carrinho (chapa, 8 rolamentos 608, pino) | 1 | 150 |
| Parafusos, pintura, fixações | 1 conj. | 100 |
| Polia de cabo com rolamento Ø ≥ 60 mm | 2 | 60 |
| Cabo 3 mm 7×19 10 m + 4 clipes + 2 sapatilhas + esticador | 1 conj. | 60 |
| Anilhas 20 kg (opcional; emprestadas = 0, areia ~30) | 20 kg | 250 a 350 |

Total do protótipo ≈ R$ 3.100 sem a massa (mecânica ≈ R$ 1.770 + motorredutor
≈ R$ 450 + eletrônica; ver `02_ARQUITETO/circuitos/esquema_potencia.md`).
