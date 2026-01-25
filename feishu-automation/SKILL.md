---
name: feishu-automation
description: This skill should be used when you need to automate Feishu workflows including bulk document operations, scheduled reports, document templates, data synchronization between bases, and smart notifications based on conditions.
---

# Feishu Automation Engine

This skill provides powerful automation capabilities for Feishu (Lark), enabling bulk operations, workflow automation, scheduled tasks, and intelligent data processing across documents, bases, and wikis.

## When to Use This Skill

Use this skill when the user needs to:
- Perform bulk operations across multiple documents or base records
- Generate automated reports from Feishu Bases on a schedule
- Create documents from templates with dynamic data
- Synchronize data between multiple Feishu Bases
- Set up smart notifications based on data conditions
- Automate repetitive Feishu workflows
- Process large volumes of Feishu data
- Maintain data consistency across resources

## Prerequisites

**Required**: Feishu app with appropriate permissions configured (see `../feishu-mcp/FEISHU_APP_SETUP.md`)

**Credentials**:
```
FEISHU_APP_ID: cli_a85833b3fc39900e
FEISHU_APP_SECRET: fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd
```

## Core Automation Capabilities

### 1. Bulk Document Operations

#### Update Multiple Documents
Update content across many documents simultaneously:

```bash
# Get token
TOKEN=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"cli_a85833b3fc39900e","app_secret":"fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd"}' \
  | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

# Search for documents to update
DOCS=$(curl -s -X POST 'https://open.feishu.cn/open-apis/drive/v1/files/search' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"search_key":"Q4 2025","page_size":50}')

# Extract document tokens and update each
echo "$DOCS" | jq -r '.data.items[].token' | while read DOC_TOKEN; do
  # Get document blocks
  BLOCKS=$(curl -s -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/$DOC_TOKEN/blocks" \
    -H "Authorization: Bearer $TOKEN")

  # Find text blocks and update
  BLOCK_ID=$(echo "$BLOCKS" | jq -r '.data.items[0].block_id')

  curl -s -X PATCH "https://open.feishu.cn/open-apis/docx/v1/documents/$DOC_TOKEN/blocks/$BLOCK_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d '{"update_text_elements":{"elements":[{"text_run":{"content":"UPDATED: Q4 2026"}}]}}'

  echo "Updated document: $DOC_TOKEN"
done
```

#### Bulk Tag/Organize Documents
Automatically categorize and tag documents:

```bash
# Search for uncategorized documents
DOCS=$(curl -s -X POST 'https://open.feishu.cn/open-apis/drive/v1/files/search' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"search_key":"project","page_size":50}')

# Add metadata/tags to each document
echo "$DOCS" | jq -r '.data.items[]' | while read -r item; do
  DOC_TOKEN=$(echo "$item" | jq -r '.token')
  DOC_TITLE=$(echo "$item" | jq -r '.name')

  # Classify based on title
  if [[ "$DOC_TITLE" == *"Meeting"* ]]; then
    CATEGORY="meetings"
  elif [[ "$DOC_TITLE" == *"Report"* ]]; then
    CATEGORY="reports"
  else
    CATEGORY="general"
  fi

  # Add category block to document
  curl -s -X POST "https://open.feishu.cn/open-apis/docx/v1/documents/$DOC_TOKEN/blocks" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d "{\"block\":{\"block_type\":1,\"text\":{\"elements\":[{\"text_run\":{\"content\":\"Category: $CATEGORY\"}}]}}}"

  echo "Categorized: $DOC_TITLE -> $CATEGORY"
done
```

### 2. Scheduled Report Generation

#### Weekly Status Report from Base
Generate automated reports from Feishu Base data:

