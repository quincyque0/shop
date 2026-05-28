# Микросервисный Интернет-Магазин 

Это финальный проект, представляющий собой распределенную микросервисную систему. Проект объединяет все ключевые технологии курса: REST API, gRPC, RabbitMQ, PostgreSQL, Docker и GitHub Actions.

##  Архитектура

Система состоит из следующих сервисов:
- API Gateway (Порт: 8000) — единая точка входа.
- Catalog Service — REST API и gRPC-сервер для управления товарами.
- Order Service — управление заказами (обращается к Catalog через gRPC).
- Notification Service — асинхронный воркер, получающий сообщения из RabbitMQ.


---

## Как запустить проект



1. Запустить все сервисы в фоновом режиме:
   
   docker compose up --build -d
   
   *Docker Compose автоматически поднимет БД (PostgreSQL), брокер сообщений (RabbitMQ) и все 4 микросервиса. Запуск может занять около 10-15 секунд.*

2. Проверить статус системы (Health Check):
   
   curl -f http://localhost:8000/health
   
   *Если всё работает корректно, получите ответ: `{"status":"ok"}`*

---

## Как проверить работоспособность (Интеграционный тест)

Протестировать весь цикл взаимодействия сервисов с помощью curl:

Шаг 1. Создание товара в каталоге:

curl -s -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -d '{"name":"MacBook Pro","description":"Apple M2","price":2000.0,"stock":10}'


Шаг 2. Проверка списка товаров:

curl -s http://localhost:8000/api/products


Шаг 3. Создание заказа (Триггерит gRPC и RabbitMQ):

curl -s -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":1,"customer_email":"user@example.com"}'

*В этот момент order-svc по gRPC проверит наличие товара в каталоге, сохранит заказ в БД и отправит событие в RabbitMQ.*

Шаг 4. Проверка получения уведомления:
Посмотрите логи сервиса уведомлений, чтобы убедиться, что он успешно обработал событие из очереди:

docker compose logs notification-svc



---

## Остановка проекта

Чтобы остановить все контейнеры и удалить созданные сети и volumes (сбросить БД):

docker compose down -v


---

## CI/CD Пайплайн

В проекте настроен автоматизированный CI/CD пайплайн на базе GitHub Actions. При каждом Push/Pull Request пайплайн выполняет 6 стадий:
1. Lint (Проверка кода Python flake8, Dockerfiles hadolint, Helm-чартов).
2. Build & Test (Сборка образов и прогон интеграционных тестов).
3. Security Scan (Поиск уязвимостей через `Trivy`).
4. Publish (Публикация в GitHub Container Registry `ghcr.io`).
5. Deploy Staging (Helm dry-run/deploy).
6. Deploy Production (Helm deploy с ручным подтверждением).
