# Testes e resultados

Data de execução: **17/11/2026**. Ambiente: Windows, Python 3.14 e Google Chrome em modo headless. Dados e encomendas utilizados são fictícios. A automação do navegador não é uma avaliação por participante externo.

## Testes automatizados

Comando reproduzível: `python -m unittest discover -s tests -v`. Resultado observado: **15 testes executados, todos aprovados**. Cada teste utiliza banco temporário; a suíte inclui servidor HTTP em porta livre para integração.

| Grupo | Verificações realizadas |
|---|---|
| Catálogo | Carga inicial, alteração persistente e disponibilidade |
| Orçamento | Preços do servidor, PIX, arredondamento, dinheiro sem desconto |
| Validação | Quantidades inválidas, tipos incorretos, pagamento inválido e dados pessoais |
| Produtos | Carrinho vazio, produto inexistente ou inativo |
| Pedido | Criação, itens, histórico e repetição idempotente |
| Conflito | Mesma chave com conteúdo diferente retorna 409 |
| Transação | Falha não deixa registros parciais |
| Histórico financeiro | Preços antigos preservados após alteração de catálogo |
| Andamento | Transições válidas, estados finais e conflito de versão |
| Busca | Filtros, pesquisa e tratamento literal de curingas |
| Concorrência | Três solicitações simultâneas com a mesma chave criam um pedido |
| HTTP protegido | Login, sessão, CSRF e logout |
| Arquivos privados | GET e HEAD não expõem banco, senha, código ou .git |
| Origem/repetição HTTP | Origem externa recusada; criação 201 e repetição 200 |
| Tentativas de senha | Limite de tentativas de autenticação |

## Fluxo real no navegador

Uma sessão do Chrome foi automatizada contra servidor isolado na porta 8011 e banco de teste; o banco da demonstração principal não foi usado. Resultado: aprovado, sem exceções JavaScript observadas.

1. Adicionar Chocolate e Morango; aumentar Chocolate para duas unidades.
2. Conferir subtotal R$ 38,00 e total sem PIX R$ 43,00.
3. Impedir confirmação com nome obrigatório vazio.
4. Preencher cliente/endereço fictícios; alternar dinheiro e PIX.
5. Confirmar PIX: desconto R$ 1,90, entrega R$ 5,00 e total R$ 41,10.
6. Registrar pedido, mostrar recibo persistido e limpar carrinho.
7. Autenticar administrador; localizar pedido e mudar para Em preparo.
8. Alterar preço de Chocolate para R$ 12,50 no banco isolado.
9. Buscar termo sem resultados e apresentar estado vazio; encerrar sessão.
10. Conferir carrinho vazio com finalização bloqueada.
11. Simular falha da API: mensagem de erro, tentativa novamente e compra desabilitada.
12. Verificar ausência de transbordamento horizontal em checkout e painel nas larguras 320, 390 e 768 px; catálogo em 320, 390, 768 e 1440 px.

Capturas em `docs/evidencias/`: checkout desktop/mobile, recibo, pedidos desktop/mobile, catálogo administrativo, catálogo da loja e erro de conexão. O script temporário de automação depende da instalação local do Playwright usada na validação; as capturas são as evidências versionadas e a suíte Python é reproduzível sem dependências externas.

## Correções decorrentes da validação técnica

- Restrições de arquivos estáticos também aplicadas às requisições HEAD.
- Validação de pagamento/status com tipos incorretos, sem erro interno não tratado.
- Corpo JSON com tamanho inválido retorna erro apropriado.
- Botão de produto recupera seu texto ao voltar à disponibilidade.
- Opções de pagamento permanecem acessíveis ao teclado, com foco visual.
- Conexões SQLite fechadas após cada operação; exclusividade de porta no Windows.

## Avaliação externa

**Pendente.** O autor informou que ainda não reuniu os cinco participantes. Não há nomes, opiniões, estatísticas ou sugestões externas coletadas. Os formulários estão preparados separadamente. Depois da coleta, registrar resultados, sugestões, correções adotadas e evidências no relatório consolidado. Os resultados técnicos acima não substituem esse requisito.
