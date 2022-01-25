##  Welltory stats API


Описание API

http://localhost:5000/swagger/

или

http://localhost/swager/ (при запуске docker-compose up --build)

Последовательность действи при работе с API:

1) Регистрируем пользователя
2) Логинимся и получаем JWT токен
3) Работаем с API - добавляем данные, смотрим статистику


### Для запуска в разработчика нужно:
#### Создать окружение
```
git clone git@github.com:mechnotech/welltory_test.git
cd welltory_test
python -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt
```
#### Запустить контейнеры с Redis и Postgres
`docker-compose -f dev-compose.yaml up -d`

#### Применить миграции alembic
`alembic upgrade head`

#### Запуск приложения:
`python src/pywsgi.py`


####

## Для запуска полной сборки на сервере
```
git clone git@github.com:mechnotech/welltory_test.git
cd welltory_test
cp .env.example .env
docker-compose -up -d
```


Приложение будет доступно по адресу http://localhost или http://127.0.0.1

Документированное API http://localhost/swagger/



