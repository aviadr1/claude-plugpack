# PlugPack MVP Launch Guide

How to use the three MVP artifacts to demonstrate value and build an audience.

---

## Quick Start

```bash
# Generate the static site
make generate-site

# Analyze a plugin
python -m skills.plugin_analyzer.analyzer https://github.com/anthropics/claude-code-plugins

# Generate a quality report
python -m generator.quality_report https://github.com/user/plugin-name
```

---

## Artifact 1: Static Site Generator

### What It Does

Generates a complete static website with 500+ Claude Code plugins, featuring:
- Rich metadata (components, dependencies, requirements)
- Category filtering
- Client-side search (Pagefind)
- "Works well with" suggestions

### How to Use

```bash
# Step 1: Run the scraper to get fresh plugin data
make scrape

# Step 2: Generate the static site
make generate-site

# Step 3: Preview locally
cd docs && python -m http.server 8080
# Visit http://localhost:8080
```

### Output Structure

```
docs/
├── index.html              # Homepage with featured plugins
├── plugins.html            # All plugins list
├── categories.html         # Category index
├── plugins/
│   ├── pr-review-toolkit.html
│   ├── feature-dev.html
│   └── ...                 # One page per plugin
├── categories/
│   ├── code-review.html
│   ├── devops.html
│   └── ...                 # One page per category
├── data/
│   └── plugins.json        # Raw data for API consumers
└── pagefind/               # Client-side search index
```

### Deployment

The site auto-deploys to GitHub Pages via `.github/workflows/deploy-site.yml`:
- **Daily at 2am UTC**: Scrapes fresh data and rebuilds
- **On push to main**: Immediate rebuild when generator changes
- **Manual trigger**: Run workflow manually from GitHub Actions

### Value Demonstration

**For the community:**
- "Find the right plugin in seconds, not hours"
- Rich metadata that no other directory provides
- See what prerequisites you need before installing

**For plugin creators:**
- Free visibility for their plugins
- Quality badges that highlight well-maintained plugins
- "Works well with" increases discoverability

---

## Artifact 2: Plugin Analyzer Skill

### What It Does

Analyzes any Claude Code plugin and extracts:
- Components (commands, agents, hooks, MCP servers)
- Dependencies (Python, Node, API keys)
- Quality signals (maintenance status, GitHub stats)
- Claude plan requirements

### How to Use

**Command Line:**
```bash
# Analyze a GitHub plugin
python -m skills.plugin_analyzer.analyzer https://github.com/anthropics/claude-code-plugins

# Analyze a local plugin
python -m skills.plugin_analyzer.analyzer /path/to/my-plugin

# Get JSON output
python -m skills.plugin_analyzer.analyzer --format json https://github.com/user/plugin
```

**Example Output:**
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
  • Maintenance: active (updated 2 weeks ago)
  • GitHub Stars: 127
  • Open Issues: 3

🎯 Best For:
  Teams with formal code review processes
```

### As a Claude Code Skill

Users can install this as a skill in their Claude Code setup:

```bash
# Copy skill to Claude Code skills directory
cp -r skills/plugin_analyzer ~/.claude/skills/

# Use in Claude Code
/analyze-plugin https://github.com/user/plugin-name
```

### Value Demonstration

**For developers:**
- "Know what you're installing before you install it"
- See exact requirements (API keys, Claude plan, dependencies)
- Compare plugins objectively

**For plugin creators:**
- Understand how their plugin will be perceived
- Identify missing metadata
- See what components are detected

---

## Artifact 3: Quality Report Generator

### What It Does

Generates comprehensive quality reports covering:
- **Security**: Dangerous patterns, external calls, file operations
- **Maintenance**: Commit frequency, issue response time, staleness
- **Documentation**: README, examples, API docs
- **Testing**: Test coverage, CI/CD setup

### How to Use

```bash
# Generate report for a GitHub plugin
python -m generator.quality_report https://github.com/anthropics/claude-code-plugins

# Generate report for a local plugin
python -m generator.quality_report /path/to/plugin

# Output formats
python -m generator.quality_report --format markdown https://github.com/user/plugin
python -m generator.quality_report --format json https://github.com/user/plugin
python -m generator.quality_report --format html https://github.com/user/plugin
```

### Example Report

```markdown
# Quality Report: pr-review-toolkit

Generated: 2025-01-11
Overall Score: 85/100

## 🔒 Security (90/100)

✅ No critical issues found
⚠️ 2 warnings:
  • Makes external API calls (standard for MCP servers)
  • Executes external processes (git commands)

## 🔧 Maintenance (95/100)

✅ Excellent
  • Last updated: 2 weeks ago
  • Commit frequency: Active
  • Recent activity detected

## 📚 Documentation (70/100)

✅ Has README
⚠️ Improvements needed:
  • Add usage examples
  • Document all commands/agents

## 🧪 Testing (40/100)

❌ Needs improvement:
  • No automated tests found
  • No CI/CD setup detected

## 💡 Recommendations

### High Priority
1. Add test coverage for command handlers

### Medium Priority
2. Add more usage examples to README

### Low Priority
3. Consider adding CHANGELOG.md
```

### Value Demonstration

**For plugin creators:**
- "Get instant feedback on your plugin's quality"
- Actionable recommendations to improve
- Security audit before publishing

**For the community:**
- Establish PlugPack as the quality authority
- Build trust through transparency
- Help creators improve the ecosystem

---

## Launch Strategy

### Phase 1: Soft Launch (Day 1-2)

1. **Deploy the static site**
   ```bash
   # Trigger manual deployment
   gh workflow run deploy-site.yml
   ```

2. **Share with 5-10 trusted users**
   - Get feedback on UX
   - Identify missing features
   - Fix critical bugs

### Phase 2: Community Launch (Day 3-4)

**Reddit Post (r/ClaudeAI):**

```markdown
**Title:** I built a better Claude Code plugin directory (500+ plugins with rich metadata)

