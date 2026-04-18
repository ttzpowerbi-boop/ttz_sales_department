"""
🛡️ ARMOR HAND - Облачный Mini App на Render v4.0 FINAL
✅ БРАУЗЕР: блокирован
✅ TELEGRAM: работает идеально
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
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; height: 100%; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #f0f2f5; 
            color: #333; 
        }
        
        #error-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            padding: 20px;
        }
        
        #error-screen.hidden { display: none !important; }
        
        .error-box {
            background: white;
            padding: 40px 30px;
            border-radius: 12px;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            text-align: center;
        }
        
        .error-box h2 {
            color: #c62828;
            font-size: 24px;
            margin-bottom: 20px;
        }
        
        .error-box p {
            font-size: 16px;
            color: #333;
            line-height: 1.5;
            margin-bottom: 15px;
        }
        
        .error-box strong { font-weight: 600; }
        
        .app { width: 100%; }
        .app.hidden { display: none !important; }
        
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
        .header p { font-size: 14px; opacity: 0.9; }
        
        .content { padding: 20px; }
        .page { display: none; }
        .page.active { display: block; }
        
        .section { margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #e0e0e0; }
        .section:last-child { border-bottom: none; }
        .section h3 { color: #1e3c72; font-size: 16px; margin-bottom: 15px; }
        
        .search-box { display: flex; gap: 10px; }
        .search-input { flex: 1; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; }
        .search-btn { padding: 12px 20px; background: #2a5298; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .search-btn:disabled { background: #ccc; cursor: not-allowed; }
        
        .products { display: flex; flex-direction: column; gap: 10px; max-height: 300px; overflow-y: auto; margin-top: 15px; }
        .product { padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; }
        .product:hover { border-color: #2a5298; background: #f0f2f5; }
        .product-name { font-weight: 600; color: #1e3c72; font-size: 13px; }
        .product-unit { font-size: 12px; color: #666; margin-top: 5px; }
        
        .message { padding: 12px; border-radius: 8px; margin-bottom: 15px; display: none; text-align: center; font-weight: 600; }
        .message.success { background: #c8e6c9; color: #2e7d32; display: block; }
        .message.error { background: #ffcdd2; color: #c62828; display: block; }
        .message.loading { background: #e0e0e0; color: #333; display: block; }
        
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 13px; }
        th { background: #e3f2fd; font-weight: 600; color: #1e3c72; }
        
        .btn { padding: 12px 20px; background: #2a5298; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .btn:disabled { background: #ccc; cursor: not-allowed; }
        .btn-delete { padding: 6px 12px; background: #f44336; font-size: 11px; }
        .btn-clear { background: #757575; }
        
        .badge { 
            display: inline-block;
            background: #ff6b6b; 
            color: white; 
            border-radius: 50%; 
            width: 24px; 
            height: 24px; 
            text-align: center;
            line-height: 24px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
            cursor: pointer;
        }
        .badge.hidden { display: none; }
        
        .buttons { display: flex; gap: 10px; margin-top: 20px; }
    </style>
</head>
<body>

<!-- ОШИБКА БРАУЗЕРА -->
<div id="error-screen">
    <div class="error-box">
        <h2>🔒 Доступ запрещён</h2>
        <p>Это приложение работает <strong>только внутри Telegram</strong>.</p>
        <p>Откройте бота:<br><strong>@TTZ_Sales_Department_bot</strong></p>
    </div>
</div>

<!-- ПРИЛОЖЕНИЕ -->
<div class="app hidden">
    <div class="container">
        <div class="header">
            <h1>🛡️ ARMOR HAND</h1>
            <p id="title">Форма предзаказа</p>
        </div>
        
        <div class="content">
            <div id="msg" class="message"></div>
            
            <!-- ПОИСК -->
            <div id="page-search" class="page active">
                <div class="section">
                    <h3>📦 Поиск товаров</h3>
                    <div class="search-box">
                        <input type="text" id="query" class="search-input" placeholder="Размер, тип, ГОСТ...">
                        <button class="search-btn" id="btn-search" onclick="search()">Найти</button>
                    </div>
                    <div id="results" class="products" style="display: none;"></div>
                </div>
            </div>
            
            <!-- КОРЗИНА -->
            <div id="page-cart" class="page">
                <div class="buttons" style="margin-bottom: 20px;">
                    <button class="btn btn-clear" onclick="showPage('search')">← Назад</button>
                </div>
                <h3 style="margin-bottom: 20px;">
                    🛒 Корзина
                    <span id="badge" class="badge hidden" onclick="showPage('search')">0</span>
                </h3>
                <table id="cart-table">
                    <tr><th>Товар</th><th style="width:60px">Кол-во</th><th style="width:50px">Удал</th></tr>
                    <tbody id="cart-items"></tbody>
                </table>
                <div class="buttons">
                    <button class="btn btn-clear" onclick="clearCart()">Очистить</button>
                    <button class="btn" onclick="submit()">Отправить</button>
                </div>
            </div>
            
            <!-- СПАСИБО -->
            <div id="page-thanks" class="page">
                <h3 style="color: #2e7d32; margin-bottom: 20px;">✅ Заказ отправлен!</h3>
                <table id="order-table">
                    <tr><th>Товар</th><th>Кол-во</th></tr>
                    <tbody id="order-items"></tbody>
                </table>
                <div class="buttons">
                    <button class="btn" onclick="newOrder()">Новый заказ</button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
let cart = [];
let products = [];
let tg = null;

// ==================== ИНИЦИАЛИЗАЦИЯ ====================
function init() {
    console.log('🔍 Проверяю окружение...');
    
    // Проверяем: есть ли Telegram.WebApp И есть ли initData (значит открыто из бота)
    const hasTelegram = typeof Telegram !== 'undefined' && Telegram.WebApp;
    const hasInitData = hasTelegram && Telegram.WebApp.initData && Telegram.WebApp.initData.length > 0;
    
    console.log('Telegram:', hasTelegram ? 'ДА' : 'НЕТ');
    console.log('initData:', hasInitData ? 'ДА' : 'НЕТ');
    
    // Если Telegram И initData - это точно Mini App из бота
    if (hasTelegram && hasInitData) {
        console.log('✅✅✅ ЭТО TELEGRAM MINI APP!');
        tg = Telegram.WebApp;
        
        // Инициализируем
        tg.ready?.();
        tg.expand?.();
        tg.setBackgroundColor?.('#f0f2f5');
        
        // Показываем приложение
        document.getElementById('error-screen').classList.add('hidden');
        document.querySelector('.app').classList.remove('hidden');
        console.log('✅ Приложение загружено');
        
    } else {
        // Браузер или неполная инициализация
        console.log('❌ НЕ TELEGRAM APP - БЛОКИРУЮ ДОСТУП');
        document.getElementById('error-screen').style.display = 'flex';
        document.querySelector('.app').classList.add('hidden');
    }
}

// Инициализируем когда скрипт Telegram загружен
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Даём время на загрузку скрипта Telegram
        setTimeout(init, 500);
    });
} else {
    setTimeout(init, 500);
}

// ==================== ФУНКЦИИ ====================
function msg(text, type = 'info') {
    const el = document.getElementById('msg');
    el.textContent = text;
    el.className = 'message ' + type;
    setTimeout(() => el.className = 'message', 4000);
}

function showPage(name) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById('page-' + name).classList.add('active');
    document.getElementById('title').textContent = 
        name === 'search' ? 'Форма предзаказа' :
        name === 'cart' ? 'Ваша корзина' : 'Спасибо!';
}

async function search() {
    const q = document.getElementById('query').value.trim();
    if (!q) { msg('Введите текст поиска', 'error'); return; }
    
    const btn = document.getElementById('btn-search');
    btn.disabled = true;
    btn.textContent = 'Загрузка...';
    msg('Ищу...', 'loading');
    
    try {
        const r = await fetch('/api/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: q})
        });
        const d = await r.json();
        
        if (d.products?.length > 0) {
            products = d.products;
            const html = products.map((p, i) => `
                <div class="product" onclick="addCart(${i})">
                    <div class="product-name">${p.name}</div>
                    <div class="product-unit">Ед: <strong>${p.unit || 'шт'}</strong></div>
                </div>
            `).join('');
            document.getElementById('results').innerHTML = html;
            document.getElementById('results').style.display = 'flex';
            msg('✅ Найдено ' + d.products.length + ' товаров', 'success');
        } else {
            msg('❌ Не найдено', 'error');
            document.getElementById('results').style.display = 'none';
        }
    } catch (e) {
        msg('❌ Ошибка: ' + e.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Найти';
    }
}

function addCart(idx) {
    const p = products[idx];
    const existing = cart.find(x => x.id === p.id);
    if (existing) {
        existing.qty++;
    } else {
        cart.push({id: p.id, name: p.name, unit: p.unit || 'шт', qty: 1});
    }
    updateBadge();
    msg('✅ Добавлено', 'success');
    showPage('cart');
    renderCart();
}

function updateBadge() {
    const total = cart.reduce((s, x) => s + x.qty, 0);
    const badge = document.getElementById('badge');
    if (total > 0) {
        badge.textContent = total;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function renderCart() {
    const html = cart.map(x => `
        <tr>
            <td>${x.name}</td>
            <td style="text-align:center">${x.qty}</td>
            <td style="text-align:center"><button class="btn btn-delete" onclick="removeCart('${x.id}')">✕</button></td>
        </tr>
    `).join('');
    document.getElementById('cart-items').innerHTML = html;
}

function removeCart(id) {
    cart = cart.filter(x => x.id !== id);
    updateBadge();
    renderCart();
    msg('🗑️ Удалено', 'success');
}

function clearCart() {
    if (confirm('Очистить?')) {
        cart = [];
        updateBadge();
        renderCart();
        msg('🗑️ Очищено', 'success');
    }
}

function submit() {
    if (cart.length === 0) { msg('Добавьте товары', 'error'); return; }
    
    console.log('📦 Отправляю заказ...');
    console.log('tg:', tg);
    
    if (!tg || !tg.sendData) {
        msg('❌ Ошибка: sendData недоступна', 'error');
        console.error('❌ tg.sendData не найдена');
        return;
    }
    
    const order = {
        items: cart.map(x => ({product: x.name, quantity: x.qty, unit: x.unit})),
        timestamp: new Date().toLocaleString('ru-RU')
    };
    
    try {
        console.log('📤 Данные:', order);
        tg.sendData(JSON.stringify(order));
        showSummary();
    } catch (error) {
        console.error('❌ Ошибка:', error);
        msg('❌ Ошибка: ' + error.message, 'error');
    }
}

function showSummary() {
    const html = cart.map(x => `<tr><td>${x.name}</td><td>${x.qty}</td></tr>`).join('');
    document.getElementById('order-items').innerHTML = html;
    showPage('thanks');
}

function newOrder() {
    cart = [];
    updateBadge();
    document.getElementById('query').value = '';
    showPage('search');
}

document.getElementById('query').addEventListener('keypress', e => {
    if (e.key === 'Enter') search();
});

console.log('✅ ARMOR HAND v4.0 FINAL загружен');
</script>

</body>
</html>'''

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
        
        print(f"\n🌐 Запрос: '{query}'")
        
        try:
            response = session.post(
                'https://criteria-waviness-entangled.ngrok-free.dev/api/search',
                json={'query': query},
                timeout=15,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                count = len(result.get('products', []))
                print(f"✅ Получено {count} товаров\n")
                return jsonify(result)
                
        except Exception as e:
            print(f"❌ Ошибка: {str(e)[:100]}\n")
        
        return jsonify({"error": "Сервер недоступен", "products": []})
        
    except Exception as e:
        return jsonify({"error": str(e)[:50], "products": []})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "version": "4.0"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*60)
    print("🛡️  ARMOR HAND v4.0 FINAL")
    print("="*60)
    print(f"✅ Браузер: БЛОКИРОВАН")
    print(f"✅ Telegram: РАБОТАЕТ")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=False)
