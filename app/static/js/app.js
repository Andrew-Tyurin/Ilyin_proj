const API_BASE = '../api/v1';
let currentUser = null;
let currentUserId = null;
let wallets = [];
let operations = [];
let currentOffset = 0;          // сколько записей пропущено
let currentWalletId = null;     // фильтр по кошельку (число или null)
let currentSort = 'decrease';   // текущая сортировка
const PAGE_LIMIT = 10;          // количество записей на страницу (1-30)

function showToast(title, message, isError = false) {
    const toastEl = document.getElementById('toastNotification');
    const toastTitle = document.getElementById('toastTitle');
    const toastBody = document.getElementById('toastBody');
    const toastHeader = toastEl.querySelector('.toast-header');
    
    toastTitle.textContent = title;
    toastBody.textContent = message;
    
    // Цвета в зависимости от типа
    if (isError) {
        toastHeader.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
        toastHeader.style.color = 'white';
    } else {
        toastHeader.style.background = 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
        toastHeader.style.color = 'white';
    }
    
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 10000
    });
    toast.show();
}

function showError(message) {
    showToast('❌ Ошибка', message, true);
}

function showSuccess(message) {
    showToast('✅ Успешно', message, false);
}

function closeModal(modalId) {
    const modalEl = document.getElementById(modalId);
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
}

function handleAuthResponse(data) {
    // data: { id, user_name, access_token }
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user_name', data.user_name);
    localStorage.setItem('user_id', data.id);
    currentUser = data.user_name;
    currentUserId = data.id;
    showSuccess('Успешно!');
    showMainSection();
}

async function getErrorMessage(response) {
    const status = response.status;
    try {
        const errorData = await response.json();
        if (errorData.detail) {
            // Если detail — массив (ошибки Pydantic)
            if (Array.isArray(errorData.detail)) {
                // Ошибки Pydantic (422)
                 const messages = errorData.detail.map(err => {
                    const field = err.loc?.filter(p => p !== 'body').join('.') || 'поле';
                    return `${field}: ${err.msg}`;
                 }).join('; ');
                 return `${status}: ${messages}`;
            }
            // Если detail — строка (ваши HTTPException)
            return `${status}: ${errorData.detail}`;
        }
        return errorData.message || 'Ошибка сервера';
    } catch (e) {
        // Если ответ не JSON
        const text = await response.text();
        const snippet = text.length > 200 ? text.substring(0, 200) + '...' : text;
        return `${status}: ${snippet || 'Неизвестная ошибка'}`;
    }
}

function getCurrencySymbol(currencyCode) {
    // Вспомогательная функция для символа валюты
    const symbols = {
        'rub': '₽',
        'usd': '$',
        'eur': '€'
    };
    return symbols[currencyCode] || currencyCode.toUpperCase();
}


function updatePaginationButtons(loadedCount) {
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    if (!prevBtn || !nextBtn) return;

    // На первой странице кнопка "Назад" неактивна
    prevBtn.disabled = (currentOffset === 0);

    // Если загружено меньше, чем PAGE_LIMIT, значит это последняя страница
    nextBtn.disabled = (loadedCount < PAGE_LIMIT);

    // Обновляем текстовый индикатор страницы (опционально)
    const pageSpan = document.getElementById('pageInfo');
    if (pageSpan) {
        const pageNumber = Math.floor(currentOffset / PAGE_LIMIT) + 1;
        pageSpan.textContent = `Страница ${pageNumber}`;
    }
}

function changePage(direction) {
    // direction: -1 (назад) или +1 (вперед)
    const newOffset = currentOffset + direction * PAGE_LIMIT;
    if (newOffset < 0) return; // нельзя уйти в минус
    currentOffset = newOffset;
    // Загружаем операции с тем же фильтром, но новым offset (не сбрасываем фильтр)
    loadOperations(false);  // resetOffset = false
}

