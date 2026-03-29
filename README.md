# Neuro-Symbolic Finance Agent

Enterprise finance reconciliation system built around a strict, auditable, multi-step agent pipeline.

## What This System Does

- Ingests Stripe webhook payloads and normalizes them into internal transaction models.
- Runs a 12-step reconciliation pipeline with idempotency, matching, reasoning, guardrails, workflow execution, and audit logging.
- Applies policy and compliance gates before any posting action.
- Executes posting and rollback actions through ERP dispatch adapters.
- Produces decision traces for auditability.

## Current Scope

- Production-style orchestration and error semantics are implemented.
- ERP connectors are currently mocked adapters for NetSuite and SAP shapes.
- Verification is context-driven and validates execution artifacts produced by dispatch.

## Repository Layout

- app/core: context, pipeline orchestration, resilient FSM, exceptions.
- app/data: ingestors, normalizer, event lineage store.
- app/matching: exact, probabilistic, and composite matching layers.
- app/engine: bayesian, symbolic, and temporal reasoning engines.
- app/safety: guardrails, policy matrix, and edge detectors.
- app/workflows: reconciliation and related workflow FSMs.
- app/execution: dispatch and ERP connector adapters.
- app/observability: audit logger and SLA monitor.
- dashboard: streamlit dashboard and impact analytics helpers.
- tests: deterministic and replay testing utilities.

## Prerequisites

- Python 3.11+
- pip
- Optional: Docker and Docker Compose

## Quick Start (Local)

1. Create and activate a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Start the API.

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4. Call the Stripe webhook endpoint.

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/webhooks/stripe" \
	-H "Content-Type: application/json" \
	-d '{
		"id": "evt_demo_001",
		"created": 1711670400,
		"data": {
			"object": {
				"id": "ch_demo_001",
				"amount": 10000,
				"currency": "usd",
				"description": "INV-1001",
				"receipt_email": "ap@acme.com"
			}
		}
	}'
```

Expected response shape:

```json
{
	"status": "success",
	"transaction_id": "ch_demo_001",
	"workflow_state": "ERP_VERIFIED"
}
```

## Testing

Run deterministic validation tests:

```bash
pytest tests/deterministic_cases.py -v
```

Run replay test over synthetic data:

```bash
PYTHONPATH=. python tests/replay_tester.py
```

## Optional Infrastructure Services

Start local supporting services from the compose file:

```bash
docker compose -f infrastructure/docker-compose.yml up -d redis zookeeper kafka postgres
```

## Optional Dashboard

The dashboard uses Streamlit and a lightweight impact calculator.

```bash
pip install streamlit
cd dashboard
streamlit run app.py
```

## Design Rules

- Specific domain exceptions instead of generic exception flow control.
- Keep all transaction state flowing through AgentContext.
- Keep external API calls constrained to the execution layer.
- Keep workflow rollback actions defined for forward actions.
- Maintain append-only audit trail behavior.
