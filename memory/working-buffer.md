# Working Buffer (Danger Zone Log)

**Purpose**: Capture EVERY exchange in the danger zone between memory flush and compaction
**Status**: INACTIVE (activate at 60% context)
**Started**: -

---

*This buffer captures raw exchanges during high context usage (>60%).*
*Format:*
```markdown
## [timestamp] Human
[their message]

## [timestamp] Agent (summary)
[1-2 sentence summary of your response + key details]
```

*After compaction, review and extract important context to SESSION-STATE.md.*