"""
🛡️ ARMOR HAND - Облачный Mini App v6.0
Новые функции:
  1. Кнопка "Мои предзаказы" — список всех созданных предзаказов
  2. Номер предзаказа при создании (ПЗ-YYYYMMDD-XXXX)
  3. Просмотр каждого предзаказа с фильтром по периоду
  4. Сохранение предзаказа в Excel (по шаблону акта)
"""

import os
import json
import io
import re
from datetime import datetime, date
from flask import Flask, render_template_string, request, jsonify, send_file
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── openpyxl для Excel ──────────────────────────────────────────────────────
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

app = Flask(__name__)
session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504])
session.mount("http://", HTTPAdapter(max_retries=retry))
session.mount("https://", HTTPAdapter(max_retries=retry))

# ── In-memory хранилище предзаказов ─────────────────────────────────────────
ORDERS: dict = {}          # { order_id: { id, number, created_at, items, comment } }
ORDER_COUNTER: list = [0]  # используем список чтобы мутировать из функции

def next_order_id():
    ORDER_COUNTER[0] += 1
    today = datetime.now().strftime("%Y%m%d")
    num = f"ПЗ-{today}-{ORDER_COUNTER[0]:04d}"
    return ORDER_COUNTER[0], num

# ============================================================================
# HTML
# ============================================================================

MINI_APP_HTML = r'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ARMOR HAND</title>
<script src="https://telegram.org/js/telegram-web-app.js" async></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f2f5;color:#333;min-height:100vh;}

