# Create Stories Batch Workflow

Batch story generation creating multiple stories at once from the backlog. Run by Scrum Master (SM) agent to efficiently prepare multiple stories for development.

## Table of Contents

- [Usage](#usage)
- [Key Features](#key-features)
- [Inputs & Outputs](#inputs--outputs)
- [Workflow Behavior](#workflow-behavior)
- [Integration](#integration)

## Usage

```bash
# SM initiates batch story creation
bmad sm *create-stories-batch
```

**When to run:**

- Sprint has capacity for multiple stories
- Multiple stories are ready in backlog
- Want to prepare stories in bulk for upcoming sprint
- Epic context is complete and ready for story development

## Key Features

### Batch Processing

- **Processes multiple backlog stories** in a single execution
- **Preserves story order** from sprint-status.yaml
- **Configurable batch size** - create all backlog or specify count
- **Progress tracking** with per-story status updates

### Smart Story Discovery

- Auto-discovers all backlog stories from sprint-status.yaml
- Respects story ordering (sequential within epic)
- Validates story enumeration in epics.md
- Handles existing stories gracefully (skip/overwrite options)

### Reuses Existing Workflow

- Invokes standard `create-story` workflow for each story
- Maintains all validation and quality checks
- Preserves story template and structure consistency
- Benefits from same document discovery and grounding

### Error Handling

- Continues processing even if individual story fails
- Tracks created, skipped, and failed stories separately
- Provides detailed summary at completion
- Non-destructive (skips existing stories by default)

## Inputs & Outputs

### Required Files

| File                     | Purpose                       | Priority |
| ------------------------ | ----------------------------- | -------- |
| sprint-status.yaml       | Story backlog tracking        | Critical |
| epics.md                 | Story enumeration (MANDATORY) | Critical |
| tech-spec-epic-{N}-*.md  | Epic technical spec           | High     |
| PRD.md                   | Product requirements          | Medium   |
| Architecture docs         | Technical constraints         | Low      |

### Variables

- `max_stories`: Optional limit on number of stories to create (empty = all backlog)
- `non_interactive`: Batch mode flag (default: true)

### Output

**Multiple Story Documents:** `{story_dir}/{story_key}.md` for each created story

Each story includes:
- User story statement (role, action, benefit)
- Acceptance criteria from tech spec/epics
- Tasks mapped to ACs
- Dev notes with architecture context
- Learnings from previous stories

**Batch Summary:**
- Total processed count
- Created stories list
- Skipped stories list
- Failed stories list (if any)

## Workflow Behavior

### Story Selection

1. Loads sprint-status.yaml completely
2. Finds all stories with status "backlog"
3. Filters to story keys (excludes epic keys and retrospectives)
4. Preserves file order for sequential processing

### Batch Size Determination

- If `max_stories` specified: Create that many (up to backlog count)
- If not specified and non-interactive: Create all backlog stories
- If not specified and interactive: Prompt user for count

### Per-Story Creation

1. Extract epic/story numbers from story key
2. Check if story file already exists
3. Invoke create-story workflow with extracted parameters
4. Track success/failure status
5. Update sprint-status.yaml (handled by create-story workflow)

### Completion Summary

Provides comprehensive report:
- Statistics (created/skipped/failed counts)
- Lists of story keys in each category
- File paths for created stories
- Recommendations for next steps

## Integration

### With Sprint Planning

Run `sprint-planning` first to ensure sprint-status.yaml is current with backlog stories.

### With Story Context

After batch creation, run `story-context` for each created story to generate technical context XML and mark as ready-for-dev.

### With Validation

Each story goes through standard create-story validation during creation. Optional independent validation via `validate-create-story` workflow.

## Example Workflow

```yaml
# Scenario: Epic 1 has 6 backlog stories ready
# Current status in sprint-status.yaml:
#   1-4: ready-for-dev
#   1-5: ready-for-dev
#   1-6: backlog  ← First in batch
#   1-7: backlog  ← Second in batch
#   1-8: backlog  ← Third in batch
#   ... (epic 2 stories)

# Run: *create-stories-batch
# Input: max_stories = 3 (or "all" for all epic 1 backlog)
# Result: Creates stories 1-6, 1-7, 1-8
# Status updates: All three marked as "drafted"
```

## Notes

- **Context Management**: Batch creation generates significant context. Consider clearing context between batches or before running story-context workflow.
- **Story Dependencies**: Ensure prerequisites are met (previous stories done/ready) before batch creation.
- **Epic Context**: Stories should only be created for epics that have tech context (status: contexted).
- **Performance**: Large batches may take time. Use max_stories to limit if needed.

