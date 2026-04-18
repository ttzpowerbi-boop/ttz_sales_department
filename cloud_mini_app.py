"""
🛡️ ARMOR HAND - Облачный Mini App на Render v3.4
✅ ИСПРАВЛЕНА проверка Telegram (больше не закрывается)
"""

import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

MINI_APP_HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARMOR HAND - Форма предзаказа</title>
    <script src="https://telegram.org/js/telegram-web-app.js" async></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; height: 100%; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #f0f2f5; 
            color: #333; 
            overflow: hidden;
        }
        
        #blockedScreen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            padding: 30px;
            text-align: center;
            color: white;
        }
        
        #blockedScreen.visible { display: flex; }
        
        #mainApp {
            width: 100%;
            height: 100%;
            display: none;
            overflow: auto;
            background: #f0f2f5;
        }
        
        #mainApp.visible { display: block; }
        
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
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }
        .header-center { flex: 1; text-align: center; }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .header p { font-size: 14px; opacity: 0.9; }
        .badge { 
            background: #ff6b6b; 
            color: white; 
            border-radius: 50%; 
            width: 32px; 
            height: 32px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-weight: bold; 
            cursor: pointer; 
            font-size: 14px;
        }
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
        
        .message { padding: 12px; border-radius: 8px; margin-bottom: 15px; display: none; text-align: center; font-weight: 600; }
        .message.success { background: #c8e6c9; color: #2e7d32; display: block; }
        .message.error { background: #ffcdd2; color: #c62828; display: block; }
        .message.loading { background: #e0e0e0; color: #333; display: block; }
        
        .cart-summary { background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196f3; margin-bottom: 20px; }
        .summary-row { display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px; font-weight: 600; }
        
        .empty-message { text-align: center; padding: 40px 20px; color: #999; }
        .buttons { display: flex; gap: 10px; margin-top: 20px; }
        .btn-primary { flex: 1; padding: 14px; background: #4caf50; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .btn-primary:disabled { background: #ccc; cursor: not-allowed; }
        .btn-secondary { flex: 1; padding: 14px; background: #757575; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .btn-back { padding: 10px 15px; background: #757575; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 13px; }
        
        .table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        .table th, .table td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 13px; }
        .table th { background: #e3f2fd; font-weight: 600; color: #1e3c72; }
        .btn-delete { padding: 6px 12px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: 600; }
    </style>
</head>
<body>

    <!-- БЛОКИРОВКА БРАУЗЕРА (СРАЗУ ПЕРЕНАПРАВЛЯЕТ) -->
    <div id="blockedScreen" class="visible">
        <div style="background: white; padding: 40px 30px; border-radius: 12px; max-width: 400px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
            <h2 style="color: #c62828; margin-bottom: 20px; font-size: 24px;">🔒 Доступ запрещён</h2>
            <p style="font-size: 16px; color: #333; margin-bottom: 30px; line-height: 1.5;">
                Это приложение работает <strong>только внутри Telegram</strong>.<br><br>
                Открываем бота...
            </p>
            <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                <div style="width: 20px; height: 20px; border: 3px solid white; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <span style="color: white; font-size: 16px;">Перенаправление...</span>
            </div>
        </div>
        <style>
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </div>

    <!-- ОСНОВНОЕ ПРИЛОЖЕНИЕ -->
    <div id="mainApp">
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
                
                <!-- ПОИСК -->
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
                
                <!-- КОРЗИНА -->
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
                
                <!-- ИТОГ -->
                <div id="summaryPage" class="page">
                    <h3 style="margin-bottom: 20px; color: #2e7d32;">✅ Заказ отправлен!</h3>
                    
                    <div class="cart-summary">
                        <div class="summary-row">
                            <span>Позиций:</span>
                            <span id="summaryPositions">0</span>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>📦 Выбранные товары</h3>
                        <table class="table">
                            <tbody id="summaryTable"></tbody>
                        </table>
                    </div>
                    
                    <div class="buttons">
                        <button class="btn-primary" onclick="startOver()">Новый заказ</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let tg = null;
        let allProducts = [];
        let orders = [];
        let currentPage = 'searchPage';
        
        // ==================== ПРОВЕРКА TELEGRAM ====================
        function initTelegram() {
            console.log('🔍 Проверяю Telegram...');
            
            // Ждём инициализации Telegram WebApp
            if (window.Telegram && window.Telegram.WebApp) {
                tg = window.Telegram.WebApp;
                console.log('✅ Telegram WebApp найден');
                console.log('📊 initData:', tg.initData ? 'YES' : 'NO');
                console.log('📊 initDataUnsafe:', tg.initDataUnsafe ? 'YES' : 'NO');
                
                // Проверяем несколькими способами:
                // 1. Есть ли initData
                // 2. Есть ли initDataUnsafe 
                // 3. Есть ли userId
                let isTelegram = false;
                
                // Способ 1: Проверяем initData
                if (tg.initData && tg.initData.length > 0) {
                    isTelegram = true;
                    console.log('✅ Способ 1: initData найден');
                }
                
                // Способ 2: Проверяем initDataUnsafe (если данные есть)
                if (tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.id) {
                    isTelegram = true;
                    console.log('✅ Способ 2: initDataUnsafe.user найден, ID:', tg.initDataUnsafe.user.id);
                }
                
                // Способ 3: Проверяем просто наличие расширенного функционала
                if (typeof tg.sendData === 'function') {
                    isTelegram = true;
                    console.log('✅ Способ 3: sendData функция доступна');
                }
                
                if (isTelegram) {
                    // ✅ Запущено из Telegram - показываем приложение
                    console.log('✅✅✅ ЗАПУЩЕНО В TELEGRAM!');
                    tg.ready();
                    tg.expand();
                    tg.setBackgroundColor('#f0f2f5');
                    
                    document.getElementById('blockedScreen').classList.remove('visible');
                    document.getElementById('mainApp').classList.add('visible');
                    
                    console.log('✅ Приложение загружено');
                    updateCartBadge();
                    return;
                }
            }
            
            // ❌ Не в Telegram - показываем блокировку и перенаправляем
            console.log('❌ НЕ В TELEGRAM - ПЕРЕНАПРАВЛЯЮ НА БОТА');
            document.getElementById('blockedScreen').classList.add('visible');
            document.getElementById('mainApp').classList.remove('visible');
            
            // СРАЗУ перенаправляем на бота
            setTimeout(function() {
                window.location.href = 'https://t.me/TTZ_Sales_Department_bot';
            }, 2000);
        }
        
        // Инициализируем СРАЗУ при загрузке
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initTelegram);
        } else {
            initTelegram();
        }
        
        // ==================== НАВИГАЦИЯ ====================
        function showPage(pageName) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(pageName).classList.add('active');
            currentPage = pageName;
            
            if (pageName === 'searchPage') {
                document.getElementById('headerSubtitle').textContent = 'Форма предзаказа';
                document.getElementById('backBtnHeader').style.display = 'none';
            } else if (pageName === 'cartPage') {
                document.getElementById('headerSubtitle').textContent = 'Ваша корзина';
                document.getElementById('backBtnHeader').style.display = 'block';
            } else if (pageName === 'summaryPage') {
                document.getElementById('headerSubtitle').textContent = 'Спасибо за заказ!';
                document.getElementById('backBtnHeader').style.display = 'none';
            }
        }
        
        function goBack() { showPage('searchPage'); }
        function goBackToSearch() { showPage('searchPage'); }
        function goToCart() { 
            showPage('cartPage'); 
            updateCartDisplay(); 
        }
        
        // ==================== ПОИСК ====================
        async function searchProducts() {
            const searchText = document.getElementById('searchInput').value.trim();
            if (!searchText) {
                showMessage('Введите текст для поиска', 'error');
                return;
            }
            
            const searchBtn = document.getElementById('searchBtn');
            searchBtn.disabled = true;
            searchBtn.textContent = 'Загрузка...';
            
            try {
                showMessage('⏳ Поиск товаров...', 'loading');
                
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: searchText })
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
                console.error('Ошибка:', error);
                showMessage('❌ Ошибка подключения', 'error');
            } finally {
                searchBtn.disabled = false;
                searchBtn.textContent = 'Найти';
            }
        }
        
        function displayProducts(products) {
            const container = document.getElementById('productsList');
            if (products.length === 0) {
                container.style.display = 'none';
                return;
            }
            
            container.innerHTML = products.map((p, idx) => `
                <div class="product-item" onclick="selectProduct(${idx})">
                    <div class="product-name">${p.name}</div>
                    <div class="product-unit">Единица: <strong>${p.unit || 'шт'}</strong></div>
                </div>
            `).join('');
            
            container.style.display = 'flex';
        }
        
        function selectProduct(index) {
            const product = allProducts[index];
            if (!product) return;
            
            const exists = orders.find(o => o.id === product.id);
            if (exists) {
                exists.quantity += 1;
            } else {
                orders.push({
                    id: product.id,
                    name: product.name,
                    unit: product.unit || 'шт',
                    quantity: 1
                });
            }
            
            updateCartBadge();
            showMessage('✅ Товар добавлен', 'success');
            goToCart();
        }
        
        // ==================== КОРЗИНА ====================
        function updateCartBadge() {
            const total = orders.reduce((sum, item) => sum + item.quantity, 0);
            const badge = document.getElementById('cartBadge');
            const container = document.getElementById('cartBadgeContainer');
            
            if (total > 0) {
                badge.textContent = total;
                container.classList.remove('hidden');
            } else {
                container.classList.add('hidden');
            }
        }
        
        function updateCartDisplay() {
            const container = document.getElementById('cartItems');
            
            if (orders.length === 0) {
                container.innerHTML = '<div class="empty-message">Товары не выбраны</div>';
                document.getElementById('submitBtn').disabled = true;
                return;
            }
            
            let html = '<table class="table"><tr><th>Товар</th><th style="text-align: center; width: 80px;">Кол-во</th><th style="text-align: center; width: 60px;">Удал.</th></tr>';
            
            orders.forEach((item) => {
                html += `
                    <tr>
                        <td>${item.name}</td>
                        <td style="text-align: center; font-weight: 600;">${item.quantity} ${item.unit}</td>
                        <td style="text-align: center;"><button class="btn-delete" onclick="removeFromOrder('${item.id}')">✕</button></td>
                    </tr>
                `;
            });
            
            html += '</table>';
            container.innerHTML = html;
            
            const totalItems = orders.reduce((sum, item) => sum + item.quantity, 0);
            document.getElementById('cartTotalItems').textContent = totalItems;
            document.getElementById('cartTotalPositions').textContent = orders.length;
            document.getElementById('submitBtn').disabled = false;
        }
        
        function removeFromOrder(id) {
            orders = orders.filter(item => item.id !== id);
            updateCartDisplay();
            updateCartBadge();
            showMessage('🗑️ Товар удален', 'success');
        }
        
        function clearOrder() {
            if (confirm('Очистить корзину?')) {
                orders = [];
                updateCartDisplay();
                updateCartBadge();
                showMessage('🗑️ Корзина очищена', 'success');
            }
        }
        
        function submitOrder() {
            if (orders.length === 0) {
                showMessage('Добавьте товары', 'error');
                return;
            }
            
            const orderData = {
                action: 'order',
                items: orders.map(item => ({
                    product: item.name,
                    quantity: item.quantity,
                    unit: item.unit
                })),
                timestamp: new Date().toLocaleString('ru-RU')
            };
            
            console.log('📦 Отправляем заказ:', orderData);
            
            if (tg && typeof tg.sendData === 'function') {
                try {
                    tg.sendData(JSON.stringify(orderData));
                    showSummary();
                } catch (error) {
                    console.error('Ошибка:', error);
                    showMessage('❌ Ошибка при отправке', 'error');
                }
            } else {
                showMessage('❌ Telegram недоступен', 'error');
            }
        }
        
        function showSummary() {
            const container = document.getElementById('summaryTable');
            
            container.innerHTML = orders.map((item) => `
                <tr>
                    <td>${item.name}</td>
                    <td>${item.quantity} ${item.unit}</td>
                </tr>
            `).join('');
            
            document.getElementById('summaryPositions').textContent = orders.length;
            showPage('summaryPage');
        }
        
        function startOver() {
            orders = [];
            updateCartBadge();
            document.getElementById('searchInput').value = '';
            document.getElementById('message').className = 'message';
            goBack();
        }
        
        function showMessage(text, type = 'info') {
            const msgEl = document.getElementById('message');
            msgEl.textContent = text;
            msgEl.className = 'message ' + type;
            setTimeout(() => { msgEl.className = 'message'; }, 4000);
        }
        
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') searchProducts();
        });
        
        console.log('✅ ARMOR HAND v3.4 загружен (исправлена проверка Telegram)');
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
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "Пустой запрос", "products": []})
        
        print(f"🌐 Облако: получен запрос '{query}'")
        
        try:
            response = requests.post(
                'https://criteria-waviness-entangled.ngrok-free.dev/api/search',
                json={'query': query},
                timeout=10,
                verify=False
            )
            result = response.json()
            print(f"✅ Облако: получен ответ с {len(result.get('products', []))} товарами")
            return jsonify(result)
        except Exception as e:
            print(f"⚠️ Ошибка туннеля: {e}")
            return jsonify({
                "error": "⚠️ Локальный сервер недоступен",
                "products": []
            })
    except Exception as e:
        print(f"❌ Ошибка облака: {e}")
        return jsonify({"error": f"Ошибка сервера: {str(e)}", "products": []})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "location": "cloud", "version": "3.4"})

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "ARMOR HAND Cloud v3.4"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*70)
    print("🛡️  ARMOR HAND - Облачный Mini App на Render v3.4".center(70))
    print("="*70)
    print(f"✅ Mini App: https://ttz-sales-department.onrender.com/webapp")
    print(f"🔒 Блокировка браузера: ВКЛЮЧЕНА")
    print(f"✅ Проверка Telegram: ИСПРАВЛЕНА (3 способа)")
    print(f"✅ Больше не закрывается в Telegram!")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=port, debug=False)