/* ── error ── */
#error-screen{position:fixed;top:0;left:0;width:100%;height:100%;background:linear-gradient(135deg,#667eea,#764ba2);display:none;align-items:center;justify-content:center;z-index:9999;padding:20px;}
.error-box{background:#fff;padding:40px 30px;border-radius:12px;max-width:400px;text-align:center;}
.error-box h2{color:#c62828;font-size:24px;margin-bottom:12px;}

/* ── layout ── */
.app{display:none;}
.container{max-width:600px;margin:0 auto;background:#fff;min-height:100vh;}
.header{background:linear-gradient(135deg,#1e3c72,#2a5298);color:#fff;padding:18px 20px;text-align:center;position:sticky;top:0;z-index:10;}
.header h1{font-size:22px;margin-bottom:3px;}
.header p{font-size:13px;opacity:.85;}

/* ── nav tabs ── */
.nav{display:flex;background:#1a3460;}
.nav-btn{flex:1;padding:11px 4px;background:none;border:none;color:rgba(255,255,255,.65);font-size:12px;cursor:pointer;border-bottom:3px solid transparent;transition:.2s;}
.nav-btn.active{color:#fff;border-bottom-color:#64b5f6;}

/* ── content ── */
.content{padding:16px;}
.page{display:none;}
.page.active{display:block;}

/* ── search ── */
.search-box{display:flex;gap:8px;}
.search-input{flex:1;padding:11px 12px;border:2px solid #ddd;border-radius:8px;font-size:14px;}
.search-btn{padding:11px 18px;background:#2a5298;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600;white-space:nowrap;}
.products{display:flex;flex-direction:column;gap:8px;max-height:380px;overflow-y:auto;margin-top:12px;}
.product{padding:12px;border:2px solid #e0e0e0;border-radius:8px;cursor:pointer;transition:.15s;}
.product:hover{border-color:#2a5298;background:#f0f4ff;}
.product-name{font-weight:600;color:#1e3c72;font-size:13px;}

/* ── cart / preview tables ── */
table{width:100%;border-collapse:collapse;margin:12px 0;font-size:13px;}
th,td{border:1px solid #ddd;padding:8px 10px;text-align:left;}
th{background:#e3f2fd;font-weight:600;}
.action-btn{padding:6px 10px;border:none;border-radius:6px;cursor:pointer;}
.edit-btn{background:#2196f3;color:#fff;}
.remove-btn{background:#f44336;color:#fff;}

/* ── buttons ── */
.btn{padding:13px;border:none;border-radius:8px;cursor:pointer;font-weight:600;color:#fff;font-size:14px;}
.btn-primary{background:#4caf50;}
.btn-secondary{background:#757575;}
.btn-danger{background:#f44336;}
.btn-blue{background:#1565c0;}
.btn-excel{background:#217346;}
.buttons{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap;}
.buttons .btn{flex:1;min-width:120px;}

/* ── message toast ── */
.message{padding:11px 14px;border-radius:8px;margin-bottom:12px;display:none;text-align:center;font-weight:600;font-size:14px;}
.message.success{background:#c8e6c9;color:#2e7d32;display:block;}
.message.error{background:#ffcdd2;color:#c62828;display:block;}
.message.info{background:#e3f2fd;color:#1565c0;display:block;}

/* ── order number banner ── */
.order-number-banner{background:linear-gradient(135deg,#1e3c72,#2a5298);color:#fff;padding:14px 18px;border-radius:10px;margin-bottom:14px;text-align:center;}
.order-number-banner .num{font-size:20px;font-weight:700;letter-spacing:1px;}
.order-number-banner .label{font-size:12px;opacity:.8;margin-top:3px;}

/* ── orders list ── */
.orders-filter{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap;align-items:center;}
.orders-filter input[type=date]{padding:8px 10px;border:2px solid #ddd;border-radius:8px;font-size:13px;flex:1;min-width:130px;}
.orders-filter label{font-size:12px;color:#555;white-space:nowrap;}
.filter-row{display:flex;gap:8px;align-items:center;flex:1;}
.order-card{border:2px solid #e0e0e0;border-radius:10px;padding:14px;margin-bottom:10px;cursor:pointer;transition:.15s;}
.order-card:hover{border-color:#2a5298;background:#f0f4ff;}
.order-card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}
.order-card-num{font-weight:700;color:#1e3c72;font-size:15px;}
.order-card-date{font-size:12px;color:#888;}
.order-card-count{font-size:13px;color:#555;}
.empty-state{text-align:center;padding:40px 20px;color:#999;}
.empty-state .icon{font-size:48px;margin-bottom:12px;}

/* ── order detail ── */
.order-detail-header{background:#f5f7fa;border-radius:10px;padding:14px;margin-bottom:14px;}
.order-detail-header .num{font-size:18px;font-weight:700;color:#1e3c72;}
.order-detail-header .meta{font-size:12px;color:#666;margin-top:4px;}

textarea{width:100%;height:70px;padding:10px;border:2px solid #ddd;border-radius:8px;font-size:14px;resize:none;}

/* ── import excel section ── */
.import-area{border:2px dashed #bbb;border-radius:10px;padding:24px;text-align:center;cursor:pointer;transition:.2s;margin-bottom:14px;}
.import-area:hover{border-color:#2a5298;background:#f0f4ff;}
.import-area .icon{font-size:36px;margin-bottom:8px;}
.import-area p{font-size:13px;color:#555;}
#fileInput{display:none;}
.import-preview{margin-top:12px;}
</style>
</head>
<body>

<div id="error-screen">
  <div class="error-box">
    <h2>🔒 Доступ запрещён</h2>
    <p>Приложение работает <strong>только внутри Telegram</strong>.</p>
    <p style="margin-top:8px;">Откройте через: <strong>@TTZ_Sales_Department_bot</strong></p>
  </div>
</div>

<div class="app">
  <div class="container">
    <div class="header">
      <h1>🛡️ ARMOR HAND</h1>
      <p id="headerTitle">Форма предзаказа</p>
    </div>

    <!-- TAB NAV -->
    <div class="nav">
      <button class="nav-btn active" onclick="switchTab('search')">🔍 Поиск</button>
      <button class="nav-btn" onclick="switchTab('orders')">📋 Предзаказы</button>
      <button class="nav-btn" onclick="switchTab('import')">📥 Импорт Excel</button>
    </div>

    <div class="content">
      <div id="message" class="message"></div>

      <!-- ══════════════ PAGE: SEARCH ══════════════ -->
      <div id="searchPage" class="page active">
        <div class="search-box">
          <input type="text" id="searchInput" class="search-input" placeholder="Размер, тип, ГОСТ..."
            onkeydown="if(event.key==='Enter') searchProducts()">
          <button class="search-btn" onclick="searchProducts()">Найти</button>
        </div>
        <div id="productsList" class="products" style="display:none;"></div>
      </div>

      <!-- ══════════════ PAGE: CART ══════════════ -->
      <div id="cartPage" class="page">
        <button class="btn btn-secondary" onclick="backToSearch()" style="margin-bottom:12px;">← Назад</button>
        <h3>🛒 Корзина</h3>
        <table id="cartTable">
          <thead><tr><th>Товар</th><th>Кол-во</th><th></th><th></th></tr></thead>
          <tbody id="cartBody"></tbody>
        </table>
        <div class="buttons">
          <button class="btn btn-danger" onclick="clearCart()">Очистить</button>
          <button class="btn btn-primary" onclick="showPreview()">Предпросмотр →</button>
        </div>
      </div>

      <!-- ══════════════ PAGE: PREVIEW ══════════════ -->
      <div id="previewPage" class="page">
        <button class="btn btn-secondary" onclick="showPage('cart')" style="margin-bottom:12px;">← В корзину</button>
        <h3>📄 Предварительный просмотр</h3>
        <table>
          <thead><tr><th>Товар</th><th style="text-align:right;">Кол-во</th></tr></thead>
          <tbody id="previewTable"></tbody>
        </table>
        <div style="margin-bottom:8px;font-size:13px;color:#555;">Позиций: <b id="previewCount">0</b></div>
        <div>
          <label style="font-size:13px;font-weight:600;display:block;margin-bottom:6px;">Комментарий:</label>
          <textarea id="orderComment" placeholder="(необязательно)"></textarea>
        </div>
        <div class="buttons">
          <button class="btn btn-secondary" onclick="showPage('cart')">Отмена</button>
          <button class="btn btn-primary" onclick="confirmAndSend()">✅ Оформить предзаказ</button>
        </div>
      </div>

      <!-- ══════════════ PAGE: SUCCESS ══════════════ -->
      <div id="successPage" class="page">
        <div class="order-number-banner">
          <div class="label">✅ Предзаказ создан!</div>
          <div class="num" id="successOrderNum">—</div>
          <div class="label" id="successOrderDate"></div>
        </div>
        <p style="font-size:14px;color:#555;margin-bottom:16px;text-align:center;">
          Консультант свяжется с вами в ближайшее время.
        </p>
        <div class="buttons">
          <button class="btn btn-blue" onclick="viewLastOrder()">👁 Открыть заказ</button>
          <button class="btn btn-excel" onclick="downloadLastOrder()">⬇ Скачать Excel</button>
        </div>
        <div class="buttons" style="margin-top:8px;">
          <button class="btn btn-secondary" onclick="newOrder()">+ Новый предзаказ</button>
        </div>
      </div>

      <!-- ══════════════ PAGE: ORDERS LIST ══════════════ -->
      <div id="ordersPage" class="page">
        <div class="orders-filter">
          <div class="filter-row">
            <label>С:</label>
            <input type="date" id="filterFrom">
            <label>По:</label>
            <input type="date" id="filterTo">
          </div>
          <button class="btn btn-blue" style="flex:0 0 auto;padding:8px 14px;font-size:13px;" onclick="renderOrdersList()">Фильтр</button>
        </div>
        <div id="ordersList"></div>
      </div>

      <!-- ══════════════ PAGE: ORDER DETAIL ══════════════ -->
      <div id="orderDetailPage" class="page">
        <button class="btn btn-secondary" onclick="backToOrders()" style="margin-bottom:12px;">← К списку</button>
        <div class="order-detail-header">
          <div class="num" id="detailNum">—</div>
          <div class="meta" id="detailMeta"></div>
        </div>
        <table>
          <thead><tr><th>Товар</th><th style="text-align:right;">Кол-во</th></tr></thead>
          <tbody id="detailTable"></tbody>
        </table>
        <div id="detailComment" style="font-size:13px;color:#555;margin-top:8px;"></div>
        <div class="buttons" style="margin-top:16px;">
          <button class="btn btn-excel" onclick="downloadCurrentDetailOrder()">⬇ Скачать Excel</button>
        </div>
      </div>

      <!-- ══════════════ PAGE: IMPORT EXCEL ══════════════ -->
      <div id="importPage" class="page">
        <h3 style="margin-bottom:12px;">📥 Импорт из Excel</h3>
        <p style="font-size:13px;color:#555;margin-bottom:14px;">
          Загрузите файл акта приёма-передачи товара (.xls / .xlsx).<br>
          Строки с товарами будут добавлены в корзину.
        </p>
        <div class="import-area" onclick="document.getElementById('fileInput').click()">
          <div class="icon">📂</div>
          <p>Нажмите для выбора файла<br><small>(.xls, .xlsx)</small></p>
        </div>
        <input type="file" id="fileInput" accept=".xls,.xlsx" onchange="handleImport(event)">
        <div id="importResult" class="import-preview"></div>
      </div>

    </div><!-- /content -->
  </div><!-- /container -->
</div><!-- /app -->

<script>
/* ════════════════════════════════════════════════════════
   STATE
════════════════════════════════════════════════════════ */
let tg = null;
let cart = [];
let lastOrderId = null;
let currentDetailOrderId = null;

/* ════════════════════════════════════════════════════════
   INIT
════════════════════════════════════════════════════════ */
function initApp(){
  const check = () => {
    if(typeof Telegram!=='undefined' && Telegram.WebApp && Telegram.WebApp.initData && Telegram.WebApp.initData.length>5){
      tg = Telegram.WebApp; tg.ready(); tg.expand();
      document.querySelector('.app').style.display='block';
      document.getElementById('error-screen').style.display='none';
      setTodayFilter();
      return true;
    }
    return false;
  };
  if(!check()) setTimeout(check,600);
}
window.onload = initApp;

function setTodayFilter(){
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth()+1).padStart(2,'0');
  const d = String(now.getDate()).padStart(2,'0');
  const today = `${y}-${m}-${d}`;
  // default: from beginning of month to today
  document.getElementById('filterFrom').value = `${y}-${m}-01`;
  document.getElementById('filterTo').value = today;
}

/* ════════════════════════════════════════════════════════
   NAVIGATION
════════════════════════════════════════════════════════ */
let activeTab = 'search';

function switchTab(tab){
  activeTab = tab;
  document.querySelectorAll('.nav-btn').forEach((b,i)=>{
    b.classList.toggle('active', ['search','orders','import'][i]===tab);
  });
  if(tab==='search')  showPage('search');
  if(tab==='orders'){ showPage('orders'); renderOrdersList(); }
  if(tab==='import')  showPage('import');
}

function showPage(page){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.getElementById(page+'Page').classList.add('active');
  const titles = {
    search:'Форма предзаказа', cart:'Корзина', preview:'Предварительный просмотр',
    success:'Предзаказ создан', orders:'Мои предзаказы',
    orderDetail:'Детали предзаказа', import:'Импорт из Excel'
  };
  document.getElementById('headerTitle').textContent = titles[page]||'';
}

function backToSearch(){
  switchTab('search');
}
function backToOrders(){
  showPage('orders');
  renderOrdersList();
}

/* ════════════════════════════════════════════════════════
   SEARCH
════════════════════════════════════════════════════════ */
async function searchProducts(){
  const query = document.getElementById('searchInput').value.trim();
  if(!query) return showMessage('Введите запрос','error');

  showMessage('⏳ Поиск...','info');
  try{
    const res = await fetch('/api/search',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({query})
    });
    const data = await res.json();
    const list = document.getElementById('productsList');
    if(data.products && data.products.length>0){
      list.innerHTML = data.products.map(p=>
        `<div class="product" onclick="addToCart(${JSON.stringify(p.name)}, ${JSON.stringify(p.unit||'шт')})">
           <div class="product-name">${p.name}</div>
         </div>`
      ).join('');
      list.style.display='flex';
      showMessage(`✅ Найдено ${data.products.length} товаров`,'success');
    } else {
      list.style.display='none';
      showMessage('❌ Товары не найдены','error');
    }
  } catch(e){
    showMessage('❌ Ошибка соединения','error');
  }
}

/* ════════════════════════════════════════════════════════
   CART
════════════════════════════════════════════════════════ */
function addToCart(name, unit){
  const ex = cart.find(i=>i.name===name);
  if(ex){ ex.qty+=1; }
  else { cart.push({name, qty:1, unit}); }
  showMessage('✅ Добавлено в корзину','success');
  updateCartDisplay();
  showPage('cart');
}

function updateCartDisplay(){
  document.getElementById('cartBody').innerHTML = cart.map((item,i)=>`
    <tr>
      <td style="font-size:12px;">${item.name}</td>
      <td style="text-align:center;">${item.qty} ${item.unit}</td>
      <td style="text-align:center;"><button class="action-btn edit-btn" onclick="editItem(${i})">✎</button></td>
      <td style="text-align:center;"><button class="action-btn remove-btn" onclick="removeItem(${i})">✕</button></td>
    </tr>`).join('');
}

function editItem(i){
  const v = prompt(`Количество для:\n${cart[i].name}`, cart[i].qty);
  if(v!==null && !isNaN(v) && parseInt(v)>0){ cart[i].qty=parseInt(v); updateCartDisplay(); }
}
function removeItem(i){
  if(confirm('Удалить товар?')){ cart.splice(i,1); updateCartDisplay(); }
}
function clearCart(){
  if(confirm('Очистить корзину?')){ cart=[]; updateCartDisplay(); }
}

/* ════════════════════════════════════════════════════════
   PREVIEW
════════════════════════════════════════════════════════ */
function showPreview(){
  if(!cart.length) return showMessage('Корзина пуста','error');
  document.getElementById('previewTable').innerHTML = cart.map(i=>
    `<tr><td style="font-size:12px;">${i.name}</td><td style="text-align:right;">${i.qty} ${i.unit}</td></tr>`
  ).join('');
  document.getElementById('previewCount').textContent = cart.length;
  showPage('preview');
}

/* ════════════════════════════════════════════════════════
   CONFIRM & SEND
════════════════════════════════════════════════════════ */
async function confirmAndSend(){
  if(!cart.length) return;
  const comment = document.getElementById('orderComment').value.trim();
  const timestamp = new Date().toLocaleString('ru-RU');

  // Сохранить на сервере
  const res = await fetch('/api/orders',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({items: cart, comment, timestamp})
  });
  const data = await res.json();
  if(data.error) return showMessage('❌ '+data.error,'error');

  lastOrderId = data.order_id;

  // Показать страницу успеха
  document.getElementById('successOrderNum').textContent = data.number;
  document.getElementById('successOrderDate').textContent = data.created_at;
  showPage('success');

  // Отправить в бот
  if(tg && tg.sendData){
    tg.sendData(JSON.stringify({
      order_number: data.number,
      items: cart,
      comment,
      timestamp
    }));
  }

  cart = [];
  updateCartDisplay();
  document.getElementById('orderComment').value='';
}

function viewLastOrder(){
  if(lastOrderId) openOrderDetail(lastOrderId);
}
function downloadLastOrder(){
  if(lastOrderId) downloadOrder(lastOrderId);
}
function newOrder(){
  switchTab('search');
}

/* ════════════════════════════════════════════════════════
   ORDERS LIST
════════════════════════════════════════════════════════ */
async function renderOrdersList(){
  const from = document.getElementById('filterFrom').value;
  const to   = document.getElementById('filterTo').value;

  const res = await fetch(`/api/orders?from=${from}&to=${to}`);
  const data = await res.json();
  const list = document.getElementById('ordersList');

  if(!data.orders || !data.orders.length){
    list.innerHTML = `<div class="empty-state"><div class="icon">📭</div><p>Предзаказов за период не найдено</p></div>`;
    return;
  }

  list.innerHTML = data.orders.map(o=>`
    <div class="order-card" onclick="openOrderDetail(${o.id})">
      <div class="order-card-header">
        <span class="order-card-num">${o.number}</span>
        <span class="order-card-date">${o.created_at}</span>
      </div>
      <div class="order-card-count">📦 ${o.item_count} поз. ${o.comment?'💬':''}</div>
    </div>
  `).join('');
}

async function openOrderDetail(orderId){
  currentDetailOrderId = orderId;
  const res = await fetch(`/api/orders/${orderId}`);
  const o = await res.json();
  if(o.error) return showMessage('❌ '+o.error,'error');

  document.getElementById('detailNum').textContent = o.number;
  document.getElementById('detailMeta').textContent = o.created_at + ' · ' + o.item_count + ' позиций';
  document.getElementById('detailTable').innerHTML = o.items.map(i=>
    `<tr><td style="font-size:12px;">${i.name}</td><td style="text-align:right;">${i.qty} ${i.unit}</td></tr>`
  ).join('');
  document.getElementById('detailComment').textContent = o.comment ? '💬 '+o.comment : '';
  showPage('orderDetail');
}

function downloadCurrentDetailOrder(){
  if(currentDetailOrderId) downloadOrder(currentDetailOrderId);
}

function downloadOrder(orderId){
  window.location.href = `/api/orders/${orderId}/excel`;
}

/* ════════════════════════════════════════════════════════
   IMPORT EXCEL
════════════════════════════════════════════════════════ */
async function handleImport(event){
  const file = event.target.files[0];
  if(!file) return;

  const formData = new FormData();
  formData.append('file', file);

  document.getElementById('importResult').innerHTML = '<p style="color:#555;font-size:13px;">⏳ Обрабатываю файл...</p>';

  try{
    const res = await fetch('/api/import-excel',{method:'POST', body: formData});
    const data = await res.json();
    if(data.error) return document.getElementById('importResult').innerHTML = `<p style="color:red;">${data.error}</p>`;

    // Добавить в корзину
    let added = 0;
    data.items.forEach(item=>{
      if(!item.name) return;
      const ex = cart.find(c=>c.name===item.name);
      if(ex){ ex.qty += item.qty; }
      else { cart.push({name:item.name, qty:item.qty, unit:item.unit||'шт'}); }
      added++;
    });
    updateCartDisplay();

    document.getElementById('importResult').innerHTML = `
      <div style="background:#c8e6c9;color:#2e7d32;padding:12px;border-radius:8px;margin-top:10px;font-weight:600;">
        ✅ Добавлено ${added} позиций из файла «${file.name}»
      </div>
      <div style="margin-top:10px;">
        ${data.items.map(i=>`<div style="font-size:12px;padding:4px 0;border-bottom:1px solid #eee;">${i.name} — ${i.qty} ${i.unit}</div>`).join('')}
      </div>`;

    // Перейти в корзину
    setTimeout(()=>{ switchTab('search'); showPage('cart'); }, 1500);
  } catch(e){
    document.getElementById('importResult').innerHTML = '<p style="color:red;">❌ Ошибка при загрузке</p>';
  }
  event.target.value='';
}

/* ════════════════════════════════════════════════════════
   UTILS
════════════════════════════════════════════════════════ */
function showMessage(text, type){
  const msg = document.getElementById('message');
  msg.textContent = text;
  msg.className = `message ${type}`;
  clearTimeout(msg._t);
  msg._t = setTimeout(()=>msg.className='message', 4000);
}
</script>
</body>
</html>'''

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/webapp')
def webapp():
    return render_template_string(MINI_APP_HTML)

# ── Product search (proxy to local API) ─────────────────────────────────────
@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json() or {}
        query = data.get('query','').strip()
        if not query:
            return jsonify({"error":"Пустой запрос","products":[]})
        response = session.post(
            'https://criteria-waviness-entangled.ngrok-free.dev/api/search',
            json={'query': query}, timeout=15, verify=False
        )
        return jsonify(response.json())
    except Exception as e:
        print(f"Proxy error: {e}")
        return jsonify({"error":"Локальный сервер недоступен","products":[]})

# ── Create order ─────────────────────────────────────────────────────────────
@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json() or {}
        items   = data.get('items', [])
        comment = data.get('comment','')
        if not items:
            return jsonify({"error":"Пустой заказ"})
        oid, num = next_order_id()
        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        ORDERS[oid] = {
            "id": oid,
            "number": num,
            "created_at": now,
            "items": items,
            "comment": comment,
            "item_count": len(items)
        }
        return jsonify({"order_id": oid, "number": num, "created_at": now})
    except Exception as e:
        return jsonify({"error": str(e)})

# ── List orders ───────────────────────────────────────────────────────────────
@app.route('/api/orders', methods=['GET'])
def list_orders():
    from_str = request.args.get('from','')
    to_str   = request.args.get('to','')
    try:
        dt_from = datetime.strptime(from_str, "%Y-%m-%d").date() if from_str else date.min
        dt_to   = datetime.strptime(to_str,   "%Y-%m-%d").date() if to_str   else date.max
    except:
        dt_from, dt_to = date.min, date.max

    result = []
    for o in ORDERS.values():
        try:
            order_date = datetime.strptime(o['created_at'], "%d.%m.%Y %H:%M").date()
        except:
            order_date = date.today()
        if dt_from <= order_date <= dt_to:
            result.append(o)

    result.sort(key=lambda x: x['id'], reverse=True)
    return jsonify({"orders": result})

# ── Get single order ──────────────────────────────────────────────────────────
@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    o = ORDERS.get(order_id)
    if not o:
        return jsonify({"error":"Заказ не найден"})
    return jsonify(o)

# ── Download order as Excel ───────────────────────────────────────────────────
@app.route('/api/orders/<int:order_id>/excel', methods=['GET'])
def download_order_excel(order_id):
    o = ORDERS.get(order_id)
    if not o:
        return jsonify({"error":"Заказ не найден"}), 404

    if not EXCEL_AVAILABLE:
        return jsonify({"error":"openpyxl не установлен"}), 500

    wb = Workbook()
    ws = wb.active
    ws.title = "Предзаказ"

    # ── helpers ──
    def hdr_font(): return Font(bold=True, size=11, name='Arial')
    def cell_font(): return Font(size=10, name='Arial')
    def thin(): return Side(style='thin', color='000000')
    def all_borders(): return Border(left=thin(), right=thin(), top=thin(), bottom=thin())
    def blue_fill(): return PatternFill('solid', start_color='DDEEFF')
    def center(): return Alignment(horizontal='center', vertical='center')
    def left_wrap(): return Alignment(horizontal='left', vertical='center', wrap_text=True)

    # ── header block ──
    ws.merge_cells('A1:F2')
    c = ws['A1']
    c.value = 'ARMOR HAND — Предзаказ'
    c.font = Font(bold=True, size=14, name='Arial', color='1E3C72')
    c.alignment = center()
    c.fill = PatternFill('solid', start_color='D6E4F7')

    ws['A3'] = 'Номер:'
    ws['B3'] = o['number']
    ws['D3'] = 'Дата:'
    ws['E3'] = o['created_at']
    for cell in [ws['A3'], ws['D3']]:
        cell.font = hdr_font()
    for cell in [ws['B3'], ws['E3']]:
        cell.font = cell_font()

    if o.get('comment'):
        ws['A4'] = 'Комментарий:'
        ws['A4'].font = hdr_font()
        ws.merge_cells('B4:F4')
        ws['B4'] = o['comment']
        ws['B4'].font = cell_font()
        ws['B4'].alignment = left_wrap()

    # ── table header ──
    row = 6
    headers = ['№', 'Наименование товара', 'Ед. изм', 'Кол-во']
    cols = [4, 34, 8, 8]
    for j,(h,w) in enumerate(zip(headers, cols), 1):
        col_letter = get_column_letter(j)
        ws.column_dimensions[col_letter].width = w
        c = ws.cell(row=row, column=j, value=h)
        c.font = hdr_font()
        c.fill = blue_fill()
        c.alignment = center()
        c.border = all_borders()

    # ── rows ──
    for idx, item in enumerate(o['items'], 1):
        r = row + idx
        data = [idx, item.get('name',''), item.get('unit','шт'), item.get('qty',1)]
        for j, val in enumerate(data, 1):
            c = ws.cell(row=r, column=j, value=val)
            c.font = cell_font()
            c.border = all_borders()
            c.alignment = center() if j != 2 else left_wrap()

    # ── total row ──
    total_row = row + len(o['items']) + 1
    ws.merge_cells(f'A{total_row}:C{total_row}')
    ws[f'A{total_row}'] = 'Итого позиций:'
    ws[f'A{total_row}'].font = hdr_font()
    ws[f'A{total_row}'].alignment = Alignment(horizontal='right')
    ws[f'D{total_row}'] = len(o['items'])
    ws[f'D{total_row}'].font = hdr_font()
    ws[f'D{total_row}'].alignment = center()

    # ── freeze + fix column widths ──
    ws.freeze_panes = 'A7'
    ws.column_dimensions['A'].width = 5
    ws.column_dimensions['B'].width = 55
    ws.column_dimensions['C'].width = 10
    ws.column_dimensions['D'].width = 10

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    fname = f"{o['number'].replace('/','-')}.xlsx"
    return send_file(buf, as_attachment=True, download_name=fname,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# ── Import Excel file ─────────────────────────────────────────────────────────
@app.route('/api/import-excel', methods=['POST'])
def import_excel():
    if 'file' not in request.files:
        return jsonify({"error":"Файл не загружен"})
    file = request.files['file']
    if not file.filename:
        return jsonify({"error":"Пустое имя файла"})

    try:
        import pandas as pd
        buf = io.BytesIO(file.read())
        xl = pd.read_excel(buf, sheet_name=0, header=None)

        items = []
        # Ищем строки с данными: первый столбец — цифра (порядковый номер)
        for _, row in xl.iterrows():
            val0 = str(row.iloc[0]).strip() if len(row) > 0 else ''
            # Числовой порядковый номер?
            cleaned = re.sub(r'\s+','',val0)
            if not re.match(r'^\d+$', cleaned):
                continue
            # Наименование — col 1
            name = str(row.iloc[1]).strip() if len(row) > 1 else ''
            if not name or name=='nan':
                continue
            # Единица — col 5
            unit = str(row.iloc[5]).strip() if len(row) > 5 else 'шт'
            unit = unit if unit and unit!='nan' else 'шт'
            # Количество — col 6
            try:
                qty_raw = str(row.iloc[6]).strip().replace(' ','') if len(row) > 6 else '1'
                qty = int(float(qty_raw))
            except:
                qty = 1
            items.append({"name": name, "unit": unit, "qty": qty})

        if not items:
            return jsonify({"error":"Не найдено товарных строк. Убедитесь, что файл содержит порядковые номера в первом столбце."})

        return jsonify({"items": items})
    except Exception as e:
        return jsonify({"error": f"Ошибка чтения файла: {str(e)}"})

# ============================================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n🛡️ ARMOR HAND Cloud v6.0")
    print("  ✅ Кнопка предзаказов с фильтром по периоду")
    print("  ✅ Номер предзаказа при создании")
    print("  ✅ Просмотр + скачать каждый предзаказ")
    print("  ✅ Импорт товаров из Excel (акт ТТЗ)")
    app.run(host='0.0.0.0', port=port, debug=False)