function updateWalletSelectForHistory() {
    const select = document.getElementById('walletSelect');
    if (!select) return;

    // Очищаем select, оставляя только опцию "Все кошельки"
    select.innerHTML = '<option value="">Все кошельки</option>';

    // Добавляем каждый кошелёк как option
    wallets.forEach(w => {
        const option = document.createElement('option');
        option.value = w.id;          // значение — числовой id
        option.textContent = `${w.name} (${w.currency.toUpperCase()})`; // например "Наличные (RUB)"
        select.appendChild(option);
    });
}

function resetToDefaultAndRefresh() {
    // Сброс фильтра по кошельку
    const walletSelect = document.getElementById('walletSelect');
    if (walletSelect) walletSelect.value = '';  // 'Все кошельки'

    // Сброс сортировки на 'decrease' (сначала новые)
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) sortSelect.value = 'decrease';

    // Сброс глобальных переменных пагинации и фильтров
    currentOffset = 0;
    currentWalletId = null;
    currentSort = 'decrease';

    // Перезагружаем все данные (кошельки, операции, баланс)
    loadAllData();
}

async function register() {
    const user_name = document.getElementById('user_name').value.trim();
    const password = document.getElementById('password').value.trim();

    try {
        const response = await fetch(`${API_BASE}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_name, password })
        });

        if (response.ok) {
            const data = await response.json();
            handleAuthResponse(data)
        } else {
            const errorMsg = await getErrorMessage(response);
            showError(errorMsg);
        }
    } catch (e) {
        console.error('Ошибка подключения:', e);
        showError('Не удалось подключиться к серверу или что-то другое');
    }
}

async function login() {
    const user_name = document.getElementById('user_name').value.trim();
    const password = document.getElementById('password').value.trim();

    try {
        const response = await fetch(`${API_BASE}/users/authorization`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_name, password })
        });

        if (response.ok) {
            const data = await response.json();
            handleAuthResponse(data, user_name);
        } else {
            const errorMsg = await getErrorMessage(response);
            showError(errorMsg);
        }
    } catch (e) {
        console.error('Ошибка подключения:', e);
        showError('Не удалось подключиться к серверу или что-то другое');
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_id');
    currentUser = null;
    currentUserId = null;
    wallets = [];
    operations = [];
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('mainSection').style.display = 'none';
    document.getElementById('TokenInfo').innerHTML = '';
}

function showMainSection() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('mainSection').style.display = 'block';
    document.getElementById('currentUser').textContent = currentUser;
    document.getElementById('currentUserId').textContent = currentUserId;
    loadAllData();
}

async function loadAllData() {
    await loadWallets();
    await loadOperations();
    await updateTotalBalance();
}

async function loadTokenInfo() {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`${API_BASE}/users/authorization/my/token-info`, {
            method: 'GET',
            headers: {'Authorization': `Bearer ${token}`}
        });
        if (response.ok) {
            const rawTokenInfo = await response.json();
            document.getElementById('TokenInfo').innerHTML = `
            Осталось: ${rawTokenInfo.expires_time_life} секунд!
            `;

        } else {
            const errorMsg = await getErrorMessage(response);
            console.error('Ошибка с токеном:', errorMsg);
            const tbody = document.getElementById('TokenInfo');
            tbody.innerHTML = `<span class="text-center text-danger">Ошибка: ${errorMsg}</span>`;
        }
    } catch (e) {
        console.error('Ошибка подключения:', e);
        const tbody = document.getElementById('TokenInfo');
        tbody.innerHTML = `
            <span class="text-center text-danger">Не удалось получить данные токена или что-то другое</span>
        `;
    }
}


async function loadWallets() {
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${API_BASE}/my/wallets/all`, {
            method: 'GET',
            headers: {'Authorization': `Bearer ${token}`,}
        });

        if (response.ok) {
            const rawWallets = await response.json();
            // Нормализуем данные от бэкенда: приводим валюту к нижнему регистру, баланс к числу
            wallets = rawWallets.map(w => {
                // Преобразуем баланс в число (обрабатываем строки, Decimal и другие типы)
                let balance = 0;
                if (typeof w.balance === 'number') {
                    balance = w.balance;
                } else if (typeof w.balance === 'string') {
                    balance = parseFloat(w.balance) || 0;
                } else if (w.balance != null) {
                    balance = Number(w.balance) || 0;
                }
                
                return {
                    ...w,
                    currency: String(w.currency || '').toLowerCase(),
                    balance: balance
                };
            });
            renderWalletsTable();
            updateWalletSelects();
            updateWalletSelectForHistory()
        } else {
            wallets = [];
            renderWalletsTable();
            updateWalletSelects();
            updateWalletSelectForHistory()
            const errorMsg = await getErrorMessage(response);
            console.error('Ошибка с кошельками:', errorMsg);
            const tbody = document.getElementById('walletsTable');
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Ошибка: ${errorMsg}</td></tr>`;
        }
    } catch (e) {
        wallets = [];
        renderWalletsTable();
        updateWalletSelects();
        updateWalletSelectForHistory()
        console.error('Ошибка подключения или загрузки кошельков:', e);
        const tbody = document.getElementById('walletsTable');
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Не удалось загрузить кошельки</td></tr>';
    }
}

async function loadOperations(resetOffset = true) {
    // Сбрасываем offset при новом поиске "Искать"
    if (resetOffset) {
        currentOffset = 0;
    }

    // Считываем значения из формы
    const sort = document.getElementById('sortSelect').value; // 'decrease' или 'increase'
    const walletSelect = document.getElementById('walletSelect');
    let walletId = null;
    if (walletSelect && walletSelect.value !== '') {
        walletId = Number(walletSelect.value);
        if (isNaN(walletId)) walletId = null;
    }

    // Сохраняем текущие фильтры для использования в пагинации
    currentSort = sort;
    currentWalletId = walletId;

    const token = localStorage.getItem('access_token');

    // Добавляем все параметры, которые есть
    let url = `${API_BASE}/my/wallets/operations/history`;
    const params = [];
    if (currentSort) params.push(`order_by_data=${encodeURIComponent(currentSort)}`);
    if (currentWalletId !== null) params.push(`wallet_id=${currentWalletId}`);
    params.push(`limit=${PAGE_LIMIT}`);
    params.push(`offset=${currentOffset}`);

    if (params.length) {
        url += '?' + params.join('&');
    }

    try {

        const response = await fetch(url, {
            method: 'GET',
            headers: {'Authorization': `Bearer ${token}`}
        });

        if (response.ok) {
            const rawOperations = await response.json();
            // Нормализуем данные от бэкенда: приводим валюту к нижнему регистру, сумму к числу
            operations = rawOperations.map(op => ({
                ...op,
                amount: parseFloat(op.amount) || 0,
                currency: String(op.currency || '').toLowerCase()
            }));
            renderOperationsTable();
            updatePaginationButtons(rawOperations.length); // Обновляем состояние кнопок пагинации
        } else {
            operations = [];
            renderOperationsTable()
            const errorMsg = await getErrorMessage(response);
            console.error('Ошибка с операциями:', errorMsg);
            const tbody = document.getElementById('transactionsTable');
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Ошибка: ${errorMsg}</td></tr>`;
        }
    } catch (e) {
        operations = [];
        renderOperationsTable()
        console.error('Ошибка подключения или загрузки операций:', e);
        const tbody = document.getElementById('transactionsTable');
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Не удалось загрузить историю</td></tr>';
    }
}

