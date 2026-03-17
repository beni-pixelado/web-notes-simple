# Nome da imagem Docker
IMAGE_NAME=notes-app

# Porta padrão
PORT=8000

# 🚀 Desenvolvimento

run:
	uvicorn backend.main:app --host 0.0.0.0 --port $(PORT) --reload

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	uvicorn backend.main:app --reload


# 🐳 Docker


docker-build:
	docker build -t $(IMAGE_NAME) .

docker-run:
	docker run -p $(PORT):$(PORT) $(IMAGE_NAME)

docker-dev:
	docker build -t $(IMAGE_NAME) .
	docker run -p $(PORT):$(PORT) -v $$(pwd):/app $(IMAGE_NAME)

# 🧹 Limpeza

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

# 🧪 Qualidade de código

format:
	black .

lint:
	flake8 .


# ⚙️ Utilitários

start:
	make install
	make run