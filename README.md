# Финальный проект

![CI](https://github.com/OWNER/REPO/actions/workflows/week-17-ci.yml/badge.svg)

## Задача
Поздравляем! Вы дошли до финала. Теперь у вас есть набор знаний, который необходимо объединить в общую картину: REST, gRPC, Docker, K8s, CI/CD.
Пришло время собрать всё это вместе в один финальный проект.

## Ваш вариант
`variants/<GROUP>/<STUDENT_ID>/week-17.json`
Там описана тема вашего проекта (например, "Сервис доставки еды" или "Трекер задач").

## Что нужно сделать
1. **Архитектура**:
   - Спроектируйте систему из 2-3 микросервисов.
   - Опишите её в `ARCHITECTURE.md` (кто с кем общается, какие базы данных, какие протоколы).
2. **Реализация**:
   - Напишите код сервисов (можно переиспользовать код с прошлых недель).
   - Выберите протокол осознанно: где-то REST для фронтенда, где-то gRPC для межсервисного общения.
3. **Инфраструктура**:
   - Упакуйте всё в Docker.
   - Напишите docker-compose для локального запуска.
   - (Опционально) Helm чарт для Кубернетиса.
   - Настройте (или опишите) CI пайплайн.
4. **Сдача**:
   - Проект должен запускаться одной командой и иметь документацию.

## Быстрый старт

```bash
# Локальный запуск
docker compose up --build -d

# Или через Makefile
make up

# Проверка здоровья
curl http://localhost:8000/health

# Остановка
make down
```

## CI/CD Pipeline

Проект использует **GitHub Actions** с 6-стадийным пайплайном:

1. **Lint** — flake8 + hadolint + helm lint
2. **Build & Test** — сборка образов + интеграционные тесты
3. **Security Scan** — Trivy (уязвимости CRITICAL/HIGH)
4. **Publish** — push в ghcr.io (только main)
5. **Deploy Staging** — Helm dry-run/deploy
6. **Deploy Production** — Helm deploy (manual approval)

### Настройка секретов

Для публикации образов в `ghcr.io` используется встроенный `GITHUB_TOKEN` — дополнительная настройка не нужна.

Для деплоя в реальный K8s-кластер добавьте в GitHub Secrets:
- `KUBE_CONFIG` — base64-encoded kubeconfig для staging
- `KUBE_CONFIG_PROD` — base64-encoded kubeconfig для production

### Makefile

```bash
make help           # Справка по командам
make build          # Сборка образов
make up             # Запуск сервисов
make down           # Остановка
make lint           # Линтинг
make test           # Интеграционные тесты
make helm-lint      # Проверка Helm-чарта
make helm-template  # Dry-run Helm
```

## Что сдавать
1. Полный код проекта.
2. `ARCHITECTURE.md`.
3. Инструкция по запуску.

## Как проверить
```bash
make test WEEK=17
```
Тест проверит наличие основных файлов и документации.
# shop
