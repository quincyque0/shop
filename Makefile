.PHONY: build up down logs lint test helm-lint helm-template clean

SERVICES = api-gateway catalog-svc order-svc notification-svc
COMPOSE  = docker compose

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f

restart:
	$(COMPOSE) down -v && $(COMPOSE) up --build -d

lint:
	@for svc in $(SERVICES); do \
		flake8 $$svc/ --max-line-length=120 --ignore=E501,W503 || exit 1; \
	done

test: up
	@sleep 15
	curl -f http://localhost:8000/health
	curl -s -X POST http://localhost:8000/api/products \
		-H "Content-Type: application/json" \
		-d '{"name":"Test","description":"test","price":100,"stock":5}'
	curl -s http://localhost:8000/api/products
	curl -s -X POST http://localhost:8000/api/orders \
		-H "Content-Type: application/json" \
		-d '{"product_id":1,"quantity":2,"customer_email":"test@test.com"}'
	curl -s http://localhost:8000/api/orders

helm-lint:
	helm lint helm/shop/

helm-template:
	helm template shop helm/shop/ -f helm/shop/values-staging.yaml

helm-template-prod:
	helm template shop helm/shop/ -f helm/shop/values-production.yaml

clean:
	docker system prune -f