```bash
#!/bin/bash
# Save as: generate_weekly_report.sh

TOKEN=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"cli_a85833b3fc39900e","app_secret":"fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd"}' \
  | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

APP_TOKEN="your_base_app_token"
TABLE_ID="your_table_id"

# Get last 7 days of data
START_DATE=$(date -d '7 days ago' +%Y-%m-%d)

# Query base records
RECORDS=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$APP_TOKEN/tables/$TABLE_ID/records/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"filter\": {
      \"conjunction\": \"and\",
      \"conditions\": [{
        \"field_name\": \"Date\",
        \"operator\": \"isGreater\",
        \"value\": [\"$START_DATE\"]
      }]
    },
    \"page_size\": 500
  }")

# Generate report content
TOTAL=$(echo "$RECORDS" | jq '.data.total')
COMPLETED=$(echo "$RECORDS" | jq '[.data.items[] | select(.fields.Status == "Done")] | length')
IN_PROGRESS=$(echo "$RECORDS" | jq '[.data.items[] | select(.fields.Status == "In Progress")] | length')

REPORT="# Weekly Status Report - $(date +%Y-%m-%d)

## Summary
- Total Tasks: $TOTAL
- Completed: $COMPLETED
- In Progress: $IN_PROGRESS
- Completion Rate: $(( COMPLETED * 100 / TOTAL ))%

## Details
$(echo "$RECORDS" | jq -r '.data.items[] | "- \(.fields.Name): \(.fields.Status)"')

Generated automatically by Feishu Automation Engine"

# Create new document with report
CREATE_RESP=$(curl -s -X POST "https://open.feishu.cn/open-apis/docx/v1/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"title\": \"Weekly Report - $(date +%Y-%m-%d)\",
    \"folder_token\": \"your_folder_token\"
  }")

DOC_TOKEN=$(echo "$CREATE_RESP" | jq -r '.data.document.document_id')

# Add content to document
curl -s -X POST "https://open.feishu.cn/open-apis/docx/v1/documents/$DOC_TOKEN/blocks" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"block\":{\"block_type\":2,\"text\":{\"elements\":[{\"text_run\":{\"content\":\"$REPORT\"}}]}}}"

echo "Report generated: https://your-domain.feishu.cn/docx/$DOC_TOKEN"
```

Schedule with cron:
```bash
# Run every Monday at 9 AM
0 9 * * 1 /path/to/generate_weekly_report.sh
```

### 3. Document Templates

#### Create Document from Template
Generate documents with dynamic content:

```bash
# Template function
create_from_template() {
  local TEMPLATE_TOKEN=$1
  local TITLE=$2
  local VARIABLES=$3  # JSON object with variable replacements

  # Read template
  TEMPLATE=$(curl -s -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/$TEMPLATE_TOKEN/blocks" \
    -H "Authorization: Bearer $TOKEN")

  # Create new document
  NEW_DOC=$(curl -s -X POST "https://open.feishu.cn/open-apis/docx/v1/documents" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d "{\"title\":\"$TITLE\"}")

  NEW_DOC_TOKEN=$(echo "$NEW_DOC" | jq -r '.data.document.document_id')

  # Copy template blocks with variable replacement
  echo "$TEMPLATE" | jq -c '.data.items[]' | while read -r block; do
    BLOCK_CONTENT=$(echo "$block" | jq -r '.text.elements[0].text_run.content // empty')

    # Replace variables
    for key in $(echo "$VARIABLES" | jq -r 'keys[]'); do
      value=$(echo "$VARIABLES" | jq -r ".$key")
      BLOCK_CONTENT=$(echo "$BLOCK_CONTENT" | sed "s/{{$key}}/$value/g")
    done

    # Add block to new document
    curl -s -X POST "https://open.feishu.cn/open-apis/docx/v1/documents/$NEW_DOC_TOKEN/blocks" \
      -H "Authorization: Bearer $TOKEN" \
      -H 'Content-Type: application/json' \
      -d "{\"block\":{\"block_type\":2,\"text\":{\"elements\":[{\"text_run\":{\"content\":\"$BLOCK_CONTENT\"}}]}}}"
  done

  echo "$NEW_DOC_TOKEN"
}

# Usage
VARIABLES='{"client_name":"Acme Corp","project":"Website Redesign","start_date":"2026-02-01","budget":"$50,000"}'
NEW_DOC=$(create_from_template "template_token_here" "Acme Corp - Project Proposal" "$VARIABLES")
echo "Created document: $NEW_DOC"
```