function renderWalletsTable() {
    const tbody = document.getElementById('walletsTable');
    
    if (wallets.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">У вас пока нет кошельков</td></tr>';
        return;
    }

    const currencySymbols = {
        'rub': '₽',
        'usd': '$',
        'eur': '€'
    };

    tbody.innerHTML = wallets.map((w, index)=> {
        // Гарантируем что баланс - число
        const balance = typeof w.balance === 'number' ? w.balance : (parseFloat(w.balance) || 0);
        const currency = String(w.currency || '').toLowerCase();
        const symbol = currencySymbols[currency] || currency.toUpperCase();
        return `
            <tr>
                <td><strong>${index + 1})</strong></td>
                <td><strong>${w.id}</strong></td>
                <td><strong>${w.name}</strong></td>
                <td><span class="badge bg-secondary">${currency.toUpperCase()}</span></td>
                <td class="text-end"><strong>${balance.toFixed(2)} ${symbol}</strong></td>
            </tr>
        `;
    }).join('');
}

function renderOperationsTable() {
    const tbody = document.getElementById('transactionsTable');
    
    if (operations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Нет транзакций</td></tr>';
        return;
    }
    
    tbody.innerHTML = operations.map((t, index)=> {
        const wallet = wallets.find(w => w.id === t.wallet_id);
        const walletName = wallet ? wallet.name : 'Неизвестно';
        let typeClass, typeIcon, typeLabel;
        if (t.operation.type === 'income') {
            typeClass = 'text-success';
            typeIcon = '➕';
            typeLabel = 'Доход';
        } else if (t.operation.type === 'expense') {
            typeClass = 'text-danger';
            typeIcon = '➖';
            typeLabel = 'Расход';
        } else if (t.operation.type === 'transfer_income') {
            typeClass = 'text-info';
            typeIcon = '➕🔄';
            typeLabel = 'Перевод себе (зачисление)';
        } else if (t.operation.type === 'transfer_expense') {
            typeClass = 'text-info';
            typeIcon = '➖🔄';
            typeLabel = 'Перевод себе (отправка)';
        } else {
            typeClass = 'text-secondary';
            typeIcon = '❓';
            typeLabel = 'Неизвестно';
        }
        const date = new Date(t.operation.created_at).toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        // Гарантируем что сумма - число
        const amount = typeof t.operation.amount === 'number' ? t.operation.amount : (parseFloat(t.operation.amount) || 0);
        const currency = String(t.currency || '').toLowerCase();
        const wallet_id = String(t.wallet_id || '').toLowerCase();
        return `
            <tr>
                <td>${currentOffset + index + 1})</td>
                <td>${date}</td>
                <td>${typeIcon} <span class="${typeClass}">${typeLabel}</span></td>
                <td>${walletName}</td>
                <td>${wallet_id}</td>
                <td>${t.operation.description}</td>
                <td class="text-end ${typeClass}"><strong>${amount.toFixed(2)} ${currency}</strong></td>
            </tr>
        `;
    }).join('');
}

