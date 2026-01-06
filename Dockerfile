FROM python:3.12-slim

# Чтоб вывод сразу шел в лог
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Сначала зависимости (кэшируется слой)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект (но не venv, если добавишь в .dockerignore)
COPY . .

# При желании: если будешь использовать .env через python-dotenv
# ENV DOTENV_PATH=/app/.env

# Точка входа — твой main.py
CMD ["python", "main.py"]