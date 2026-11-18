'use strict';
const $ = selector => document.querySelector(selector);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money = value => (value / 100).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
const labels = {recebido:'Recebido',preparando:'Em preparo',saiu_entrega:'Saiu para entrega',entregue:'Entregue',cancelado:'Cancelado'};
const transitions = {recebido:['preparando','cancelado'],preparando:['saiu_entrega','cancelado'],saiu_entrega:['entregue'],entregue:[],cancelado:[]};
let csrf = '';
let page = 1;
let pages = 1;
let orderVersion = 0;
function message(text, error = true) {
  $('#admin-message').textContent = text;
  $('#admin-message').hidden = !text;
  $('#admin-message').classList.toggle('notice-success', !error);
}
function sessionState(authenticated) {
  $('#login-panel').hidden = authenticated;
  $('#admin-workspace').hidden = !authenticated;
  if (!authenticated) { csrf = ''; $('#orders-list').replaceChildren(); $('#admin-products').replaceChildren(); }
}
async function api(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(path,{...options,signal:controller.signal,headers:{'Content-Type':'application/json','X-CSRF-Token':csrf,...options.headers}});
    const data = await response.json();
    if (!response.ok) {
      if (response.status === 401 && !path.endsWith('/login')) sessionState(false);
      throw new Error(data.error || 'Não foi possível completar a solicitação.');
    }
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('O servidor demorou para responder. Atualize a lista antes de repetir a ação.');
    if (error instanceof TypeError || error instanceof SyntaxError) throw new Error('Não foi possível acessar o servidor. Confira a conexão e tente novamente.');
    throw error;
  } finally { clearTimeout(timeout); }
}
const formatDate = value => new Date(value).toLocaleString('pt-BR',{dateStyle:'short',timeStyle:'short'});

