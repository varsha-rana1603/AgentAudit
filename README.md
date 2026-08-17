# AgentAudit
AgentAudit points at a raw Python ML repository and works out what it does — no manual test writing, no instrumentation. It builds a system spec from static analysis, infers the assumptions your code is silently relying on, then generates and executes tests to find where those assumptions break.