async function updateTotalBalance() {
    const currency = document.getElementById('currencySelect').value; // rub, usd, eur
    const token = localStorage.getItem('access_token');
    // Формируем URL с query-параметром, если валюта выбрана
    let url = `${API_BASE}/my/wallets/balances`;
    if (currency) {
        url += `?currency=${currency}`;
    }

    try {
        // Получаем общий баланс в рублях с сервера (с конвертацией валют)
        const response = await fetch(url, {
            method: 'GET',
            headers: {'Authorization': `Bearer ${token}`}
        });

        if (response.ok) {
            const providerMap = {
                'api': { class: 'bg-success text-light', label: '👌 Данные точны!' },
                'app': { class: 'bg-warning', label: '❗❗❗ Данные не точны ❗❗❗' },
                'no_provider': { class: 'bg-primary text-light', label: '😂 Ваш общий баланс пуст' }
            };

            const data = await response.json();
            const total = parseFloat(data.total_balance) || 0;
            const currencySymbol = getCurrencySymbol(data.currency);
            const providerInfo = providerMap[data.provider] || providerMap['no_provider'];
            document.getElementById('totalBalance').innerHTML = `
                ${total.toFixed(2)} ${currencySymbol}
                <div class="fs-6 text-muted mt-2">Общий баланс по всем кошелькам</div>
            `;
            document.getElementById("totalBalanceProvider").innerHTML = `
                <b><span class="${providerInfo.class} p-2 rounded">${providerInfo.label}</span></b>    
            `;
        } else {
            const errorMsg = await getErrorMessage(response);
            console.error('Ошибка с балансом:', errorMsg);
            document.getElementById('totalBalance').innerHTML = `
                0.00
                <div class="fs-6 text-center mt-2 text-danger">
                    <hr><tr><td colspan="6">Ошибка: ${errorMsg}</td></tr><hr>
                </div>
            `;
        }
    } catch (e) {
        console.error('Ошибка подключения или загрузки общего баланса:', e);
        // При ошибке показываем 0
        document.getElementById('totalBalance').innerHTML = `
            0.00
            <div class="fs-6 text-muted mt-2">Ошибка подключения или что-то другое</div>
        `;
    }
}

