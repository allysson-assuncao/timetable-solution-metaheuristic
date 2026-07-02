# State Memory and Artifacts Rules

**DIRECTIVE A (Agent Behavior):**
This directory is your short/medium-term memory. You **MUST ALWAYS** follow this procedural workflow when assigned a complex task:
1. Generate pre-execution plans and save them in `/implementation-plans`.
2. Create actionable checklists and save them in `/tasks`. Update them as you progress.
3. Save code audits, test coverages, and security reviews in `/reviews`.
4. Document post-action reports and summaries in `/walkthroughs`.
You are strictly required to persist your progress and decisions here to ensure continuity.

**DIRECTIVE B (Directory Indexing & Lazy Loading):**
Use the following subdirectories to store specific types of artifacts:

- **`/implementation-plans`**: Contains approved execution plans and architectural proposals.
- **`/tasks`**: Contains active task checklists (TODO lists).
- **`/walkthroughs`**: Contains visual debug evidence, post-task summaries, and E2E logs.
- **`/reviews`**: Contains code audits, security assessments, and test coverage reports.
