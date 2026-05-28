# Финальный проект


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


## Как проверить
```bash
make test WEEK=17
```
Тест проверит наличие основных файлов и документации.
# shop