#### Common Templates

**Meeting Notes Template**:
```markdown
# Meeting Notes - {{date}}

## Attendees
{{attendees}}

## Agenda
{{agenda_items}}

## Discussion Points
{{discussion}}

## Action Items
{{action_items}}

## Next Steps
{{next_steps}}
```

**Project Proposal Template**:
```markdown
# Project Proposal: {{project_name}}

## Client
{{client_name}}

## Objective
{{objective}}

## Scope
{{scope}}

## Timeline
Start: {{start_date}}
End: {{end_date}}

## Budget
{{budget}}

## Team
{{team_members}}

## Deliverables
{{deliverables}}
```

### 4. Data Synchronization Between Bases

#### Sync Records Between Tables
Keep multiple bases in sync automatically:

```bash
#!/bin/bash
# sync_bases.sh - Sync data from source to target base

sync_bases() {
  local SOURCE_APP=$1
  local SOURCE_TABLE=$2
  local TARGET_APP=$3
  local TARGET_TABLE=$4
  local SYNC_FIELD=$5  # Field to match records on (e.g., "ID" or "Email")

  # Get all records from source
  SOURCE_RECORDS=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$SOURCE_APP/tables/$SOURCE_TABLE/records/search" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d '{"page_size":500}')

  # Get all records from target
  TARGET_RECORDS=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$TARGET_APP/tables/$TARGET_TABLE/records/search" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d '{"page_size":500}')

  # For each source record
  echo "$SOURCE_RECORDS" | jq -c '.data.items[]' | while read -r src_record; do
    SYNC_VALUE=$(echo "$src_record" | jq -r ".fields.$SYNC_FIELD")

    # Check if exists in target
    TARGET_EXISTS=$(echo "$TARGET_RECORDS" | jq -r ".data.items[] | select(.fields.$SYNC_FIELD == \"$SYNC_VALUE\") | .record_id")

    if [ -n "$TARGET_EXISTS" ]; then
      # Update existing record
      curl -s -X PUT "https://open.feishu.cn/open-apis/bitable/v1/apps/$TARGET_APP/tables/$TARGET_TABLE/records/$TARGET_EXISTS" \
        -H "Authorization: Bearer $TOKEN" \
        -H 'Content-Type: application/json' \
        -d "{\"fields\":$(echo "$src_record" | jq '.fields')}"
      echo "Updated: $SYNC_VALUE"
    else
      # Create new record
      curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$TARGET_APP/tables/$TARGET_TABLE/records" \
        -H "Authorization: Bearer $TOKEN" \
        -H 'Content-Type: application/json' \
        -d "{\"fields\":$(echo "$src_record" | jq '.fields')}"
      echo "Created: $SYNC_VALUE"
    fi
  done
}

# Usage: Sync customer data from CRM to Invoice base
sync_bases "crm_app_token" "customers_table" "invoice_app_token" "clients_table" "Email"
```

#### One-Way Sync with Transformation
Transform data while syncing:

```bash
sync_with_transform() {
  SOURCE_RECORDS=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$SOURCE_APP/tables/$SOURCE_TABLE/records/search" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d '{"page_size":500}')

  echo "$SOURCE_RECORDS" | jq -c '.data.items[]' | while read -r record; do
    # Transform fields
    TRANSFORMED=$(echo "$record" | jq '{
      fields: {
        Name: .fields.CustomerName,
        Email: .fields.Email,
        Status: (if .fields.IsActive then "Active" else "Inactive" end),
        Revenue: (.fields.MonthlyRevenue * 12),
        LastUpdated: now | todate
      }
    }')

    # Insert into target
    curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$TARGET_APP/tables/$TARGET_TABLE/records" \
      -H "Authorization: Bearer $TOKEN" \
      -H 'Content-Type: application/json' \
      -d "$TRANSFORMED"
  done
}
```

