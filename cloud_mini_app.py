"""
🛡️ ARMOR HAND - Облачный Mini App на Render v4.2
Исправлено: кнопки редактирования и удаления в корзине + нормальный flow
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
        .section { margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #e0e0e0; }
        .section h3 { color: #1e3c72; font-size: 16px; margin-bottom: 15px; }
        
        .search-box { display: flex; gap: 10px; }
        .search-input { flex: 1; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; }
        .search-btn { padding: 12px 20px; background: #2a5298; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        
        .products { display: flex; flex-direction: column; gap: 10px; max-height: 350px; overflow-y: auto; margin-top: 15px; }
        .product { padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; }
        .product:hover { border-color: #2a5298; background: #f0f2f5; }
        .product-name { font-weight: 600; color: #1e3c72; }
        
        .quantity-controls { display: flex; align-items: center; gap: 10px; margin: 15px 0; }
        .qty-btn { width: 40px; height: 40px; border: 2px solid #2a5298; background: white; color: #2a5298; border-radius: 8px; font-size: 20px; cursor: pointer; }
        .qty-input { flex: 1; padding: 10px; text-align: center; font-size: 18px; border: 2px solid #ddd; border-radius: 8px; }
        
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #e3f2fd; }
        .action-btn { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .edit-btn { background: #2196f3; color: white; }
        .remove-btn { background: #f44336; color: white; }
        
        .message { padding: 12px; border-radius: 8px; margin-bottom: 15px; display: none; text-align: center; font-weight: 600; }
        .message.success { background: #c8e6c9; color: #2e7d32; display: block; }
        .message.error { background: #ffcdd2; color: #c62828; display: block; }
        
        .buttons { display: flex; gap: 10px; margin-top: 20px; }
        .btn { flex: 1; padding: 14px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .btn-primary { background: #4caf50; color: white; }
        .btn-secondary { background: #757575; color: white; }
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
                <div class="section">
                    <h3>📦 Поиск товаров</h3>
                    <div class="search-box">
                        <input type="text" id="searchInput" class="search-input" placeholder="Размер, тип, ГОСТ...">
                        <button class="search-btn" onclick="searchProducts()">Найти</button>
                    </div>
                    <div id="productsList" class="products" style="display:none;"></div>
                </div>
            </div>
            
            <!-- Детальный просмотр товара -->
            <div id="detailPage" class="page">
                <button class="btn btn-secondary" onclick="goBack()" style="margin-bottom:15px;">← Назад</button>
                <div class="section">
                    <h3 id="detailName"></h3>
                    <div class="quantity-controls">
                        <button class="qty-btn" onclick="changeQty(-1)">−</button>
                        <input type="number" id="qtyInput" class="qty-input" value="1" min="1">
                        <button class="qty-btn" onclick="changeQty(1)">+</button>
                    </div>
                    <div class="buttons">
                        <button class="btn btn-secondary" onclick="goBack()">Отмена</button>
                        <button class="btn btn-primary" onclick="addToCart()">Добавить в корзину</button>
                    </div>
                </div>
            </div>
            
            <!-- Корзина -->
            <div id="cartPage" class="page">
                <button class="btn btn-secondary" onclick="goBackToSearch()" style="margin-bottom:15px;">← Продолжить покупки</button>
                <h3>🛒 Корзина</h3>
                <table id="cartTable">
                    <thead><tr><th>Товар</th><th>Кол-во</th><th>Ред.</th><th>Удал.</th></tr></thead>
                    <tbody id="cartBody"></tbody>
                </table>
                <div class="buttons">
                    <button class="btn btn-secondary" onclick="clearCart()">Очистить</button>
                    <button class="btn btn-primary" onclick="goToCheckout()">Отправить заказ</button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
let tg = null;
let cart = [];
let selectedProduct = null;

function initApp() {
    if (typeof Telegram !== 'undefined' && Telegram.WebApp && Telegram.WebApp.initData && Telegram.WebApp.initData.length > 10) {
        tg = Telegram.WebApp;
        tg.ready();
        tg.expand();
        document.querySelector('.app').style.display = 'block';
        document.getElementById('error-screen').style.display = 'none';
        console.log('✅ Запущено внутри Telegram');
    } else {
        document.getElementById('error-screen').style.display = 'flex';
    }
}
window.onload = () => setTimeout(initApp, 600);

function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(page + 'Page').classList.add('active');
    document.getElementById('headerTitle').textContent = page === 'search' ? 'Форма предзаказа' : 'Ваша корзина';
}

function searchProducts() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return showMessage('Введите запрос', 'error');
    
    fetch('/api/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query})
    })
    .then(r => r.json())
    .then(data => {
        if (data.products && data.products.length > 0) {
            let html = '';
            data.products.forEach((p, i) => {
                html += `<div class="product" onclick="selectProduct(${i}, '${p.name}', '${p.unit || "шт"}')">
                    <div class="product-name">${p.name}</div>
                </div>`;
            });
            document.getElementById('productsList').innerHTML = html;
            document.getElementById('productsList').style.display = 'block';
        } else {
            showMessage('Товары не найдены', 'error');
        }
    })
    .catch(() => showMessage('Ошибка соединения', 'error'));
}

function selectProduct(index, name, unit) {
    selectedProduct = {name, unit};
    document.getElementById('detailName').textContent = name;
    document.getElementById('qtyInput').value = 1;
    showPage('detail');
}

function changeQty(delta) {
    let val = parseInt(document.getElementById('qtyInput').value) || 1;
    val = Math.max(1, val + delta);
    document.getElementById('qtyInput').value = val;
}

function addToCart() {
    if (!selectedProduct) return;
    const qty = parseInt(document.getElementById('qtyInput').value) || 1;
    
    const existing = cart.find(item => item.name === selectedProduct.name);
    if (existing) {
        existing.qty += qty;
    } else {
        cart.push({name: selectedProduct.name, qty: qty, unit: selectedProduct.unit});
    }
    
    showMessage('✅ Добавлено в корзину', 'success');
    updateCart();
    showPage('search');
}

function updateCart() {
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
    selectedProduct = {name: cart[index].name, unit: cart[index].unit};
    document.getElementById('qtyInput').value = cart[index].qty;
    document.getElementById('detailName').textContent = cart[index].name;
    showPage('detail');
}

function removeItem(index) {
    if (confirm('Удалить товар?')) {
        cart.splice(index, 1);
        updateCart();
        showMessage('🗑️ Удалено', 'success');
    }
}

function clearCart() {
    if (confirm('Очистить всю корзину?')) {
        cart = [];
        updateCart();
    }
}

function goToCheckout() {
    if (cart.length === 0) return showMessage('Корзина пуста', 'error');
    if (tg && tg.sendData) {
        tg.sendData(JSON.stringify({items: cart}));
        showMessage('✅ Заказ отправлен!', 'success');
        setTimeout(() => {
            cart = [];
            updateCart();
            showPage('search');
        }, 1500);
    }
}

function goBack() { showPage('search'); }
function goBackToSearch() { showPage('search'); }

function showMessage(text, type) {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.className = `message ${type}`;
    setTimeout(() => msg.className = 'message', 3000);
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
        return jsonify({"error": "Сервер недоступен", "products": []})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n🛡️ ARMOR HAND v4.2 — кнопки редактирования восстановлены")
    app.run(host='0.0.0.0', port=port, debug=False)
