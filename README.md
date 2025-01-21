# Build da imagem do app
docker build -t deboraferrarids2/app:latest .
docker push deboraferrarids2/app:latest

# Build da imagem do worker (Celery)
docker build -t deboraferrarids2/worker:latest .
docker push deboraferrarids2/worker:latest



# testes

pytest app/tests/test_app.py --disable-warnings -v

coverage run --source=app --omit=app/tests/* -m pytest --disable-warnings
coverage report -m


