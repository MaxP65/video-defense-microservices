# Docker-проверка: 8 ноября 2026

Статус: завершено. Все пять образов собраны; Collector, Storage, ML, Web Master и Visualization запущены и healthy. Незапланированных перезапусков контейнеров на момент проверки: 0.

Запуск:

```bash
docker compose --env-file config/ports.env up --build -d --wait --wait-timeout 180
docker compose --env-file config/ports.env ps
python scripts/demo.py --epochs 40 --output artifacts/docker
```

Интерфейс: http://localhost:8760. Swagger Web Master: http://localhost:8761/docs. Локальные Python-процессы проекта остановлены, эти порты обслуживают контейнеры. Контейнеры оставлены запущенными.

| Сервис | Проверка | Результат |
|---|---|---|
| Collector | Импорт, повторный импорт, батч val с offset | 72 видео; повторно 0 новых; 2/18 элементов |
| Storage | Создание, чтение, обновление, удаление записи; хранение видео и весов | passed |
| ML | Обучение обеих моделей, summary, FGSM и очистка validation-клипа | completed |
| Web Master | Сценарии по HTTP, health зависимостей, ошибка неверного split | passed, HTTP 422 для неверного split |
| Visualization | HTML страницы и API-прокси; доступ к двум обученным моделям | HTTP 200, passed |

Окружение ML-контейнера: Python 3.12.16, PyTorch 2.4.1+cpu, OpenCV 4.11.0, FastAPI 0.124.4, CUDA не используется. ID контейнеров и образов, версии и статусы сохранены в `artifacts/docker/runtime-run.json` и [сгенерированной карточке](experiments/runs/docker.md).

Обучение: 40 эпох каждой модели, seed 42, train 36 / validation 18 / test 18, разбиение по группам исходных видео. Контроль MSE×0: тот же бюджет. Веса выбраны по validation-loss; test не использован. Диагностика классификатора: passed, очистителя: passed. Время классификатора: 32.92 с; очистителя с контрольной абляцией: 48.34 с.

| CPU validation-протокол | Правильные / всего |
|---|---:|
| Исходные клипы | 13/18 |
| FGSM против классификатора | 5/18 |
| Очистка тех же FGSM-примеров | 8/18 |
| Очистка исходных клипов | 14/18 |
| Контроль MSE×0 после FGSM | 5/18 |

PSNR по общей MSE: 30.43 → 31.92 дБ. Это диагностика обучения при classifier-only FGSM, не adaptive robust accuracy. Один шаг FGSM, EOT=1, voting=1. На первом validation-примере ApplyEyeMakeup атака изменила класс на BasketballDunk; CPU-очиститель уменьшил MSE, но правильный класс не восстановил. Результаты CPU отличаются от предыдущего GPU-запуска и сохраняются отдельно. Настройки по test не подбирались; adaptive/transfer sweep в этой Docker-проверке не запускался.

Веса и метаданные CPU-запуска находятся в отдельном named volume `vcr-microservices_storage`; прежние локальные веса и SQLite не изменены. Полные manifests, loss, градиенты, SHA256 кода и весов, split, ID запусков, времена и результаты: `artifacts/docker/` и [карточки](experiments/runs/docker.md).