### 5. Smart Notifications

#### Condition-Based Alerts
Monitor data and send alerts when conditions are met:

```bash
#!/bin/bash
# monitor_and_alert.sh

check_conditions_and_alert() {
  local APP_TOKEN=$1
  local TABLE_ID=$2
  local WEBHOOK_URL=$3  # Feishu bot webhook

  # Query records with high-priority conditions
  ALERTS=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$APP_TOKEN/tables/$TABLE_ID/records/search" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d '{
      "filter": {
        "conjunction": "or",
        "conditions": [
          {
            "field_name": "Budget",
            "operator": "isGreater",
            "value": ["80000"]
          },
          {
            "field_name": "Status",
            "operator": "is",
            "value": ["Overdue"]
          },
          {
            "field_name": "Priority",
            "operator": "is",
            "value": ["Critical"]
          }
        ]
      }
    }')

  ALERT_COUNT=$(echo "$ALERTS" | jq '.data.total')

  if [ "$ALERT_COUNT" -gt 0 ]; then
    # Build alert message
    MESSAGE="🚨 Alert: $ALERT_COUNT items need attention\n\n"
    MESSAGE+=$(echo "$ALERTS" | jq -r '.data.items[] | "• \(.fields.Name): \(.fields.Status) (Budget: \(.fields.Budget))"')

    # Send to Feishu bot
    curl -X POST "$WEBHOOK_URL" \
      -H 'Content-Type: application/json' \
      -d "{
        \"msg_type\": \"text\",
        \"content\": {
          \"text\": \"$MESSAGE\"
        }
      }"

    echo "Alert sent: $ALERT_COUNT items"
  fi
}

# Run every hour
check_conditions_and_alert "app_token" "table_id" "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook"
```

#### Budget Threshold Monitoring
Alert when projects exceed budget thresholds:

```bash
monitor_budgets() {
  PROJECTS=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$APP_TOKEN/tables/$TABLE_ID/records/search" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d '{"page_size":500}')

  echo "$PROJECTS" | jq -c '.data.items[]' | while read -r project; do
    BUDGET=$(echo "$project" | jq -r '.fields.Budget // 0')
    SPENT=$(echo "$project" | jq -r '.fields.AmountSpent // 0')
    NAME=$(echo "$project" | jq -r '.fields.Name')

    PERCENT=$(echo "scale=2; $SPENT * 100 / $BUDGET" | bc)

    if (( $(echo "$PERCENT > 80" | bc -l) )); then
      LEVEL="⚠️ WARNING"
      COLOR="yellow"
    fi

    if (( $(echo "$PERCENT > 90" | bc -l) )); then
      LEVEL="🔴 CRITICAL"
      COLOR="red"
    fi

    if [ -n "$LEVEL" ]; then
      curl -X POST "$WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d "{
          \"msg_type\": \"interactive\",
          \"card\": {
            \"header\": {
              \"title\": {\"content\": \"$LEVEL: Budget Alert\", \"tag\": \"plain_text\"},
              \"template\": \"$COLOR\"
            },
            \"elements\": [
              {\"tag\": \"div\", \"text\": {\"content\": \"Project: $NAME\", \"tag\": \"plain_text\"}},
              {\"tag\": \"div\", \"text\": {\"content\": \"Budget: $BUDGET | Spent: $SPENT ($PERCENT%)\", \"tag\": \"plain_text\"}}
            ]
          }
        }"
    fi
  done
}
```

### 6. Workflow Automation Patterns

#### Document Approval Workflow
Automate document review and approval:

