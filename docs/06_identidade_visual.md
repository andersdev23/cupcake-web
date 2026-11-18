# Continuidade visual — Sweet Bloom no PI II

Registro da revisão de 17/11/2026. Esta entrega amplia a aplicação existente; não estabelece uma nova identidade nem substitui o sistema visual do PI I. O escopo e a preservação da marca estão registrados em `PRODUCT.md`.

## Base e extensão

| Elemento | Base em `css/style.css` | Extensão em `css/pi2.css` |
| --- | --- | --- |
| Marca e tipografia | Sweet Bloom; Playfair Display para títulos e marca; DM Sans para textos e controles | Mesmas famílias nos recibos, formulários e administração |
| Cores principais | Rosa `#e8677a`, rosa escuro `#c04f60`, marrom `#3d2114`, creme `#fdf6f0` | Rosa `#b64058`, rosa escuro `#8c2b40`; marrom e creme herdados |
| Texto secundário | Cinza `#6b7280` | Cinza `#59616d` |
| Formas | Cartões com raio de 18 px, campos com 10 px e botões principais arredondados | Novos painéis com raios de 12–16 px; ações secundárias com 8 px; botão principal herdado |

O rosa e o cinza foram escurecidos para favorecer a leitura. Essa diferença é uma adaptação funcional da paleta existente. As cores adicionais de sucesso e status distinguem situações de pedidos; não substituem as cores da marca. A administração usa maior densidade de informação, preservando fundo creme, superfícies brancas e texto marrom.

`css/fonts.css` declara arquivos locais de DM Sans (300–700) e Playfair Display (regular, itálico e negrito), com `font-display: swap`. Os arquivos e as licenças `DM-Sans-OFL.txt` e `Playfair-Display-OFL.txt` estão em `assets/fonts/`.

## Estados e adaptação

Checkout e administração carregam primeiro `css/style.css` e depois `css/pi2.css`. A extensão inclui foco visível, link de salto, mensagens de erro e sucesso, controles desabilitados, tratamento de textos longos e movimento reduzido. Há ajustes do painel em 900 e 600 px; no limite de 600 px, os campos usam texto de 16 px e os principais controles têm altura mínima de 44 px. São regras observadas no código, não uma certificação de acessibilidade.

## Evidência conferida

Foram lidos `PRODUCT.md`, `css/style.css`, `css/pi2.css`, `css/fonts.css`, `checkout.html` e `admin.html`, e conferida a presença dos arquivos de fontes e licenças. Foram inspecionadas visualmente as capturas existentes:

- `docs/evidencias/catalogo-desktop.png`: marca, títulos, cartões, rosa e fundo creme do catálogo.
- `docs/evidencias/checkout-mobile.png`: formulário em uma coluna, resumo, seleção de pagamento e ação principal.
- `docs/evidencias/admin-pedidos.png`: filtros, cartões de pedidos, status e continuidade tipográfica e cromática.

As capturas e o código conferidos sustentam a continuidade da identidade. As diferenças observadas são as adaptações de cor, raios e densidade descritas acima; nenhuma foi alterada por esta revisão documental. Não foi encontrado desvio material que exigisse substituir a identidade.

## Limites

Este registro descreve os arquivos e três capturas conferidos. Não representa teste em todos os navegadores, todas as larguras ou todos os estados possíveis. As demais imagens da pasta não foram revisadas nesta etapa. Não comprova avaliações com participantes, processamento financeiro ou disponibilidade pública. Nenhum arquivo da aplicação ou documento acadêmico anterior foi modificado nesta revisão; não foi criado um novo `DESIGN.md` para esta extensão de escopo localizado.
