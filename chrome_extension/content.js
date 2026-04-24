// Парсим оценки из одного семестра
async function parseGradesFromCurrentView() {
    const grades = [];

    console.log('Parsing grades from current view...');

    // Ищем ВСЕ элементы на странице
    const allElements = document.querySelectorAll('*');
    console.log('Total elements:', allElements.length);

    // Паттерн для оценок: число/число или число.число/число
    const gradePattern = /(\d+(?:\.\d+)?\/\d+)/;

    const gradeElements = [];

    // Сначала собираем все элементы с оценками
    allElements.forEach((el) => {
        if (el.children.length === 0) {
            const text = el.textContent.trim();

            if (gradePattern.test(text)) {
                const match = text.match(gradePattern);
                if (match) {
                    const gradeValue = match[1];

                    // Пропускаем если в той же строке есть процент (итоговые суммы)
                    const parentRow = el.closest('tr, div, .row, [class*="row"]');
                    if (parentRow) {
                        const rowText = parentRow.textContent;
                        if (rowText.includes('%')) {
                            return;
                        }
                    }

                    // Ищем кликабельный родительский элемент
                    let clickableElement = el;
                    let current = el;
                    for (let i = 0; i < 10 && current; i++) {
                        if (current.onclick || current.style.cursor === 'pointer' ||
                            window.getComputedStyle(current).cursor === 'pointer') {
                            clickableElement = current;
                            break;
                        }
                        current = current.parentElement;
                    }

                    gradeElements.push({
                        element: clickableElement,
                        value: gradeValue,
                        textElement: el
                    });
                }
            }
        }
    });

    console.log(`Found ${gradeElements.length} grade elements`);

    // Теперь кликаем на каждую оценку и парсим детали
    for (let i = 0; i < gradeElements.length; i++) {
        const gradeData = gradeElements[i];

        console.log(`Processing grade ${i + 1}/${gradeElements.length}: ${gradeData.value}`);

        // Кликаем на оценку
        gradeData.element.click();

        // Ждем появления окошка справа
        await new Promise(resolve => setTimeout(resolve, 500));

        // Ищем дату и вес в окошке справа
        let date = '';
        let weight = '1'; // По умолчанию вес 1

        // Вариант 1: Ищем строку с меткой "Data" и "Waga"
        const infoRows = document.querySelectorAll('.info-row, [class*="info"], [class*="detail"], [class*="row"]');
        console.log(`Found ${infoRows.length} potential info rows`);

        for (const row of infoRows) {
            const label = row.querySelector('.info-label, [class*="label"]');
            if (label) {
                const labelText = label.textContent.trim();

                // Ищем дату
                if (labelText.includes('Data')) {
                    const valueCell = row.querySelector('.info-text, [class*="text"], [class*="value"]');
                    if (valueCell) {
                        date = valueCell.textContent.trim();
                        console.log(`Found date in info-row: ${date}`);
                    }
                }

                // Ищем вес
                if (labelText.includes('Waga')) {
                    const valueCell = row.querySelector('.info-text, [class*="text"], [class*="value"]');
                    if (valueCell) {
                        weight = valueCell.textContent.trim();
                        console.log(`Found weight in info-row: ${weight}`);
                    }
                }
            }
        }

        // Вариант 2: Ищем любой текст с форматом даты DD.MM.YYYY
        if (!date) {
            const allText = document.body.textContent;
            const datePattern = /(\d{2}\.\d{2}\.\d{4})/g;
            const dates = allText.match(datePattern);
            if (dates && dates.length > 0) {
                // Берем последнюю найденную дату (скорее всего из открытого окошка)
                date = dates[dates.length - 1];
                console.log(`Found date via pattern: ${date}`);
            }
        }

        // Пропускаем если дата не найдена (это не настоящая оценка)
        if (!date) {
            console.log(`Skipping ${gradeData.value} - no date found`);
            continue;
        }

        // Ищем предмет
        let subject = 'Неизвестный предмет';
        let current = gradeData.textElement.parentElement;

        for (let j = 0; j < 20 && current; j++) {
            const heading = current.querySelector('h1, h2, h3, h4, h5, h6');
            if (heading && heading.textContent.trim().length > 0 && heading.textContent.trim().length < 100) {
                subject = heading.textContent.trim();
                break;
            }
            current = current.parentElement;
        }

        console.log(`Grade ${gradeData.value} -> Subject: ${subject}`);

        // Пропускаем оценки с предметом "Oceny" (это не настоящий предмет)
        if (subject === 'Oceny' || subject.includes('Oceny')) {
            console.log(`Skipping grade from non-subject: ${subject}`);
            continue;
        }

        grades.push({
            subject: subject,
            value: gradeData.value,
            weight: weight,
            description: gradeData.textElement.title || gradeData.textElement.getAttribute('aria-label') || '',
            date: date,
            teacher: ''
        });

        // Закрываем окошко (если есть кнопка закрытия)
        const closeButton = document.querySelector('[class*="close"], [aria-label*="close"], [aria-label*="Close"]');
        if (closeButton) {
            closeButton.click();
            await new Promise(resolve => setTimeout(resolve, 200));
        }
    }

    console.log(`Grades parsed from current view: ${grades.length}`);
    return grades;
}

// Парсим оценки со всех семестров
async function parseGrades() {
    console.log('Starting to parse grades...');
    console.log('Current URL:', window.location.href);

    // Просто парсим все видимые оценки на странице
    // Пользователь сам разворачивает нужный семестр перед импортом
    const grades = await parseGradesFromCurrentView();

    console.log(`=== FINAL: Total grades parsed: ${grades.length} ===`);
    return grades;
}

// Отправляем оценки на сервер
async function sendGradesToServer(grades, apiKey) {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/import-grades/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey
            },
            body: JSON.stringify({ grades: grades })
        });

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error sending grades:', error);
        throw error;
    }
}

// Слушаем сообщения от popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'ping') {
        sendResponse({ success: true });
        return true;
    }

    if (request.action === 'parseGrades') {
        parseGrades().then(grades => {
            if (grades.length > 0) {
                chrome.storage.sync.get(['apiKey'], (result) => {
                    if (result.apiKey) {
                        sendGradesToServer(grades, result.apiKey)
                            .then(response => {
                                sendResponse({
                                    success: true,
                                    count: grades.length,
                                    message: `Сохранено ${grades.length} оценок`
                                });
                            })
                            .catch(error => {
                                sendResponse({
                                    success: false,
                                    error: error.message
                                });
                            });
                    } else {
                        sendResponse({
                            success: false,
                            error: 'API ключ не настроен'
                        });
                    }
                });
            } else {
                sendResponse({
                    success: false,
                    error: 'Оценки не найдены на странице'
                });
            }
        }).catch(error => {
            sendResponse({
                success: false,
                error: error.message
            });
        });
        return true; // Асинхронный ответ
    }
});

console.log('Vulcan Tracker content script loaded');
