from flask import Flask
from flask import request
from threading import Thread
import time
import requests
from github import Github

def download_file_from_github():
    # Инициализация объекта GitHub с использованием персонального токена
    g = Github('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')
    
    # Получаем репозиторий
    repo = g.get_user().get_repo('tg_ystal_db')
    
    # Получаем содержимое файла users.db
    contents = repo.get_contents('users.db')
    
    # Скачиваем файл
    with open('users.db', 'wb') as file:
        file.write(contents.decoded_content)
        print('File downloaded successfully.')

def upload_file_to_github():
    # Инициализация объекта GitHub с использованием персонального токена
    g = Github('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')
    
    # Получаем репозиторий
    repo = g.get_user().get_repo('tg_ystal_db')
    
    # Получаем содержимое файла users.db
    contents = repo.get_contents('users.db')
    
    # Читаем локальный файл users.db
    with open('users.db', 'rb') as file:
        content = file.read()
    
    # Обновляем файл на GitHub
    repo.update_file(contents.path, "Updated successfully", content, contents.sha)
    print('File updated successfully.')




app = Flask(__name__)

@app.route('/')
def home():
    return "Всё работает! Я живой и готов к работе!"

def run():
    app.run(host='0.0.0.0', port=8080)



def print_hello():
    while True:
        upload_file_to_github()
        download_file_from_github()
        
        time.sleep(60)  # Подождать 60 секунд (1 минута)

def start_all():
    # Запускаем Flask приложение в отдельном потоке
    flask_thread = Thread(target=run)
    flask_thread.start()

    # Запускаем поток для print("Hello")
    print_hello_thread = Thread(target=print_hello)
    print_hello_thread.start()