```bash
document_approval_workflow() {
  local DOC_TOKEN=$1
  local APPROVERS=("user1@email.com" "user2@email.com" "user3@email.com")

  # Create approval tracking base record
  APPROVAL_RECORD=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$APPROVAL_APP/tables/$APPROVAL_TABLE/records" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d "{
      \"fields\": {
        \"DocumentToken\": \"$DOC_TOKEN\",
        \"Status\": \"Pending\",
        \"Approvers\": $(printf '%s\n' "${APPROVERS[@]}" | jq -R . | jq -s .),
        \"CreatedAt\": \"$(date -Iseconds)\"
      }
    }")

  RECORD_ID=$(echo "$APPROVAL_RECORD" | jq -r '.data.record.record_id')

  # Send approval requests
  for approver in "${APPROVERS[@]}"; do
    # Get document info
    DOC_INFO=$(curl -s -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/$DOC_TOKEN" \
      -H "Authorization: Bearer $TOKEN")

    DOC_TITLE=$(echo "$DOC_INFO" | jq -r '.data.document.title')

    # Send message to approver
    curl -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=email" \
      -H "Authorization: Bearer $TOKEN" \
      -H 'Content-Type: application/json' \
      -d "{
        \"receive_id\": \"$approver\",
        \"msg_type\": \"interactive\",
        \"content\": {
          \"card\": {
            \"header\": {\"title\": {\"content\": \"Document Approval Request\", \"tag\": \"plain_text\"}},
            \"elements\": [
              {\"tag\": \"div\", \"text\": {\"content\": \"Document: $DOC_TITLE\", \"tag\": \"plain_text\"}},
              {\"tag\": \"div\", \"text\": {\"content\": \"Link: https://domain.feishu.cn/docx/$DOC_TOKEN\", \"tag\": \"plain_text\"}},
              {\"tag\": \"action\", \"actions\": [
                {\"tag\": \"button\", \"text\": {\"content\": \"Approve\", \"tag\": \"plain_text\"}, \"value\": {\"record_id\": \"$RECORD_ID\", \"action\": \"approve\"}},
                {\"tag\": \"button\", \"text\": {\"content\": \"Reject\", \"tag\": \"plain_text\"}, \"value\": {\"record_id\": \"$RECORD_ID\", \"action\": \"reject\"}}
              ]}
            ]
          }
        }
      }"
  done

  echo "Approval workflow initiated for: $DOC_TITLE"
}
```

#### New Client Onboarding Automation
Complete workflow for new client setup:

