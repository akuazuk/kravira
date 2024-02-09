# Используйте официальный образ Python как базовый
FROM python:3.8-slim

# Установите рабочую директорию в контейнере
WORKDIR /app

# Копируйте файлы проекта в контейнер
COPY . .

# Установите Python зависимости из файла requirements.txt
# Создает виртуальное окружение и активирует его
# Устанавливает зависимости из файла requirements.txt
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Укажите переменную окружения для использования виртуального окружения
ENV PATH="/opt/venv/bin:$PATH"

# Команда для запуска бота
CMD ["python", "bot.py"]