async function loadOrders() {
  const version = ++orderVersion;
  $('#refresh-orders').disabled = true;
  $('#orders-list').setAttribute('aria-busy','true');
  try {
    const params = new URLSearchParams({status:$('#order-status').value,q:$('#order-search').value.trim(),page:String(page)});
    const result = await api('/api/admin/orders?' + params);
    if (version !== orderVersion) return;
    pages = result.pages;
    if (page > pages) { page = pages; return loadOrders(); }
    $('#orders-count').textContent = result.total + (result.total === 1 ? ' pedido encontrado' : ' pedidos encontrados');
    $('#page-info').textContent = 'Página ' + page + ' de ' + pages;
    $('#previous-page').disabled = page <= 1;
    $('#next-page').disabled = page >= pages;
    $('#orders-list').innerHTML = result.orders.map(order => {
      const choices = transitions[order.status] || [];
      const items = order.items.map(item => '<li><span>' + esc(item.product_name) + ' × ' + item.quantity +
        '</span><strong>' + money(item.unit_price_cents * item.quantity) + '</strong></li>').join('');
      const history = order.history.map(entry => '<li>' + esc(labels[entry.status]) + ' · ' + esc(formatDate(entry.changed_at)) + '</li>').join('');
      return '<article class="order-card"><div class="order-card-heading"><div><h3>Pedido #' + String(order.id).padStart(5,'0') +
        '</h3><p>' + esc(formatDate(order.created_at)) + '</p></div><span class="order-status ' + esc(order.status) + '">' +
        esc(labels[order.status]) + '</span></div><div class="order-card-grid"><div><h4>' + esc(order.recipient_name) +
        '</h4><p>' + esc(order.recipient_phone) + '</p>' + (order.recipient_email ? '<p>' + esc(order.recipient_email) + '</p>' : '') +
        '<p>' + esc(order.street) + ', ' + esc(order.neighborhood) + '</p>' +
        (order.complement ? '<p>' + esc(order.complement) + '</p>' : '') +
        (order.postal_code ? '<p>CEP ' + esc(order.postal_code) + '</p>' : '') +
        (order.notes ? '<p class="order-notes"><strong>Observações:</strong> ' + esc(order.notes) + '</p>' : '') +
        '</div><div><ul class="order-items">' + items + '</ul><p class="order-total">Total: ' + money(order.total_cents) +
        '</p><p class="field-help">Desconto: ' + money(order.discount_cents) + ' · Entrega: ' + money(order.delivery_cents) +
        '<br>Forma: ' + esc({pix:'PIX',cartao:'Crédito',debito:'Débito',dinheiro:'Dinheiro'}[order.payment]) +
        ' · cobrança combinada com a loja</p></div></div>' +
        (choices.length ? '<form class="status-form" data-order="' + order.id + '" data-version="' + order.version +
        '"><label>Próximo status<select name="status">' + choices.map(status => '<option value="' + status + '">' +
        esc(labels[status]) + '</option>').join('') + '</select></label><button class="btn-primary" type="submit">Atualizar pedido</button></form>' :
        '<p class="field-help">Pedido finalizado. O histórico é preservado.</p>') +
        '<details class="order-history"><summary>Histórico de status</summary><ul>' + history + '</ul></details></article>';
    }).join('') || '<div class="empty-panel"><h3>Nenhum pedido por aqui.</h3><p>As encomendas registradas na loja aparecem nesta lista. Se estiver usando filtros, tente outra busca.</p></div>';
  } catch (error) { message(error.message); }
  finally {
    if (version === orderVersion) { $('#refresh-orders').disabled = false; $('#orders-list').setAttribute('aria-busy','false'); }
  }
}
async function loadProducts() {
  $('#admin-products').setAttribute('aria-busy','true');
  try {
    const {products} = await api('/api/admin/products');
    $('#admin-products').innerHTML = products.map(product => '<form class="product-edit" data-product="' + product.id +
      '"><div><h3>' + esc(product.name) + '</h3><p>' + esc(product.description) +
      '</p></div><label>Preço (R$)<input name="price" type="number" step="0.01" min="0.01" max="10000" value="' +
      (product.price_cents / 100).toFixed(2) + '" required></label><label class="checkbox-label"><input type="checkbox" name="active" ' +
      (product.active ? 'checked' : '') + '> Disponível na loja</label><button class="btn-secondary" type="submit">Salvar produto</button></form>').join('');
  } catch (error) { message(error.message); }
  finally { $('#admin-products').setAttribute('aria-busy','false'); }
}
async function initialize() {
  try {
    const session = await api('/api/admin/session');
    csrf = session.csrf;
    sessionState(session.authenticated);
    if (session.authenticated) await loadOrders();
  } catch (error) { sessionState(false); message(error.message); }
  finally { $('#session-loading').hidden = true; }
}
$('#login-form').addEventListener('submit', async event => {
  event.preventDefault();
  const button = $('#login-button'); button.disabled = true; button.textContent = 'Entrando…'; message('');
  try {
    const session = await api('/api/admin/login',{method:'POST',body:JSON.stringify({password:$('#admin-password').value})});
    csrf = session.csrf; $('#admin-password').value = ''; sessionState(true); await loadOrders();
    $('#orders-title').setAttribute('tabindex','-1'); $('#orders-title').focus();
  } catch (error) { message(error.message); }
  finally { button.disabled = false; button.textContent = 'Entrar no painel'; }
});
$('#logout').addEventListener('click', async () => {
  try { await api('/api/admin/logout',{method:'POST',body:'{}'}); sessionState(false); message(''); $('#admin-password').focus(); }
  catch (error) { message(error.message); }
});
document.querySelectorAll('[data-tab]').forEach(button => button.addEventListener('click', () => {
  const products = button.dataset.tab === 'products';
  $('#products-panel').hidden = !products; $('#orders-panel').hidden = products;
  document.querySelectorAll('[data-tab]').forEach(tab => {
    if (tab === button) tab.setAttribute('aria-current','page'); else tab.removeAttribute('aria-current');
  });
  message('');
  if (products) loadProducts(); else loadOrders();
}));
$('#order-filters').addEventListener('submit', event => { event.preventDefault(); page = 1; message(''); loadOrders(); });
$('#refresh-orders').addEventListener('click', () => { message(''); loadOrders(); });
$('#previous-page').addEventListener('click', () => { if (page > 1) { page--; loadOrders(); } });
$('#next-page').addEventListener('click', () => { if (page < pages) { page++; loadOrders(); } });
document.addEventListener('submit', async event => {
  const form = event.target;
  if (!form.matches('.status-form,.product-edit')) return;
  event.preventDefault();
  const button = form.querySelector('button'); if (button.disabled) return;
  const original = button.textContent;
  if (form.matches('.status-form') && form.elements.status.value === 'cancelado' && !confirm('Cancelar este pedido? O registro permanecerá no histórico.')) return;
  button.disabled = true; button.textContent = 'Salvando…'; message('');
  try {
    if (form.matches('.status-form')) {
      await api('/api/admin/orders/' + form.dataset.order,{method:'PATCH',body:JSON.stringify({status:form.elements.status.value,version:Number(form.dataset.version)})});
      await loadOrders(); message('Status do pedido atualizado.', false);
    } else {
      await api('/api/admin/products/' + form.dataset.product,{method:'PATCH',body:JSON.stringify({price_cents:Math.round(Number(form.elements.price.value) * 100),active:form.elements.active.checked})});
      await loadProducts(); message('Produto atualizado. Os novos valores já estão disponíveis na loja.', false);
    }
  } catch (error) { message(error.message); }
  finally { button.disabled = false; button.textContent = original; }
});
initialize();
