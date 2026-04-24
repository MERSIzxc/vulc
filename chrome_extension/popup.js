document.addEventListener('DOMContentLoaded', () => {
    const parseBtn = document.getElementById('parseBtn');
    const setupBtn = document.getElementById('setupBtn');
    const saveKeyBtn = document.getElementById('saveKeyBtn');
    const backBtn = document.getElementById('backBtn');
    const statusDiv = document.getElementById('status');
    const mainDiv = document.getElementById('main');
    const setupDiv = document.getElementById('setup');
    const apiKeyInput = document.getElementById('apiKey');

    // Проверяем есть ли API ключ
    chrome.storage.sync.get(['apiKey'], (result) => {
        if (!result.apiKey) {
            showStatus('Настрой API ключ в настройках', 'info');
        }
    });

    // Показать настройки
    setupBtn.addEventListener('click', () => {
        mainDiv.style.display = 'none';
        setupDiv.classList.add('active');

        chrome.storage.sync.get(['apiKey'], (result) => {
            if (result.apiKey) {
                apiKeyInput.value = result.apiKey;
            }
        });
    });

    // Назад
    backBtn.addEventListener('click', () => {
        setupDiv.classList.remove('active');
        mainDiv.style.display = 'block';
    });

    // Сохранить API ключ
    saveKeyBtn.addEventListener('click', () => {
        const apiKey = apiKeyInput.value.trim();

        if (apiKey) {
            chrome.storage.sync.set({ apiKey: apiKey }, () => {
                showStatus('API ключ сохранен!', 'success');
                setTimeout(() => {
                    setupDiv.classList.remove('active');
                    mainDiv.style.display = 'block';
                }, 1500);
            });
        } else {
            showStatus('Введи API ключ', 'error');
        }
    });

    // Парсить оценки
    parseBtn.addEventListener('click', async () => {
        parseBtn.disabled = true;
        parseBtn.textContent = 'Сохранение...';
        statusDiv.innerHTML = '';

        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            if (!tab.url.includes('vulcan.net.pl') && !tab.url.includes('eduvulcan.pl')) {
                showStatus('Открой страницу с оценками в Vulcan', 'error');
                parseBtn.disabled = false;
                parseBtn.textContent = 'Сохранить оценки';
                return;
            }

            // Проверяем что content script загружен
            try {
                await chrome.tabs.sendMessage(tab.id, { action: 'ping' });
            } catch (e) {
                showStatus('Перезагрузи страницу Vulcan и попробуй снова', 'error');
                parseBtn.disabled = false;
                parseBtn.textContent = 'Сохранить оценки';
                return;
            }

            chrome.tabs.sendMessage(tab.id, { action: 'parseGrades' }, (response) => {
                parseBtn.disabled = false;
                parseBtn.textContent = 'Сохранить оценки';

                if (chrome.runtime.lastError) {
                    showStatus('Ошибка: ' + chrome.runtime.lastError.message, 'error');
                    return;
                }

                if (response && response.success) {
                    showStatus(response.message, 'success');
                } else {
                    showStatus('Ошибка: ' + (response ? response.error : 'Нет ответа'), 'error');
                }
            });
        } catch (error) {
            parseBtn.disabled = false;
            parseBtn.textContent = 'Сохранить оценки';
            showStatus('Ошибка: ' + error.message, 'error');
        }
    });

    function showStatus(message, type) {
        statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
    }
});
