"""
🛡️ ARMOR HAND - Облачный Mini App v6.3
База — твой рабочий v5.0 + детальная страница заказа + экспорт в Excel/PDF (формат Акта)
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ARMOR HAND</title>
    <script src="https://telegram.org/js/telegram-web-app.js" async></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #333; height: 100vh; overflow: hidden; }
        #error-screen { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: none; align-items: center; justify-content: center; z-index: 9999; padding: 20px; }
        .error-box { background: white; padding: 40px 30px; border-radius: 12px; max-width: 400px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); text-align: center; }
        .app { display: none; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; min-height: 100vh; }
        .header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 16px 20px; text-align: center; }
        .header h1 { font-size: 22px; margin-bottom: 4px; }
        .content { padding: 20px; }
        .page { display: none; }
        .page.active { display: block; }
        .search-box { display: flex; gap: 10px; }
        .search-input { flex: 1; padding: 14px 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 15px; }
        .search-btn { padding: 14px 24px; background: #2a5298; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .products { display: flex; flex-direction: column; gap: 10px; max-height: calc(100vh - 280px); overflow-y: auto; margin-top: 15px; }
        .product { padding: 14px; border: 2px solid #e0e0e0; border-radius: 10px; cursor: pointer; }
        .product:hover { border-color: #2a5298; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 12px 8px; text-align: left; }
        th { background: #e3f2fd; }
        .action-btn { padding: 8px 12px; border: none; border-radius: 6px; cursor: pointer; font-size: 17px; width: 42px; }
        .edit-btn { background: #2196f3; color: white; }
        .remove-btn { background: #f44336; color: white; }
        .message { padding: 14px; border-radius: 8px; margin-bottom: 15px; display: none; text-align: center; font-weight: 600; }
        .message.success { background: #c8e6c9; color: #2e7d32; display: block; }
        .message.error { background: #ffcdd2; color: #c62828; display: block; }
        .buttons { display: flex; gap: 12px; margin-top: 20px; }
        .btn { flex: 1; padding: 16px; border: none; border-radius: 10px; cursor: pointer; font-weight: 600; color: white; }
        .btn-primary { background: #4caf50; }
        .btn-secondary { background: #757575; }
        .order-card { cursor: pointer; }
        .order-detail { padding: 20px; }
        .print-area { display: none; }
    </style>
</head>
<body>
<div id="error-screen"> ... (без изменений) ... </div>
<div class="app">
    <div class="container">
        <div class="header">
            <h1>🛡️ ARMOR HAND</h1>
            <p id="headerTitle">Форма предзаказа</p>
        </div>
        <div class="content">
            <div id="message" class="message"></div>

            <!-- Поиск, Корзина, Предпросмотр — без изменений (как в v5.0) -->
            <!-- ... (весь код страниц searchPage, cartPage, previewPage остался точно как у тебя) ... -->

            <!-- Мои предзаказы -->
            <div id="ordersPage" class="page">
                <button class="btn btn-secondary" onclick="showPage('search')" style="margin-bottom:15px;">← Назад</button>
                <h3>📦 Мои предзаказы</h3>
                <div id="ordersList"></div>
            </div>

            <!-- Детальная страница заказа -->
            <div id="detailPage" class="page">
                <button class="btn btn-secondary" onclick="showPage('orders')" style="margin-bottom:15px;">← Назад к заказам</button>
                <div id="detailContent" class="order-detail"></div>
                <div class="buttons">
                    <button class="btn btn-secondary" onclick="downloadExcel()">📊 Скачать в Excel</button>
                    <button class="btn btn-primary" onclick="printToPDF()">📄 Скачать в PDF</button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
let tg = null;
let cart = [];
let orders = JSON.parse(localStorage.getItem('armorOrders') || '[]');
let currentOrder = null;

// ... (весь твой предыдущий JavaScript initApp, searchProducts, addToCart, confirmAndSend и т.д. — без изменений) ...

function renderOrders() {
    const container = document.getElementById('ordersList');
    if (orders.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#999;padding:40px;">Пока нет предзаказов</p>';
        return;
    }
    let html = '';
    orders.forEach((order, index) => {
        html += `<div class="order-card" onclick="showOrderDetail(${index})" style="border:1px solid #ddd;border-radius:10px;padding:15px;margin-bottom:15px;background:#f8f9ff;">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                <strong>${order.id}</strong>
                <span style="color:#2e7d32;">${order.status}</span>
            </div>
            <small>${order.date}</small>
            <div style="margin-top:10px;font-size:13px;">
                ${order.items.map(item => `• ${item.name} — ${item.qty} ${item.unit}`).join('<br>')}
            </div>
        </div>`;
    });
    container.innerHTML = html;
}

function showOrderDetail(index) {
    currentOrder = orders[index];
    const html = `
        <h3>${currentOrder.id}</h3>
        <p><strong>Дата:</strong> ${currentOrder.date}</p>
        <p><strong>Статус:</strong> <span style="color:#2e7d32;">${currentOrder.status}</span></p>
        <table style="width:100%;margin-top:15px;">
            <thead><tr><th>Товар</th><th>Кол-во</th></tr></thead>
            <tbody>
                ${currentOrder.items.map(item => `<tr><td>${item.name}</td><td style="text-align:right">${item.qty} ${item.unit}</td></tr>`).join('')}
            </tbody>
        </table>
        ${currentOrder.comment !== '—' ? `<p style="margin-top:15px;"><strong>Комментарий:</strong> ${currentOrder.comment}</p>` : ''}
    `;
    document.getElementById('detailContent').innerHTML = html;
    showPage('detail');
}

function downloadExcel() {
    if (!currentOrder) return;
    let csv = "№ п/п;Наименование;Ед. изм;Кол-во;Цена без НДС, сум;Цена включая НДС, сум;Сумма включая НДС сум\n";
    currentOrder.items.forEach((item, i) => {
        csv += `${i+1};${item.name};${item.unit};${item.qty};;;;\n`;
    });
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${currentOrder.id}.csv`;
    link.click();
    showMessage('✅ Файл Excel скачан', 'success');
}

function printToPDF() {
    if (!currentOrder) return;
    const printContent = `
        <div style="padding:40px;font-family:Arial;">
            <h2 style="text-align:center;">АКТ приема-передачи товара</h2>
            <p style="text-align:center;">№ ${currentOrder.id} от ${currentOrder.date}</p>
            <table style="width:100%;border-collapse:collapse;margin-top:30px;">
                <thead><tr><th style="border:1px solid #000;">Товар</th><th style="border:1px solid #000;">Кол-во</th></tr></thead>
                <tbody>
                    ${currentOrder.items.map(item => `<tr><td style="border:1px solid #000;">${item.name}</td><td style="border:1px solid #000;text-align:center;">${item.qty} ${item.unit}</td></tr>`).join('')}
                </tbody>
            </table>
            <p style="margin-top:40px;">Комментарий: ${currentOrder.comment}</p>
            <p style="margin-top:60px;text-align:right;">Подписи сторон</p>
        </div>
    `;
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
}

function showMessage(text, type) {
    const msg = document.getElementById('message');
    msg.innerHTML = text;
    msg.className = `message ${type}`;
    setTimeout(() => msg.className = 'message', 5000);
}

// Остальной код (searchProducts, addToCart и т.д.) остался точно как в твоём v5.0
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
    print("\n🛡️ ARMOR HAND Cloud v6.3 — детальная страница + экспорт в Excel/PDF")
    app.run(host='0.0.0.0', port=port, debug=False)
