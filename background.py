from flask import Flask
from flask import request
from threading import Thread
import time
import requests
from github import Github
import hashlib
import base64

def is_file_changed_locally():
    # Инициализация объекта GitHub с использованием персонального токена
    g = Github('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')
    
    # Получаем репозиторий
    repo = g.get_user().get_repo('tg_ystal_db')
    
    # Получаем содержимое файла users.db с GitHub
    contents = repo.get_contents('users.db')
    
    # Получаем MD5 текущего содержимого на GitHub
    github_content_md5 = hashlib.md5(contents.decoded_content).hexdigest()
    
    # Читаем локальный файл и вычисляем его MD5
    with open('users.db', 'rb') as file:
        local_content = file.read()
        local_content_md5 = hashlib.md5(local_content).hexdigest()
    
    # Сравниваем MD5
    if local_content_md5 != github_content_md5:
        return True
    else:
        return False




def download_file_from_github():
    try:
        if is_file_changed_locally():
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
        else:
            pass
    except Exception as e:
        if "No such file or directory: 'users.db'" in str(e):
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
    if is_file_changed_locally():
        # Инициализация объекта GitHub с использованием персонального токена
        g = Github('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')
        
        # Получаем репозиторий
        repo = g.get_user().get_repo('tg_ystal_db')
        
        # Читаем локальный файл users.db
        with open('users.db', 'rb') as file:
            content = file.read()
        
        # Получаем содержимое файла users.db на GitHub
        contents = repo.get_contents('users.db')
        
        # Обновляем файл на GitHub
        repo.update_file(contents.path, "Updated successfully", content, contents.sha)
        print('File updated successfully.')
    else:
        pass





app = Flask(__name__)

@app.route('/')
def home():
    return "Всё работает! Я живой и готов к работе!"

def run():
    app.run(host='0.0.0.0', port=8080)



def print_hello():
    while True:
        time.sleep(40)
        upload_file_to_github()
        download_file_from_github()
        
          # Подождать 60 секунд (1 минута)

def keep_alive():
    # Запускаем Flask приложение в отдельном потоке
    download_file_from_github()
    flask_thread = Thread(target=run)
    flask_thread.start()

    # Запускаем поток для print("Hello")
    print_hello_thread = Thread(target=print_hello)
    print_hello_thread.start()
