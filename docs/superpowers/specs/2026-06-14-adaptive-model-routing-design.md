# Adaptive Model Routing Design

## Goal

Use a lower-cost Codex subagent for bounded implementation work while the user's selected main model retains planning, risk decisions, review and final validation. Routing must be automatic after ContextGuard initialization and must preserve RAW-equivalent behavior.

## Supported Mechanism

Codex project custom agents support independent `model` and `model_reasoning_effort` settings. ContextGuard will install `.codex/agents/contextguard-worker.toml` with `gpt-5.4-mini` and medium reasoning. Managed project guidance and prompt context will authorize the main agent to spawn exactly one worker when the task becomes well scoped.

Hooks cannot change the model of an existing thread or directly spawn an agent. ContextGuard therefore coordinates supported Codex subagent behavior rather than pretending to rewrite the active model. `SubagentStart` and `SubagentStop` hooks provide routing telemetry and bounded worker guidance.

## Routing Policy

The main model always performs initial orientation and planning. A worker is eligible only when the implementation package has explicit files or responsibility, objective acceptance criteria and no unresolved architectural decision.

Do not delegate security, authentication, authorization, migrations, schemas, destructive operations, concurrency, payments, secrets, production incidents or data-integrity decisions. Do not delegate trivial work where handoff overhead is likely to exceed savings. Use one sequential worker only; no recursive delegation and no parallel writers.

## Quality Gate

The worker edits and runs focused checks. The main model reviews the diff, checks requirements and runs final validation. A failed, incomplete or ambiguous worker result triggers local continuation by the main model. ContextGuard never treats worker completion as final acceptance.

## Measurement

Acceptance requires proof that the parent used GPT-5.5, the worker used GPT-5.4-mini, the routed and RAW implementations pass identical hidden tests, and routed estimated model cost or included-limit pressure is lower. Token count, tool calls, latency and handoff overhead are reported separately.

## Limitations

Model routing is agent-directed because current command hooks cannot invoke subagents. Codex may decline delegation when the task is unsafe or unsuitable. Subscription quota accounting remains proprietary; model-specific included-limit guidance is measured using documented relative consumption where available, not presented as an entitlement guarantee.
