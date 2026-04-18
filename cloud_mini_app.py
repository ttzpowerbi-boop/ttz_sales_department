"""
🛡️ ARMOR HAND - Облачный Mini App v5.1
Рабочая версия v5.0 + История заказов + Excel + PDF
"""

import os
from flask import Flask, render_template_string, request, jsonify
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)
session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

MINI_APP_HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARMOR HAND</title>
    <script src="https://telegram.org/js/telegram-web-app.js" async></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #333; height: 100vh; overflow: hidden; }
        
        #error-screen { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: none; align-items: center; justify-content: center; z-index: 9999; padding: 20px; }
        .error-box { background: white; padding: 40px 30px; border-radius: 12px; max-width: 400px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); text-align: center; }
        .error-box h2 { color: #c62828; font-size: 24px; margin-bottom: 20px; }
        
        .app { display: none; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; min-height: 100vh; }
        .header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 20px; text-align: center; }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .content { padding: 20px; }
        .page { display: none; }
        .page.active { display: block; }
        
        .search-box { display: flex; gap: 10px; }
        .search-input { flex: 1; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; }
        .search-btn { padding: 12px 20px; background: #2a5298; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        
        .products { display: flex; flex-direction: column; gap: 10px; max-height: 400px; overflow-y: auto; margin-top: 15px; }
        .product { padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; }
        .product:hover { border-color: #2a5298; background: #f0f2f5; }
        .product-name { font-weight: 600; color: #1e3c72; }
        
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #e3f2fd; font-weight: 600; }
        .action-btn { padding: 8px 12px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; }
        .edit-btn { background: #2196f3; color: white; }
        .remove-btn { background: #f44336; color: white; }
        
        .summary-table { background: #f9f9f9; padding: 15px; border-radius: 8px; }
        .summary-row { display: flex; justify-content: space-between; padding: 8px 0; font-weight: 600; }
        
        .message { padding: 12px; border-radius: 8px; margin-bottom: 15px; display: none; text-align: center; font-weight: 600; }
        .message.success { background: #c8e6c9; color: #2e7d32; display: block; }
        .message.error { background: #ffcdd2; color: #c62828; display: block; }
        
        .buttons { display: flex; gap: 10px; margin-top: 20px; }
        .btn { flex: 1; padding: 14px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; color: white; }
        .btn-primary { background: #4caf50; }
        .btn-secondary { background: #757575; }
        .btn-danger { background: #f44336; }
        
        textarea { width: 100%; height: 80px; padding: 10px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; }
        
        .order-card { border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-bottom: 10px; background: #f8f9ff; cursor: pointer; }
        .order-card:hover { border-color: #2a5298; background: #f0f4ff; }
        .order-id { font-weight: 600; color: #1e3c72; }
        .order-date { font-size: 12px; color: #666; margin-top: 4px; }
        .order-items { font-size: 12px; color: #666; margin-top: 6px; }
    </style>
</head>
<body>

<div id="error-screen">
    <div class="error-box">
        <h2>🔒 Доступ запрещён</h2>
        <p>Это приложение работает <strong>только внутри Telegram</strong>.</p>
        <p>Откройте через бота: <strong>@TTZ_Sales_Department_bot</strong></p>
    </div>
</div>

<div class="app">
    <div class="container">
        <div class="header">
            <h1>🛡️ ARMOR HAND</h1>
            <p id="headerTitle">Форма предзаказа</p>
        </div>
        <div class="content">
            <div id="message" class="message"></div>
            
            <!-- Поиск -->
            <div id="searchPage" class="page active">
                <div class="search-box">
                    <input type="text" id="searchInput" class="search-input" placeholder="Размер, тип, ГОСТ...">
                    <button class="search-btn" onclick="searchProducts()">Найти</button>
                </div>
                <div id="productsList" class="products" style="display:none;"></div>
                <button class="btn btn-secondary" onclick="showPage('orders')" style="margin-top:20px;width:100%;">📦 Мои заказы</button>
            </div>
            
            <!-- Корзина -->
            <div id="cartPage" class="page">
                <button class="btn btn-secondary" onclick="showPage('search')" style="margin-bottom:15px;">← Назад</button>
                <h3>🛒 Корзина</h3>
                <table id="cartTable">
                    <thead><tr><th>Товар</th><th>Кол-во</th><th>Ред.</th><th>Удал.</th></tr></thead>
                    <tbody id="cartBody"></tbody>
                </table>
                <div class="buttons">
                    <button class="btn btn-secondary" onclick="clearCart()">Очистить</button>
                    <button class="btn btn-primary" onclick="showPreview()">Предварительный просмотр</button>
                </div>
            </div>
            
            <!-- Предварительный просмотр (ЭСФ) -->
            <div id="previewPage" class="page">
                <button class="btn btn-secondary" onclick="showPage('cart')" style="margin-bottom:15px;">← Назад в корзину</button>
                <h3>📄 Предварительный просмотр заказа</h3>
                <div class="summary-table">
                    <table style="width:100%;">
                        <thead><tr><th>Товар</th><th>Кол-во</th></tr></thead>
                        <tbody id="previewTable"></tbody>
                    </table>
                    <div class="summary-row" style="margin-top:15px;">
                        <span>Итого позиций:</span>
                        <span id="previewCount">0</span>
                    </div>
                </div>
                <div style="margin-top:20px;">
                    <h4>Комментарий к заказу</h4>
                    <textarea id="orderComment" placeholder="Добавьте комментарий (необязательно)..."></textarea>
                </div>
                <div class="buttons">
                    <button class="btn btn-secondary" onclick="showPage('cart')">Отмена</button>
                    <button class="btn btn-primary" onclick="confirmAndSend()">Подтвердить и отправить заказ</button>
                </div>
            </div>
            
            <!-- МОИ ЗАКАЗЫ -->
            <div id="ordersPage" class="page">
                <button class="btn btn-secondary" onclick="showPage('search')" style="margin-bottom:15px;">← Назад</button>
                <h3>📦 Мои заказы</h3>
                <div id="ordersList"></div>
            </div>
            
            <!-- ДЕТАЛИ ЗАКАЗА -->
            <div id="detailPage" class="page">
                <button class="btn btn-secondary" onclick="showPage('orders')" style="margin-bottom:15px;">← Назад</button>
                <div id="detailContent"></div>
                <div class="buttons">
                    <button class="btn btn-secondary" onclick="downloadExcel()">📊 Excel</button>
                    <button class="btn btn-primary" onclick="downloadPDF()">📄 PDF</button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
let tg = null;
let cart = [];
let orders = JSON.parse(localStorage.getItem('armorOrders') || '[]');
let currentOrder = null;

function initApp() {
    const check = () => {
        if (typeof Telegram !== 'undefined' && Telegram.WebApp && Telegram.WebApp.initData && Telegram.WebApp.initData.length > 5) {
            tg = Telegram.WebApp;
            tg.ready();
            tg.expand();
            document.querySelector('.app').style.display = 'block';
            document.getElementById('error-screen').style.display = 'none';
            return true;
        }
        return false;
    };
    if (check()) return;
    setTimeout(check, 600);
}
window.onload = initApp;

function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(page + 'Page').classList.add('active');
    document.getElementById('headerTitle').textContent = 
        page === 'search' ? 'Форма предзаказа' : 
        page === 'cart' ? 'Ваша корзина' : 
        page === 'preview' ? 'Предварительный просмотр' :
        page === 'orders' ? 'Мои заказы' : 'Детали заказа';
    if (page === 'orders') renderOrders();
}

async function searchProducts() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return showMessage('Введите запрос', 'error');
    
    try {
        const res = await fetch('/api/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query})
        });
        const data = await res.json();
        
        const list = document.getElementById('productsList');
        if (data.products && data.products.length > 0) {
            let html = '';
            data.products.forEach(p => {
                html += `<div class="product" onclick="addToCart('${p.name.replace(/'/g, "\\'")}', '${p.unit || "шт"}')">
                    <div class="product-name">${p.name}</div>
                </div>`;
            });
            list.innerHTML = html;
            list.style.display = 'flex';
            showMessage(`✅ Найдено ${data.products.length} товаров`, 'success');
        } else {
            list.style.display = 'none';
            showMessage('❌ Товары не найдены', 'error');
        }
    } catch (e) {
        showMessage('❌ Ошибка соединения', 'error');
    }
}

function addToCart(name, unit) {
    const existing = cart.find(item => item.name === name);
    if (existing) {
        existing.qty += 1;
    } else {
        cart.push({name: name, qty: 1, unit: unit});
    }
    showMessage('✅ Добавлено в корзину', 'success');
    updateCartDisplay();
    showPage('cart');
}

function updateCartDisplay() {
    let html = '';
    cart.forEach((item, index) => {
        html += `<tr>
            <td>${item.name}</td>
            <td style="text-align:center">${item.qty}</td>
            <td style="text-align:center"><button class="action-btn edit-btn" onclick="editItem(${index})">✎</button></td>
            <td style="text-align:center"><button class="action-btn remove-btn" onclick="removeItem(${index})">✕</button></td>
        </tr>`;
    });
    document.getElementById('cartBody').innerHTML = html;
}

function editItem(index) {
    const newQty = prompt(`Новое количество для:\n${cart[index].name}`, cart[index].qty);
    if (newQty !== null && !isNaN(newQty) && parseInt(newQty) > 0) {
        cart[index].qty = parseInt(newQty);
        updateCartDisplay();
        showMessage('✅ Количество обновлено', 'success');
    }
}

function removeItem(index) {
    if (confirm('Удалить товар из корзины?')) {
        cart.splice(index, 1);
        updateCartDisplay();
        showMessage('🗑️ Товар удалён', 'success');
    }
}

function clearCart() {
    if (confirm('Очистить всю корзину?')) {
        cart = [];
        updateCartDisplay();
    }
}

function showPreview() {
    if (cart.length === 0) return showMessage('Корзина пуста', 'error');
    
    let html = '';
    cart.forEach(item => {
        html += `<tr><td>${item.name}</td><td style="text-align:right">${item.qty} ${item.unit}</td></tr>`;
    });
    document.getElementById('previewTable').innerHTML = html;
    document.getElementById('previewCount').textContent = cart.length;
    
    showPage('preview');
}

function confirmAndSend() {
    if (cart.length === 0) return;
    
    const comment = document.getElementById('orderComment').value.trim();
    const orderNum = 'PRE-' + String(1000 + Math.floor(Math.random() * 9000));
    
    const orderData = {
        id: orderNum,
        date: new Date().toLocaleString('ru-RU'),
        status: 'Новый',
        items: [...cart],
        comment: comment || '—'
    };
    
    orders.unshift(orderData);
    localStorage.setItem('armorOrders', JSON.stringify(orders));
    
    if (tg && tg.sendData) {
        const telegramData = {
            items: cart,
            comment: comment,
            timestamp: new Date().toLocaleString('ru-RU')
        };
        tg.sendData(JSON.stringify(telegramData));
    }
    
    showMessage('✅ Заказ успешно отправлен в бота!', 'success');
    
    setTimeout(() => {
        cart = [];
        updateCartDisplay();
        showPage('search');
    }, 1800);
}

function renderOrders() {
    const container = document.getElementById('ordersList');
    if (orders.length === 0) {
        container.innerHTML = '<div style="color:#999;padding:40px;text-align:center;">Нет заказов</div>';
        return;
    }
    
    let html = '';
    orders.forEach((order, idx) => {
        html += `<div class="order-card" onclick="showDetail(${idx})">
            <div class="order-id">${order.id} — ${order.status}</div>
            <div class="order-date">${order.date}</div>
            <div class="order-items">${order.items.map(i => `${i.name} (${i.qty})`).join(', ')}</div>
        </div>`;
    });
    
    container.innerHTML = html;
}

function showDetail(idx) {
    currentOrder = orders[idx];
    let html = `<h3>${currentOrder.id}</h3>`;
    html += `<p><strong>Дата:</strong> ${currentOrder.date}</p>`;
    html += `<p><strong>Статус:</strong> <span style="color:#2e7d32;">${currentOrder.status}</span></p>`;
    html += `<table><thead><tr><th>Товар</th><th style="text-align:right;">Кол-во</th></tr></thead><tbody>`;
    
    currentOrder.items.forEach(item => {
        html += `<tr><td>${item.name}</td><td style="text-align:right;">${item.qty} ${item.unit}</td></tr>`;
    });
    
    html += `</tbody></table>`;
    if (currentOrder.comment !== '—') {
        html += `<p><strong>Комментарий:</strong> ${currentOrder.comment}</p>`;
    }
    
    document.getElementById('detailContent').innerHTML = html;
    showPage('detail');
}

function downloadExcel() {
    if (!currentOrder) return;
    
    let csv = "№;Наименование;Ед.изм;Кол-во\n";
    currentOrder.items.forEach((item, i) => {
        csv += `${i+1};${item.name};${item.unit};${item.qty}\n`;
    });
    
    const blob = new Blob(['\ufeff' + csv], {type: 'text/csv;charset=utf-8;'});
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${currentOrder.id}.csv`;
    link.click();
    showMessage('✅ Excel скачан', 'success');
}

function downloadPDF() {
    if (!currentOrder) return;
    
    const win = window.open('', '_blank');
    let html = `
        <html>
        <head><meta charset="utf-8">
        <style>body{font-family:Arial;padding:30px}h2{text-align:center;margin-bottom:10px}p{text-align:center;margin:5px 0}table{width:100%;border-collapse:collapse;margin-top:30px}th,td{border:1px solid #000;padding:12px;text-align:left}th{background:#eee;font-weight:bold}</style>
        </head>
        <body>
        <h2>АКТ приема-передачи товара</h2>
        <p><strong>№ ${currentOrder.id}</strong></p>
        <p>от ${currentOrder.date}</p>
        <table><tr><th>Товар</th><th>Кол-во</th></tr>
    `;
    
    currentOrder.items.forEach(item => {
        html += `<tr><td>${item.name}</td><td>${item.qty} ${item.unit}</td></tr>`;
    });
    
    html += `</table></body></html>`;
    
    win.document.write(html);
    win.document.close();
    setTimeout(() => win.print(), 500);
}

function showMessage(text, type) {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.className = `message ${type}`;
    setTimeout(() => msg.className = 'message', 4000);
}
</script>
</body>
</html>'''

# ===================== ROUTES =====================
@app.route('/webapp', methods=['GET'])
def webapp():
    return render_template_string(MINI_APP_HTML)

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        if not query:
            return jsonify({"error": "Пустой запрос", "products": []})
        
        response = session.post(
            'https://criteria-waviness-entangled.ngrok-free.dev/api/search',
            json={'query': query},
            timeout=15,
            verify=False
        )
        return jsonify(response.json())
    except Exception as e:
        print(f"Proxy error: {e}")
        return jsonify({"error": "Локальный сервер недоступен", "products": []})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n🛡️ ARMOR HAND Cloud v5.1 — рабочая v5.0 + история заказов + Excel + PDF")
    app.run(host='0.0.0.0', port=port, debug=False)
