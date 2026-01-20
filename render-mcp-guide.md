# Render MCP - Complete Setup Guide

## What is Render MCP?

Render MCP is a Model Context Protocol (MCP) server that integrates Render's cloud platform with Claude Code. It allows you to manage your Render infrastructure directly from Claude - creating services, databases, deploying code, monitoring logs, and more.

## What You Can Do with Render MCP

### Services Management
- ✅ Create web services (Node.js, Python, Go, Rust, Ruby, etc.)
- ✅ Create static sites (React, Vue, Gatsby)
- ✅ List and monitor all your services
- ✅ Get service details and status

### Database Operations
- ✅ Create and manage PostgreSQL databases
- ✅ Create and manage Key-Value stores (Redis)
- ✅ Query databases with read-only SQL
- ✅ Monitor database metrics and performance

### Deployment & Monitoring
- ✅ List deployments for services
- ✅ Get deployment details and status
- ✅ View build and deploy logs
- ✅ Monitor real-time application logs

### Logs & Metrics
- ✅ Query logs with filtering (by time, text, level, etc.)
- ✅ Get performance metrics (CPU, memory, bandwidth)
- ✅ Monitor HTTP request metrics
- ✅ Track database connections

### Environment Management
- ✅ Update environment variables
- ✅ Manage service configuration
- ✅ Workspace selection and management

## Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **Render API Key**: Get it from your Render dashboard
3. **Claude Code**: Latest version installed
4. **MCP Server**: The Render MCP server needs to be installed

## Installation Steps

### Step 1: Get Your Render API Key

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click on your profile (top right) → **Account Settings**
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Give it a name (e.g., "Claude Code MCP")
6. Copy the generated key (keep it safe!)

### Step 2: Install Render MCP Server

There are multiple ways to install the Render MCP server:

#### Option A: Using npx (Recommended)
```bash
npx @render/mcp
```

#### Option B: Clone from GitHub
```bash
git clone https://github.com/render-oss/render-mcp-server
cd render-mcp-server
npm install
npm run build
```

#### Option C: Global Install
```bash
npm install -g @render/mcp
```

### Step 3: Configure Claude Code

Add the Render MCP server to your Claude Code configuration:

