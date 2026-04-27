---
description: "Apply the standard board kit (~/.claude/commands/_board-kit.json) to a GitHub Project v2: customize Status options, add Priority + Target fields."
---

You are running **`/board-setup`**.

**Args:** $ARGUMENTS  → project number under @me (e.g. `1`) OR full project URL `https://github.com/users/<owner>/projects/<n>`.

## What to do

1. Resolve project number + owner from args.
2. Get project node ID:
   ```bash
   PROJECT_ID=$(gh project view <num> --owner <owner> --format json --jq .id)
   ```
3. List current fields:
   ```bash
   gh project field-list <num> --owner <owner> --format json
   ```
4. **Status field** — already exists by default in every Project v2 with options Todo/In Progress/Done. Replace its options with the board-kit's `status_options`. This requires GraphQL (the `gh project field-create` CLI doesn't support editing existing single-select options reliably):
   ```bash
   STATUS_FIELD_ID=$(gh project field-list <num> --owner <owner> --format json --jq '.fields[] | select(.name=="Status") | .id')
   gh api graphql -f query='
     mutation($field: ID!, $opts: [ProjectV2SingleSelectFieldOptionInput!]!) {
       updateProjectV2Field(input: {fieldId: $field, singleSelectOptions: $opts}) {
         projectV2Field { ... on ProjectV2SingleSelectField { id name options { id name } } }
       }
     }' -F field="$STATUS_FIELD_ID" -f opts='[{"name":"Backlog","color":"GRAY","description":"Filed, not yet scheduled"},{"name":"Up Next","color":"PURPLE","description":"Top of the queue"},{"name":"In Progress","color":"BLUE","description":"Active"},{"name":"In Review","color":"YELLOW","description":"PR open"},{"name":"Done","color":"GREEN","description":"Shipped"}]'
   ```
   If `updateProjectV2Field` is rejected by the schema, fall back to: delete + recreate the Status field. Note that deleting Status loses item placements; back them up first via `gh project item-list` and re-set after.
5. **Priority field** — single-select, options from `priority_options`. Create if absent:
   ```bash
   gh project field-create <num> --owner <owner> --name "Priority" --data-type SINGLE_SELECT --single-select-options "P0,P1,P2,P3"
   ```
6. **Target field** — text, free-form. Create if absent:
   ```bash
   gh project field-create <num> --owner <owner> --name "Target" --data-type TEXT
   ```
7. Print: `Board ready: <project URL>` and a list of fields with options.

If a particular gh command is too new and not available, fall back to the GraphQL `gh api graphql` mutation equivalent. The exact mutation names you may need:
- `createProjectV2Field`
- `updateProjectV2Field`
- `deleteProjectV2Field`

Report what worked and what didn't — don't pretend everything succeeded.
