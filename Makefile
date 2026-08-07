.PHONY: help build test lint fmt clean install run

help:
	@echo "ELAP Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install     Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make build       Build all (Rust + Python + Web)"
	@echo "  make test        Run all tests"
	@echo "  make lint        Run linters"
	@echo "  make fmt         Format code"
	@echo "  make clean       Clean build artifacts"
	@echo ""
	@echo "Running:"
	@echo "  make run         Start all services"
	@echo "  make run-rust    Start Rust core"
	@echo "  make run-python  Start Python AI Runtime"
	@echo "  make run-web     Start Web dev server"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up   Start services (docker-compose)"
	@echo "  make docker-down Stop services"

install:
	@echo "Installing dependencies..."
	cd crates/elap-core && cargo build --release
	cd python && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	cd web && npm install
	@echo "✅ Installation complete"

build:
	@echo "Building all projects..."
	cd crates/elap-core && cargo build --release
	cd python && python -m venv venv 2>/dev/null || true
	cd web && npm run build
	@echo "✅ Build complete"

build-rust:
	cd crates/elap-core && cargo build --release

build-python:
	cd python && python -m venv venv 2>/dev/null || true

build-web:
	cd web && npm run build

test:
	@echo "Running tests..."
	@echo "Rust tests..."
	cd crates/elap-core && cargo test
	@echo "Python tests..."
	cd python && pytest --cov=elap_ai 2>/dev/null || true
	@echo "✅ Tests complete"

test-rust:
	cd crates/elap-core && cargo test

test-python:
	cd python && pytest --cov=elap_ai

test-web:
	cd web && npm run test 2>/dev/null || true

lint:
	@echo "Running linters..."
	@echo "Rust format check..."
	cargo fmt -- --check
	@echo "Rust clippy..."
	cargo clippy --all -- -D warnings
	@echo "Python ruff..."
	cd python && ruff check . 2>/dev/null || true
	@echo "Cargo audit..."
	cargo audit 2>/dev/null || true
	@echo "✅ Lint complete"

fmt:
	@echo "Formatting code..."
	cargo fmt --all
	cd python && black . 2>/dev/null || true
	cd web && npm run fmt 2>/dev/null || true
	@echo "✅ Format complete"

clean:
	@echo "Cleaning build artifacts..."
	cargo clean
	rm -rf python/venv
	rm -rf web/node_modules web/dist
	rm -rf .pytest_cache
	@echo "✅ Clean complete"

run:
	@echo "Starting all services..."
	@echo "Make sure you have:"
	@echo "  - Ollama running on localhost:11434"
	@echo "  - Docker/services ready"
	@echo ""
	@echo "In separate terminals, run:"
	@echo "  1. make run-rust"
	@echo "  2. make run-python"
	@echo "  3. make run-web"

run-rust:
	@echo "Starting Rust Core (localhost:3000)..."
	cd crates/elap-desktop && cargo run --release

run-python:
	@echo "Starting Python AI Runtime (localhost:50051)..."
	cd python && . venv/bin/activate && python -m elap_ai.grpc_server

run-web:
	@echo "Starting Web (localhost:5173)..."
	cd web && npm run dev

docker-up:
	docker-compose -f deployment/docker/docker-compose.yml up -d
	@echo "✅ Services up: Rust (3000), Python (50051), Ollama (11434), Postgres (5432), Qdrant (6333)"

docker-down:
	docker-compose -f deployment/docker/docker-compose.yml down

docker-logs:
	docker-compose -f deployment/docker/docker-compose.yml logs -f

bench:
	@echo "Running benchmarks..."
	cd crates/elap-core && cargo bench

version:
	@echo "ELAP Versions:"
	@echo -n "Rust: " && rustc --version
	@echo -n "Python: " && python --version
	@echo -n "Node: " && node --version
	@echo -n "Cargo: " && cargo --version

.DEFAULT_GOAL := help
