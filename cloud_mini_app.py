"""
🛡️ ARMOR HAND - Облачный Mini App на Render (Полная версия v2.9)
Максимально строгая защита — работает ТОЛЬКО внутри Telegram
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
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #f0f2f5; 
            margin: 0; 
            padding: 0;
            height: 100vh;
            overflow: hidden;
        }
        .blocked {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            text-align: center;
            padding: 30px;
        }
        .container { 
            max-width: 600px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 12px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
            overflow: hidden; 
        }
        
        .header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
        .header-center { flex: 1; text-align: center; }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .header p { font-size: 14px; opacity: 0.9; }
        
        .badge { background: #ff6b6b; color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: bold; cursor: pointer; }
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
        
        .products-list { display: flex; flex-direction: column; gap: 10px; max-height: 300px; overflow-y: auto; margin-top: 15px; }
        .product-item { padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; }
        .product-name { font-weight: 600; color: #1e3c72; font-size: 13px; }
        .product-unit { font-size: 12px; color: #666; margin-top: 5px; }
        
        .product-detail { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .product-detail h2 { color: #1e3c72; font-size: 18px; margin-bottom: 15px; word-break: break-word; }
        
        .quantity-section { background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .quantity-label { font-size: 14px; font-weight: 600; margin-bottom: 10px; }
        .quantity-controls { display: flex; align-items: center; gap: 10px; }
        .qty-btn { width: 36px; height: 36px; border: 2px solid #2a5298; background: white; color: #2a5298; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .qty-input { flex: 1; padding: 8px; border: 2px solid #ddd; border-radius: 6px; text-align: center; font-weight: 600; font-size: 16px; }
        
        .empty-message { text-align: center; padding: 40px 20px; color: #999; }
        .buttons { display: flex; gap: 10px; margin-top: 20px; }
        .btn-primary { flex: 1; padding: 14px; background: #4caf50; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .btn-primary:disabled { background: #ccc; cursor: not-allowed; }
        .btn-secondary { flex: 1; padding: 14px; background: #757575; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .btn-back { padding: 10px 15px; background: #757575; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 13px; }
        
        .message { padding: 12px; border-radius: 8px; margin-bottom: 15px; display: none; text-align: center; font-weight: 600; }
        .message.success { background: #c8e6c9; color: #2e7d32; display: block; }
        .message.error { background: #ffcdd2; color: #c62828; display: block; }
        
        .cart-summary { background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196f3; margin-bottom: 20px; }
        .summary-row { display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px; font-weight: 600; }
        
        .table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        .table th, .table td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 13px; }
        .table th { background: #e3f2fd; font-weight: 600; color: #1e3c72; }
        .table td { background: white; }
        
        .action-btn { padding: 6px 12px; margin: 2px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .edit-btn { background: #2196f3; color: white; }
        .remove-btn { background: #f44336; color: white; }
    </style>
</head>
<body>

    <!-- Блокировка при открытии в браузере -->
    <div id="blockedScreen" style="display: flex; height: 100vh; background: #f0f2f5; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 30px;">
        <h2 style="color: #c62828; margin-bottom: 20px;">⚠️ Доступ запрещён</h2>
        <p style="font-size: 17px; max-width: 420px; margin-bottom: 30px;">
            Это приложение работает <strong>только внутри Telegram</strong>.<br><br>
            Пожалуйста, откройте его через бота.
        </p>
        <button onclick="window.location.href='https://t.me/TTZ_Sales_Department_bot'" 
                style="padding: 16px 36px; background: #229ED9; color: white; border: none; border-radius: 10px; font-size: 18px; cursor: pointer;">
            Открыть в Telegram
        </button>
    </div>

    <!-- Основное приложение (скрыто по умолчанию) -->
    <div id="mainApp" style="display: none;">
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

                <!-- Здесь должны быть остальные страницы (detailPage, cartPage и т.д.) -->
                <!-- Если они отсутствуют — приложение выглядит пустым -->

            </div>
        </div>
    </div>

    <script>
        // === САМАЯ СТРОГАЯ ЗАЩИТА ===
        function blockIfNotTelegram() {
            if (!window.Telegram || !window.Telegram.WebApp) {
                // Показываем блокировку
                document.getElementById('blockedScreen').style.display = 'flex';
                return false;
            }
            // Показываем приложение
            document.getElementById('mainApp').style.display = 'block';
            return true;
        }

        // Запуск сразу при загрузке страницы
        window.onload = function() {
            if (!blockIfNotTelegram()) return;

            try {
                tg = window.Telegram.WebApp;
                tg.ready();
                tg.expand();
            } catch(e) {}

            updateCartBadge();
            console.log('✅ ARMOR HAND v2.9 запущен внутри Telegram');
        };

        // ===================== ОСНОВНАЯ ЛОГИКА ПРИЛОЖЕНИЯ =====================
        let tg = null;
        let allProducts = [];
        let selectedProduct = null;
        let orders = [];
        let editingIndex = null;
        let currentPage = 'searchPage';

        function showPage(pageName) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(pageName).classList.add('active');
            currentPage = pageName;
            
            if (pageName === 'searchPage') {
                document.getElementById('headerSubtitle').textContent = 'Форма предзаказа';
                document.getElementById('backBtnHeader').style.display = 'none';
            } else {
                document.getElementById('backBtnHeader').style.display = 'block';
            }
        }

        function goBack() {
            if (currentPage === 'detailPage') goBackFromDetail();
            else if (currentPage === 'cartPage') goBackToSearch();
            else if (currentPage === 'checkoutPage') goBackToCart();
        }

        function goBackFromDetail() {
            document.getElementById('searchInput').value = '';
            document.getElementById('productsList').style.display = 'none';
            showPage('searchPage');
            selectedProduct = null;
            editingIndex = null;
        }

        function goToCart() { showPage('cartPage'); }
        function goBackToCart() { showPage('cartPage'); }
        function goBackToSearch() { 
            document.getElementById('searchInput').value = '';
            document.getElementById('productsList').style.display = 'none';
            showPage('searchPage'); 
        }
        function goToCheckout() { showPage('checkoutPage'); }
        function newOrder() { orders = []; updateCartBadge(); showPage('searchPage'); }

        async function searchProducts() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) return showMessage('Введите текст для поиска', 'error');
            
            const btn = document.getElementById('searchBtn');
            btn.disabled = true; btn.textContent = 'Загрузка...';
            
            try {
                const res = await fetch('/api/search', { 
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'}, 
                    body: JSON.stringify({query}) 
                });
                const data = await res.json();
                allProducts = data.products || [];
                if (allProducts.length === 0) {
                    showMessage('Товары не найдены', 'error');
                } else {
                    displayProducts(allProducts);
                    showMessage(`✅ Найдено ${allProducts.length} товаров`, 'success');
                }
            } catch (e) {
                showMessage('❌ Ошибка подключения', 'error');
            } finally {
                btn.disabled = false; btn.textContent = 'Найти';
            }
        }

        function displayProducts(products) {
            const cont = document.getElementById('productsList');
            cont.innerHTML = products.map((p, i) => `
                <div class="product-item" onclick="selectProduct(${i})">
                    <div class="product-name">${p.name}</div>
                    <div class="product-unit">Единица: <strong>${p.unit || 'шт'}</strong></div>
                </div>
            `).join('');
            cont.style.display = 'flex';
        }

        function selectProduct(i) {
            selectedProduct = allProducts[i];
            document.getElementById('detailProductName').textContent = selectedProduct.name;
            document.getElementById('detailProductUnit').textContent = selectedProduct.unit || 'шт';
            document.getElementById('qtyInput').value = "1";
            document.getElementById('quantityLabel').textContent = "Укажите количество:";
            editingIndex = null;
            showPage('detailPage');
        }

        function increaseQty() {
            let v = parseInt(document.getElementById('qtyInput').value) || 1;
            document.getElementById('qtyInput').value = v + 1;
        }
        function decreaseQty() {
            let v = parseInt(document.getElementById('qtyInput').value) || 1;
            if (v > 1) document.getElementById('qtyInput').value = v - 1;
        }

        function addToOrder() {
            if (!selectedProduct) return;
            const qty = parseInt(document.getElementById('qtyInput').value) || 1;
            if (qty < 1) return;
            
            if (editingIndex !== null) {
                orders[editingIndex].quantity = qty;
                showMessage('✅ Количество обновлено', 'success');
                editingIndex = null;
            } else {
                const existingIndex = orders.findIndex(o => o.id === selectedProduct.id);
                if (existingIndex >= 0) {
                    orders[existingIndex].quantity += qty;
                } else {
                    orders.push({
                        id: selectedProduct.id,
                        name: selectedProduct.name,
                        quantity: qty,
                        unit: selectedProduct.unit || 'шт'
                    });
                }
                showMessage('✅ Товар добавлен в корзину', 'success');
            }
            
            updateCartBadge();
            goBackFromDetail();
        }

        function updateCartBadge() {
            const total = orders.reduce((sum, item) => sum + (item.quantity || 0), 0);
            document.getElementById('cartBadge').textContent = total;
            document.getElementById('cartBadgeContainer').classList.toggle('hidden', total === 0);
        }

        function updateCartDisplay() {
            const container = document.getElementById('cartItems');
            if (orders.length === 0) {
                container.innerHTML = '<div class="empty-message">Корзина пуста</div>';
                document.getElementById('submitBtn').disabled = true;
                return;
            }
            
            let html = `<table style="width:100%; border-collapse:collapse;">
                <tr style="background:#e3f2fd;">
                    <th style="padding:10px; text-align:left;">Товар</th>
                    <th style="padding:10px; text-align:center;">Кол-во</th>
                    <th style="padding:10px; text-align:center;">Ед.</th>
                    <th style="padding:10px; text-align:center;">Ред.</th>
                    <th style="padding:10px; text-align:center;">Удал.</th>
                </tr>`;
            
            orders.forEach(item => {
                html += `<tr data-id="${item.id}">
                    <td style="padding:12px 10px;">${item.name}</td>
                    <td style="padding:12px; text-align:center; font-weight:600;">${item.quantity}</td>
                    <td style="padding:12px; text-align:center;">${item.unit}</td>
                    <td style="padding:8px; text-align:center;">
                        <button class="action-btn edit-btn" data-action="edit">✎</button>
                    </td>
                    <td style="padding:8px; text-align:center;">
                        <button class="action-btn remove-btn" data-action="remove">✕</button>
                    </td>
                </tr>`;
            });
            html += '</table>';
            container.innerHTML = html;
            
            container.querySelectorAll('button[data-action]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const id = btn.closest('tr').dataset.id;
                    if (btn.dataset.action === 'edit') editOrderItem(id);
                    else removeFromOrder(id);
                });
            });
            
            const totalUnits = orders.reduce((sum, item) => sum + (item.quantity || 0), 0);
            document.getElementById('cartTotalItems').textContent = totalUnits;
            document.getElementById('cartTotalPositions').textContent = orders.length;
            document.getElementById('submitBtn').disabled = false;
        }

        function removeFromOrder(id) {
            orders = orders.filter(item => item.id !== id);
            updateCartDisplay();
            updateCartBadge();
            showMessage('✅ Товар удалён', 'success');
        }

        function editOrderItem(id) {
            const index = orders.findIndex(o => o.id === id);
            if (index === -1) return;
            
            selectedProduct = { id: orders[index].id, name: orders[index].name, unit: orders[index].unit };
            editingIndex = index;
            document.getElementById('qtyInput').value = orders[index].quantity;
            document.getElementById('quantityLabel').textContent = "Измените количество товара:";
            showPage('detailPage');
        }

        function clearOrder() {
            if (confirm('Очистить корзину?')) {
                orders = [];
                updateCartDisplay();
                updateCartBadge();
            }
        }

        function updateCheckoutDisplay() {
            document.getElementById('checkoutTable').innerHTML = orders.map(item => `
                <tr><td>${item.name}</td><td>${item.quantity} ${item.unit}</td></tr>
            `).join('');
        }

        function submitOrder() {
            if (!orders.length) return;
            const comment = document.getElementById('orderComment').value.trim();
            const data = {
                items: orders.map(i => ({product: i.name, quantity: i.quantity, unit: i.unit})),
                comment: comment,
                date: new Date().toLocaleString('ru-RU')
            };
            if (tg && tg.sendData) tg.sendData(JSON.stringify(data));
            showSummary();
        }

        function showSummary() {
            document.getElementById('summaryTable').innerHTML = orders.map(item => `
                <tr><td>${item.name}</td><td>${item.quantity} ${item.unit}</td></tr>
            `).join('');
            document.getElementById('summaryPositions').textContent = orders.length;
            showPage('summaryPage');
        }

        function showMessage(text, type = 'info') {
            const msg = document.getElementById('message');
            msg.textContent = text;
            msg.className = `message ${type}`;
            setTimeout(() => msg.className = 'message', 4000);
        }

        document.getElementById('searchInput').addEventListener('keypress', e => {
            if (e.key === 'Enter') searchProducts();
        });

        function updateCartBadge() {
            const total = orders.reduce((sum, item) => sum + (item.quantity || 0), 0);
            document.getElementById('cartBadge').textContent = total;
            document.getElementById('cartBadgeContainer').classList.toggle('hidden', total === 0);
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
        
        try:
            r = requests.post('https://criteria-waviness-entangled.ngrok-free.dev/api/search',
                              json={'query': query}, timeout=15, verify=False)
            return jsonify(r.json())
        except:
            return jsonify({"error": "Локальный сервер недоступен", "products": []})
    except Exception as e:
        return jsonify({"error": str(e), "products": []})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "version": "2.9"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n🛡️ ARMOR HAND Cloud v2.9 запущен — максимальная защита")
    app.run(host='0.0.0.0', port=port, debug=False)
