#!/usr/bin/env bash

set -e

echo "🚀 Creating ProofRelay project structure..."

# =========================

# SERVICES

# =========================

services=(
"api"
"indexer"
"confirmation_worker"
"webhook_dispatcher"
"retry_worker"
)

for service in "${services[@]}"; do
mkdir -p services/$service/app
touch services/$service/app/main.py
touch services/$service/Dockerfile
touch services/$service/requirements.txt
done

# API specific

mkdir -p services/api/app/routes
mkdir -p services/api/app/schemas
mkdir -p services/api/app/service

touch services/api/app/routes/payments.py
touch services/api/app/schemas/payment.py
touch services/api/app/service/payment_service.py
touch services/api/app/dependencies.py
touch services/api/app/config.py

# INDEXER

touch services/indexer/app/listener.py
touch services/indexer/app/scanner.py
touch services/indexer/app/matcher.py
touch services/indexer/app/rpc.py

# CONFIRMATION WORKER

touch services/confirmation_worker/app/worker.py
touch services/confirmation_worker/app/confirmations.py
touch services/confirmation_worker/app/repository.py

# WEBHOOK DISPATCHER

touch services/webhook_dispatcher/app/dispatcher.py
touch services/webhook_dispatcher/app/signer.py
touch services/webhook_dispatcher/app/client.py
touch services/webhook_dispatcher/app/idempotency.py

# RETRY WORKER

touch services/retry_worker/app/scheduler.py
touch services/retry_worker/app/retry_logic.py

# =========================

# CORE

# =========================

mkdir -p core/config
mkdir -p core/db/models
mkdir -p core/db/migrations
mkdir -p core/redis
mkdir -p core/blockchain
mkdir -p core/events
mkdir -p core/security
mkdir -p core/utils

touch core/config/settings.py

touch core/db/base.py
touch core/db/session.py
touch core/db/models/payment.py

touch core/redis/client.py
touch core/redis/queues.py
touch core/redis/retry_queue.py

touch core/blockchain/types.py

touch core/events/payment.py
touch core/events/base.py

touch core/security/hmac.py

touch core/utils/logger.py
touch core/utils/time.py

# =========================

# INFRA

# =========================

mkdir -p infra/scripts

touch infra/docker-compose.yml
touch infra/.env

touch infra/scripts/wait_for_db.sh
touch infra/scripts/wait_for_redis.sh

# =========================

# TESTS

# =========================

mkdir -p tests/api
mkdir -p tests/indexer
mkdir -p tests/workers
mkdir -p tests/integration

# =========================

# ROOT FILES

# =========================

touch README.md
touch pyproject.toml
touch Makefile

# =========================

# REQUIREMENTS

# =========================

mkdir -p requirements

cat <<EOF > requirements/base.txt
pydantic==2.7.1
python-dotenv==1.0.1

sqlalchemy==2.0.30
asyncpg==0.29.0

redis==5.0.4

structlog==24.1.0
EOF

cat <<EOF > requirements/api.txt
-r base.txt

fastapi==0.111.0
uvicorn[standard]==0.30.0

httpx==0.27.0
EOF

cat <<EOF > requirements/indexer.txt
-r base.txt

web3==6.17.0
websockets==12.0
EOF

cat <<EOF > requirements/workers.txt
-r base.txt

httpx==0.27.0
web3==6.17.0
EOF

echo "✅ Structure created successfully!"
echo "👉 Next step: start implementing the database schema"
