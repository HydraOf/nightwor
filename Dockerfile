# Базовый образ Python 3.11
FROM python:3.11-slim

# Обновляем pip
RUN pip install --upgrade pip

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем все файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Запуск бота
CMD ["python", "bot.py"]
