# Video Defense Microservices

Обучение классификатора действий в видео, FGSM-атака и очистка атакованных кадров. Используется небольшая выборка UCF101 из трёх классов.

Пять сервисов: Collector, Storage, ML, Web Master и Visualization. Каждый запускается в отдельном Docker-контейнере.

## Запуск

Нужны Python 3.12 и запущенный Docker Desktop.

```bash
pip install -r requirements-api.txt
python scripts/prepare_data.py
docker compose --env-file config/ports.env up --build -d
```

Интерфейс: http://localhost:8760. API: http://localhost:8761/docs.

В интерфейсе загрузить подготовленный набор, обучить классификатор, затем очиститель. Выбрать видео и модели, нажать «Сравнить». Результаты сохраняются в истории.

Остановка:

```bash
docker compose --env-file config/ports.env down
```

Настройки находятся в `config/`. Результаты проверки: [docs/docker-verification.md](docs/docker-verification.md).
