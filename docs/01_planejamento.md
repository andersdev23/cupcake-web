# Planejamento e evolução

Autor: **Anderson Alves de Souza**. RGM: **37137794**. Instituição: **Universidade Positivo (UP)**. Tutora: **Fabiana Sabai Rodrigues Bastos**. Data: **17/11/2026**.

## Problema e continuidade do PI I

O autor confirmou que Sweet Bloom foi seu projeto do PI I. A base é o repositório `andersdev23/cupcake-web`, revisão `1c64815`: quatro páginas HTML, CSS e JavaScript, com catálogo e carrinho local, mas sem servidor, banco ou registro efetivo de encomendas. O PI II transforma essa confirmação demonstrativa em pedidos persistidos e acompanhados pela confeitaria.

## Objetivo e escopo

Aplicação web local com front-end HTML/CSS/JavaScript, back-end Python, SQLite e separação inspirada em MVC. O cliente registra uma encomenda e recebe seu número real; o administrador consulta pedidos, acompanha o andamento e mantém preços e disponibilidade dos seis sabores originais.

Não fazem parte desta versão: cobrança financeira, WhatsApp automático, rastreamento externo, cadastro de novos sabores, múltiplos funcionários, conta do cliente ou hospedagem pública de produção. A identidade rosa, marrom e creme e as páginas originais foram preservadas.

## Requisitos e aceitação

| ID | Requisito | Critério verificável |
|---|---|---|
| RF01 | Catálogo | Produtos ativos e preços consultados no banco |
| RF02 | Carrinho | Adicionar, alterar, remover e persistir entre páginas |
| RF03 | Orçamento | Total calculado no servidor com PIX e entrega |
| RF04 | Pedido | Dados validados e gravação atômica de pedido, itens e histórico |
| RF05 | Repetição | Mesma chave/corpo retorna mesmo pedido; corpo diferente gera conflito |
| RF06 | Administração | Sessão obrigatória para consultar dados pessoais |
| RF07 | Consulta | Busca por nome/número, filtro e paginação |
| RF08 | Andamento | Somente transições válidas, com histórico e controle de versão |
| RF09 | Catálogo administrativo | Editar preço/disponibilidade preservando pedidos anteriores |
| RNF01 | Consistência | Centavos inteiros, transações, chaves estrangeiras e restrições |
| RNF02 | Segurança local | SQL parametrizado, escape de saída, sessão, CSRF e bloqueio de arquivos privados |
| RNF03 | IHC | Rótulos, foco visível, estados vazios/erro e responsividade |
| RNF04 | Reprodução | Python sem bibliotecas externas; testes com bancos temporários |

## Regras e experiência

Quantidade inteira entre 1 e 99 por sabor, até 20 entradas distintas e 200 unidades por pedido. Produtos precisam estar ativos. Entrega de R$ 5,00; PIX desconta 5% dos produtos, arredondado ao centavo mais próximo. Selecionar pagamento não executa cobrança.

Andamento: Recebido -> Em preparo -> Saiu para entrega -> Entregue. Pode-se cancelar em Recebido ou Em preparo. Entregues e cancelados são finais e permanecem no histórico.

Os públicos são o cliente e o responsável pelo atendimento. A loja mantém navegação e vocabulário familiares. O checkout identifica campos opcionais, mostra valores antes da confirmação, bloqueia envio duplicado e apresenta recibo real. Mensagens permitem corrigir campos ou recuperar conexão. O painel privilegia lista, busca e status, sem expor encomendas publicamente.

## Evidências e limites

Implementação e verificações técnicas realizadas em 17/11/2026 com clientes fictícios. O autor informou que ainda não possui os cinco participantes exigidos. As avaliações e o vídeo continuam pendentes até sua realização; não foram criados depoimentos ou resultados presumidos.

Referência: `PITESoftwareII.pdf`, fornecido pelo autor. O enunciado contém orientações distintas para o vídeo (até cinco minutos e pelo menos cinco minutos); o roteiro propõe cinco minutos. Conferir o modelo de submissão no AVA e a orientação da tutora.
