all: build up migrate
	@echo "TerraPulse is running at http://localhost:8000"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

shell:
	docker compose exec web python manage.py shell

migrate:
	docker compose exec web python manage.py migrate

clean:
	docker compose down -v --rmi local
	@echo "Volumes and images removed."

.PHONY: all build up down restart logs shell migrate clean