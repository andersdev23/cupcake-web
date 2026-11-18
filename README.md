# Sweet Bloom - Projeto Integrador II

**Anderson Alves de Souza · RGM 37137794 · Universidade Positivo (UP)**
**Tutora:** Fabiana Sabai Rodrigues Bastos.

Evolução do Sweet Bloom entregue no PI I. A loja estática agora tem servidor Python, SQLite, registro real de pedidos, administração autenticada, validação, histórico e testes.

## Executar

Requer Python 3.10+. Não exige pip, Node ou instalação de banco. No terminal desta pasta:

No Windows, também é possível dar dois cliques em `iniciar.cmd`.

```powershell
python app.py
```

Se `python` abrir a Microsoft Store, nesta máquina use:

```powershell
& 'C:\Users\ander\AppData\Local\Programs\Python\Python314\python.exe' app.py
```

- Loja: <http://127.0.0.1:8010/>
- Painel: <http://127.0.0.1:8010/admin.html>
- Senha: arquivo local `data/admin-password.txt`, gerado no primeiro início.
- Consultar senha: `python app.py --show-admin-password`.
- Encerrar: Ctrl+C no terminal do servidor.

Abra pelo servidor Python. Duplo clique no HTML ou Live Server não executam a API. O endereço <https://cupcake-web-eight.vercel.app/> ainda corresponde à versão estática do PI I. Publicar esta evolução exige hospedagem Python com armazenamento persistente.

## Funcionalidades

Catálogo com seis sabores; carrinho persistente; cadastro de destinatário/endereço; cálculo de valores no servidor; registro transacional; recibo com número real; painel com sessão, busca, filtros, paginação, histórico e atualização de status; edição de preços e disponibilidade.

Valores são guardados em centavos. Entrega: R$ 5,00. PIX: desconto de 5% sobre os produtos. Pedidos anteriores preservam os preços praticados. A chave de idempotência evita duplicação na repetição da mesma solicitação. Controle de versão identifica conflitos administrativos.

O pagamento é **apenas registrado para combinar com a loja**. Não há cobrança, integração WhatsApp, cadastro de novos sabores ou múltiplos funcionários. O servidor usa 127.0.0.1 e destina-se à demonstração local; publicação pública exige infraestrutura e configuração próprias.

## Testar

```powershell
python -m unittest discover -s tests -v
```

São 15 testes de regras, persistência, concorrência e HTTP, usando bancos temporários e dados fictícios. Capturas adicionais do navegador: `docs/evidencias/`.

## Estrutura

| Caminho | Responsabilidade |
|---|---|
| app.py | Inicialização e configuração |
| backend/models.py | Banco, esquema físico e consultas |
| backend/services.py | Regras e transações |
| backend/controllers.py | HTTP, autenticação e respostas |
| *.html, css/, js/ | Vistas da loja e administração |
| tests/ | Testes automatizados |
| docs/ | Documentação acadêmica |
| data/ | Banco e senha locais, ignorados no Git |

Configuração opcional: `SWEETBLOOM_ADMIN_PASSWORD` (mínimo oito caracteres), `SWEETBLOOM_DB` (caminho do banco) e `python app.py --port 8012`. Não publique a pasta data. Faça backup do banco com o servidor encerrado.

As fontes da interface estão incluídas localmente, com licenças OFL em assets/fonts. Para gerar novamente os PDFs (opcional), instale `reportlab` e execute `python scripts/gerar_documentos.py`; isso não é necessário para executar a aplicação ou seus testes.

## Documentação e entrega

1. [Planejamento](docs/01_planejamento.md)
2. [UML, banco e dicionário](docs/02_modelagem.md)
3. [Formulário para cinco avaliadores](docs/03_formulario_avaliacao.md)
4. [Testes e resultados](docs/04_testes_resultados.md)
5. [Manual, vídeo e checklist](docs/05_manual_video_entrega.md)
6. [Continuidade visual](docs/06_identidade_visual.md)
7. [Matriz de atendimento ao enunciado](docs/07_matriz_enunciado.md)

PDFs preparados: [relatório técnico](output/pdf/relatorio_tecnico_sweet_bloom_pi2.pdf) e [formulários preenchíveis para cinco participantes](output/pdf/formularios_cinco_avaliadores.pdf). Os formulários estão em branco; preenchê-los e salvar após os testes reais.

**Pendências humanas:** cinco avaliações reais, consolidação em PDF e vídeo narrado. Formulários vazios e testes automatizados não substituem as avaliações. Conferir o modelo oficial no AVA.

Origem: <https://github.com/andersdev23/cupcake-web>, revisão `1c64815`. Branch local: `pi2/evolucao-sweet-bloom`. A branch local não significa que as alterações foram enviadas ao GitHub.
