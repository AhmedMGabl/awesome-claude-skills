# Skill Requirements and Authentication Guide

This document outlines external dependencies, authentication requirements, and setup instructions for all skills in the repository.

## Skills Requiring No External Authentication

These skills work entirely locally without requiring external API keys or authentication:

### Development & Code Tools
- **Artifacts Builder** - Builds React artifacts locally using npm/Node.js
- **Changelog Generator** - Works with local git repositories
- **MCP Builder** - Guides MCP server creation locally
- **Skill Creator** - Creates skill files locally
- **Template Skill** - Template for creating new skills
- **Webapp Testing** - Uses Playwright for local web testing

### Creative & Media
- **Algorithmic Art** - Creates art using local computational methods
- **Canvas Design** - Creates designs locally
- **Theme Factory** - Applies themes to artifacts locally

### Productivity & Organization
- **File Organizer** - Organizes local files
- **Invoice Organizer** - Organizes local invoice files
- **Raffle Winner Picker** - Selects winners from local data
- **Template Skill** - Infrastructure template

### Document Processing
- **document-skills (docx, pdf, pptx, xlsx)** - Works with local Office documents

---

## Skills Requiring API Keys or External Authentication

### Business & Marketing

#### **Brand Guidelines**
- **Requirements**: None (uses Anthropic brand colors, no API needed)
- **Setup**: Ready to use

#### **Competitive Ads Extractor**
- **Requirements**:
  - Meta (Facebook) Ad Library access
  - LinkedIn Campaign Manager access (for LinkedIn ads)
- **Authentication**: Web-based, may require logging into ad platforms
- **Setup**: Navigate to ad library URLs when prompted

#### **Domain Name Brainstormer**
- **Requirements**:
  - Various domain registrar APIs (optional)
  - WHOIS lookup access
- **Authentication**: May use public WHOIS APIs (no auth typically required)
- **Setup**: Works without auth for basic checks

#### **Internal Comms**
- **Requirements**: None (template-based)
- **Setup**: Customize templates for your organization

#### **Lead Research Assistant**
- **Requirements**:
  - Web search capabilities (via WebSearch tool)
  - LinkedIn access (optional, for lead research)
  - Company database APIs (optional)
- **Authentication**: Uses Claude's built-in web search
- **Setup**: Works with web search, enhanced with LinkedIn access

### Communication & Writing

#### **Content Research Writer**
- **Requirements**:
  - Web search capabilities (via WebSearch tool)
  - Citation databases (optional)
- **Authentication**: Uses Claude's built-in web search
- **Setup**: Ready to use with WebSearch

#### **Meeting Insights Analyzer**
- **Requirements**: Meeting transcript files (local)
- **Authentication**: None
- **Setup**: Provide transcript files

### Creative & Media

#### **Image Enhancer**
- **Requirements**:
  - Image processing libraries (local)
  - Upscaling models (downloads automatically)
- **Authentication**: None
- **Setup**: First run downloads required models

#### **Slack GIF Creator**
- **Requirements**:
  - ImageMagick or similar (for GIF creation)
  - Slack workspace (for uploading)
- **Authentication**: Slack OAuth token (if uploading directly)
- **Setup**: Install ImageMagick, configure Slack token if needed

#### **Video Downloader**
- **Requirements**:
  - yt-dlp or youtube-dl
  - FFmpeg (for format conversion)
- **Authentication**: None for public videos
- **Setup**: Install yt-dlp and FFmpeg

### Development & Code Tools

#### **Developer Growth Analysis**
- **Requirements**:
  - Claude Code chat history access
  - HackerNews API access (public)
  - Slack workspace and bot token
- **Authentication**:
  - Slack Bot OAuth Token required
  - Configure in `~/.claude/developer-growth-analysis/config.json`
- **Setup**:
  ```json
  {
    "slack_token": "xoxb-your-token-here",
    "slack_channel": "#dev-growth"
  }
  ```

#### **Feishu MCP**
- **Requirements**:
  - Feishu (Lark) workspace
  - Feishu App credentials
- **Authentication**:
  - App ID and App Secret
  - Tenant Access Token
- **Setup**:
  1. Create Feishu app at https://open.feishu.cn/
  2. Configure MCP server with credentials
  3. Set environment variables:
     ```bash
     export FEISHU_APP_ID="your-app-id"
     export FEISHU_APP_SECRET="your-app-secret"
     ```

#### **Skill Share**
- **Requirements**:
  - Slack workspace
  - Rube integration (for Slack posting)
- **Authentication**: Slack Bot OAuth Token via Rube
- **Setup**: Configure Rube with Slack credentials

---

## MCP Servers and Integrations

Several skills integrate with MCP (Model Context Protocol) servers:

### Already Configured in Your Environment

Based on available tools, you have:

1. **GitHub MCP** - GitHub API integration
   - Requires: GitHub personal access token
   - Setup: Configure via Claude Code settings

2. **Greptile MCP** - Code search and custom context
   - Requires: Greptile API key
   - Setup: Sign up at greptile.com