```bash
onboard_new_client() {
  local CLIENT_NAME=$1
  local CLIENT_EMAIL=$2
  local PROJECT_TYPE=$3

  echo "🚀 Starting onboarding for: $CLIENT_NAME"

  # 1. Create client record in CRM base
  CLIENT_RECORD=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$CRM_APP/tables/$CLIENTS_TABLE/records" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d "{
      \"fields\": {
        \"ClientName\": \"$CLIENT_NAME\",
        \"Email\": \"$CLIENT_EMAIL\",
        \"Status\": \"Onboarding\",
        \"ProjectType\": \"$PROJECT_TYPE\",
        \"OnboardDate\": \"$(date +%Y-%m-%d)\"
      }
    }")

  CLIENT_ID=$(echo "$CLIENT_RECORD" | jq -r '.data.record.record_id')

  # 2. Create project folder
  FOLDER=$(curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/folders" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d "{\"name\":\"$CLIENT_NAME - Project\",\"folder_token\":\"root\"}")

  FOLDER_TOKEN=$(echo "$FOLDER" | jq -r '.data.token')

  # 3. Create project documents from templates
  VARIABLES="{\"client_name\":\"$CLIENT_NAME\",\"project_type\":\"$PROJECT_TYPE\",\"date\":\"$(date +%Y-%m-%d)\"}"

  PROPOSAL_DOC=$(create_from_template "$PROPOSAL_TEMPLATE" "$CLIENT_NAME - Proposal" "$VARIABLES")
  CONTRACT_DOC=$(create_from_template "$CONTRACT_TEMPLATE" "$CLIENT_NAME - Contract" "$VARIABLES")
  KICKOFF_DOC=$(create_from_template "$KICKOFF_TEMPLATE" "$CLIENT_NAME - Kickoff Notes" "$VARIABLES")

  # 4. Create project tracking record
  PROJECT_RECORD=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$PROJECT_APP/tables/$PROJECTS_TABLE/records" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d "{
      \"fields\": {
        \"ClientID\": \"$CLIENT_ID\",
        \"ClientName\": \"$CLIENT_NAME\",
        \"Status\": \"Planning\",
        \"ProposalDoc\": \"$PROPOSAL_DOC\",
        \"ContractDoc\": \"CONTRACT_DOC\",
        \"FolderToken\": \"$FOLDER_TOKEN\"
      }
    }")

  # 5. Send welcome email
  curl -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=email" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d "{
      \"receive_id\": \"$CLIENT_EMAIL\",
      \"msg_type\": \"text\",
      \"content\": {
        \"text\": \"Welcome to our team! Your project folder and documents are ready. Check your Feishu workspace for details.\"
      }
    }"

  # 6. Notify internal team
  curl -X POST "$TEAM_WEBHOOK" \
    -H 'Content-Type: application/json' \
    -d "{
      \"msg_type\": \"text\",
      \"content\": {
        \"text\": \"✅ New client onboarded: $CLIENT_NAME\\nProject Type: $PROJECT_TYPE\\nFolder: https://domain.feishu.cn/drive/folder/$FOLDER_TOKEN\"
      }
    }"

  echo "✅ Onboarding complete for: $CLIENT_NAME"
  echo "   - Client ID: $CLIENT_ID"
  echo "   - Folder: $FOLDER_TOKEN"
  echo "   - Documents: Proposal, Contract, Kickoff Notes"
}

# Usage
onboard_new_client "Acme Corporation" "contact@acme.com" "Web Development"
```

## Advanced Automation Patterns

### Data Quality Monitoring

```bash
# Find and fix data quality issues
audit_data_quality() {
  local APP_TOKEN=$1
  local TABLE_ID=$2

  RECORDS=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$APP_TOKEN/tables/$TABLE_ID/records/search" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d '{"page_size":500}')

  ISSUES=0

  echo "$RECORDS" | jq -c '.data.items[]' | while read -r record; do
    RECORD_ID=$(echo "$record" | jq -r '.record_id')

    # Check for missing required fields
    NAME=$(echo "$record" | jq -r '.fields.Name // empty')
    EMAIL=$(echo "$record" | jq -r '.fields.Email // empty')

    if [ -z "$NAME" ] || [ -z "$EMAIL" ]; then
      echo "⚠️  Missing data in record: $RECORD_ID"
      ((ISSUES++))
    fi

    # Check email format
    if [[ ! "$EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$ ]]; then
      echo "⚠️  Invalid email in record: $RECORD_ID ($EMAIL)"
      ((ISSUES++))
    fi

    # Check for duplicates
    DUPLICATES=$(echo "$RECORDS" | jq "[.data.items[] | select(.fields.Email == \"$EMAIL\")] | length")
    if [ "$DUPLICATES" -gt 1 ]; then
      echo "⚠️  Duplicate email: $EMAIL (appears $DUPLICATES times)"
      ((ISSUES++))
    fi
  done

  echo "Data quality audit complete: $ISSUES issues found"
}
```

### Scheduled Data Export

```bash
# Export base data to CSV for backup/analysis
export_base_to_csv() {
  local APP_TOKEN=$1
  local TABLE_ID=$2
  local OUTPUT_FILE=$3

  RECORDS=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$APP_TOKEN/tables/$TABLE_ID/records/search" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d '{"page_size":500}')

  # Extract field names
  FIELDS=$(echo "$RECORDS" | jq -r '.data.items[0].fields | keys | @csv')
  echo "$FIELDS" > "$OUTPUT_FILE"

  # Extract data
  echo "$RECORDS" | jq -r '.data.items[].fields | [.Name, .Email, .Status, .Amount] | @csv' >> "$OUTPUT_FILE"

  echo "Exported to: $OUTPUT_FILE"
}

# Schedule daily exports
0 2 * * * export_base_to_csv "app_token" "table_id" "/backups/export_$(date +%Y%m%d).csv"
```

