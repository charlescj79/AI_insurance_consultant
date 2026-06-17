# R33 — n8n Integration Plan (保险咨询MCP Server)

## Overview
n8n is a workflow automation platform with 21,100+ GitHub stars, v2.57.4 active maintenance. Supports MCP protocol through HTTP nodes and custom integrations.

## Why n8n for Insurance Sales?
- **Private deployment on Hong Kong** → data export risk = NONE
- **No code visual workflow** → sales team can build lead routing pipelines
- **MCP support via HTTP/SSE** → direct connection to our MCP server
- **CRON triggers** → automated daily compliance checks, content scheduling

## Integration Patterns

### Pattern 1: HTTP API (Quick Start)
```json
{
  "name": "Insurance MCP Query",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://localhost:18060/v1/execute",
    "method": "POST",
  "headers": {
    "X-API-Key": "{{ $env.MCP_API_KEY }}",
    "Content-Type": "application/json"
  },
    "body": {
      "jsonrpc": "2.0",
      "method": "tools/call",
      "params": {
        "name": "compliance_check",
        "arguments": {
          "text": "{{ $json.content }}"
        }
      },
      "id": 1
    }
  }
}
```

**n8n Workflow Example:**
```
[Webhook Trigger] → [HTTP Request (MCP Server)] → [Switch Node] → [Telegram/Email Notification]
     ↓                                       ↓
[Gemini AI Summarize]              [GCS Store Compliance Report]
```

### Pattern 2: MCP SSE Endpoint
```json
{
  "name": "MCP SSE Connector",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://localhost:18060/mcp/sse",
    "method": "GET",
    "responseFormat": "streaming"
  }
}
```

### Pattern 3: n8n MCP Custom Node (Advanced)
Create custom node package following n8n community template:
```bash
npm create n8n-npm-package@latest n8n-nodes-insurance-mcp
# Then reference our MCP server via MCP SDK in the custom node
```

## Docker Compose Deployment

### n8n Container
```yaml
version: '3.8'
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    environment:
      - N8N_SECURE_COOKIE=true
      - GENERIC_TIMEZONE=Asia/Hong_Kong
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=30
      - DB_TYPE=postgresdb
      - POSTGRESDB_HOST=db
      - POSTGRESDB_DATABASE=n8n
    ports:
      - "5678:5678"
    volumes:
      - n8n_data:/data
  insurance-mcp-server:
    build: ./mcp
    environment:
      - SERVER_TRANSPORT=http
      - SERVER_PORT=18060
      - SERVER_API_KEY=${MCP_API_KEY}
      - PYTHONPATH=/app/knowledge/sales-skills/mcp
    ports:
      - "18060:18060"
  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  n8n_data:
  postgres_data:
```

## Compliance Assessment for n8n Deployment

| Item | Risk Level | Details |
|------|-----------|---------|
| Data Export | NONE (PRIVATE) | All containers deployed in Hong Kong cloud/VM |
| PII Processing | LOW | Configurable data retention policies |
| GL-44 Alignment | COMPLIANT | compliance_check tool runs in pipeline |
| Scheduling | COMPLIANT | Cron-based daily checks within local boundary |

## Workflow Templates to Build
1. **Lead Ingestion Pipeline**: Webhook → MCP qualification → CRM sync
2. **Compliance Gatekeeper**: Content draft → compliance_check → approve/reject routing
3. **Daily Reporting**: MCP data export → summary generation → Telegram notification
4. **Customer Follow-up Scheduler**: Session data → needs_assessment → reminder cron

## Production Checklist
- [ ] n8n hosted on Hong Kong cloud (AWS/ap-northeast-1 or local VPS)
- [ ] API_KEY rotated monthly via secrets manager
- [ ] CORS whitelist restricted to internal domains
- [ ] Rate limiting at 100 req/min for production volume
- [ ] Audit logging of all MCP tool calls
- [ ] Data retention policy: max 90 days session data
