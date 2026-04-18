"""
🛡️ ARMOR HAND - Облачный Mini App v6.3 FINAL
Твой рабочий v5.0 + Мои предзаказы + детальная страница + Excel + PDF
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ARMOR HAND</title>
    <script src="https://telegram.org/js/telegram-web-app.js" async></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #333; height: 100vh; overflow: hidden; }
        #error-screen { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: none; align-items: center; justify-content: center; z-index: 9999; padding: 20px; }
        .error-box { background: white; padding: 40px 30px; border-radius: 12px; max-width: 400px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); text-align: center; }
        .app { display: none; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; min-height: 100vh; }
        .header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 16px 20px; text-align: center; }
        .header h1 { font-size: 22px; margin-bottom: 4px; }
        .content { padding: 20px; }
        .page { display: none; }
        .page.active { display: block; }
        .search-box { display: flex; gap: 10px; }
        .search-input { flex: 1; padding: 14px 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 15px; }
        .search-btn { padding: 14px 24px; background: #2a5298; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .products { display: flex; flex-direction: column; gap: 10px; max-height: calc(100vh - 280px); overflow-y: auto; margin-top: 15px; }
        .product { padding: 14px; border: 2px solid #e0e0e0; border-radius: 10px; cursor: pointer; }
        .product:hover { border-color: #2a5298; background: #f8f9ff; }
        .product-name { font-weight: 600; color: #1e3c72; word-break: break-word; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 12px 8px; text-align: left; }
        th { background: #e3f2fd; font-weight: 600; }
        .action-btn { padding: 8px 12px; border: none; border-radius: 6px; cursor: pointer; font-size: 17px; width: 42px; }
        .edit-btn { background: #2196f3; color: white; }
        .remove-btn { background: #f44336; color: white; }
        .message { padding: 14px; border-radius: 8px; margin-bottom: 15px; display: none; text-align: center; font-weight: 600; font-size: 15px; }
        .message.success { background: #c8e6c9; color: #2e7d32; display: block; }
        .message.error { background: #ffcdd2; color: #c62828; display: block; }
        .buttons { display: flex; gap: 12px; margin-top: 20px; }
        .btn { flex: 1; padding: 16px; border: none; border-radius: 10px; cursor: pointer; font-weight: 600; font-size: 15px; color: white; }
        .btn-primary { background: #4caf50; }
        .btn-secondary { background: #757575; }
        .order-card { cursor: pointer; }
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
                <button class="btn btn-secondary" onclick="showPage('orders')" style="margin-top:20px;width:100%;">📦 Мои предзаказы</button>
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
            
            <!-- Предварительный просмотр -->
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

            <!-- Мои предзаказы -->
            <div id="ordersPage" class="page">
                <button class="btn btn-secondary" onclick="showPage('search')" style="margin-bottom:15px;">← Назад</button>
                <h3>📦 Мои предзаказы</h3>
                <div id="ordersList"></div>
            </div>

            <!-- Детальная страница заказа -->
            <div id="detailPage" class="page">
                <button class="btn btn-secondary" onclick="showPage('orders')" style="margin-bottom:15px;">← Назад к заказам</button>
                <div id="detailContent"></div>
                <div class="buttons">
                    <button class="btn btn-secondary" onclick="downloadExcel()">📊 Скачать Excel</button>
                    <button class="btn btn-primary" onclick="printToPDF()">📄 Скачать PDF</button>
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
    const titles = { 'search': 'Форма предзаказа', 'cart': 'Ваша корзина', 'preview': 'Предварительный просмотр', 'orders': 'Мои предзаказы', 'detail': 'Детали заказа' };
    document.getElementById('headerTitle').textContent = titles[page] || 'ARMOR HAND';
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
                html += `<div class="product" onclick="addToCart('${p.name.replace(/'/g, "\\'")}', '${p.unit || "шт"}')"><div class="product-name">${p.name}</div></div>`;
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
    if (existing) existing.qty += 1;
    else cart.push({name: name, qty: 1, unit: unit});
    showMessage('✅ Добавлено в корзину', 'success');
    updateCartDisplay();
    showPage('cart');
}

function updateCartDisplay() {
    let html = '';
    cart.forEach((item, index) => {
        html += `<tr><td>${item.name}</td><td style="text-align:center">${item.qty}</td><td style="text-align:center"><button class="action-btn edit-btn" onclick="editItem(${index})">✎</button></td><td style="text-align:center"><button class="action-btn remove-btn" onclick="removeItem(${index})">✕</button></td></tr>`;
    });
    document.getElementById('cartBody').innerHTML = html || '<tr><td colspan="4" style="text-align:center;color:#999;padding:40px;">Корзина пуста</td></tr>';
}

function editItem(index) {
    const newQty = prompt(`Новое количество для:\n${cart[index].name}`, cart[index].qty);
    if (newQty !== null && !isNaN(newQty) && parseInt(newQty) > 0) {
        cart[index].qty = parseInt(newQty);
        updateCartDisplay();
    }
}
function removeItem(index) {
    if (confirm('Удалить товар?')) {
        cart.splice(index, 1);
        updateCartDisplay();
    }
}
function clearCart() {
    if (confirm('Очистить корзину?')) {
        cart = [];
        updateCartDisplay();
    }
}

function showPreview() {
    if (cart.length === 0) return showMessage('Корзина пуста', 'error');
    let html = '';
    cart.forEach(item => html += `<tr><td>${item.name}</td><td style="text-align:right">${item.qty} ${item.unit}</td></tr>`);
    document.getElementById('previewTable').innerHTML = html;
    document.getElementById('previewCount').textContent = cart.length;
    showPage('preview');
}

function confirmAndSend() {
    if (cart.length === 0) return;
    const comment = document.getElementById('orderComment').value.trim();
    const orderNumber = 'PRE-' + String(1000 + Math.floor(Math.random() * 9000));
    const orderData = {
        id: orderNumber,
        date: new Date().toLocaleString('ru-RU'),
        status: 'Новый',
        items: cart,
        comment: comment || '—'
    };
    orders.unshift(orderData);
    localStorage.setItem('armorOrders', JSON.stringify(orders));
    if (tg && tg.sendData) tg.sendData(JSON.stringify(orderData));
    showMessage(`🎉 Предзаказ создан!<br><span style="font-size:20px;color:#2a5298;">${orderNumber}</span>`, 'success');
    setTimeout(() => {
        cart = [];
        updateCartDisplay();
        showPage('search');
    }, 2200);
}

function renderOrders() {
    const container = document.getElementById('ordersList');
    if (orders.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#999;padding:40px;">Пока нет предзаказов</p>';
        return;
    }
    let html = '';
    orders.forEach((order, i) => {
        html += `<div onclick="showOrderDetail(${i})" style="border:1px solid #ddd;border-radius:10px;padding:15px;margin-bottom:15px;background:#f8f9ff;cursor:pointer;">
            <div style="display:flex;justify-content:space-between;"><strong>${order.id}</strong><span style="color:#2e7d32;">${order.status}</span></div>
            <small>${order.date}</small>
            <div style="margin-top:10px;font-size:13px;">${order.items.map(item => `• ${item.name} — ${item.qty} ${item.unit}`).join('<br>')}</div>
        </div>`;
    });
    container.innerHTML = html;
}

function showOrderDetail(index) {
    currentOrder = orders[index];
    let html = `<h3>${currentOrder.id}</h3><p><strong>Дата:</strong> ${currentOrder.date}</p><p><strong>Статус:</strong> <span style="color:#2e7d32;">${currentOrder.status}</span></p>`;
    html += `<table style="width:100%;margin-top:15px;"><thead><tr><th>Товар</th><th>Кол-во</th></tr></thead><tbody>`;
    currentOrder.items.forEach(item => html += `<tr><td>${item.name}</td><td style="text-align:right">${item.qty} ${item.unit}</td></tr>`);
    html += `</tbody></table>`;
    if (currentOrder.comment !== '—') html += `<p style="margin-top:15px;"><strong>Комментарий:</strong> ${currentOrder.comment}</p>`;
    document.getElementById('detailContent').innerHTML = html;
    showPage('detail');
}

function downloadExcel() {
    if (!currentOrder) return;
    let csv = "№;Наименование;Ед.изм;Кол-во\n";
    currentOrder.items.forEach((item, i) => csv += `${i+1};${item.name};${item.unit};${item.qty}\n`);
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${currentOrder.id}.csv`;
    link.click();
    showMessage('✅ Excel скачан', 'success');
}

function printToPDF() {
    if (!currentOrder) return;
    const win = window.open('', '_blank');
    win.document.write(`
        <div style="padding:30px;font-family:Arial;max-width:800px;margin:auto;">
            <h2 style="text-align:center;">АКТ приема-передачи товара</h2>
            <p style="text-align:center;">№ ${currentOrder.id} от ${currentOrder.date}</p>
            <table border="1" style="width:100%;border-collapse:collapse;margin-top:30px;">
                <tr><th>Товар</th><th>Кол-во</th></tr>
                ${currentOrder.items.map(item => `<tr><td>${item.name}</td><td style="text-align:center">${item.qty} ${item.unit}</td></tr>`).join('')}
            </table>
        </div>
    `);
    win.document.close();
    win.print();
}

function showMessage(text, type) {
    const msg = document.getElementById('message');
    msg.innerHTML = text;
    msg.className = `message ${type}`;
    setTimeout(() => msg.className = 'message', 5000);
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
    print("\n🛡️ ARMOR HAND Cloud v6.3 FINAL — полностью рабочий + сохранение документов")
    app.run(host='0.0.0.0', port=port, debug=False)
