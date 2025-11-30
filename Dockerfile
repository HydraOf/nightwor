FROM python:3.11-slim

# Обновляем pip
RUN pip install --upgrade pip

# Рабочая директория
WORKDIR /app

# Копируем проект
COPY . .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Запуск бота
CMD ["python", "nightwor/bot.py"]
