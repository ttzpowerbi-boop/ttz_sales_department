"""
🛡️ ARMOR HAND - Облачный Mini App на Render
Красивая форма предзаказа с интеграцией локального API через ngrok
"""

import os
import json
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# HTML форма (встроенная)
MINI_APP_HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARMOR HAND - Форма предзаказа</title>
    <script src="https://telegram.org/js/telegram-web-app.js" async></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #333; padding-bottom: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; }
        
        .header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
        .header-center { flex: 1; text-align: center; }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .header p { font-size: 14px; opacity: 0.9; }
        
        .badge { background: #ff6b6b; color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; cursor: pointer; }
        .badge.hidden { display: none; }
        
        .content { padding: 20px; }
        .page { display: none; }
        .page.active { display: block; }
        
        .section { margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #e0e0e0; }
        .section:last-child { border-bottom: none; }
        .section h3 { color: #1e3c72; font-size: 16px; margin-bottom: 15px; }
        
        .search-container { display: flex; gap: 10px; }
        .search-input { flex: 1; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; }
        .search-btn { padding: 12px 20px; background: #2a5298; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .search-btn:disabled { background: #ccc; cursor: not-allowed; }
        
        .products-list { display: flex; flex-direction: column; gap: 10px; max-height: 300px; overflow-y: auto; margin-top: 15px; }
        .product-item { padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; }
        .product-item:hover { border-color: #2a5298; background: #f0f2f5; }
        .product-name { font-weight: 600; color: #1e3c72; font-size: 13px; }
        .product-unit { font-size: 12px; color: #666; margin-top: 5px; }
        
        .quantity-section { background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .quantity-label { font-size: 14px; font-weight: 600; margin-bottom: 10px; }
        .quantity-controls { display: flex; align-items: center; gap: 10px; }
        .qty-btn { width: 36px; height: 36px; border: 2px solid #2a5298; background: white; color: #2a5298; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .qty-input { flex: 1; padding: 8px; border: 2px solid #ddd; border-radius: 6px; text-align: center; font-weight: 600; }
        
        .cart-summary { background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196f3; margin-bottom: 20px; }
        .summary-row { display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px; font-weight: 600; }
        
        .empty-message { text-align: center; padding: 40px 20px; color: #999; }
        .buttons { display: flex; gap: 10px; margin-top: 20px; }
        .btn-primary { flex: 1; padding: 14px; background: #4caf50; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .btn-primary:disabled { background: #ccc; cursor: not-allowed; }
        .btn-secondary { flex: 1; padding: 14px; background: #757575; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .btn-back { padding: 10px 15px; background: #757575; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 13px; }
        
        .message { padding: 12px; border-radius: 8px; margin-bottom: 15px; display: none; text-align: center; font-weight: 600; }
        .message.success { background: #c8e6c9; color: #2e7d32; display: block; }
        .message.error { background: #ffcdd2; color: #c62828; display: block; }
        .message.loading { background: #e0e0e0; color: #333; display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div id="backBtnHeader" style="display: none; cursor: pointer; font-size: 16px;" onclick="goBack()">← Назад</div>
            <div class="header-center">
                <h1>🛡️ ARMOR HAND</h1>
                <p id="headerSubtitle">Форма предзаказа</p>
            </div>
            <div id="cartBadgeContainer" class="badge hidden" onclick="goToCart()">
                <span id="cartBadge">0</span>
            </div>
        </div>
        
        <div class="content">
            <div id="message" class="message"></div>
            
            <div id="searchPage" class="page active">
                <div class="section">
                    <h3>📦 Поиск товаров</h3>
                    <div class="search-container">
                        <input type="text" id="searchInput" class="search-input" placeholder="Размер, тип, ГОСТ...">
                        <button class="search-btn" id="searchBtn" onclick="searchProducts()">Найти</button>
                    </div>
                    <div id="productsList" class="products-list" style="display: none;"></div>
                </div>
            </div>
            
            <div id="detailPage" class="page">
                <div class="buttons" style="margin-top: 0;">
                    <button class="btn-back" onclick="goBackFromDetail()">← Назад</button>
                </div>
                <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 id="detailProductName" style="color: #1e3c72; font-size: 18px; margin-bottom: 15px; word-break: break-word;"></h2>
                    <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #2a5298;">
                        <div style="display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px;">
                            <span style="font-weight: 600; color: #666;">Единица:</span>
                            <span id="detailProductUnit" style="color: #333; font-weight: 600;">-</span>
                        </div>
                    </div>
                </div>
                <div class="quantity-section">
                    <div class="quantity-label">Укажите количество:</div>
                    <div class="quantity-controls">
                        <button class="qty-btn" onclick="decreaseQty()">−</button>
                        <input type="number" id="qtyInput" class="qty-input" value="1" min="1">
                        <button class="qty-btn" onclick="increaseQty()">+</button>
                    </div>
                    <div style="margin-top: 10px; display: flex; gap: 10px;">
                        <button class="btn-secondary" style="margin: 0;" onclick="goBackFromDetail()">Отмена</button>
                        <button class="btn-primary" style="margin: 0;" onclick="addToOrder()">Добавить</button>
                    </div>
                </div>
            </div>
            
            <div id="cartPage" class="page">
                <div class="buttons" style="margin-top: 0; margin-bottom: 20px;">
                    <button class="btn-back" onclick="goBackToSearch()">← Продолжить покупки</button>
                </div>
                <h3 style="margin-bottom: 20px;">🛒 Ваша корзина</h3>
                <div class="cart-summary">
                    <div class="summary-row">
                        <span>Всего единиц:</span>
                        <span id="cartTotalItems">0</span>
                    </div>
                    <div class="summary-row">
                        <span>Позиций:</span>
                        <span id="cartTotalPositions">0</span>
                    </div>
                </div>
                <div class="section" style="border-bottom: none;">
                    <h3>📋 Выбранные товары</h3>
                    <div id="cartItems"></div>
                </div>
                <div class="buttons">
                    <button class="btn-secondary" onclick="clearOrder()">Очистить</button>
                    <button class="btn-primary" id="submitBtn" onclick="submitOrder()">Отправить</button>
                </div>
            </div>
            
            <div id="summaryPage" class="page">
                <h3 style="margin-bottom: 20px;">✅ Заказ отправлен!</h3>
                <div class="cart-summary">
                    <div class="summary-row">
                        <span>Позиций:</span>
                        <span id="summaryPositions">0</span>
                    </div>
                </div>
                <div class="section">
                    <h3>📦 Выбранные товары</h3>
                    <table style="width: 100%; border-collapse: collapse;" id="summaryTable"></table>
                </div>
                <div class="buttons">
                    <button class="btn-primary" onclick="startOver()">Новый заказ</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let tg = window.Telegram?.WebApp;
        let allProducts = [];
        let selectedProduct = null;
        let orders = [];
        
        if (tg) {
            tg.ready();
            tg.expand();
            tg.setBackgroundColor('#f0f2f5');
        }
        
        function showPage(pageName) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(pageName).classList.add('active');
        }
        
        function goBack() { showPage('searchPage'); document.getElementById('backBtnHeader').style.display = 'none'; }
        function goBackFromDetail() { showPage('searchPage'); document.getElementById('backBtnHeader').style.display = 'none'; }
        function goToDetail() { showPage('detailPage'); document.getElementById('backBtnHeader').style.display = 'block'; }
        function goToCart() { showPage('cartPage'); updateCartDisplay(); document.getElementById('backBtnHeader').style.display = 'block'; }
        function goBackToSearch() { showPage('searchPage'); document.getElementById('backBtnHeader').style.display = 'none'; }
        
        async function searchProducts() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) { showMessage('Введите название товара', 'error'); return; }
            
            const btn = document.getElementById('searchBtn');
            btn.disabled = true;
            btn.textContent = 'Поиск...';
            
            try {
                showMessage('⏳ Поиск товаров...', 'loading');
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                if (data.error) {
                    showMessage('❌ ' + data.error, 'error');
                    allProducts = [];
                } else if (data.products && data.products.length > 0) {
                    allProducts = data.products;
                    displayProducts(data.products);
                    showMessage('✅ Найдено ' + data.products.length + ' товаров', 'success');
                } else {
                    showMessage('❌ Товары не найдены', 'error');
                    allProducts = [];
                    document.getElementById('productsList').style.display = 'none';
                }
            } catch (error) {
                showMessage('❌ Ошибка подключения', 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Найти';
            }
        }
        
        function displayProducts(products) {
            const container = document.getElementById('productsList');
            if (products.length === 0) { container.style.display = 'none'; return; }
            container.innerHTML = products.map((p, idx) => `
                <div class="product-item" onclick="selectProduct(${idx})">
                    <div class="product-name">${p.name}</div>
                    <div class="product-unit">Единица: <strong>${p.unit || 'шт'}</strong></div>
                </div>
            `).join('');
            container.style.display = 'flex';
        }
        
        function selectProduct(index) {
            selectedProduct = allProducts[index];
            document.getElementById('detailProductName').textContent = selectedProduct.name;
            document.getElementById('detailProductUnit').textContent = selectedProduct.unit || 'шт';
            document.getElementById('qtyInput').value = '1';
            goToDetail();
        }
        
        function increaseQty() { const input = document.getElementById('qtyInput'); input.value = parseInt(input.value) + 1; }
        function decreaseQty() { const input = document.getElementById('qtyInput'); if (parseInt(input.value) > 1) input.value = parseInt(input.value) - 1; }
        
        function addToOrder() {
            if (!selectedProduct) return;
            const quantity = parseInt(document.getElementById('qtyInput').value);
            const exists = orders.find(o => o.id === selectedProduct.id);
            if (exists) { exists.quantity += quantity; } else {
                orders.push({ id: selectedProduct.id, name: selectedProduct.name, unit: selectedProduct.unit || 'шт', quantity: quantity });
            }
            updateCartBadge();
            showMessage('✅ Товар добавлен', 'success');
            goBackFromDetail();
        }
        
        function updateCartBadge() {
            const total = orders.reduce((sum, item) => sum + item.quantity, 0);
            const badge = document.getElementById('cartBadge');
            const container = document.getElementById('cartBadgeContainer');
            if (total > 0) { badge.textContent = total; container.classList.remove('hidden'); } else { container.classList.add('hidden'); }
        }
        
        function updateCartDisplay() {
            const container = document.getElementById('cartItems');
            if (orders.length === 0) { container.innerHTML = '<div class="empty-message">Товары не выбраны</div>'; document.getElementById('submitBtn').disabled = true; return; }
            
            let html = '<table style="width: 100%; border-collapse: collapse;"><tr style="background: #e3f2fd;"><th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: 600; font-size: 13px;">Товар</th><th style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: 600; font-size: 13px;">Кол-во</th><th style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: 600; font-size: 13px;">Удал.</th></tr>';
            orders.forEach((item) => {
                html += `<tr><td style="border: 1px solid #ddd; padding: 10px; font-size: 12px;">${item.name}</td><td style="border: 1px solid #ddd; padding: 10px; text-align: center; font-weight: 600; font-size: 13px;">${item.quantity} ${item.unit}</td><td style="border: 1px solid #ddd; padding: 8px; text-align: center;"><button onclick="removeFromOrder('${item.id}')" style="padding: 6px 12px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: 600;">✕</button></td></tr>`;
            });
            html += '</table>';
            container.innerHTML = html;
            const totalItems = orders.reduce((sum, item) => sum + item.quantity, 0);
            document.getElementById('cartTotalItems').textContent = totalItems;
            document.getElementById('cartTotalPositions').textContent = orders.length;
            document.getElementById('submitBtn').disabled = false;
        }
        
        function removeFromOrder(id) { orders = orders.filter(item => item.id !== id); updateCartDisplay(); updateCartBadge(); showMessage('🗑️ Товар удален', 'success'); }
        function clearOrder() { if (confirm('Очистить корзину?')) { orders = []; updateCartDisplay(); updateCartBadge(); showMessage('🗑️ Корзина очищена', 'success'); } }
        
        function submitOrder() {
            if (orders.length === 0) { showMessage('Добавьте товары', 'error'); return; }
            const orderData = {
                action: 'order',
                items: orders.map(item => ({ product: item.name, quantity: item.quantity, unit: item.unit })),
                timestamp: new Date().toLocaleString('ru-RU')
            };
            if (tg && typeof tg.sendData === 'function') {
                try { tg.sendData(JSON.stringify(orderData)); showSummary(); } catch (error) { showMessage('❌ Ошибка при отправке', 'error'); }
            } else { showSummary(); }
        }
        
        function showSummary() {
            const container = document.getElementById('summaryTable');
            container.innerHTML = orders.map((item) => `<tr><td style="border: 1px solid #ddd; padding: 10px;">${item.name}</td><td style="border: 1px solid #ddd; padding: 10px;">${item.quantity} ${item.unit}</td></tr>`).join('');
            document.getElementById('summaryPositions').textContent = orders.length;
            showPage('summaryPage');
        }
        
        function startOver() { orders = []; updateCartBadge(); document.getElementById('searchInput').value = ''; document.getElementById('message').className = 'message'; goBack(); }
        function showMessage(text, type = 'info') { const msgEl = document.getElementById('message'); msgEl.textContent = text; msgEl.className = 'message ' + type; setTimeout(() => { msgEl.className = 'message'; }, 4000); }
        
        document.getElementById('searchInput').addEventListener('keypress', function(e) { if (e.key === 'Enter') searchProducts(); });
        updateCartBadge();
    </script>
</body>
</html>'''

@app.route('/webapp', methods=['GET'])
def webapp():
    """Возвращает HTML Mini App"""
    return render_template_string(MINI_APP_HTML)

@app.route('/api/search', methods=['POST'])
def search():
    """Прокси для локального API через ngrok туннель"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "Пустой запрос", "products": []})
        
        print(f"🌐 Облако: получен запрос '{query}'")
        
        import requests
        try:
            response = requests.post(
                'https://criteria-waviness-entangled.ngrok-free.dev/api/search',
                json={'query': query},
                timeout=10,
                verify=False  # Отключаем проверку SSL для ngrok
            )
            result = response.json()
            print(f"✅ Облако: получен ответ с {len(result.get('products', []))} товарами")
            return jsonify(result)
        except Exception as e:
            print(f"⚠️ Ошибка туннеля: {e}")
            return jsonify({
                "error": "⚠️ Локальный сервер недоступен. Убедитесь что ngrok туннель запущен",
                "products": []
            })
    except Exception as e:
        print(f"❌ Ошибка облака: {e}")
        return jsonify({"error": f"Ошибка сервера: {str(e)}", "products": []})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "location": "cloud", "tunnel": "ngrok"})

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "ARMOR HAND Online", "version": "3.0"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*70)
    print("🛡️  ARMOR HAND - Облачный Mini App на Render v3.0".center(70))
    print("="*70)
    print(f"✅ Mini App: https://ttz-sales-department.onrender.com/webapp")
    print(f"🌐 Туннель: https://criteria-waviness-entangled.ngrok-free.dev")
    print("✅ Красивая форма предзаказа с полным функционалом")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=port, debug=False)
