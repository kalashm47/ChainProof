# ChainProof

## Description

**ChainProof** is a blockchain-based payment proof verification system that enables businesses and individuals to monitor and validate cryptocurrency payments off-chain. The system provides a robust webhook infrastructure for real-time payment confirmation, eliminating the need for direct blockchain interaction in the main application flow.

## Overview

ChainProof acts as a middleware layer between blockchain networks and client systems, offering a reliable, scalable, and fault-tolerant payment verification service. It listens to blockchain transactions, matches them against registered payment addresses, and dispatches webhook notifications to client endpoints with cryptographic proof of payment.

## Key Features

- **Off-chain Payment Monitoring**: Track blockchain transactions without requiring clients to run blockchain nodes
- **Webhook Dispatching**: Real-time HTTP callbacks with HMAC-SHA256 signed payloads
- **Configurable Confirmation Blocks**: Wait for N block confirmations before dispatching notifications
- **Idempotent Processing**: Prevent duplicate webhook deliveries with idempotency keys
- **Automatic Retry Mechanism**: Exponential backoff retry strategy for failed webhooks (max 5 attempts, 300s cap)
- **Multi-currency Support**: Handle various cryptocurrencies (ETH, BTC, etc.) through extensible architecture
- **Redis-based Queue System**: Asynchronous processing with Redis for high throughput and reliability

## Architecture

The system is composed of six microservices:

| Service | Responsibility |
|---------|---------------|
| **API** | REST endpoint for payment registration and validation |
| **Indexer** | Scans blockchain blocks and extracts transactions |
| **Confirmation Worker** | Waits for N confirmations before marking payments as valid |
| **Webhook Dispatcher** | Sends signed notifications to client endpoints |
| **Retry Worker** | Manages failed webhook deliveries with exponential backoff |
| **Blockchain Listener** | Monitors new blocks via WebSocket/RPC connection |

## Technology Stack

- **Language**: Python 3.12+
- **Framework**: FastAPI (REST API)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Message Queue**: Redis (BRPOP/LPUSH queues)
- **Blockchain**: Web3.py for Ethereum compatibility
- **Validation**: Pydantic v2 with custom field validators
- **Testing**: pytest with comprehensive unit and integration tests

## Core Flow

1. Client registers a payment to watch via `POST /watch_payment`
2. API validates input (address, amount, currency, webhook URL)
3. Payment record is stored in database with `pending` status
4. Job is pushed to Redis `payment_detection` queue
5. Indexer scans blockchain blocks for matching addresses
6. Confirmation worker waits for required block confirmations
7. Webhook dispatcher sends signed payload to client endpoint
8. Failed deliveries trigger retry with exponential backoff

## Webhook Payload Structure

```json
{
  "event": "payment.confirmed",
  "transaction_hash": "0x...",
  "address": "0x...",
  "amount_wei": "50000000000000000",
  "confirmations": 12,
  "timestamp": "2025-01-01T10:00:00Z",
  "signature": "hmac-sha256..."
}
