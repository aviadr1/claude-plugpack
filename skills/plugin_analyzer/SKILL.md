# Plugin Analyzer Skill

Analyzes Claude Code plugins to extract comprehensive metadata, assess quality,
and identify requirements before installation.

## What This Skill Does

Given a plugin (GitHub URL or local path), extracts:
- **Metadata**: Name, version, author, description, keywords
- **Components**: Count of commands, agents, hooks, MCP servers
- **Dependencies**: Python/Node packages, API keys required
- **Quality**: Maintenance status, issue count, last commit
- **Requirements**: Prerequisites, Claude plan needs

## When to Use

- Before installing an unknown plugin
- When documenting a plugin
- When building a plugin directory/catalog
- When assessing plugin compatibility

## Usage

```bash
# Analyze a GitHub plugin
/analyze-plugin https://github.com/user/plugin-name

# Analyze local plugin
/analyze-plugin /path/to/plugin

# Get JSON output
/analyze-plugin --format json https://github.com/user/plugin-name
```

## Output Example

```
Plugin: pr-review-toolkit
Version: 1.0.0
Author: Anthropic

Components:
  - 6 agents
  - 1 command (/pr-review-toolkit:review-pr)
  - 0 hooks
  - 0 MCP servers

Requirements:
  - Claude Pro or Max plan (agent-heavy)
  - Git repository with commits
  - No external API keys

Dependencies:
  - None

Quality:
  - Active (updated 2 weeks ago)
  - 127 GitHub stars
  - 3 open issues (down from 8)
  - No automated tests found

Best For:
  Teams with formal code review processes

Notes:
  - Heavy context usage - may consume quota quickly
  - Requires Pro+ plan for 6 parallel agents
```

## How It Works

1. **Clone/Access**: Fetches the plugin from GitHub or accesses local directory
2. **Parse**: Reads plugin.json, SKILL.md, and other configuration files
3. **Analyze Structure**: Counts commands, agents, hooks, MCP servers
4. **Detect Dependencies**: Scans for requirements.txt, package.json, API key patterns
5. **Check Quality**: Queries GitHub API for stars, issues, last commit
6. **Generate Report**: Formats findings into readable output

## Installation

This skill is part of the PlugPack plugin analyzer tools.

```bash
# Clone the repository
git clone https://github.com/aviadr1/claude-plugpack.git

# The skill is in skills/plugin-analyzer/
```

## Contributing

Found a bug or want to improve the analyzer? Contributions welcome!
