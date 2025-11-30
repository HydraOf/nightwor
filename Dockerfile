# Используем стабильный Python 3.11
FROM python:3.11-slim

# Обновляем pip
RUN pip install --upgrade pip

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Команда запуска бота
CMD ["python", "bot.py"]
