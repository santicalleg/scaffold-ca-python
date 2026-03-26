# Quickstart: Python Clean Architecture Scaffold

**Branch**: `002-scaffold-clean-arch` | **Date**: 2026-03-25

This document describes how to use the scaffold tool end-to-end, from installation to a running project with components.

---

## Installation

```bash
pip install scaffold-ca-python
# or with uv:
uv add scaffold-ca-python
```

Verify:
```bash
scaffold version
# Scaffold version: 1.0.0
```

---

## Create a New Project

```bash
scaffold new --name order_service
# or with a custom package namespace:
scaffold new --name order_service --package org.example.orders
# or async mode:
scaffold new --name order_service --async
```

Generated structure:
```
order_service/
├── .scaffold-ca.json          ← project metadata marker
├── pyproject.toml             ← project config with pytest + dependencies
├── README.md
├── order_service/
│   ├── __init__.py
│   ├── domain/
│   │   ├── model/
│   │   │   ├── __init__.py
│   │   │   └── gateways/
│   │   │       └── __init__.py
│   │   └── usecase/
│   │       └── __init__.py
│   ├── infrastructure/
│   │   ├── driven_adapters/
│   │   │   └── __init__.py
│   │   ├── entry_points/
│   │   │   └── __init__.py
│   │   └── helpers/
│   │       └── __init__.py
│   └── app/
│       ├── __init__.py
│       └── main.py            ← DI wiring + application entry point
├── tests/
│   ├── __init__.py
│   ├── test_architecture.py   ← ArchitectureTest (enforces layer rules)
│   └── unit/
│       └── __init__.py
└── deployment/
    ├── Dockerfile
    └── .github/
        └── workflows/
            └── ci.yml
```

Run the default tests immediately:
```bash
cd order_service
pytest
# 2 passed in 0.12s
```

---

## Add a Domain Model

```bash
cd order_service
scaffold generate model --name Order
```

Creates:
- `order_service/domain/model/order.py` — `Order` dataclass
- `order_service/domain/model/gateways/order_gateway.py` — `OrderGateway` abstract base
- `tests/unit/model/test_order.py`

---

## Add a Use Case

```bash
scaffold generate use-case --name ProcessOrder
```

Creates:
- `order_service/domain/usecase/process_order_use_case.py`
- `tests/unit/usecase/test_process_order_use_case.py`

---

## Add a Driven Adapter

```bash
# SQLAlchemy/asyncpg repository
scaffold generate driven-adapter --type repository --name OrderRepository

# HTTP client
scaffold generate driven-adapter --type rest-client --name PaymentClient --url https://payments.example.com

# Kafka producer
scaffold generate driven-adapter --type kafka-sender --name NotificationSender
```

---

## Add an Entry Point

```bash
# REST API
scaffold generate entry-point --type rest-api --name OrderApi

# Kafka consumer
scaffold generate entry-point --type kafka-consumer --name OrderConsumer

# CLI command
scaffold generate entry-point --type cli --name ProcessOrderCommand
```

---

## Add a Helper

```bash
scaffold generate helper --name JwtHelper
```

---

## Validate Architecture

```bash
scaffold validate
# ✅ scaffold validate — no violations found

# After introducing a violation (e.g. importing infrastructure in domain/model):
scaffold validate
# ❌ Violation: order_service/domain/model/order.py imports from infrastructure/driven_adapters/
#    Rule: domain/model MUST NOT import from any other layer
# exit code: 1
```

---

## List Available Component Types

```bash
scaffold list
scaffold list --type driven-adapter
scaffold list --type entry-point
```

---

## Delete a Module

```bash
scaffold delete --module order_repository
# ✅ Deleted: infrastructure/driven_adapters/order_repository/ (3 files)
```

---

## Update Boilerplate

```bash
# Commit your work first, then:
scaffold update
# or skip the git check:
scaffold update --skip-git-check
# or preview without writing:
scaffold update --dry-run
```

---

## Verbosity Flags

```bash
scaffold generate use-case --name ProcessOrder --verbose
# [DEBUG] Template: templates/use_case/use_case.py.jinja2
# [DEBUG] Output: order_service/domain/usecase/process_order_use_case.py
# [DEBUG] Normalized: ProcessOrder → process_order_use_case (snake), ProcessOrderUseCase (class)

scaffold generate use-case --name ProcessOrder --quiet
# (no output on success)
```
