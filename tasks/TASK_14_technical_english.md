# TASK_14 — Codebase Technical English

**Output files**: all backend `.py` files, all frontend `.ts`/`.tsx` files, all `tasks/*.md`, `CLAUDE.md`, `ARCHITECTURE.md`, `TASK_GRAPH.md`, `PROJECT_SPEC.md`
**Branch**: `task/14-technical-english`
**Depends on**: TASK_13 (all code complete, stable baseline)
**Milestone**: M4 pre-i18n

---

## Objective

Translate all **technical and developer-facing content** to English.

The rule is simple:

> **If a developer reads it, it must be in English.**
> **If an end user reads it, it stays in Italian** (until TASK_15 introduces i18n).

This task does NOT change any behavior. No logic is modified.
Every file touched in this task produces a diff of comments/strings only.

---

## Scope

### Translate → English

| Category | Examples |
|---|---|
| Python docstrings | `"""Calcola il PnL..."""` → `"""Calculates the PnL..."""` |
| Python inline comments | `# Aggiorna il prezzo` → `# Update price` |
| TypeScript JSDoc | `/** Pannello portfolio */` → `/** Portfolio panel */` |
| TypeScript inline comments | `// Usa prop, non key` → `// Use prop, not key` |
| Task sheets (`tasks/*.md`) | All content |
| `CLAUDE.md` | All content |
| `ARCHITECTURE.md` | All content |
| `TASK_GRAPH.md` | All content |
| `PROJECT_SPEC.md` | All content |

### Do NOT translate

| Category | Reason |
|---|---|
| UI strings visible to the user | Will be handled by TASK_15 (i18n) |
| FastAPI HTTP error `detail` strings | User-facing — TASK_15 scope |
| Simulation asset names (`SIM-A`, etc.) | Proper nouns, not translatable |
| `README.md` | Intentionally bilingual, left as-is |
| `BACKLOG.md` | Working document, left as-is |
| `LICENSE` | Legal text, left as-is |

---

## Backend — Files to Translate

Translate **docstrings and inline comments** only. Do not change logic, variable names, or string literals.

### `backend/state.py`
- Class `SimulationState` docstring
- Method docstrings: `get_state_snapshot()`, `save_to_remote()`, `load_from_remote()`
- Inline comments

### `backend/orchestrator.py`
- Class `TickOrchestrator` docstring
- Method `run_tick()` docstring and inline comments
- `# DIDACTIC:` comments — translate to English but keep the `# DIDACTIC:` prefix

### `backend/main.py`
- Lifespan docstring
- `_restore_state_from_snapshot()` docstring and inline comments
- Router include comments

### `backend/schemas.py`
- All Pydantic model docstrings (if present)
- Field comments

### `backend/market/asset.py`
- Class `Asset` docstring
- Method docstrings: `step()`, `to_dict()`, `from_dict()`

### `backend/market/simulator.py`
- Class `MarketSimulator` docstring
- Method docstrings

### `backend/traders/retail.py`
- Class `Trade` docstring
- Class `RetailTrader` docstring
- All method docstrings
- `# ASSUMPTION:` comments — translate but keep the prefix

### `backend/traders/professional.py`
- Class `StrategyProfile` docstring
- Class `ProfessionalTrader` docstring
- All method docstrings including FSM phase transition comments

### `backend/traders/copy_engine.py`
- Class `CopyRelation` docstring
- Class `CopyEngine` docstring
- All method docstrings

### `backend/algorithm/scorer.py`
- All docstrings and comments

### `backend/algorithm/recommender.py`
- All docstrings and comments

### `backend/manager/` (router files)
- All docstrings and inline comments

---

## Frontend — Files to Translate

Translate **JSDoc block comments and inline comments** only.
Do not touch `className`, `text-*`, or any string that renders in the UI.

### `frontend/src/App.tsx`
- JSDoc block comment