function updateWalletSelects() {
    const selects = [
        'incomeWallet', 'expenseWallet', 'transferFrom', 'transferTo'
    ];

    const currencySymbols = {
        'rub': '₽',
        'usd': '$',
        'eur': '€'
    };

    selects.forEach(id => {
        const select = document.getElementById(id);
        if (!select) return;
        
        if (wallets.length === 0) {
            select.innerHTML = '<option value="">Сначала создайте кошелек</option>';
        } else {
            select.innerHTML = wallets.map(w => {
                // Гарантируем что баланс - число
                const balance = typeof w.balance === 'number' ? w.balance : (parseFloat(w.balance) || 0);
                const currency = String(w.currency || '').toLowerCase();
                const symbol = currencySymbols[currency] || currency.toUpperCase();
                return `<option value="${w.id}">${w.name} - ${balance.toFixed(2)} ${symbol}</option>`;
            }).join('');
        }
    });
}

async function addWallet() {
    const name = document.getElementById('walletName').value.trim();
    const currency = document.getElementById('walletCurrency').value;
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${API_BASE}/my/wallets`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({name, currency})
        });

        if (response.ok) {
            const data = await response.json();
            const walletId = data.wallet.id
            showSuccess(`Кошелек создан! Его id=${walletId}`);
            closeModal('addWalletModal');
            await loadWallets();
        } else {
            const errorMsg = await getErrorMessage(response);
            showError(errorMsg);
        }
    } catch (e) {
            console.error('Ошибка подключения:', e);
            showError('Не удалось подключиться к серверу или что-то другое');
    }
}

async function addIncome() {
    const token = localStorage.getItem('access_token');
    const wallet_id = parseInt(document.getElementById('incomeWallet').value);
    const amount = parseFloat(document.getElementById('incomeAmount').value);
    const descriptionRaw = document.getElementById('incomeDescription').value.trim();

    const body = {
        wallet_id,
        amount,
    }

    if (descriptionRaw) {
        body.description = descriptionRaw
    }

    try {
        const response = await fetch(`${API_BASE}/my/wallets/operations/income`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(body)
        });

        if (response.ok) {
            const data = await response.json();
            const timeCreate = new Date(data.operation.created_at).toLocaleString('ru-RU', {
                day: '2-digit',
                month: '2-digit',
                year: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            const amountData = data.operation.amount
            const walletName = data.wallet_name
            const currencyData = getCurrencySymbol(data.currency)
            showSuccess(`Доход: ${walletName} + ${amountData} ${currencyData}; Дата создания операции: ${timeCreate}`);
            closeModal('addIncomeModal');
            resetToDefaultAndRefresh();
        } else {
            const errorMsg = await getErrorMessage(response);
            showError(errorMsg);
        }
    } catch (e) {
        console.error('Ошибка подключения:', e);
        showError('Не удалось подключиться к серверу или что-то другое');
    }
}

async function addExpense() {
    const token = localStorage.getItem('access_token');
    const wallet_id = parseInt(document.getElementById('expenseWallet').value);
    const amount = parseFloat(document.getElementById('expenseAmount').value);
    const descriptionRaw = document.getElementById('expenseDescription').value.trim();

    const body = {
        wallet_id,
        amount,
    }

    if (descriptionRaw) {
        body.description = descriptionRaw
    }

    try {
        const response = await fetch(`${API_BASE}/my/wallets/operations/expense`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(body)
        });

        if (response.ok) {
            const data = await response.json();
            const timeCreate = new Date(data.operation.created_at).toLocaleString('ru-RU', {
                day: '2-digit',
                month: '2-digit',
                year: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            const amountData = data.operation.amount
            const walletName = data.wallet_name
            const currencyData = getCurrencySymbol(data.currency)
            showSuccess(`Расход: ${walletName} - ${amountData} ${currencyData}; Дата создания операции: ${timeCreate}`);
            closeModal('addExpenseModal');
            resetToDefaultAndRefresh();
        } else {
            const errorMsg = await getErrorMessage(response);
            showError(errorMsg);
        }
    } catch (e) {
        console.error('Ошибка подключения:', e);
        showError('Не удалось подключиться к серверу или что-то другое');
    }
}

async function transfer() {
    const token = localStorage.getItem('access_token');
    const from_wallet_id = parseInt(document.getElementById('transferFrom').value);
    const to_wallet_id = parseInt(document.getElementById('transferTo').value);
    const amount = parseFloat(document.getElementById('transferAmount').value);

    const providerMap = {
        'api': 'Данные точны!',
        'app': 'Данные НЕ точны!',
        'no_provider': 'Что-то пошло не так!'
    };

    try {
        const response = await fetch(`${API_BASE}/my/wallets/operations/transfer`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ from_wallet_id, to_wallet_id, amount })
        });

        if (response.ok) {
            const data = await response.json();

            const amountDataFrom = data.from_wallet.operation.amount
            const walletNameFrom = data.from_wallet.wallet_name
            const currencyDataFrom = getCurrencySymbol(data.from_wallet.currency)

            const amountDataTo = data.to_wallet.operation.amount
            const walletNameTo = data.to_wallet.wallet_name
            const currencyDataTo = getCurrencySymbol(data.to_wallet.currency)

            const providerInfo = providerMap[data.provider] || providerMap['no_provider'];
            showSuccess(
                `Перевод с: ${walletNameFrom} на: ${walletNameTo};
                ${amountDataFrom} ${currencyDataFrom} -> ${amountDataTo} ${currencyDataTo}; ${providerInfo}`
            );
            closeModal('transferModal');
            resetToDefaultAndRefresh();
        } else {
            const errorMsg = await getErrorMessage(response);
            showError(errorMsg);
        }
    } catch (e) {
        console.error('Ошибка подключения:', e);
        showError('Не удалось подключиться к серверу или что-то другое');
    }
}

function initReportDates() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    
    document.getElementById('reportDateFrom').valueAsDate = firstDay;
    document.getElementById('reportDateTo').valueAsDate = tomorrow;
}

async function loadReport() {
    const token = localStorage.getItem('access_token');
    const dateFrom = document.getElementById('reportDateFrom').value;
    const dateTo = document.getElementById('reportDateTo').value;

    if (!dateFrom || !dateTo) {
        showError('Выберите период');
        return;
    }

    try {
        const params = new URLSearchParams({
            date_from: `${dateFrom}`,
            date_to: `${dateTo}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        });

        const response = await fetch(`${API_BASE}/my/wallets/operations/download?${params}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'operations.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            showSuccess('История транзакций скачана!');
        } else {
            const errorMsg = await getErrorMessage(response);
            showError(errorMsg);
        }
    } catch (e) {
        console.error('Ошибка загрузки отчета:', e);
        showError('Ошибка подключения к серверу или что-то другое');
    }
}

// Инициализация после загрузки страницы (событие change)
document.addEventListener('DOMContentLoaded', () => {
    const currencySelect = document.getElementById('currencySelect');
    const token = localStorage.getItem('access_token');

    if (token) {
        currentUser = localStorage.getItem('user_name');
        currentUserId = localStorage.getItem('user_id');
        showMainSection(); // Если пользователь уже авторизован (токен есть), загружаем данные
    }

    if (currencySelect) {
        currencySelect.addEventListener('change', () => {
            updateTotalBalance(); // обновляем общий баланс при смене валюты
        });
    }

});
