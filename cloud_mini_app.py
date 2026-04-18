"""
🛡️ ARMOR HAND - Облачный Mini App на Render (Полная версия v3.1)
Исправлена инициализация внутри Telegram
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
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #f0f2f5; 
            color: #333; 
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
        
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; }
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
        .product-item:hover { border-color: #2a5298; background: #f0f2f5; }
        .product-name { font-weight: 600; color: #1e3c72; font-size: 13px; }
        .product-unit { font-size: 12px; color: #666; margin-top: 5px; }
        .product-detail { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .product-detail h2 { color: #1e3c72; font-size: 18px; margin-bottom: 15px; word-break: break-word; }
        .product-detail-info { background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #2a5298; }
        .info-row { display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px; }
        .info-label { font-weight: 600; color: #666; }
        .info-value { color: #333; font-weight: 600; }
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
        .success-message { background: #c8e6c9; color: #2e7d32; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-weight: 600; }
        textarea { font-family: inherit; width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; min-height: 80px; }
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

    <!-- Блокировка -->
    <div id="blockedScreen" class="blocked" style="display: none;">
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

    <!-- Основное приложение -->
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
                
                <!-- Добавьте сюда остальные страницы (detailPage, cartPage и т.д.), если они есть в вашей версии -->
            </div>
        </div>
    </div>

    <script>
        let tg = null;

        function initApp() {
            // Ждём, пока Telegram WebApp полностью загрузится
            if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.ready) {
                tg = window.Telegram.WebApp;
                tg.ready();
                tg.expand();
                document.getElementById('mainApp').style.display = 'block';
                console.log('✅ Mini App запущен внутри Telegram');
                updateCartBadge();
            } else {
                // Если Telegram не инициализировался — показываем блокировку
                document.getElementById('blockedScreen').style.display = 'flex';
                console.log('❌ Запуск вне Telegram — доступ запрещён');
            }
        }

        // Запускаем проверку с небольшой задержкой
        setTimeout(initApp, 800);   // 800мс — достаточно для загрузки Telegram скрипта

        // ===================== ОСНОВНАЯ ЛОГИКА =====================
        // Вставьте сюда весь ваш JavaScript (showPage, searchProducts, addToOrder и т.д.)

        function showPage(pageName) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(pageName).classList.add('active');
            currentPage = pageName;
        }

        // ... остальной код (updateCartBadge, searchProducts и т.д.)

        console.log('✅ ARMOR HAND v3.1 загружен');
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n🛡️ ARMOR HAND Cloud v3.1 запущен")
    app.run(host='0.0.0.0', port=port, debug=False)
