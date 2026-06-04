# Автоматизированная система уведомлений для медицинского центра

**Корпоративная платформа для автоматической отправки уведомлений пациентам через WhatsApp и SMS с интеграцией CRM Bitrix24 и Telegram-панелью администратора.**

## 🚀 Возможности

- **Dual-channel отправка**: Автоматическая доставка сообщений через WhatsApp (Wazzup) для клиники и SMS (SMS Aero) для психологической службы
- **Интеграция с Bitrix24**: Автоматическое извлечение номеров телефонов из сделок CRM и формирование ссылок на карточки сделок
- **Telegram Admin Bot**: Полноценная панель управления рассылками с созданием, редактированием и удалением сообщений
- **Ролевая модель**: Разграничение прав между пользователями и администраторами с хешированием паролей (bcrypt)
- **Автоматическая отчётность**: Ежедневные сводки об отправке сообщений (успешно/неуспешно/затраты) с доставкой в Telegram
- **Планировщик задач**: Автоматический запуск отчётов по расписанию через APScheduler
- **Логирование отправок**: Полное сохранение истории сообщений с метаданными (статус, цена, ID сделки)

## 🛠 Технологии

- **API сервер**: FastAPI (асинхронный), Uvicorn
- **Telegram бот**: Aiogram 3.x (FSM, Inline-клавиатуры, пагинация)
- **База данных**: PostgreSQL, SQLAlchemy 2.0 (async), asyncpg
- **Внешние сервисы**: SMS Aero API, Wazzup API (WhatsApp), Bitrix24 REST API
- **Деплой**: Docker, Docker Compose
- **Авторизация**: Bcrypt (хеширование паролей администратора)

## 🏗 Архитектура

```
├── API сервис (FastAPI)   → Webhook-приём данных из CRM, отправка уведомлений
├── Bot сервис (Aiogram)   → Панель управления рассылками, авторизация
├── PostgreSQL             → Сообщения, отчёты об отправках, пользователи
└── Внешние API            → Bitrix24 (CRM), SMS Aero, Wazzup (WhatsApp)
```

## 📦 Быстрый старт

```bash
# Клонирование репозитория
git clone <repository-url>
cd mcmk-notification-service

# Настройка окружения
cp .env.example .env
# Отредактируйте .env (укажите API-ключи, данные БД, токен Telegram)

# Запуск через Docker Compose
docker-compose up -d

# Проверка работы API
curl http://localhost/health
```

## 🔧 Переменные окружения

```env
# База данных
POSTGRES_ENGINE=postgresql+asyncpg://user:pass@localhost:5432/db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=mcmk_notifications

# Bitrix24 интеграция
BITRIX24_WEBHOOK_URL=https://klinikamsmk.bitrix24.ru/rest/1/.../crm.deal.get.json

# SMS Aero (для психологической службы)
SMSAERO_EMAIL=your@email.com
SMSAERO_API_KEY=your_api_key

# Wazzup (WhatsApp для клиники)
WAZZUP_API_KEY=your_wazzup_key
WAZZUP_CHANNEL_ID=your_channel_id

# Telegram бот
TELEGRAM_API_TOKEN=your_bot_token
TELEGRAM_USER_ID=your_admin_chat_id
TG_HASHED_PASSWORD=bcrypt_hashed_password
```

## 📁 Структура проекта

```
├── api/                    # FastAPI эндпоинты, helpers, маршруты
│   ├── routers/            # messages.py, tests.py
│   ├── tlg.py              # Отправка уведомлений в Telegram
│   └── helpers.py          # MessageSender, обработка webhook-ов
├── bot/                    # Aiogram бот (handlers, keyboards)
│   ├── handlers/           # user.py, admin.py, messages.py
│   ├── keyboards/          # Инлайн-клавиатуры с пагинацией
│   └── scheduler.py        # APScheduler (ежедневные отчёты)
├── database/               # Модели SQLAlchemy, сервисы для БД
│   ├── core.py             # AsyncSession, engine
│   └── messages/           # models.py, services.py
├── docker-compose.yml      # PostgreSQL + API + Bot
└── .env                    # Конфигурация окружения
```

## 🧪 Тестовые сценарии

### Через API (Bitrix24 webhook)
```bash
# Webhook для клиники (WhatsApp)
POST /api/messages/clinic
{
  "document_id[2]": "DEAL_12345",
  ...
}

# Ручной вызов для психологической службы (SMS)
POST /api/messages/psy?phone_number=79001234567
```

### Через Telegram бота
1. **Старт**: `/start` → авторизация с паролем администратора
2. **Управление рассылками**: Создание, просмотр, удаление сообщений
3. **Просмотр всех сообщений**: Пагинированный список через `KeyboardPaginator`
4. **Автоматические отчёты**: Ежедневно в 20:00 (PSY) и 23:59 (Клиника)

## 📊 Формат отчёта

```html
<b>🟢 МСМК-Веб | Сообщение отправлено</b>
<b>Номер:</b> 79001234567
<b>Время:</b> 14:30
<b>Сообщение:</b> "Ваша запись подтверждена..."
<b>Стоимость:</b> 0.85 р.
```

## 🐳 Docker Compose

```yaml
services:
  db:     # PostgreSQL
  api:    # FastAPI на порту 80
  bot:    # Aiogram бот
```

## 📝 Примечания

- SMS Aero требует валидации номера телефона (при неудаче — подробности в кабинете)
- WhatsApp-уведомления отправляются через Wazzup, требуется наличие активного канала
- Bitrix24 интеграция работает через REST API с предустановленным webhook
