# Awesome Claude Skills - Project Overview

## Purpose
This repository is a curated collection of practical Claude Skills for enhancing productivity across Claude.ai, Claude Code, and the Claude API. It serves as both a marketplace of skills and a resource for creating new skills.

## What are Claude Skills?
Claude Skills are customizable workflows that teach Claude how to perform specific tasks according to unique requirements. Skills enable Claude to execute tasks in a repeatable, standardized manner across all Claude platforms.

## Key Features
- Collection of 50+ practical skills across multiple categories
- Skills work across Claude.ai, Claude Code, and Claude API
- Progressive disclosure pattern for efficient context usage
- Marketplace integration via `.claude-plugin/marketplace.json`

## Target Users
- Claude users looking for pre-built productivity workflows
- Developers creating custom Claude skills
- Contributors adding new skills to the community

## Repository Structure
- Individual skill folders at root level (e.g., `skill-creator/`, `mcp-builder/`)
- Documentation: `README.md`, `CONTRIBUTING.md`, `CLAUDE.md`
- Marketplace config: `.claude-plugin/marketplace.json`
- Utility scripts: `create_skill_zips.py`, `verify_skills.py`
- Output directory: `skill-zips/` (generated, gitignored)