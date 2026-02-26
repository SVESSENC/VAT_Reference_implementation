# Severity Guide

Use this rubric when ranking findings.

- Critical: Security breach, data loss/corruption, auth bypass, or production outage risk with realistic trigger.
- High: Major functional break, unsafe migration, incorrect financial/business result, or severe reliability issue.
- Medium: Real bug with bounded impact, edge-case failure, or missing safeguards likely to cause incidents.
- Low: Minor defect, maintainability risk with clear downside, or non-critical missing tests.

Use confidence labels in review text when needed:

- High confidence: Clear code path proves the issue.
- Medium confidence: Strong signal, but runtime context or config can alter outcome.
- Low confidence: Plausible risk that needs confirmation.

Escalate severity only when impact and trigger conditions are both concrete.
