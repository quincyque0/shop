# Архитектура проекта devices-s22

## Описание
Проект состоит из двух микросервисов:
1. **devices-svc-s22** - основной сервис для управления устройствами.
2. **API Gateway** - точка входа, маршрутизирует запросы (например, `/api/devices`) к сервису.

## Взаимодействие
- Внешние клиенты общаются с API Gateway по HTTP (REST/GraphQL).
- API Gateway общается с микросервисами по gRPC.

## Инфраструктура
- Сервисы упакованы в Docker.
- Локальный запуск осуществляется через `docker-compose up`.

## Дополнительные поля
Устройство (device) содержит дополнительное поле `serial` (str).

## CI/CD Pipeline

Проект использует **GitHub Actions** для автоматизации всего жизненного цикла.

### Стадии пайплайна

```
┌──────────┐   ┌──────────────┐   ┌─────────────┐   ┌──────────┐   ┌─────────┐   ┌────────────┐
│  1. Lint  │──▶│ 2. Build &   │──▶│ 3. Security │──▶│4. Publish│──▶│5.Deploy │──▶│ 6. Deploy  │
│  (flake8  │   │    Test      │   │    Scan     │   │ (ghcr.io)│   │ Staging │   │ Production │
│  hadolint │   │ (compose+    │   │  (Trivy)    │   │          │   │ (Helm)  │   │   (Helm)   │
│  helm)    │   │  curl tests) │   │             │   │          │   │         │   │            │
└──────────┘   └──────────────┘   └─────────────┘   └──────────┘   └─────────┘   └────────────┘
```

| Стадия | Описание | Триггер |
|--------|----------|---------|
| **Lint** | flake8 (Python), hadolint (Dockerfile), helm lint | Каждый push/PR |
| **Build & Test** | Сборка Docker-образов, интеграционные тесты через docker-compose | После lint |
| **Security Scan** | Trivy — сканирование на уязвимости (CRITICAL, HIGH) | После build |
| **Publish** | Push образов в GitHub Container Registry (ghcr.io) | Только push в main |
| **Deploy Staging** | Helm deploy/dry-run в staging namespace | После publish |
| **Deploy Production** | Helm deploy/dry-run в production namespace (manual approval) | После staging |