3. **Context7 MCP** - Documentation search
   - Requires: No authentication
   - Setup: Works out of box

4. **Pinecone MCP** - Vector database
   - Requires: Pinecone API key
   - Setup: Sign up at pinecone.io

5. **Render MCP** - Render.com deployment
   - Requires: Render API key
   - Setup: Get from render.com dashboard

6. **Railway MCP** - Railway.app deployment
   - Requires: Railway API token
   - Setup: Get from railway.app

7. **Playwright MCP** - Browser automation
   - Requires: Playwright installation
   - Setup: Automatically installed

8. **Serena MCP** - Code analysis
   - Requires: Serena configuration
   - Setup: Automatically configured

---

## Installation Commands

### Required Dependencies

#### For Artifacts Builder
```bash
# Install Node.js and npm
node --version  # Should be v18+
npm --version

# Dependencies installed automatically by skill
```

#### For Video Downloader
```bash
# Install yt-dlp
pip install yt-dlp

# Install FFmpeg
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg  # Debian/Ubuntu
sudo dnf install ffmpeg  # Fedora

# Windows
# Download from https://ffmpeg.org/download.html
```

#### For Image Enhancer
```bash
# Install Python dependencies
pip install pillow opencv-python

# Models download automatically on first use
```

#### For Slack GIF Creator
```bash
# Install ImageMagick
# macOS
brew install imagemagick

# Linux
sudo apt install imagemagick  # Debian/Ubuntu
sudo dnf install imagemagick  # Fedora

# Windows
# Download from https://imagemagick.org/script/download.php
```

#### For Webapp Testing
```bash
# Playwright installed via MCP
# If manual install needed:
npm install playwright
npx playwright install chromium
```

---

## Environment Variables Quick Reference

Create a `.env` file in your Claude Code config directory:

```bash
# Slack Integrations
SLACK_BOT_TOKEN=xoxb-your-token

# Feishu/Lark
FEISHU_APP_ID=your-app-id
FEISHU_APP_SECRET=your-app-secret

# GitHub (usually configured via Claude Code)
GITHUB_TOKEN=ghp_your-token

# Pinecone
PINECONE_API_KEY=your-api-key

# Render
RENDER_API_KEY=your-api-key

# Railway
RAILWAY_API_TOKEN=your-token

# Greptile
GREPTILE_API_KEY=your-api-key
```

---

## Testing Checklist

### ✅ Skills Ready to Test Without Authentication

1. File Organizer
2. Invoice Organizer
3. Raffle Winner Picker
4. Changelog Generator (needs git repo)
5. Skill Creator
6. Theme Factory
7. Canvas Design
8. Algorithmic Art
9. Meeting Insights Analyzer (needs transcript)
10. Content Research Writer (uses WebSearch)
11. Domain Name Brainstormer
12. Brand Guidelines
13. Internal Comms

### 🔐 Skills Requiring Setup Before Testing

1. Developer Growth Analysis (needs Slack token)
2. Feishu MCP (needs Feishu credentials)
3. Skill Share (needs Slack via Rube)
4. Video Downloader (needs yt-dlp)
5. Image Enhancer (needs models)
6. Slack GIF Creator (needs ImageMagick)
7. Artifacts Builder (needs npm/Node.js)
8. Webapp Testing (Playwright configured)
9. Competitive Ads Extractor (needs ad platform access)

### 📦 Skills Needing External Dependencies

1. Document Skills (needs python-docx, openpyxl, PyPDF2, python-pptx)
   ```bash
   pip install python-docx openpyxl PyPDF2 python-pptx
   ```

---

## Common Issues and Solutions

### "API key not found"
- Check environment variables are set
- Restart Claude Code after setting env vars
- Verify `.env` file location

### "Module not found" errors
- Install required Python packages
- Check Node.js version for Artifacts Builder
- Verify system dependencies (FFmpeg, ImageMagick)

### Playwright browser not installed
```bash
npx playwright install chromium
```

### Git operations failing
- Ensure repository has `.git` directory
- Check git is installed: `git --version`
- Verify user has commit permissions

---

## Skill Categories by Complexity

### Beginner-Friendly (No Setup)
- Template Skill
- Skill Creator
- Brand Guidelines
- Theme Factory
- File Organizer
- Raffle Winner Picker

### Intermediate (Minimal Setup)
- Changelog Generator
- Content Research Writer
- Domain Name Brainstormer
- Meeting Insights Analyzer
- Canvas Design
- Algorithmic Art

### Advanced (Requires Configuration)
- Feishu MCP
- Developer Growth Analysis
- Skill Share
- Artifacts Builder
- Video Downloader
- Webapp Testing

---

## Getting Help

For skill-specific issues:
1. Check the skill's SKILL.md file for detailed instructions
2. Review error messages carefully
3. Verify all prerequisites are installed
4. Check authentication credentials are valid
5. Consult the skill's references/ directory if available

For MCP server issues:
1. Verify MCP server is running
2. Check API keys and tokens
3. Review MCP server logs
4. Restart Claude Code

---

Last Updated: 2026-01-22
