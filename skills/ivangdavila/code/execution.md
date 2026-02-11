# Execution Reference

Consult when running multi-step implementations.

## Core Rule
Don't stop between steps unless blocked. After step N passes → start N+1 immediately.

## When to Stop
- Missing credential or permission
- User decision needed (A vs B, both valid)
- Request complete

Everything else: keep going.

## Parallel Steps
Independent steps can run simultaneously. Track with:
```
- ✅ Step 1
- 🔄 Step 2 ← current
- ⬜ Step 3
```

## Error Recovery
1. Identify root cause
2. Fix
3. Re-test
4. Proceed when test passes

Don't ask permission to retry.

## Anti-Patterns
- "Done, let me know if you want me to continue"
- Reporting each step completion
- Stopping on first error without attempting fix
