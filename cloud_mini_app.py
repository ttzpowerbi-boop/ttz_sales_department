"""
🛡️ ARMOR HAND - Облачный Mini App на Render (Полная версия v3.0)
Самая строгая защита — в браузере ничего не видно
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
            background: #f0f2f5;
        }
        .main-app { display: none; }
    </style>
</head>
<body>

    <!-- Блокировка при открытии в браузере -->
    <div id="blockedScreen" class="blocked">
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
    <div id="mainApp" class="main-app">
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
                
                <!-- Поиск -->
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
                
                <!-- Детальный просмотр -->
                <div id="detailPage" class="page">
                    <div class="buttons" style="margin-top: 0;">
                        <button class="btn-back" onclick="goBackFromDetail()">← Назад</button>
                    </div>
                    <div class="product-detail">
                        <h2 id="detailProductName"></h2>
                        <div class="product-detail-info">
                            <div class="info-row">
                                <span class="info-label">Единица:</span>
                                <span class="info-value" id="detailProductUnit">-</span>
                            </div>
                        </div>
                    </div>
                    <div class="quantity-section">
                        <div class="quantity-label" id="quantityLabel">Укажите количество:</div>
                        <div class="quantity-controls">
                            <button class="qty-btn" onclick="decreaseQty()">−</button>
                            <input type="number" id="qtyInput" class="qty-input" value="1" min="1">
                            <button class="qty-btn" onclick="increaseQty()">+</button>
                        </div>
                        <div style="margin-top: 15px; display: flex; gap: 10px;">
                            <button class="btn-secondary" onclick="goBackFromDetail()">Отмена</button>
                            <button class="btn-primary" onclick="addToOrder()">Добавить в корзину</button>
                        </div>
                    </div>
                </div>
                
                <!-- Корзина -->
                <div id="cartPage" class="page">
                    <div class="buttons" style="margin-top: 0; margin-bottom: 20px;">
                        <button class="btn-back" onclick="goBackToSearch()">← Продолжить покупки</button>
                    </div>
                    <h3 style="margin-bottom: 20px;">🛒 Ваша корзина</h3>
                    <div class="cart-summary">
                        <div class="summary-row"><span>Всего единиц:</span><span id="cartTotalItems">0</span></div>
                        <div class="summary-row"><span>Позиций:</span><span id="cartTotalPositions">0</span></div>
                    </div>
                    <div class="section" style="border-bottom: none;">
                        <h3>📋 Выбранные товары</h3>
                        <div id="cartItems"></div>
                    </div>
                    <div class="buttons">
                        <button class="btn-secondary" onclick="clearOrder()">Очистить</button>
                        <button class="btn-primary" id="submitBtn" onclick="goToCheckout()" disabled>Оформить заказ</button>
                    </div>
                </div>

                <!-- Оформление -->
                <div id="checkoutPage" class="page">
                    <div class="buttons" style="margin-top: 0; margin-bottom: 20px;">
                        <button class="btn-back" onclick="goBackToCart()">← Назад</button>
                    </div>
                    <h3 style="margin-bottom: 20px;">📝 Счет-фактура</h3>
                    <table class="table">
                        <thead><tr><th>Товар</th><th>Кол-во</th></tr></thead>
                        <tbody id="checkoutTable"></tbody>
                    </table>
                    <div class="section">
                        <h3>📝 Комментарий</h3>
                        <textarea id="orderComment" placeholder="Добавьте комментарий..."></textarea>
                    </div>
                    <div class="buttons">
                        <button class="btn-secondary" onclick="goBackToCart()">Отмена</button>
                        <button class="btn-primary" onclick="submitOrder()">Отправить заказ</button>
                    </div>
                </div>

                <!-- Итог -->
                <div id="summaryPage" class="page">
                    <div class="success-message">✅ Заказ отправлен!</div>
                    <h3 style="margin-bottom: 20px;">📊 Итого по заказу</h3>
                    <table class="table">
                        <thead><tr><th>Товар</th><th>Кол-во</th></tr></thead>
                        <tbody id="summaryTable"></tbody>
                    </table>
                    <div class="cart-summary">
                        <div class="summary-row"><span>Всего позиций:</span><span id="summaryPositions">0</span></div>
                    </div>
                    <div class="buttons">
                        <button class="btn-primary" onclick="newOrder()">Новый заказ</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // === САМАЯ ЖЁСТКАЯ ЗАЩИТА ===
        function initApp() {
            if (!window.Telegram || !window.Telegram.WebApp) {
                // Показываем блокировку
                document.getElementById('blockedScreen').style.display = 'flex';
                return;
            }

            // Если внутри Telegram — показываем приложение
            document.getElementById('mainApp').style.display = 'block';

            try {
                tg = window.Telegram.WebApp;
                tg.ready();
                tg.expand();
            } catch(e) {}

            updateCartBadge();
            console.log('✅ ARMOR HAND v3.0 запущен внутри Telegram');
        }

        // Запуск сразу
        window.onload = initApp;

        // ===================== ОСНОВНАЯ ЛОГИКА =====================
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
                if (pageName === 'cartPage') updateCartDisplay();
                if (pageName === 'checkoutPage') updateCheckoutDisplay();
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
    return jsonify({"status": "ok", "version": "3.0"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n🛡️ ARMOR HAND Cloud v3.0 запущен — максимальная защита")
    app.run(host='0.0.0.0', port=port, debug=False)