**For macOS/Linux**: `~/.config/claude-code/claude_desktop_config.json`
**For Windows**: `%APPDATA%\claude-code\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "render": {
      "command": "npx",
      "args": ["@render/mcp"],
      "env": {
        "RENDER_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

**Alternative (if cloned from GitHub)**:
```json
{
  "mcpServers": {
    "render": {
      "command": "node",
      "args": ["/path/to/render-mcp-server/build/index.js"],
      "env": {
        "RENDER_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

### Step 4: Restart Claude Code

After updating the configuration:
1. Completely quit Claude Code
2. Restart Claude Code
3. The Render MCP server should connect automatically

## Verification

To verify Render MCP is working, ask Claude:

```
"List my Render services"
"Show my Render workspaces"
"What databases do I have on Render?"
```

If configured correctly, Claude will use the Render MCP tools to fetch this information.

## Common Use Cases

### 1. Create a Web Service

```
"Create a Node.js web service on Render:
- Name: my-api
- Repository: https://github.com/myuser/myrepo
- Branch: main
- Build command: npm install
- Start command: npm start
- Region: Oregon"
```

### 2. Create a Static Site

```
"Deploy a static site on Render:
- Name: my-portfolio
- Repository: https://github.com/myuser/portfolio
- Build command: npm run build
- Publish path: ./dist"
```

### 3. Create PostgreSQL Database

```
"Create a PostgreSQL database:
- Name: my-app-db
- Plan: free
- Version: 16"
```

### 4. View Logs

```
"Show me the latest logs from my web service"
"Get deployment logs for service [service-id]"
"Show logs from the last hour with errors only"
```

### 5. Monitor Metrics

```
"Show CPU and memory usage for my service over the last 24 hours"
"Get HTTP request metrics for my API"
"Show database connection count"
```

### 6. Update Environment Variables

```
"Add these environment variables to my service:
- DATABASE_URL=postgres://...
- API_KEY=abc123
- NODE_ENV=production"
```

## Available Tools Reference

Here are all the Render MCP tools available:

### Service Tools
- `create_web_service` - Create new web service
- `create_static_site` - Create static site
- `get_service` - Get service details
- `list_services` - List all services
- `update_web_service` - Update web service
- `update_static_site` - Update static site

### Database Tools
- `create_postgres` - Create PostgreSQL instance
- `create_key_value` - Create Key-Value store
- `get_postgres` - Get Postgres details
- `get_key_value` - Get Key-Value details
- `list_postgres_instances` - List all databases
- `list_key_value` - List Key-Value stores
- `query_render_postgres` - Run SQL queries (read-only)

### Deployment Tools
- `list_deploys` - List deployments
- `get_deploy` - Get deployment details

### Logs & Metrics Tools
- `list_logs` - Query application logs
- `list_log_label_values` - List available log filters
- `get_metrics` - Get performance metrics

### Workspace Tools
- `list_workspaces` - List all workspaces
- `get_selected_workspace` - Get current workspace
- `select_workspace` - Switch workspace

### Environment Tools
- `update_environment_variables` - Update env vars

## Best Practices

### 1. Security
- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys periodically
- Use read-only keys when possible

### 2. Service Management
- Use descriptive service names
- Tag services by environment (dev, staging, prod)
- Set up auto-deploy for development branches
- Use manual deploy for production

### 3. Database Management
- Start with free tier for development
- Monitor connection counts regularly
- Use read replicas for read-heavy workloads
- Backup before major changes

### 4. Monitoring
- Check logs regularly for errors
- Set up alerts for critical metrics
- Monitor CPU and memory trends
- Track database performance

### 5. Cost Optimization
- Use free tier for testing
- Scale down unused services
- Use starter plans for low-traffic apps
- Monitor bandwidth usage

## Troubleshooting

### MCP Server Not Connecting

**Problem**: Render tools not available in Claude

**Solutions**:
1. Check API key is correct in config
2. Verify config file path is correct
3. Restart Claude Code completely
4. Check Claude Code logs for errors
5. Verify internet connection

### API Key Invalid

**Problem**: "Authentication failed" errors

**Solutions**:
1. Generate new API key from Render dashboard
2. Update config with new key
3. Ensure no extra spaces in API key
4. Restart Claude Code

### Service Creation Fails

**Problem**: Cannot create services

**Solutions**:
1. Check workspace has available resources
2. Verify repository URL is accessible
3. Ensure branch exists in repository
4. Check Render account limits

### Logs Not Showing

**Problem**: Empty log results

**Solutions**:
1. Verify service ID is correct
2. Check time range (must be within 30 days)
3. Ensure service has been deployed
4. Try broader filter criteria

## Additional Resources

- **Render Documentation**: [docs.render.com](https://docs.render.com)
- **Render API Docs**: [api-docs.render.com](https://api-docs.render.com)
- **MCP Documentation**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Render Support**: support@render.com
- **Render Community**: [community.render.com](https://community.render.com)

## Quick Reference Commands

```bash
# List services
"Show all my Render services"

# Create service
"Create a web service on Render with [details]"

# View logs
"Get logs from service [name]"

# Check metrics
"Show metrics for service [name]"

# Create database
"Create a PostgreSQL database named [name]"

# Update env vars
"Update environment variables for [service]"

# List deployments
"Show recent deployments for [service]"

# Query database
"Query my Render database: SELECT * FROM users LIMIT 10"
```

## Example Workflow

### Deploying a Full Stack Application

```
1. "Create a PostgreSQL database named myapp-db with free plan"

2. "Create a web service for my backend:
   - Repository: github.com/me/backend
   - Build: npm install
   - Start: npm start
   - Environment: Add DATABASE_URL from the database"

3. "Create a static site for my frontend:
   - Repository: github.com/me/frontend
   - Build: npm run build
   - Publish: ./build"

4. "Generate domain for my backend service"

5. "Show logs for both services to verify deployment"

6. "Get metrics for the backend to monitor performance"
```

---

## Support

If you need help:
1. Check Render status page
2. Review Render documentation
3. Ask in Render community forums
4. Contact Render support
5. Check Claude Code documentation

**Version**: 1.0
**Last Updated**: January 2026
**Author**: Ahmed Gabl

---

Happy deploying with Render MCP! 🚀
