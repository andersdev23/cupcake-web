# 🧁 Sweet Bloom – Loja de Cupcakes Artesanais

[AcessarSite](https://cupcake-web-eight.vercel.app/)

Projeto de mini loja online de cupcakes desenvolvido com HTML, CSS e JavaScript puro. Trabalho acadêmico de desenvolvimento web.

---

## 📁 Estrutura de Pastas

```
cupcake-web/
│
├── index.html        → Página inicial (Home)
├── produtos.html     → Catálogo de produtos com detalhes e tabela de preços
├── carrinho.html     → Carrinho de compras
├── checkout.html     → Finalização do pedido
│
├── css/
│   └── style.css     → Estilos globais (variáveis, layout, responsividade)
│
└── js/
    └── script.js     → Lógica do carrinho, formulário e interações
```

---

## 🚀 Como Executar

1. Baixe ou clone o projeto
2. Abra o arquivo `index.html` em qualquer navegador moderno
3. Nenhuma instalação ou servidor é necessário

> ✅ Funciona 100% offline — basta abrir o arquivo no navegador.

---

## 📄 Páginas

### 1. `index.html` — Home
- Nome e identidade da loja
- Hero animado com os sabores disponíveis
- Grid de produtos com botão "Adicionar ao Carrinho"
- Seção de diferenciais da loja

### 2. `produtos.html` — Produtos
- Cards detalhados com descrição e ingredientes de cada cupcake
- Tabela resumida com todos os preços
- Botão de compra em cada item

### 3. `carrinho.html` — Carrinho
- Lista de itens adicionados
- Controle de quantidade (+ / −)
- Cálculo automático do subtotal, entrega e total
- Botão para finalizar pedido

### 4. `checkout.html` — Finalizar Pedido
- Campos: nome, telefone, e-mail, endereço, complemento, CEP
- Seleção de forma de pagamento (PIX, Crédito, Débito, Dinheiro)
- Campo de observações
- Modal de confirmação com resumo do pedido

---

## ⚙️ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| Carrinho persistente | Usa `localStorage` — não perde os itens ao trocar de página |
| Contador na navbar | Atualiza em tempo real ao adicionar/remover itens |
| Controle de quantidade | Botões + e − com remoção automática ao chegar em zero |
| Cálculo de total | Subtotal + taxa de entrega fixa de R$ 5,00 |
| Validação de formulário | Verifica campos obrigatórios antes de confirmar |
| Toast notification | Notificação animada ao adicionar produto ao carrinho |
| Modal de confirmação | Exibe resumo completo do pedido após confirmar |
| Responsivo | Layout adaptado para desktop, tablet e celular |
| Menu mobile | Hambúrguer com navegação colapsável em telas pequenas |

---

## 🎨 Tecnologias Utilizadas

- **HTML5** — Estrutura semântica das páginas
- **CSS3** — Estilização com variáveis CSS, Grid, Flexbox e animações
- **JavaScript (ES6+)** — Lógica do carrinho, DOM e eventos
- **Google Fonts** — Playfair Display + DM Sans
- **localStorage** — Persistência do carrinho no navegador

> Sem frameworks, sem bibliotecas externas, sem backend.

---

## 🛍️ Produtos Disponíveis

| Sabor | Preço |
|---|---|
| 🍫 Cupcake Chocolate | R$ 12,00 |
| 🍓 Cupcake Morango | R$ 14,00 |
| ❤️ Red Velvet | R$ 15,00 |
| 🌰 Cupcake Nutella | R$ 16,00 |
| 🍋 Limão Siciliano | R$ 13,00 |
| 🥜 Cupcake Amendoim | R$ 13,00 |

---

## 👩‍💻 Autora

Desenvolvido como trabalho acadêmico.

**Sweet Bloom** – Cupcakes Artesanais · Curitiba, PR