After spending hours searching through scattered marketplaces, I built PlugPack -
an enhanced plugin directory with:

✅ Rich metadata (components, dependencies, requirements)
✅ Quality badges (maintenance status, security checks)
✅ Smart filters (by category, requirements, activity)
✅ "Works well with" suggestions

Plus two free tools:
• Plugin analyzer - inspect any plugin before installing
• Quality reports - for plugin creators

Check it out: https://plugpack.github.io

Open source: https://github.com/your-username/claude-plugpack
```

**Twitter Thread:**

```
1/ Built a better way to discover Claude Code plugins 🔌

After wasting hours on scattered directories, I made PlugPack -
500+ plugins with the metadata you actually need.

2/ Unlike existing directories, PlugPack shows:
• Components (agents, commands, hooks)
• Requirements (API keys, Claude plan)
• Maintenance status
• What plugins work well together

3/ Also open-sourced two tools:
• Plugin analyzer - inspect before installing
• Quality reports - feedback for creators

Try it: https://plugpack.github.io
```

### Phase 3: Creator Outreach (Day 5-7)

1. **Generate reports for top 20 plugins**
   ```bash
   # Create reports directory
   mkdir -p reports

   # Generate reports
   python -m generator.quality_report https://github.com/anthropics/claude-code-plugins > reports/anthropics.md
   # ... repeat for other plugins
   ```

2. **DM plugin creators with their reports**

   Template:
   ```
   Hi [creator],

   I built a Claude Code plugin quality analyzer and ran it on [plugin-name].

   Your plugin scored 85/100! Here's the full report: [link]

   Key highlights:
   - Great maintenance score (95/100)
   - Security looks solid
   - Could improve test coverage

   I'm building PlugPack (https://plugpack.github.io) to help developers
   discover quality plugins. Would love your feedback!
   ```

3. **Collect testimonials**
   - Ask creators for quotes
   - Feature on the site

---

## Success Metrics

### Week 1 Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Unique visitors | 200+ | GitHub Pages analytics |
| Analyzer usage | 10+ | Track via GitHub stars/issues |
| Quality reports | 5+ | Direct requests |
| Reddit upvotes | 20+ | Post score |
| GitHub stars | 10+ | Repository stars |

### Validation Questions

1. **Is rich metadata valuable?**
   - Track: Click-through on "View Details"

2. **Do people use the analyzer?**
   - Track: GitHub clones, issues, feedback

3. **Do creators want quality reports?**
   - Track: Report requests, positive responses

4. **Is there demand for curated packs?**
   - Track: Feedback mentioning "packs" or "workflows"

---

## Common Use Cases

### For Developers

**"I need a plugin for code review"**
1. Visit https://plugpack.github.io
2. Browse "Code Review" category
3. Compare plugins by components and requirements
4. Run analyzer on top candidates
5. Install the best fit

**"Is this plugin safe to install?"**
```bash
python -m generator.quality_report https://github.com/unknown/plugin
# Check security section
```

**"What Claude plan do I need?"**
```bash
python -m skills.plugin_analyzer.analyzer https://github.com/user/plugin
# Check "Claude Plan" in requirements
```

### For Plugin Creators

**"How do I improve my plugin?"**
```bash
python -m generator.quality_report /path/to/my-plugin
# Follow the recommendations
```

**"How do I get discovered?"**
1. Ensure your plugin has good metadata (name, description, keywords)
2. Maintain active development
3. Add documentation and tests
4. Submit to the official marketplaces (we scrape them)

**"How do I compare to other plugins?"**
```bash
# Analyze competitors
python -m skills.plugin_analyzer.analyzer https://github.com/competitor/plugin
python -m skills.plugin_analyzer.analyzer /path/to/my-plugin
# Compare the outputs
```

---

## Troubleshooting

### Static Site Issues

**Site not updating:**
```bash
# Check workflow status
gh run list --workflow=deploy-site.yml

# Trigger manual rebuild
gh workflow run deploy-site.yml
```

**Missing plugins:**
```bash
# Re-run scraper
make scrape

# Check scraped data
cat scraped_plugins.json | jq length
```

### Analyzer Issues

**"Plugin not found":**
- Ensure the URL is a valid GitHub repository
- Check if the repo is public

**"No plugin.json found":**
- The plugin may not follow standard structure
- Analyzer will still extract what it can

### Quality Report Issues

**"Clone failed":**
- Check if the repository is public
- Verify your GitHub token if rate limited

**Low scores:**
- Reports are intentionally strict
- Follow recommendations to improve

---

## What's Next

After validating the MVP:

1. **If successful (200+ visitors, positive feedback):**
   - Add user bookmarking (localStorage)
   - Build pack creation flow
   - Consider adding database for dynamic features

2. **If mixed results:**
   - Double down on what works
   - Pivot away from what doesn't
   - Focus on creator tools if directory underperforms

3. **If unsuccessful:**
   - Keep tools available (still useful)
   - Gather feedback on what's missing
   - Consider different distribution channels

---

## Support

- **Issues**: https://github.com/your-username/claude-plugpack/issues
- **Discussions**: https://github.com/your-username/claude-plugpack/discussions
