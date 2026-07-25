# AutoShip Agent — Codex Instructions

## Architecture
- Backend: FastAPI (Python)
- Agents: backend/agents/
- Goal: plan → detect → fix → review

## Agent Workflow Requirement
For every task, Codex must:
1. State a Plan.
2. Implement code.
3. Run a test.
4. Provide a Self-Review of the work.
