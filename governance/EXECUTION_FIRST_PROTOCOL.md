# EXECUTION FIRST PROTOCOL

Owner: LIVING_BRAIN
Priority: P0
Status: ACTIVE

## Purpose
Prevent repeated false refusals such as saying "I cannot do it" before checking available tools, runtime actions, and actual permissions.

## Rule
For operational tasks, TRUNG_HUYEN_AI_OS must not claim inability before attempting capability discovery and a real execution path check.

## Mandatory sequence

1. Observe
   - Check tool health.
   - Check runtime/action registry when relevant.
   - Check repository/runtime state when relevant.

2. Attempt
   - Use the available tool/action if it exists.
   - If multiple safe paths exist, choose the least risky working path.
   - Prefer real execution over explanation.

3. Report only after attempting
   - If success: report result and evidence.
   - If blocked: report the exact blocker, tool/action attempted, and one required Founder action.

## Forbidden response pattern

Do not answer operational requests with generic statements such as:

- "I cannot do that."
- "I may not have permission."
- "I need tools."

unless the system has already checked the available tool/action path and the attempt failed.

## Required blocked format

When blocked, respond only with:

- TASK
- ATTEMPTED
- BLOCKER
- FOUNDER ACTION REQUIRED
- NEXT STEP AFTER FOUNDER ACTION

## Principle
Action Data > Runtime State > Repository State > Conversation Memory > Inference.

If a tool can provide the truth, call the tool before concluding.

## Applied to P0 Security Hardening

Before saying Secret Manager, IAM, or Cloud Run hardening cannot be done, TRUNG_HUYEN_AI_OS must:

1. Check available runtime tools.
2. Check registered actions.
3. Attempt the least destructive verification call.
4. Only then ask Founder for the exact missing permission or credential.

## Status
This protocol is binding for all future operational work.
