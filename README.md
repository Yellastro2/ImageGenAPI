# OpenAI API Wrapper

Минималистичное Flask API для генерации изображений и текста через OpenAI с поддержкой анализа изображений.

## 🚀 Возможности

- **Генерация изображений**: DALL-E 3 с поддержкой различных размеров
- **Генерация текста**: GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Анализ изображений**: GPT-4o с поддержкой Vision API
- **Селективный прокси**: Только для OpenAI запросов (опционально)
- **Веб-интерфейс**: Документация и примеры использования

## 📋 Зависимости

```bash
pip install flask flask-cors openai gunicorn httpx
```

Или используйте `pyproject.toml` из проекта.

## ⚙️ Настройка

1. **Скопируйте проект**:
   ```bash
   # Клонируйте или скачайте файлы проекта
   git clone <ваш-репозиторий>
   cd openai-api-wrapper
   ```

2. **Установите зависимости**:
   ```bash
   pip install -r dependencies.txt
   # или
   pip install flask flask-cors openai gunicorn httpx
   ```

3. **Настройте окружение**:
   ```bash
   cp .env.example .env
   nano .env
   ```

4. **Добавьте OpenAI API ключ**:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Запустите сервер**:
   ```bash
   # Для разработки
   python main.py
   
   # Для продакшена
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

## 🔧 API Endpoints

### Генерация изображений
```bash
POST /api/generate-image
{
  "prompt": "A beautiful sunset over mountains",
  "size": "1024x1024"
}
```

### Генерация текста
```bash
POST /api/generate-text
{
  "prompt": "Расскажи о котах",
  "max_tokens": 200,
  "model": "gpt-4"
}
```

### Анализ изображений
```bash
POST /api/generate-text
{
  "prompt": "Что изображено на картинке?",
  "image_url": "https://example.com/image.jpg"
}
```

## 🌐 Прокси (опционально)

Для использования HTTP прокси только для OpenAI запросов:

```env
OPENAI_PROXY=http://your-proxy-server:port
```

## 📂 Структура проекта

```
├── app.py              # Основное приложение Flask
├── main.py             # Точка входа
├── templates/
│   └── index.html      # Веб-интерфейс с документацией
├── static/
│   └── style.css       # Стили
├── .env.example        # Пример конфигурации
├── dependencies.txt    # Список зависимостей
└── README.md          # Этот файл
```

## 🔄 Копирование как Git репозиторий

### Вариант 1: Создание нового репозитория

1. Создайте новый репозиторий на GitHub/GitLab
2. Скопируйте файлы проекта в локальную папку
3. Инициализируйте git:

```bash
cd your-project-folder
git init
git add .
git commit -m "Initial commit: OpenAI API Wrapper"
git branch -M main
git remote add origin https://github.com/username/repo-name.git
git push -u origin main
```

### Вариант 2: Fork на Replit

1. В Replit нажмите "Fork" на этом проекте
2. Переименуйте fork по желанию
3. Настройте свои секреты (OPENAI_API_KEY)

### Важные файлы для копирования

- `app.py` - основная логика API
- `main.py` - точка входа
- `templates/index.html` - веб-интерфейс
- `static/style.css` - стили
- `.env.example` - пример конфигурации
- `pyproject.toml` - зависимости Python

## 🛡️ Безопасность

- API ключ OpenAI храните в переменных окружения
- Не коммитьте файлы `.env` в git
- Используйте HTTPS в продакшене

## 📈 Мониторинг

Логи доступны через:
- Консоль приложения
- Gunicorn логи
- OpenAI API rate limits в заголовках ответов

## ⚡ Развертывание

Проект готов к развертыванию на:
- Replit (текущая платформа)
- Heroku
- Vercel
- Railway
- Любой VPS с Python

Просто настройте переменные окружения и запустите через gunicorn.