// Sweet Bloom PI II: catálogo e totais são validados pelo servidor.
'use strict';
const $ = selector => document.querySelector(selector);
const money = cents => (Number(cents) / 100).toLocaleString('pt-BR', {style:'currency',currency:'BRL'});
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let catalog = [];
let catalogLoaded = false;
let submitting = false;
let quoteVersion = 0;
let currentQuote = null;
let toastTimer;
let retryPayload = null;
const productEmojis = {'Cupcake Chocolate':'🍫','Cupcake Morango':'🍓','Cupcake Red Velvet':'❤️','Cupcake Nutella':'🌰','Cupcake Limão Siciliano':'🍋','Cupcake Amendoim':'🥜'};

async function api(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(path, {...options, signal:controller.signal, headers:{'Content-Type':'application/json',...options.headers}});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Não foi possível concluir a solicitação.');
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('A conexão demorou. Tente novamente; o mesmo pedido não será duplicado.');
    if (error instanceof TypeError || error instanceof SyntaxError) throw new Error('Não foi possível acessar a loja. Verifique o servidor e tente novamente.');
    throw error;
  } finally { clearTimeout(timer); }
}

function banner(message, retry = false) {
  let element = $('#service-message');
  if (!element) {
    element = document.createElement('div');
    element.id = 'service-message'; element.className = 'service-message'; element.setAttribute('role','alert');
    $('.navbar').insertAdjacentElement('afterend', element);
  }
  element.replaceChildren(document.createTextNode(message + ' '));
  if (retry) {
    const button = document.createElement('button'); button.textContent = 'Tentar novamente';
    button.className = 'btn-secondary'; button.addEventListener('click', loadCatalog);
    element.append(button);
  }
  element.hidden = !message;
}

function getCart() {
  try {
    const data = JSON.parse(localStorage.getItem('sweetbloom_cart') || '[]');
    if (!Array.isArray(data)) throw new Error();
    return data.filter(item => item && typeof item.name === 'string' && item.name.length <= 120 &&
      Number.isInteger(item.qty) && item.qty >= 1 && item.qty <= 99).map(item => {
      const product = catalog.find(product => product.name === item.name || product.id === item.product_id);
      return {name:product ? product.name : item.name, product_id:product ? product.id : item.product_id,
        price:product ? product.price_cents / 100 : Number(item.price || 0), qty:item.qty, unavailable:catalogLoaded && !product};
    });
  } catch {
    banner('O carrinho salvo não pôde ser lido. Adicione novamente os produtos desejados.');
    return [];
  }
}

function saveCart(cart) {
  try { localStorage.setItem('sweetbloom_cart', JSON.stringify(cart)); updateCartBadge(); return true; }
  catch { banner('O navegador não permitiu salvar o carrinho. Libere o armazenamento local para continuar.'); return false; }
}

function updateCartBadge() {
  const count = getCart().reduce((sum, item) => sum + item.qty, 0);
  document.querySelectorAll('#cartCount').forEach(element => {
    element.textContent = count; element.style.display = count ? 'inline-flex' : 'none';
  });
}

function addToCart(name) {
  if (!catalogLoaded) { banner('Aguarde o catálogo carregar ou use “Tentar novamente”.', true); return; }
  const product = catalog.find(product => product.name === name);
  if (!product) { showToast('Esse produto está indisponível.'); return; }
  const cart = getCart();
  const existing = cart.find(item => item.product_id === product.id);
  if (existing && existing.qty >= 99) { showToast('O limite é de 99 unidades por produto.'); return; }
  if (existing) existing.qty++;
  else cart.push({name:product.name,product_id:product.id,price:product.price_cents / 100,qty:1});
  if (saveCart(cart)) showToast(product.name + ' adicionado ao carrinho.');
}

function removeFromCart(index) {
  const cart = getCart();
  if (!cart[index]) return;
  cart.splice(index, 1); if (saveCart(cart)) refreshCartViews();
}

function changeQty(index, delta) {
  const cart = getCart();
  if (!cart[index] || ![-1,1].includes(delta)) return;
  const quantity = cart[index].qty + delta;
  if (quantity > 99) { showToast('O limite é de 99 unidades por produto.'); return; }
  if (quantity <= 0) cart.splice(index, 1);
  else cart[index].qty = quantity;
  if (saveCart(cart)) refreshCartViews();
}

