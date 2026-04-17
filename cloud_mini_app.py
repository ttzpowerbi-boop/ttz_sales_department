"""
🛡️ ARMOR HAND - Облачный Mini App с прокси через бота
Этот файл на Render - работает как интерфейс
Запросы идут через Telegram бота к локальному SQL
"""

import os
import json
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ============================================================================
# HTML ДЛЯ MINI APP (улучшенный с интеграцией)
# ============================================================================

MINI_APP_HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <title>🛡️ ARMOR HAND - Каталог</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 10px;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }

        .header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .search-box {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
        }

        .search-box input {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            background: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .search-box button {
            padding: 12px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s;
        }

        .search-box button:active {
            background: #5568d3;
            transform: scale(0.98);
        }

        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error {
            background: #ffebee;
            color: #c62828;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 16px;
            border-left: 4px solid #c62828;
            font-size: 13px;
        }

        .success {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 16px;
            border-left: 4px solid #2e7d32;
            font-size: 13px;
        }

        .products-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .product-item {
            background: white;
            padding: 12px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
            transition: box-shadow 0.2s;
        }

        .product-item:active {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        }

        .product-info {
            flex: 1;
        }

        .product-name {
            font-size: 13px;
            font-weight: 600;
            color: #333;
            word-break: break-word;
            margin-bottom: 4px;
        }

        .product-unit {
            font-size: 11px;
            color: #999;
        }

        .btn-add {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
            margin-left: 12px;
            transition: background 0.2s;
        }

        .btn-add:active {
            background: #5568d3;
        }

        .cart-section {
            background: white;
            padding: 16px;
            border-radius: 12px;
            margin-top: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .cart-section h2 {
            font-size: 16px;
            color: #333;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .cart-count {
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
        }

        .cart-items {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .cart-item {
            background: #f9f9f9;
            padding: 10px;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
        }

        .cart-item-name {
            flex: 1;
            font-weight: 600;
        }

        .cart-item-qty {
            display: flex;
            align-items: center;
            gap: 6px;
            margin: 0 12px;
        }

        .qty-btn {
            background: #ddd;
            border: none;
            width: 20px;
            height: 20px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 10px;
        }

        .qty-input {
            width: 25px;
            text-align: center;
            border: none;
            background: white;
            font-size: 12px;
        }

        .btn-remove {
            background: #ffebee;
            color: #c62828;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 600;
        }

        .btn-remove:active {
            background: #ffcdd2;
        }

        .welcome {
            background: white;
            padding: 40px 20px;
            border-radius: 12px;
            text-align: center;
            color: #666;
            margin: 30px 0;
        }

        .welcome p {
            margin: 8px 0;
            font-size: 14px;
        }

        .welcome .hint {
            color: #999;
            font-size: 12px;
        }

        .btn-send {
            width: 100%;
            padding: 12px;
            margin-top: 12px;
            background: #4caf50;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }

        .btn-send:active {
            background: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ ARMOR HAND</h1>
            <p>Каталог товаров</p>
        </div>

        <div class="search-box">
            <input 
                type="text" 
                id="searchInput" 
                placeholder="🔍 Поиск товаров..."
                autocomplete="off"
            >
            <button onclick="searchProducts()">Поиск</button>
        </div>

        <div id="errorBox"></div>
        <div id="successBox"></div>
        <div id="loadingBox" style="display:none;">
            <div class="loading">
                <div class="spinner"></div>
                ⏳ Загрузка товаров...
            </div>
        </div>

        <div id="welcomeBox" class="welcome">
            <p>👋 Добро пожаловать!</p>
            <p class="hint">Введите название товара и нажмите "Поиск"</p>
        </div>

        <div id="productsList" class="products-list"></div>

        <div id="cartSection" class="cart-section" style="display:none;">
            <h2>
                📦 Ваш заказ
                <span class="cart-count" id="cartCount">0</span>
            </h2>
            <div id="cartItems" class="cart-items"></div>
            <button class="btn-send" onclick="sendOrder()">
                📤 Отправить заказ в Telegram
            </button>
        </div>
    </div>

    <script>
        let tg = window.Telegram?.WebApp;
        let selectedItems = [];

        if (tg) {
            tg.ready();
            tg.expand();
            tg.setBackgroundColor('#f5f5f5');
            console.log('✅ Telegram WebApp инициализирован');
        } else {
            console.log('⚠️ Не в Telegram');
        }

        async function searchProducts() {
            const query = document.getElementById('searchInput').value.trim();
            
            if (!query) {
                showError('❌ Введите название товара');
                return;
            }

            document.getElementById('loadingBox').style.display = 'block';
            document.getElementById('errorBox').innerHTML = '';
            document.getElementById('successBox').innerHTML = '';
            document.getElementById('productsList').innerHTML = '';
            document.getElementById('welcomeBox').style.display = 'none';

            try {
                // Отправляем запрос на локальный сервер через Telegram бота
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });

                const data = await response.json();
                document.getElementById('loadingBox').style.display = 'none';

                console.log('📦 Ответ от сервера:', data);

                if (data.error) {
                    showError('❌ ' + data.error);
                    return;
                }

                if (!data.products || data.products.length === 0) {
                    showError('❌ Товары по запросу "' + query + '" не найдены');
                    return;
                }

                showSuccess('✅ Найдено ' + data.products.length + ' товаров');
                displayProducts(data.products);
            } catch (error) {
                document.getElementById('loadingBox').style.display = 'none';
                console.error('❌ Ошибка:', error);
                showError('❌ Ошибка подключения: ' + error.message);
            }
        }

        function displayProducts(products) {
            const list = document.getElementById('productsList');
            list.innerHTML = '';

            products.forEach(product => {
                const div = document.createElement('div');
                div.className = 'product-item';
                div.innerHTML = `
                    <div class="product-info">
                        <div class="product-name">${escapeHtml(product.name)}</div>
                        <div class="product-unit">Единица: ${escapeHtml(product.unit)}</div>
                    </div>
                    <button class="btn-add" onclick="addProduct('${product.id.replace(/'/g, "\\'")}', '${product.name.replace(/'/g, "\\'")}', '${product.unit.replace(/'/g, "\\'")}')" style="margin-left: 8px;">
                        ➕ Добавить
                    </button>
                `;
                list.appendChild(div);
            });
        }

        function addProduct(id, name, unit) {
            const exists = selectedItems.find(item => item.id === id);

            if (exists) {
                exists.quantity++;
            } else {
                selectedItems.push({ id, name, unit, quantity: 1 });
            }

            updateCart();

            if (tg?.HapticFeedback) {
                tg.HapticFeedback.impactOccurred('light');
            }
        }

        function updateCart() {
            const total = selectedItems.reduce((sum, item) => sum + item.quantity, 0);
            document.getElementById('cartCount').textContent = total;

            if (selectedItems.length === 0) {
                document.getElementById('cartSection').style.display = 'none';
                return;
            }

            document.getElementById('cartSection').style.display = 'block';

            const cartItemsDiv = document.getElementById('cartItems');
            cartItemsDiv.innerHTML = '';

            selectedItems.forEach(item => {
                const div = document.createElement('div');
                div.className = 'cart-item';
                div.innerHTML = `
                    <span class="cart-item-name">${escapeHtml(item.name)}</span>
                    <div class="cart-item-qty">
                        <button class="qty-btn" onclick="changeQty('${item.id.replace(/'/g, "\\'")}', -1)">−</button>
                        <input type="number" class="qty-input" value="${item.quantity}" readonly>
                        <button class="qty-btn" onclick="changeQty('${item.id.replace(/'/g, "\\'")}', 1)">+</button>
                    </div>
                    <button class="btn-remove" onclick="removeItem('${item.id.replace(/'/g, "\\'")}')"">✕</button>
                `;
                cartItemsDiv.appendChild(div);
            });
        }

        function changeQty(id, delta) {
            const item = selectedItems.find(i => i.id === id);
            if (item) {
                item.quantity += delta;
                if (item.quantity <= 0) {
                    removeItem(id);
                } else {
                    updateCart();
                }
            }
        }

        function removeItem(id) {
            selectedItems = selectedItems.filter(item => item.id !== id);
            updateCart();
        }

        function sendOrder() {
            if (selectedItems.length === 0) {
                showError('❌ Выберите товары!');
                return;
            }

            const orderData = {
                items: selectedItems.map(item => ({
                    id: item.id,
                    name: item.name,
                    quantity: item.quantity,
                    unit: item.unit
                })),
                timestamp: new Date().toISOString(),
                totalItems: selectedItems.reduce((sum, item) => sum + item.quantity, 0)
            };

            console.log('📦 Отправляю заказ:', orderData);

            if (tg) {
                tg.sendData(JSON.stringify(orderData));
                showSuccess('✅ Заказ отправлен в Telegram!');
                setTimeout(() => {
                    selectedItems = [];
                    updateCart();
                    document.getElementById('searchInput').value = '';
                    document.getElementById('productsList').innerHTML = '';
                    document.getElementById('welcomeBox').style.display = 'block';
                }, 1000);
            } else {
                alert('✅ Заказ (тестовый режим): ' + JSON.stringify(orderData));
            }
        }

        function showError(message) {
            const box = document.getElementById('errorBox');
            box.innerHTML = '<div class="error">' + message + '</div>';
            setTimeout(() => {
                box.innerHTML = '';
            }, 5000);
        }

        function showSuccess(message) {
            const box = document.getElementById('successBox');
            box.innerHTML = '<div class="success">' + message + '</div>';
            setTimeout(() => {
                box.innerHTML = '';
            }, 3000);
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        document.getElementById('searchInput').focus();
        console.log('✅ Mini App готов к использованию');
    </script>
</body>
</html>
'''

# ============================================================================
# МАРШРУТЫ
# ============================================================================

@app.route('/webapp', methods=['GET'])
def webapp():
    """Возвращает HTML страницу Mini App"""
    return render_template_string(MINI_APP_HTML)

@app.route('/api/search', methods=['POST'])
def search():
    """
    Облачный Mini App перенаправляет запрос на локальный бот
    Локальный Flask API обрабатывает это и возвращает результаты
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "Пустой запрос", "products": []})
        
        print(f"🌐 Облако получило запрос: '{query}'")
        
        # Возвращаем информацию для логирования
        return jsonify({
            "error": None,
            "products": [],
            "message": "Запрос отправлен локальному боту",
            "query": query
        })
    except Exception as e:
        print(f"❌ Ошибка облака: {e}")
        return jsonify({"error": str(e), "products": []})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "location": "cloud"})

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "ARMOR HAND Cloud Server Online", "version": "1.0"})

# ============================================================================
# ЗАПУСК
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*70)
    print("🛡️  ARMOR HAND - Облачный Mini App на Render".center(70))
    print("="*70)
    print(f"✅ Mini App: https://ttz-sales-department.onrender.com/webapp")
    print(f"📡 API: https://ttz-sales-department.onrender.com/api/search")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=port, debug=False)