### `frontend/src/views/retail/*.tsx` (6 files)
- All JSDoc `/** ... */` comments
- All `// ...` inline comments

### `frontend/src/views/manager/*.tsx` (6 files)
- All JSDoc `/** ... */` comments
- All `// ...` inline comments

### `frontend/src/didactic/components/*.tsx` (8 files)
- JSDoc comments
- Inline comments

### `frontend/src/components/*.tsx`
- JSDoc comments
- Inline comments

### `frontend/src/api/*.ts`
- JSDoc comments
- Inline comments

### `frontend/src/types/index.ts`
- Section header comments (`// ── Market ──`, etc.) → translate section labels

---

## Project Documentation — Files to Translate

These are fully translated, including headings, table content, and body text.

| File | Notes |
|---|---|
| `CLAUDE.md` | Keep all code blocks and command examples unchanged |
| `ARCHITECTURE.md` | Translate all prose and table labels |
| `TASK_GRAPH.md` | Translate task names, milestone names, notes; keep IDs unchanged |
| `PROJECT_SPEC.md` | Full translation |
| `tasks/TASK_01_state.md` through `tasks/TASK_13_remote_persistence.md` | Full translation of prose; keep code blocks unchanged |

---

## Conventions

### Python docstrings — style

Use Google-style docstrings (already in use in the codebase):

```python
def method(self, param: int) -> str:
    """Short description in English.

    Longer explanation if needed.

    Args:
        param: Description of the parameter.

    Returns:
        Description of the return value.
    """
```

### TypeScript JSDoc — style

```ts
/**
 * Short description in English.
 *
 * @param prop - Description of the prop.
 */
```

### Special comment prefixes — keep as-is

These prefixes carry semantic meaning and must be preserved in English:

- `# ASSUMPTION:` — documents a design assumption made during implementation
- `# TODO:` — marks intentionally incomplete work
- `# DIDACTIC:` — explains a mechanism for educational purposes

Example: `# DIDACTIC: Il fallimento del salvataggio non blocca la simulazione`
becomes: `# DIDACTIC: Save failure does not block the simulation tick`

---

## Execution Order

To avoid conflicts, process files in this order:

1. `backend/` — one module at a time, commit per module
2. `frontend/src/` — one directory at a time
3. `tasks/*.md` — all in one commit
4. Root `.md` files (`CLAUDE.md`, `ARCHITECTURE.md`, etc.) — one commit

Suggested commit messages:
```
chore(state): translate docstrings and comments to English
chore(market): translate docstrings and comments to English
chore(traders): translate docstrings and comments to English
chore(algorithm): translate docstrings and comments to English
chore(api): translate docstrings and comments to English
chore(orchestrator): translate docstrings and comments to English
chore(frontend): translate JSDoc and inline comments to English
chore(tasks): translate all task sheets to English
chore(docs): translate technical documentation to English
```

---

## What This Task Does NOT Do

- Does not change any function, class, or variable names
- Does not modify any logic or control flow
- Does not translate UI strings (buttons, labels, tooltips, didactic text)
- Does not modify `openapi.yaml` (API descriptions remain in Italian until TASK_15)
- Does not add, remove, or restructure any file

---

## Completion Criteria

- [ ] All Python docstrings in `backend/` are in English
- [ ] All Python inline comments in `backend/` are in English
- [ ] All TypeScript JSDoc and inline comments in `frontend/src/` are in English
- [ ] `CLAUDE.md` fully translated (code blocks unchanged)
- [ ] `ARCHITECTURE.md` fully translated
- [ ] `TASK_GRAPH.md` fully translated (IDs unchanged)
- [ ] `PROJECT_SPEC.md` fully translated
- [ ] All `tasks/TASK_*.md` files fully translated (code blocks unchanged)
- [ ] No UI string has been changed
- [ ] No logic has been modified
- [ ] All tests (if present) still pass
- [ ] Build compiles without new errors or warnings
