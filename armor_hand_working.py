"""
🛡️ ARMOR HAND - С HTTPS поддержкой (ИСПРАВЛЕННАЯ ВЕРСИЯ)
Использует 127.0.0.1 вместо localhost для совместимости с Telegram
"""

import logging
import sqlite3
import pyodbc
import json
import threading
import ssl
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "8280279511:AAEIZRDP4MJ1vCRmyxZn8mwS08ec0ZOpnIk"
CORRECT_INN = "305832915"
CORRECT_PHONE = "+99897 1004551"
DB_PATH = 'armor_hand_users.db'

SQL_SERVER = "ERPAPP"
SQL_DATABASE = "erp_ttz"
SQL_USER = "sa"
SQL_PASSWORD = "10ca!@sa"

# ✅ HTTPS URL с IP адресом (Telegram требует это вместо localhost!)
WEB_APP_URL = "https://127.0.0.1:5000/webapp"

INN_INPUT, PHONE_INPUT, MAIN_MENU = range(3)

# ============================================================================
# HTML ДЛЯ MINI APP
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
        <div id="loadingBox" style="display:none;">
            <div class="loading">
                <div class="spinner"></div>
                ⏳ Загрузка...
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
            <button 
                onclick="sendOrder()" 
                style="width: 100%; padding: 12px; margin-top: 12px; background: #667eea; color: white; border: none; border-radius: 6px; font-weight: 600; cursor: pointer;"
            >
                📤 Отправить заказ
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
        }

        async function searchProducts() {
            const query = document.getElementById('searchInput').value.trim();
            
            if (!query) {
                showError('❌ Введите запрос');
                return;
            }

            document.getElementById('loadingBox').style.display = 'block';
            document.getElementById('errorBox').innerHTML = '';
            document.getElementById('productsList').innerHTML = '';
            document.getElementById('welcomeBox').style.display = 'none';

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });

                const data = await response.json();
                document.getElementById('loadingBox').style.display = 'none';

                if (data.error) {
                    showError('❌ ' + data.error);
                    return;
                }

                if (!data.products || data.products.length === 0) {
                    showError('❌ Товары не найдены');
                    return;
                }

                displayProducts(data.products);
            } catch (error) {
                document.getElementById('loadingBox').style.display = 'none';
                showError('❌ Ошибка подключения: ' + error.message);
            }
        }

        function displayProducts(products) {
            const list = document.getElementById('productsList');
            list.innerHTML = '<p style="font-size: 12px; color: #666; margin-bottom: 10px;">Найдено товаров: ' + products.length + '</p>';

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
            } else {
                alert('✅ Заказ: ' + JSON.stringify(orderData));
            }
        }

        function showError(message) {
            const box = document.getElementById('errorBox');
            box.innerHTML = '<div class="error">' + message + '</div>';
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        document.getElementById('searchInput').focus();
    </script>
</body>
</html>
'''

# ============================================================================
# FLASK APP С HTTPS
# ============================================================================

flask_app = Flask(__name__)
CORS(flask_app)

class SQLDatabase:
    def __init__(self, server, database, user, password):
        self.server = server
        self.database = database
        self.user = user
        self.password = password
    
    def get_connection(self):
        try:
            conn_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.user};PWD={self.password}'
            return pyodbc.connect(conn_string, timeout=5)
        except Exception as e:
            logger.error(f"SQL ошибка: {e}")
            return None
    
    def search_products(self, search_text):
        try:
            logger.info(f"🔍 SQL поиск: '{search_text}'")
            conn = self.get_connection()
            if not conn:
                return {"error": "Ошибка подключения к БД", "products": []}
            
            cursor = conn.cursor()
            search_words = search_text.strip().split()
            where_conditions = []
            for word in search_words:
                if len(word) > 0:
                    where_conditions.append(f"UPPER(r386._Description) LIKE UPPER('%{word}%')")
            
            if not where_conditions:
                return {"error": "Пусто", "products": []}
            
            search_condition = " AND ".join(where_conditions)
            query = f"""
            SELECT TOP 100
                r386._IDRRef AS 'ID',
                r386._Description AS 'Трубка',
                COALESCE(units1._Description, units2._Description, units3._Description,
                    units4._Description, units5._Description, units6._Description,
                    units7._Description, 'шт') AS 'Unit'
            FROM [dbo].[_Reference386X1] r386
            INNER JOIN [dbo].[_Reference113] r113 ON r386._Fld67276RRef = r113._IDRRef
            LEFT JOIN [dbo].[_Reference113] parent113 ON r113._ParentIDRRef = parent113._IDRRef
            LEFT JOIN [dbo].[_Reference113] grandparent113 ON parent113._ParentIDRRef = grandparent113._IDRRef
            LEFT JOIN [dbo].[_Reference822] units1 ON r386._Fld67268RRef = units1._IDRRef
            LEFT JOIN [dbo].[_Reference355] packings ON r386._Fld67265RRef = packings._IDRRef
            LEFT JOIN [dbo].[_Reference822] units2 ON packings._Fld66460RRef = units2._IDRRef
            LEFT JOIN [dbo].[_Reference822] units3 ON r386._Fld67354RRef = units3._IDRRef
            LEFT JOIN [dbo].[_Reference822] units4 ON r386._Fld67325RRef = units4._IDRRef
            LEFT JOIN [dbo].[_Reference822] units5 ON r386._Fld99589RRef = units5._IDRRef
            LEFT JOIN [dbo].[_Reference822] units6 ON r386._Fld99495RRef = units6._IDRRef
            LEFT JOIN [dbo].[_Reference822] units7 ON r386._Fld67265RRef = units7._IDRRef
            WHERE r386._Marked = 0x0 AND r113._Marked = 0x0
                AND grandparent113._Description = 'Готовая продукция'
                AND ({search_condition})
            ORDER BY r386._Description
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            
            products = []
            for product in results:
                products.append({
                    "id": str(product[0]),
                    "name": product[1],
                    "unit": product[2] if len(product) > 2 else "шт"
                })
            
            logger.info(f"✅ Найдено {len(products)} товаров")
            return {"error": None, "products": products, "total": len(products)}
        except Exception as e:
            logger.error(f"❌ SQL ошибка: {e}")
            return {"error": str(e), "products": []}

sql_db = SQLDatabase(SQL_SERVER, SQL_DATABASE, SQL_USER, SQL_PASSWORD)

@flask_app.route('/webapp', methods=['GET'])
def webapp():
    return render_template_string(MINI_APP_HTML)

@flask_app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "Пустой запрос", "products": []})
        
        logger.info(f"📲 API SEARCH: '{query}'")
        result = sql_db.search_products(query)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"API ошибка: {e}")
        return jsonify({"error": str(e), "products": []})

@flask_app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

def generate_self_signed_cert():
    """Генерирует самоподписанный сертификат для HTTPS"""
    import os
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    import datetime
    
    cert_file = 'cert.pem'
    key_file = 'key.pem'
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        return cert_file, key_file
    
    logger.info("🔒 Генерирую самоподписанный сертификат...")
    
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"UZ"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Tashkent"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Tashkent"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"ARMOR HAND"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"127.0.0.1"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(u"127.0.0.1"),
            x509.IPAddress(u"127.0.0.1"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())
    
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    logger.info("✅ Сертификат создан!")
    return cert_file, key_file

def run_flask():
    print("\n" + "="*70)
    print("🌐 FLASK API SERVER (HTTPS)".center(70))
    print("="*70)
    print("✅ Mini App: https://127.0.0.1:5000/webapp")
    print("✅ API: https://127.0.0.1:5000/api/search")
    print("⚠️  (самоподписанный сертификат для локального использования)")
    print("="*70 + "\n")
    
    try:
        cert_file, key_file = generate_self_signed_cert()
        
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert_file, key_file)
        
        flask_app.run(
            debug=False,
            host='127.0.0.1',
            port=5000,
            use_reloader=False,
            ssl_context=ssl_context
        )
    except Exception as e:
        logger.error(f"❌ Ошибка HTTPS: {e}")
        logger.info("Установите: pip install cryptography")

# ============================================================================
# TELEGRAM BOT
# ============================================================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, inn TEXT, phone TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    cursor.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, items TEXT, comment TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()
    logger.info("✅ БД инициализирована")

def save_user(user_id, inn, phone):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, inn, phone) VALUES (?, ?, ?)', (user_id, inn, phone))
    conn.commit()
    conn.close()

def save_order(user_id, items):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (user_id, items) VALUES (?, ?)', (user_id, items))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"👤 /start от {update.effective_user.id}")
    await update.message.reply_text("🛡️ Добро пожаловать в ARMOR HAND!\n\nВведите ваш ИНН:")
    return INN_INPUT

async def inn_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inn = update.message.text.strip()
    if inn != CORRECT_INN:
        await update.message.reply_text("❌ ИНН неверный")
        return INN_INPUT
    context.user_data['inn'] = inn
    keyboard = [[KeyboardButton("📱 Отправить номер", request_contact=True)]]
    await update.message.reply_text("✅ ИНН верный!\n\nПодтвердите номер:", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return PHONE_INPUT

async def phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.contact:
        await update.message.reply_text("❌ Нажмите кнопку")
        return PHONE_INPUT
    
    phone = update.message.contact.phone_number
    phone_clean = ''.join(filter(str.isdigit, phone))
    correct_phone_clean = ''.join(filter(str.isdigit, CORRECT_PHONE))
    
    if phone_clean != correct_phone_clean:
        await update.message.reply_text(f"❌ Номер неверный")
        return PHONE_INPUT
    
    user_id = update.effective_user.id
    inn = context.user_data.get('inn')
    save_user(user_id, inn, phone)
    logger.info(f"✅ AUTH: User {user_id}")
    
    buttons = [
        [InlineKeyboardButton("📋 Каталог товаров", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton("👨‍💼 Консультант", callback_data="contact_consultant")],
        [InlineKeyboardButton("❌ Выход", callback_data="logout")]
    ]
    await update.message.reply_text("🛡️ Главное меню:\n\n✅ Авторизация успешна!", reply_markup=InlineKeyboardMarkup(buttons))
    return MAIN_MENU

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "contact_consultant":
        buttons = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]]
        await query.edit_message_text(f"📞 Консультант:\n\n{CORRECT_PHONE}", reply_markup=InlineKeyboardMarkup(buttons))
    elif query.data == "logout":
        await query.edit_message_text("🚪 Выход")
        return ConversationHandler.END
    elif query.data == "back_to_menu":
        buttons = [
            [InlineKeyboardButton("📋 Каталог товаров", web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton("👨‍💼 Консультант", callback_data="contact_consultant")],
            [InlineKeyboardButton("❌ Выход", callback_data="logout")]
        ]
        await query.edit_message_text("🛡️ Главное меню", reply_markup=InlineKeyboardMarkup(buttons))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка данных от Mini App"""
    try:
        message = update.message
        
        if hasattr(message, 'web_app_data') and message.web_app_data:
            user_id = update.effective_user.id
            web_app_data = message.web_app_data.data
            
            logger.info(f"📦 Получен заказ от пользователя {user_id}")
            
            try:
                data = json.loads(web_app_data)
            except json.JSONDecodeError:
                data = {"raw": web_app_data}
            
            save_order(user_id, web_app_data)
            
            items_text = ""
            if "items" in data and data["items"]:
                items_text = "\n".join([
                    f"  • {item.get('name', 'Неизвестный товар')}: {item.get('quantity', 1)} {item.get('unit', 'шт')}"
                    for item in data["items"]
                ])
            else:
                items_text = "  • Данные получены"
            
            message_text = f"""✅ Ваш заказ принят!

📦 Товары:
{items_text}

📊 Всего: {data.get('totalItems', 0)} единиц

Консультант свяжется с вами в ближайшее время."""
            
            await update.message.reply_text(message_text)
            logger.info(f"✅ Заказ сохранён: {data}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("❌ Ошибка при обработке данных")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Отмена")
    return ConversationHandler.END

def main():
    print("\n" + "="*70)
    print("🛡️  ARMOR HAND - ПОЛНОЕ РЕШЕНИЕ (HTTPS)".center(70))
    print("="*70)
    print(f"📱 Mini App: {WEB_APP_URL}")
    print(f"✅ ВСЁ В ОДНОЙ ПАПКЕ!")
    print("="*70 + "\n")
    
    init_db()
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            INN_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, inn_input)],
            PHONE_INPUT: [MessageHandler(filters.CONTACT, phone_input)],
            MAIN_MENU: [CallbackQueryHandler(callback_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(callback_handler, pattern="^(contact_consultant|logout|back_to_menu)$"))
    app.add_handler(MessageHandler(filters.ALL, message_handler))
    
    logger.info("🚀 Бот запущен")
    app.run_polling()

if __name__ == '__main__':
    main()
