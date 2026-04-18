"""
🛡️ ARMOR HAND - Облачный Mini App v5.6
Простая версия без строгой проверки — должна открываться из бота
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
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #f0f2f5; 
            color: #333; 
            height: 100vh; 
            overflow: hidden; 
            margin: 0;
        }
        
        #error-screen { 
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            display: none; 
            align-items: center; 
            justify-content: center; 
            z-index: 9999; 
            padding: 20px; 
            color: white;
            text-align: center;
        }
        
        .app { display: block; } /* Показываем сразу */
        .container { 
            max-width: 600px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 12px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
            overflow: hidden; 
            min-height: 100vh; 
        }
        .header { 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
            color: white; 
            padding: 20px; 
            text-align: center; 
        }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .content { padding: 20px; }
        .page { display: none; }
        .page.active { display: block; }
        
        .search-box { display: flex; gap: 10px; }
        .search-input { flex: 1; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; }
        .search-btn { padding: 12px 20px; background: #2a5298; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        
        .products { display: flex; flex-direction: column; gap: 10px; max-height: 420px; overflow-y: auto; margin-top: 15px; }
        .product { 
            padding: 14px; 
            border: 2px solid #e0e0e0; 
            border-radius: 10px; 
            cursor: pointer; 
            background: white;
        }
        .product:hover { border-color: #2a5298; background: #f8f9ff; }
        .product-name { font-weight: 600; color: #1e3c72; line-height: 1.4; }
        
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; }
        th { background: #e3f2fd; font-weight: 600; }
        .action-btn { 
            padding: 8px 12px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 16px; 
            width: 40px;
        }
        .edit-btn { background: #2196f3; color: white; }
        .remove-btn { background: #f44336; color: white; }
        
        .message { 
            padding: 12px; 
            border-radius: 8px; 
            margin-bottom: 15px; 
            display: none; 
            text-align: center; 
            font-weight: 600; 
        }
        .message.success { background: #c8e6c9; color: #2e7d32; display: block; }
        .message.error { background: #ffcdd2; color: #c62828; display: block; }
        
        .buttons { display: flex; gap: 10px; margin-top: 20px; }
        .btn { flex: 1; padding: 14px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; color: white; }
        .btn-primary { background: #4caf50; }
        .btn-secondary { background: #757575; }
    </style>
</head>
<body>

<div id="error-screen">
    <div class="error-box">
        <h2>🔒 Доступ запрещён</h2>
        <p>Это приложение работает <strong>только внутри Telegram</strong>.</p>
        <p>Откройте его через бота:</p>
        <p><strong>@TTZ_Sales_Department_bot</strong></p>
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
        </div>
    </div>
</div>

<script>
let tg = null;
let cart = [];

// Простая инициализация
function startApp() {
    if (window.Telegram && window.Telegram.WebApp) {
        tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();
        console.log("✅ Telegram WebApp инициализирован");
    } else {
        console.log("⚠️ Запущено не в Telegram");
    }
    
    // Показываем приложение в любом случае
    document.querySelector('.app').style.display = 'block';
    document.getElementById('error-screen').style.display = 'none';
}

window.onload = startApp;

function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(page + 'Page').classList.add('active');
    document.getElementById('headerTitle').textContent = page === 'search' ? 'Форма предзаказа' : 'Ваша корзина';
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
        list.innerHTML = '';
        
        if (data.products && data.products.length > 0) {
            data.products.forEach(p => {
                const div = document.createElement('div');
                div.className = 'product';
                div.innerHTML = `<div class="product-name">${p.name}</div>`;
                div.onclick = () => addToCart(p.name, p.unit || 'шт');
                list.appendChild(div);
            });
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
    
    showMessage('✅ Товар добавлен в корзину', 'success');
    updateCartDisplay();
    showPage('cart');
}

function updateCartDisplay() {
    let html = '';
    cart.forEach((item, index) => {
        html += `<tr>
            <td>${item.name}</td>
            <td style="text-align:center; font-weight:600;">${item.qty}</td>
            <td style="text-align:center"><button class="action-btn edit-btn" onclick="editItem(${index})">✎</button></td>
            <td style="text-align:center"><button class="action-btn remove-btn" onclick="removeItem(${index})">✕</button></td>
        </tr>`;
    });
    document.getElementById('cartBody').innerHTML = html || '<tr><td colspan="4" style="text-align:center;color:#999;padding:40px;">Корзина пуста</td></tr>';
}

function editItem(index) {
    const newQty = prompt(`Новое количество для:\n${cart[index].name}`, cart[index].qty);
    if (newQty && !isNaN(newQty) && parseInt(newQty) > 0) {
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
    alert('Предварительный просмотр будет добавлен позже.\n\nВ корзине сейчас ' + cart.length + ' позиций.');
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
    print("\n🛡️ ARMOR HAND Cloud v5.6 — простая версия без строгой проверки")
    app.run(host='0.0.0.0', port=port, debug=False)
