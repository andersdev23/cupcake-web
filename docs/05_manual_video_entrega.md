# Manual, vídeo e entrega

## Iniciar

1. No terminal da pasta sweet-bloom-pi2, execute `python app.py`. O README contém o caminho alternativo do Python instalado.
2. Abra <http://127.0.0.1:8010/> e mantenha o terminal aberto.
3. Leia a senha em `data/admin-password.txt` e entre em <http://127.0.0.1:8010/admin.html>.
4. Não exponha a senha ou dados pessoais no vídeo/GitHub. Use dados fictícios.

127.0.0.1 funciona somente no computador que executa o servidor. Para teste remoto, os colegas precisam executar o projeto ou usar hospedagem adequada. O endereço antigo da Vercel não executa a nova API Python.

## Cliente

Adicione sabores na página inicial ou em Produtos. No Carrinho, aumente/diminua quantidades ou remova. Em Finalizar pedido, preencha nome, telefone, rua/número e bairro. E-mail, CEP, complemento e observações são opcionais. Selecione pagamento, confira resumo e registre. PIX dá 5% de desconto nos produtos; a entrega é R$ 5,00. O site não processa cobrança.

Após sucesso, o recibo mostra o número salvo e o carrinho é limpo. Se houver falha de conexão, mantenha a página aberta, restaure o servidor e tente novamente. A repetição na mesma página usa a mesma chave. Recarregar/fechar a página após resposta incerta perde a chave em memória; consulte o painel antes de refazer o pedido.

## Administrador

Em Pedidos, busque nome/número, filtre status, atualize a lista e consulte o histórico. Escolha próximo status e use Atualizar pedido. Cancelamento requer confirmação e só é possível antes da saída para entrega. Em conflito de versão, recarregue a lista.

Em Catálogo, altere preço e/ou disponibilidade e use Salvar produto. Novos orçamentos usam os valores atuais; pedidos anteriores permanecem iguais. Não existe inclusão de sabores nesta versão. Use Sair ao concluir.

## Recuperação

- Porta ocupada: encerre o terminal deste servidor ou use `python app.py --port 8012`.
- Catálogo não carrega: confira servidor ativo e URL/porta corretos.
- Senha: consulte arquivo local ou configure SWEETBLOOM_ADMIN_PASSWORD e reinicie.
- Backup: encerre servidor e copie data/sweetbloom.sqlite3 para local privado.
- Não publique data/. Hospedagem pública exige HTTPS, servidor apropriado, backups e configuração de acesso.

## Roteiro narrado de cinco minutos

| Tempo | Mostrar e explicar |
|---|---|
| 00:00-00:25 | Nome, RGM, instituição, Sweet Bloom e continuidade do PI I |
| 00:25-00:55 | Problema da loja estática e objetivo da evolução |
| 00:55-02:05 | Catálogo, carrinho, dados fictícios, PIX/dinheiro, registro e número real |
| 02:05-03:00 | Painel, busca, status, histórico e edição de preço; ocultar senha |
| 03:00-03:40 | Arquitetura MVC/camadas, modelo relacional e banco SQLite |
| 03:40-04:10 | Executar testes e mostrar validação de campo/erro controlado |
| 04:10-04:45 | Cinco avaliações reais e correções, se coletadas; declarar pendência caso não realizadas |
| 04:45-05:00 | Repositório, documentação, limite do pagamento sem cobrança e encerramento |

O enunciado apresenta limites diferentes de duração; cinco minutos é o ponto comum. Confirme no AVA. Grave com ferramenta disponível e assista ao arquivo antes de enviar para verificar áudio e legibilidade.

## Avaliações e entrega

Use o convite e formulário de `03_formulario_avaliacao.md` para cinco pessoas reais. Recolha nome, perfil, data, funções que funcionaram/falharam/não foram testadas e justificativas. Consolide em PDF com sugestões, evidências e correções realmente adotadas. Não preencha resultados em nome dos participantes.

- [ ] Conferir modelo oficial e campos do AVA.
- [ ] Testar compra e painel e rodar os testes automatizados.
- [ ] Revisar identificação e modelagem.
- [ ] Coletar cinco avaliações reais e consolidar PDF.
- [ ] Gravar e assistir ao vídeo narrado.
- [ ] Enviar código/documentação ao GitHub e verificar o link.
- [ ] Anexar relatório, avaliações e vídeo/links conforme o AVA.
- [ ] Confirmar envio antes das 23:00 e guardar comprovante.

Código e documentação não substituem submissão, avaliações ou gravação. A versão estática da Vercel não é automaticamente a evolução Python.