## Best Practices

### Error Handling

```bash
# Robust API call with retry logic
api_call_with_retry() {
  local endpoint=$1
  local method=$2
  local data=$3
  local max_retries=3
  local retry=0

  while [ $retry -lt $max_retries ]; do
    response=$(curl -s -w "\n%{http_code}" -X $method \
      "https://open.feishu.cn/open-apis$endpoint" \
      -H "Authorization: Bearer $TOKEN" \
      -H 'Content-Type: application/json' \
      -d "$data")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "200" ]; then
      echo "$body"
      return 0
    else
      echo "Retry $retry: HTTP $http_code" >&2
      ((retry++))
      sleep $((retry * 2))
    fi
  done

  echo "Failed after $max_retries retries" >&2
  return 1
}
```

### Rate Limiting

```bash
# Respect API rate limits
RATE_LIMIT=50  # requests per minute
CALL_COUNT=0
MINUTE_START=$(date +%s)

rate_limited_call() {
  current_time=$(date +%s)
  elapsed=$((current_time - MINUTE_START))

  if [ $elapsed -ge 60 ]; then
    CALL_COUNT=0
    MINUTE_START=$current_time
  fi

  if [ $CALL_COUNT -ge $RATE_LIMIT ]; then
    sleep_time=$((60 - elapsed))
    echo "Rate limit reached, sleeping ${sleep_time}s..." >&2
    sleep $sleep_time
    CALL_COUNT=0
    MINUTE_START=$(date +%s)
  fi

  ((CALL_COUNT++))
  # Make actual API call here
}
```

### Logging and Monitoring

```bash
# Comprehensive logging
LOG_FILE="/var/log/feishu_automation.log"

log() {
  local level=$1
  shift
  echo "[$(date -Iseconds)] [$level] $*" | tee -a "$LOG_FILE"
}

log "INFO" "Starting automation workflow"
log "ERROR" "Failed to update record: $RECORD_ID"
log "SUCCESS" "Workflow completed: 42 records processed"
```

## Common Automation Workflows

### 1. Daily Summary Email
Send daily digest of Feishu activity

### 2. Abandoned Task Reminders
Notify owners of stale tasks

### 3. Document Archival
Auto-archive old documents to specific folders

### 4. Cross-Base Analytics
Aggregate data from multiple bases for reporting

### 5. Approval Escalation
Auto-escalate pending approvals after timeout

## Integration with External Tools

### Webhook Triggers
Trigger automations from external events

### API Integrations
Connect Feishu with CRMs, project management tools, etc.

### Database Sync
Keep Feishu Bases in sync with external databases

## Security Considerations

- Store credentials securely (environment variables, secrets management)
- Use minimum required permissions
- Audit automation logs regularly
- Implement approval gates for sensitive operations
- Rate limit and monitor API usage

## Performance Optimization

- Batch operations when possible (update 100 records at once vs 100 API calls)
- Cache frequently accessed data
- Use webhooks instead of polling
- Parallelize independent operations
- Implement incremental sync (only changed data)

## Troubleshooting

### Common Issues

**Problem**: Token expires during long operations
**Solution**: Refresh token before each batch of operations

**Problem**: Rate limit exceeded
**Solution**: Implement exponential backoff and request queuing

**Problem**: Data sync conflicts
**Solution**: Use timestamp-based conflict resolution or last-write-wins

## Resources

- Feishu Open API: https://open.feishu.cn/document/home/index
- Rate Limits: https://open.feishu.cn/document/ukTMukTMukTM/uITNz4iM1MjLyUzM
- Webhooks: https://open.feishu.cn/document/ukTMukTMukTM/uUTNz4SN1MjL1UzM
