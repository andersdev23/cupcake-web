// ============================
//   SWEET BLOOM – JAVASCRIPT
// ============================

// Emojis dos produtos para o carrinho
const productEmojis = {
  'Cupcake Chocolate': '🍫',
  'Cupcake Morango': '🍓',
  'Cupcake Red Velvet': '❤️',
  'Cupcake Nutella': '🌰',
  'Cupcake Limão Siciliano': '🍋',
  'Cupcake Amendoim': '🥜',
};

// ---- CARRINHO (localStorage) ----

function getCart() {
  const data = localStorage.getItem('sweetbloom_cart');
  return data ? JSON.parse(data) : [];
}

function saveCart(cart) {
  localStorage.setItem('sweetbloom_cart', JSON.stringify(cart));
  updateCartBadge();
}

function updateCartBadge() {
  const cart = getCart();
  const total = cart.reduce((sum, item) => sum + item.qty, 0);
  const badges = document.querySelectorAll('#cartCount');
  badges.forEach(b => {
    b.textContent = total;
    b.style.display = total > 0 ? 'inline-flex' : 'none';
  });
}

function addToCart(name, price) {
  const cart = getCart();
  const existing = cart.find(i => i.name === name);
  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({ name, price, qty: 1 });
  }
  saveCart(cart);
  showToast(`✅ ${name} adicionado!`);
}

function removeFromCart(index) {
  const cart = getCart();
  cart.splice(index, 1);
  saveCart(cart);
  renderCart();
}

function changeQty(index, delta) {
  const cart = getCart();
  cart[index].qty += delta;
  if (cart[index].qty <= 0) {
    cart.splice(index, 1);
  }
  saveCart(cart);
  renderCart();
}

function clearCart() {
  localStorage.removeItem('sweetbloom_cart');
  updateCartBadge();
}

// ---- RENDER CART PAGE ----

function renderCart() {
  const cart = getCart();
  const listEl = document.getElementById('cartItemsList');
  const emptyEl = document.getElementById('cartEmpty');
  if (!listEl) return;

  if (cart.length === 0) {
    listEl.innerHTML = '';
    if (emptyEl) emptyEl.style.display = 'block';
    updateCartTotals(cart);
    return;
  }

  if (emptyEl) emptyEl.style.display = 'none';

  listEl.innerHTML = cart.map((item, i) => `
    <div class="cart-item">
      <span class="cart-item-emoji">${productEmojis[item.name] || '🧁'}</span>
      <div class="cart-item-info">
        <h4>${item.name}</h4>
        <span>R$ ${item.price.toFixed(2).replace('.', ',')} / un.</span>
      </div>
      <div class="cart-controls">
        <div class="cart-qty">
          <button class="qty-btn" onclick="changeQty(${i}, -1)">−</button>
          <span>${item.qty}</span>
          <button class="qty-btn" onclick="changeQty(${i}, 1)">+</button>
        </div>
        <span class="cart-item-price">R$ ${(item.price * item.qty).toFixed(2).replace('.', ',')}</span>
        <button class="remove-btn" onclick="removeFromCart(${i})" title="Remover">🗑️</button>
      </div>
    </div>
  `).join('');

  updateCartTotals(cart);
}

function updateCartTotals(cart) {
  const subtotal = cart.reduce((sum, i) => sum + i.price * i.qty, 0);
  const delivery = cart.length > 0 ? 5 : 0;
  const total = subtotal + delivery;

  const fmtBR = v => `R$ ${v.toFixed(2).replace('.', ',')}`;

  const sub = document.getElementById('subtotal');
  const del = document.getElementById('delivery');
  const tot = document.getElementById('totalPrice');
  if (sub) sub.textContent = fmtBR(subtotal);
  if (del) del.textContent = fmtBR(delivery);
  if (tot) tot.textContent = fmtBR(total);

  const btn = document.getElementById('checkoutBtn');
  if (btn) {
    btn.style.opacity = cart.length === 0 ? '0.4' : '1';
    btn.style.pointerEvents = cart.length === 0 ? 'none' : 'auto';
  }
}

// ---- RENDER CHECKOUT SUMMARY ----

function renderCheckoutSummary() {
  const cart = getCart();
  const listEl = document.getElementById('checkoutItems');
  if (!listEl) return;

  const fmtBR = v => `R$ ${v.toFixed(2).replace('.', ',')}`;

  listEl.innerHTML = cart.map(item => `
    <div class="checkout-item-row">
      <span>${productEmojis[item.name] || '🧁'} ${item.name} ×${item.qty}</span>
      <span>${fmtBR(item.price * item.qty)}</span>
    </div>
  `).join('') || '<p style="color:var(--gray);font-size:0.875rem;">Nenhum item no carrinho.</p>';

  const subtotal = cart.reduce((sum, i) => sum + i.price * i.qty, 0);
  const total = subtotal + (cart.length > 0 ? 5 : 0);

  const sub = document.getElementById('checkoutSubtotal');
  const tot = document.getElementById('checkoutTotal');
  if (sub) sub.textContent = fmtBR(subtotal);
  if (tot) tot.textContent = fmtBR(total);
}

// ---- CONFIRMAR PEDIDO ----

function confirmarPedido() {
  const nome     = document.getElementById('nome')?.value.trim();
  const tel      = document.getElementById('telefone')?.value.trim();
  const rua      = document.getElementById('rua')?.value.trim();
  const bairro   = document.getElementById('bairro')?.value.trim();
  const pagamento = document.querySelector('input[name="pagamento"]:checked')?.value;

  if (!nome || !tel || !rua || !bairro) {
    alert('⚠️ Por favor, preencha todos os campos obrigatórios (*).');
    return;
  }

  const cart = getCart();
  if (cart.length === 0) {
    alert('⚠️ Seu carrinho está vazio!');
    return;
  }

  const payLabels = {
    pix: 'PIX', cartao: 'Cartão de Crédito',
    dinheiro: 'Dinheiro', debito: 'Cartão de Débito'
  };

  const subtotal = cart.reduce((sum, i) => sum + i.price * i.qty, 0);
  const total = subtotal + 5;

  const modal = document.getElementById('successModal');
  const details = document.getElementById('modalDetails');

  details.innerHTML = `
    <p>👤 <strong>Nome:</strong> ${nome}</p>
    <p>📞 <strong>Telefone:</strong> ${tel}</p>
    <p>📍 <strong>Endereço:</strong> ${rua}, ${bairro}</p>
    <p>💳 <strong>Pagamento:</strong> ${payLabels[pagamento] || pagamento}</p>
    <p>💰 <strong>Total:</strong> R$ ${total.toFixed(2).replace('.', ',')}</p>
    <p style="margin-top:0.75rem;font-size:0.8rem;color:var(--gray);">Pedido #${Math.floor(Math.random()*9000)+1000} • ${new Date().toLocaleString('pt-BR')}</p>
  `;

  modal.style.display = 'flex';
}

// ---- TOAST ----

function showToast(msg) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2800);
}

// ---- MOBILE MENU ----

function toggleMenu() {
  const nav = document.getElementById('navLinks');
  if (nav) nav.classList.toggle('open');
}

// ---- INIT ----
document.addEventListener('DOMContentLoaded', () => {
  updateCartBadge();
});
