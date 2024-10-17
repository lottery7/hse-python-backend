# Запуск приложения без тестов
```
uvicorn lecture_1.hw.math_plain_asgi:app
```

# Запуск тестов через poetry
```
poetry run pytest -vv --strict --showlocals .\tests\test_homework_1.py
```