function clearCart() {
  try { localStorage.removeItem('sweetbloom_cart'); updateCartBadge(); } catch {}
}

function renderCart() {
  const list = $('#cartItemsList');
  if (!list) return;
  const cart = getCart();
  $('#cartEmpty').hidden = cart.length > 0;
  $('#cartEmpty').style.display = cart.length ? 'none' : 'block';
  list.innerHTML = cart.map((item, index) => '<div class="cart-item"><span class="cart-item-emoji" aria-hidden="true">' +
    (productEmojis[item.name] || '🧁') + '</span><div class="cart-item-info"><h4>' + esc(item.name) +
    '</h4><span>' + (item.unavailable ? 'Indisponível — remova para continuar' : money(Math.round(item.price * 100)) + ' / un.') +
    '</span></div><div class="cart-controls"><div class="cart-qty"><button type="button" class="qty-btn" onclick="changeQty(' +
    index + ',-1)" aria-label="Diminuir quantidade de ' + esc(item.name) + '">−</button><span>' + item.qty +
    '</span><button type="button" class="qty-btn" onclick="changeQty(' + index + ',1)" aria-label="Aumentar quantidade de ' +
    esc(item.name) + '">+</button></div><span class="cart-item-price">' + money(Math.round(item.price * 100) * item.qty) +
    '</span><button type="button" class="remove-btn" onclick="removeFromCart(' + index + ')" aria-label="Remover ' +
    esc(item.name) + '">Remover</button></div></div>').join('');
  updateCartTotals(cart);
}

function updateCartTotals(cart) {
  const subtotal = cart.reduce((sum, item) => sum + Math.round(item.price * 100) * item.qty, 0);
  if ($('#subtotal')) $('#subtotal').textContent = money(subtotal);
  if ($('#delivery')) $('#delivery').textContent = money(cart.length ? 500 : 0);
  if ($('#totalPrice')) $('#totalPrice').textContent = money(subtotal + (cart.length ? 500 : 0));
  const disabled = !catalogLoaded || !cart.length || cart.some(item => item.unavailable);
  if ($('#checkoutBtn')) {
    $('#checkoutBtn').setAttribute('aria-disabled', String(disabled));
    $('#checkoutBtn').classList.toggle('is-disabled', disabled);
    $('#checkoutBtn').tabIndex = disabled ? -1 : 0;
  }
}

async function renderCheckoutSummary() {
  if (!$('#checkoutItems')) return;
  const version = ++quoteVersion;
  const cart = getCart();
  currentQuote = null;
  $('#confirm-order').disabled = true;
  $('#checkoutItems').innerHTML = cart.map(item => '<div class="checkout-item-row"><span>' + esc(item.name) +
    ' ×' + item.qty + '</span><span>' + money(Math.round(item.price * 100) * item.qty) + '</span></div>').join('') ||
    '<p>Seu carrinho está vazio. <a href="produtos.html">Escolher produtos</a></p>';
  for (const id of ['checkoutSubtotal','checkoutDiscount','checkoutTotal']) $('#' + id).textContent = '—';
  if (!catalogLoaded) return;
  if (!cart.length || cart.some(item => item.unavailable)) {
    $('#checkout-error').textContent = cart.length ? 'Há produto indisponível. Revise o carrinho.' : 'Adicione um produto antes de registrar o pedido.';
    $('#checkout-error').hidden = false; return;
  }
  try {
    const quote = await api('/api/quote', {method:'POST',body:JSON.stringify({
      items:cart.map(item => ({product_id:item.product_id,quantity:item.qty})),
      payment:document.querySelector('[name="pagamento"]:checked').value
    })});
    if (version !== quoteVersion) return;
    currentQuote = quote;
    $('#checkoutSubtotal').textContent = money(quote.subtotal_cents);
    $('#checkoutDiscount').textContent = '− ' + money(quote.discount_cents);
    $('#checkoutTotal').textContent = money(quote.total_cents);
    $('#checkout-error').hidden = true;
    $('#confirm-order').disabled = submitting;
  } catch (error) {
    if (version !== quoteVersion) return;
    $('#checkout-error').textContent = error.message + ' Use “Atualizar valores” para tentar novamente.';
    $('#checkout-error').hidden = false;
  }
}

function refreshCartViews() {
  updateCartBadge(); renderCart();
  if ($('#checkoutItems')) renderCheckoutSummary();
}

