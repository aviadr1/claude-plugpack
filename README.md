# PlugPack

**The Ultimate Directory for Claude Code Extensions**

Find the perfect Claude Code plugins in 5 minutes, not 5 hours.

[![CI](https://github.com/aviadr1/claude-plugpack/actions/workflows/ci.yml/badge.svg)](https://github.com/aviadr1/claude-plugpack/actions/workflows/ci.yml)
[![Deploy](https://github.com/aviadr1/claude-plugpack/actions/workflows/deploy-site.yml/badge.svg)](https://github.com/aviadr1/claude-plugpack/actions/workflows/deploy-site.yml)

---

## What is PlugPack?

PlugPack solves plugin discovery for Claude Code developers through:

- **Rich Metadata** - Components, dependencies, requirements auto-detected
- **Quality Signals** - Maintenance status, security checks, activity level
- **Smart Filtering** - By category, Claude plan requirement, framework
- **Works Well With** - See which plugins complement each other

## MVP Artifacts

### 1. Static Site Generator

Generates a complete plugin directory website with 500+ enriched plugins.

```bash
# Generate the static site
make generate-site

# Preview locally
cd docs && python -m http.server 8080
```

### 2. Plugin Analyzer Skill

Analyze any Claude Code plugin before installing.

```bash
# Analyze a GitHub plugin
python -m skills.plugin_analyzer.analyzer https://github.com/user/plugin

# Analyze a local plugin
python -m skills.plugin_analyzer.analyzer /path/to/plugin
```

**Output:**
```
Plugin Analysis: pr-review-toolkit
==================================

📦 Components:
  • Commands: 1
  • Agents: 6
  • Hooks: 0
  • MCP Servers: 0

⚙️ Requirements:
  • Claude Plan: pro (agent-heavy plugin)
  • Prerequisites: Git repository
  • API Keys: None required

📊 Quality Signals:
  • Maintenance: active
  • GitHub Stars: 127
```

### 3. Quality Report Generator

Generate comprehensive quality reports for plugin creators.

```bash
# Generate a quality report
python -m generator.quality_report https://github.com/user/plugin

# Output formats: markdown, json, html
python -m generator.quality_report --format json https://github.com/user/plugin
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/aviadr1/claude-plugpack.git
cd claude-plugpack

# Install dependencies
make install

# Run quality checks
make check
```

### Development

```bash
# Start the FastAPI dev server
make dev

# Run tests
make test

# Run linter + formatter + type checker
make check
```

---

## Project Structure

```
claude-plugpack/
├── src/plugpack/          # FastAPI application
│   ├── api/               # API endpoints
│   ├── models/            # SQLModel database models
│   ├── scraper/           # Plugin data scraping
│   └── templates/         # Jinja2 templates
├── generator/             # Static site generator
│   ├── generate.py        # Main generator
│   ├── quality_report.py  # Quality report generator
│   └── templates/         # HTML templates
├── skills/                # Claude Code skills
│   └── plugin_analyzer/   # Plugin analysis skill
├── tests/                 # Test suite
└── documentation/         # Project documentation
    └── prd/               # Product requirements
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [CLAUDE.md](./CLAUDE.md) | Development guide for Claude |
| [LAUNCH_GUIDE.md](./LAUNCH_GUIDE.md) | How to use and launch the MVP |
| [Original PRD](./documentation/prd/01-original-platform-prd.md) | Full platform vision |
| [MVP PRD](./documentation/prd/02-mvp-prd.md) | 7-day MVP execution plan |

---

## Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make dev` | Start development server |
| `make test` | Run tests |
| `make check` | Run linter + formatter + type checker |
| `make generate-site` | Generate static site |
| `make scrape` | Scrape plugin data |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Database | PostgreSQL + SQLModel |
| Templates | Jinja2 + HTMX |
| Styling | Tailwind CSS |
| Search | Meilisearch / Pagefind |
| Package Manager | uv |
| Linting | ruff |
| Type Checking | pyright |

---

## Status

**Current Phase:** MVP Complete

- [x] Static site generator
- [x] Plugin analyzer skill
- [x] Quality report generator
- [x] GitHub Actions deployment
- [ ] Public launch
- [ ] Community feedback

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make check` and `make test`
5. Submit a pull request

---

## License

MIT
