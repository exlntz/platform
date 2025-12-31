чтобы запустить скачайте docker desktop,
в файл .env вставьте данные из тг,
запуск приложения docker-compose up -d --build,
далее создание БД docker-compose run --rm app alembic upgrade head,
бекенд http://localhost:8000 ,
документация http://localhost:8000/docs ,
фронтенд http://localhost:5173 ,
логи бек docker-compose logs -f app ,
логи фронт docker-compose logs -f web