async function loadCatalog() {
  try {
    const data = await api('/api/products');
    catalog = data.products; catalogLoaded = true;
    banner('');
    document.querySelectorAll('[data-product-name]').forEach(button => {
      if (!button.dataset.originalLabel) button.dataset.originalLabel = button.textContent;
      const product = catalog.find(product => product.name === button.dataset.productName);
      button.disabled = !product;
      if (!product) { button.textContent = 'Indisponível'; return; }
      button.textContent = button.dataset.originalLabel;
      const card = button.closest('.product-card, .product-detail-card, tr');
      const price = card && card.querySelector('.price, .price-big, td:nth-child(3)');
      if (price) price.textContent = money(product.price_cents);
    });
    refreshCartViews();
  } catch (error) {
    catalogLoaded = false;
    document.querySelectorAll('[data-product-name]').forEach(button => { button.disabled = true; });
    banner(error.message, true);
    updateCartTotals(getCart());
  }
}

async function confirmarPedido(event) {
  if (event) event.preventDefault();
  if (submitting || !currentQuote || !$('#checkout-form').reportValidity()) return;
  const cart = getCart();
  const payload = {
    customer:{name:$('#nome').value.trim(),phone:$('#telefone').value.trim(),email:$('#email').value.trim()},
    address:{street:$('#rua').value.trim(),neighborhood:$('#bairro').value.trim(),postal_code:$('#cep').value.trim(),complement:$('#complemento').value.trim()},
    payment:document.querySelector('[name="pagamento"]:checked').value,
    notes:$('#obs').value.trim(),
    items:cart.map(item => ({product_id:item.product_id,quantity:item.qty}))
  };
  const serialized = JSON.stringify(payload);
  if (!retryPayload || retryPayload.body !== serialized) retryPayload = {body:serialized,key:crypto.randomUUID()};
  submitting = true;
  const button = $('#confirm-order'); button.disabled = true; button.textContent = 'Registrando pedido…';
  $('#checkout-error').hidden = true;
  try {
    const {order} = await api('/api/orders', {method:'POST',headers:{'Idempotency-Key':retryPayload.key},body:serialized});
    $('#receipt-title').textContent = 'Pedido #' + String(order.id).padStart(5,'0') + ' registrado';
    $('#receipt-details').innerHTML = '<p><strong>Cliente:</strong> ' + esc(order.recipient_name) +
      '</p><p><strong>Entrega:</strong> ' + esc(order.street) + ', ' + esc(order.neighborhood) +
      '</p><p><strong>Total confirmado:</strong> ' + money(order.total_cents) +
      '</p><p><strong>Status:</strong> Recebido</p><p>O pedido foi gravado. A forma de pagamento será combinada com a loja; o site não realiza cobranças.</p>';
    $('#order-receipt').hidden = false;
    $('#checkout-workspace').hidden = true;
    $('#receipt-title').focus();
    clearCart();
    retryPayload = null;
  } catch (error) {
    $('#checkout-error').textContent = error.message; $('#checkout-error').hidden = false;
    $('#checkout-error').focus();
  } finally {
    submitting = false; button.textContent = 'Registrar pedido'; button.disabled = !currentQuote;
  }
}

function showToast(message) {
  const element = $('#toast');
  if (!element) return;
  clearTimeout(toastTimer); element.textContent = message; element.classList.add('show');
  toastTimer = setTimeout(() => element.classList.remove('show'), 3500);
}

function toggleMenu() {
  const nav = $('#navLinks'); nav.classList.toggle('open');
  $('.menu-toggle').setAttribute('aria-expanded', String(nav.classList.contains('open')));
}

document.addEventListener('DOMContentLoaded', () => {
  $('#checkout-form')?.addEventListener('submit', confirmarPedido);
  document.querySelectorAll('[name="pagamento"]').forEach(input => input.addEventListener('change', renderCheckoutSummary));
  $('#refresh-quote')?.addEventListener('click', renderCheckoutSummary);
  $('#checkoutBtn')?.addEventListener('click', event => { if ($('#checkoutBtn').getAttribute('aria-disabled') === 'true') event.preventDefault(); });
  updateCartBadge(); loadCatalog();
});
window.addEventListener('storage', event => { if (event.key === 'sweetbloom_cart') refreshCartViews(); });
