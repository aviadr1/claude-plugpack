# PRD: Claude Plugin Pack Hub

## The Ultimate Directory for Claude Code Extensions

**Version:** 1.0
**Date:** January 2026
**Status:** Draft

---

## Executive Summary

Claude Code's plugin ecosystem is exploding with 500+ plugins across dozens of marketplaces, but discovery is broken. Developers waste hours searching through GitHub repos, can't tell which plugins actually work together, and have no way to know if a plugin is maintained or abandoned.

**The opportunity:** Build the "Product Hunt for Claude Code plugins" - a community-powered aggregator that solves plugin discovery through rich metadata, curated workflow packs, and smart recommendations.

**The approach:** Don't rebuild what works. Clone the technical foundation from existing aggregators (claudecodeplugin.com, jeremylongshore's marketplace) and add the missing layers that make discovery actually work.

---

## Problem Statement

### The Current State

From our research of existing aggregators:

> "Most plugins are open-source and free. Some enterprise or specialized plugins may have commercial licenses. **Check each plugin's license in its plugin.json manifest.**"
> — claudecodeplugin.com

This sentence reveals the core problem: **users must manually investigate every plugin** to understand if it's appropriate for them.

### What Developers Face Today

**1. The Description Problem**

Looking at Anthropic's official marketplace, even well-maintained plugins have terse descriptions:

- `agent-sdk-dev`: "Development kit for working with the Claude Agent SDK"
- `hook-creator`: "Easily create custom hooks to prevent unwanted behaviors"

**What's missing:** What does "working with" mean? What can I actually build? What do I need installed first?

**2. The Discovery Black Hole**

Jeremy Longshore's marketplace has 259 plugins. A developer thinking "I want to improve my deployment workflow" has to:
1. Browse 259 plugin names
2. Click into ~15-20 that sound relevant
3. Read each README (if it exists)
4. Try to understand dependencies
5. Test combinations that might work together

**Estimated time:** 3-4 hours. **Success rate:** Maybe they find something useful.

**3. The Trust Vacuum**

From the claudemarketplaces.com homepage:

> "A comprehensive directory for discovering plugin marketplaces"

But no indicators of:
- Which marketplaces are actively maintained
- Which plugins actually work
- Which combinations are battle-tested
- Who's using what in production

### The Hidden Cost

Developers are either:
1. **Rebuilding wheels** - Creating their own solutions because they can't find existing plugins
2. **Abandoning customization** - Sticking with defaults because discovery is too hard
3. **Creating fragmentation** - Building narrow, personal marketplaces that don't get shared

---

## The Opportunity

### Market Size

**Current ecosystem:**
- 500+ Claude Code plugins across 20+ marketplaces
- 10,000+ MCP servers (per [claude-plugin-ecosystem-hub](https://github.com/pluginagentmarketplace/claude-plugin-ecosystem-hub))
- Growing 15-20% monthly (based on Jeremy Longshore's release cadence)

**Target users:**
- **Solo developers** using Claude Code (estimated 50K+ based on GitHub stars, Discord membership)
- **Engineering teams** (2-50 devs) adopting Claude Code for workflows
- **Plugin creators** who want distribution and feedback

### Comparable Markets

**npm has 2M+ packages** but succeeded because of:
- Rich metadata (weekly downloads, last publish date, dependencies)
- Community signals (GitHub stars, issues, maintainers)
- Smart search (can find packages by use case, not just name)

**Product Hunt launched 100K+ products** and works because:
- Curated collections ("Best tools for remote teams")
- Community reviews and maker stories
- Quality gatekeeping (featured vs. not featured)

**DEV.to has 1M+ articles** and thrives on:
- Tag-based discovery
- Community upvoting
- Tutorial/example focus

**Our opportunity:** Combine these models for Claude Code plugins.

---

## Solution Overview

### Core Value Proposition

**For Developers:**
"Find the perfect Claude Code plugins for your workflow in 5 minutes, not 5 hours - with confidence they'll work together."

**For Plugin Creators:**
"Get your plugins discovered by the right users with zero marketing effort."

**For the Ecosystem:**
"Accelerate Claude Code adoption by making customization accessible."

### Differentiation

| Feature | claudemarketplaces.com | claudecodeplugin.com | jeremylongshore | **Plugin Pack Hub** |
|---------|------------------------|----------------------|-----------------|---------------------|
| Basic listing | ✅ | ✅ | ✅ | ✅ |
| Categories | ❌ | ✅ | ✅ | ✅ |
| Install commands | ✅ | ✅ | ✅ | ✅ |
| Dependencies shown | ❌ | ❌ | Partial | ✅ Auto-detected |
| Prerequisites | ❌ | ❌ | ❌ | ✅ Auto-detected |
| Maintenance status | ❌ | ❌ | ❌ | ✅ Auto-tracked |
| User reviews | ❌ | ❌ | ❌ | ✅ |
| Curated packs | ❌ | ❌ | Collections | ✅ Workflow-based |
| Smart search | ❌ | Basic | ❌ | ✅ Intent-based |
| Compatibility matrix | ❌ | ❌ | ❌ | ✅ |

---

## User Personas

### 1. **Sarah - Full-Stack Freelancer**

**Background:** Solo developer shipping MVPs for startups. Uses Claude Code heavily but overwhelmed by plugin options.

**Pain Points:**
- "I spent 2 hours yesterday trying to find plugins for Next.js deployment"
- "Installed 5 plugins that conflicted with each other"
- "Can't tell which plugins are maintained vs abandoned"

**Jobs to Be Done:**
- Find a complete stack for her typical project (Next.js + Supabase + Vercel)
- Know which plugins work together
- Get started quickly without extensive configuration

**Success Metrics:**
- Finds relevant plugin pack in < 3 minutes
- Installs full stack without conflicts
- Deploys first feature same day

### 2. **Marcus - DevOps Lead at Series B Startup**

**Background:** Managing 8-person team. Wants to standardize Claude Code usage but needs control.

**Pain Points:**
- "Can't enforce consistency - everyone uses different plugins"
- "No way to vet security/quality before team adoption"
- "Plugin documentation is scattered across READMEs"

**Jobs to Be Done:**
- Find production-grade plugins for CI/CD + security + monitoring
- Verify plugins meet security standards
- Create team-specific plugin pack with their standards

**Success Metrics:**
- Team adopts standardized plugin pack within 1 week
- Zero security incidents from plugin vulnerabilities
- 30% reduction in "works on my machine" issues

### 3. **Alex - Plugin Creator**

**Background:** Built 3 popular plugins for mobile development. Wants more users and contributions.

**Pain Points:**
- "My plugins get buried in huge marketplace lists"
- "No idea who's using my plugins or how"
- "Users report issues but I can't tell if it's misconfiguration or bugs"

**Jobs to Be Done:**
- Get plugins discovered by mobile developers
- Understand user feedback and use cases
- Build reputation in the ecosystem

**Success Metrics:**
- 3x increase in plugin installations
- Regular user reviews identify improvement areas
- Invited to curate an "iOS Development Pack"

---

## Detailed Features

### Feature 1: Rich Plugin Profiles (Automated)

#### The Problem

Current plugin pages look like this:

```
pr-review-toolkit
By Anthropic
Updated 2 months ago
v1.0.0

Comprehensive PR review agents specializing in comments, tests,
error handling, type design, code quality, and code simplification

[Get Plugin] [View Source]
```

**That's it.** To learn more, you click through to GitHub and hunt through the README.

#### The Solution

**Auto-discover metadata** from plugin sources:

```
┌─────────────────────────────────────────────────────┐
│ pr-review-toolkit                    ★ 4.8 (127)   │
├─────────────────────────────────────────────────────┤
│ By Anthropic · v1.0.0 · Updated 2 weeks ago        │
│ ✅ Actively maintained · ✅ Official                 │
│                                                      │
│ Comprehensive PR review with 6 specialized agents   │
│ for comments, tests, error handling, types, quality,│
│ and code simplification.                            │
│                                                      │
│ 🎯 Best for: Teams with formal review processes     │
│ 📊 Downloads: 1.2K this month                       │
│ 🕐 Avg. setup time: < 5 minutes                     │
│                                                      │
│ ✅ What it includes:                                 │
│   • 6 specialized review agents                     │
│   • /pr-review-toolkit:review-pr command            │
│   • Confidence-based scoring                        │
│   • False positive filtering                        │
│                                                      │
│ ⚠️ Prerequisites:                                    │
│   • Git repository with commits                     │
│   • GitHub/GitLab integration recommended           │
│   • Works with Pro/Max plans (agent-heavy)         │
│                                                      │
│ 🔗 Dependencies: None                               │
│ 💰 Cost: Free (Claude Code Pro+ required)          │
│ 🏗️ Maintenance: Active (last commit 2 weeks ago)   │
│                                                      │
│ 🔥 Works well with:                                 │
│   • feature-dev (for development workflow)          │
│   • commit-commands (for Git integration)           │
│   • security-guidance (for sec review)              │
│                                                      │
│ 📚 Resources:                                        │
│   • [Setup guide] [Video tutorial] [Examples]      │
│                                                      │
│ [Install Plugin] [Add to Pack] [Report Issue]      │
└─────────────────────────────────────────────────────┘
```

#### Technical Implementation

**Data Sources (Auto-scraped):**

1. **From `plugin.json`:**
   ```json
   {
     "name": "pr-review-toolkit",
     "version": "1.0.0",
     "description": "...",
     "author": {...},
     "keywords": ["code-review", "pr", "quality"],
     "homepage": "...",
     "repository": "..."
   }
   ```

2. **From Git Repository:**
   - Last commit date → Maintenance status
   - Commit frequency → Activity level
   - Open issues → Support health
   - Stars/forks → Popularity

3. **From Plugin Structure:**
   ```bash
   plugin/
   ├── commands/          # → "Includes 1 slash command"
   ├── agents/            # → "Provides 6 agents"
   ├── .mcp.json          # → "Integrates 2 MCP servers"
   └── hooks/hooks.json   # → "Uses 3 hooks"
   ```

4. **From MCP/Dependencies:**
   - Parse `.mcp.json` for external service requirements
   - Detect Python/Node dependencies in plugin scripts
   - Flag API key requirements

### Feature 2: Curated Plugin Packs (Human-Generated)

#### The Problem

Jeremy's marketplace has "packs" like `devops-automation-pack`, but they're just bundles:

```json
{
  "name": "devops-automation-pack",
  "description": "25 plugins covering Git workflows, CI/CD pipelines,
                  Docker, Kubernetes, and Terraform infrastructure"
}
```

**Missing:** Why these 25? How do they work together? What's the onboarding flow?

#### The Solution

**Workflow-based packs with deep curation:**

```
┌──────────────────────────────────────────────────────────┐
│ 🚀 Full-Stack SaaS Starter Pack                         │
│ By Sarah Chen · For Next.js + Supabase + Vercel         │
│ ★ 4.9 (89 reviews) · 2.4K installs                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ Everything you need to go from idea to deployed MVP in   │
│ a weekend. This pack includes plugins for scaffolding,   │
│ database management, deployment automation, and          │
│ monitoring - all configured to work together.            │
│                                                           │
│ 📦 What's Inside (8 plugins):                            │
│                                                           │
│ Phase 1: Setup (Day 1 morning)                          │
│   ✓ nextjs-scaffolder - Project structure + configs     │
│   ✓ supabase-toolkit - Database setup + auth            │
│   └─→ Run: /nextjs-scaffold my-app, /supabase-init      │
│                                                           │
│ Phase 2: Development (Day 1-2)                          │
│   ✓ frontend-design - Component library + Tailwind      │
│   ✓ api-dev-toolkit - API routes + validation           │
│   ✓ db-migrations - Schema versioning                   │
│   └─→ Workflow: Design → API → DB in sync               │
│                                                           │
│ Phase 3: Quality (Day 2)                                │
│   ✓ test-generator - E2E tests for critical paths       │
│   ✓ pr-review-toolkit - Pre-deploy code review          │
│   └─→ Run: /test-generate, /pr-review before deploy     │
│                                                           │
│ Phase 4: Deploy (Day 2 evening)                         │
│   ✓ vercel-deployer - One-command deployment            │
│   └─→ Run: /vercel-deploy --production                  │
│                                                           │
│ [Install Full Pack] [Customize] [Add to Favorites]      │
└──────────────────────────────────────────────────────────┘
```

### Feature 3: Community-Powered Reviews & Examples

Review system (inspired by Product Hunt + DEV.to) with:
- Star ratings
- Pro tips and gotchas
- Framework/team size context
- Example links

### Feature 4: Smart Discovery (Intent-Based Search)

Natural language search that understands intent:
- "I want to improve my deployment workflow" → deployment plugins
- "React testing is painful" → testing plugins for React
- "security audit for Node.js API" → security scanning plugins

### Feature 5: Educational Hub (External Links Only)

Curated link directory organizing tutorials, videos, and examples from across the web.

### Feature 6: Quality Gatekeeping

Automated quality signals:
- Security scanning
- Maintenance status
- Compatibility checks
- Badge system (Verified, Featured, Popular, Secure, Active, Well-Documented)

---

## Technical Architecture

### Stack

- **Frontend:** Next.js (static + incremental)
- **Data Layer:** PostgreSQL + GitHub (source of truth) + Redis
- **Search:** Meilisearch
- **Background Jobs:** Scraper, quality checks, analytics

### Data Model

Core entities: Plugin, PluginPack, Review, User

---

## Success Metrics

### North Star Metric

**Time to productive plugin setup** (TTPS): < 5 minutes

### Key Metrics

- Monthly active users: 5K (Month 3), 20K (Month 6)
- Search → Install rate: 40%
- Pack adoption rate: 25%
- Plugins with rich profiles: 80%
- Curated packs: 50 by Month 6

---

## Go-To-Market Strategy

1. **Phase 1 (Month 1):** Private beta with 50 power users
2. **Phase 2 (Month 2):** Public launch on Product Hunt, Reddit, HN
3. **Phase 3 (Months 3-6):** Content marketing, partnerships, SEO

---

## Implementation Roadmap

### Month 1: MVP Foundation
- Data layer + scraper
- Plugin listing + search
- Pack creation + review forms

### Month 2: Community Features
- Reviews & examples
- User authentication
- Quality badges

### Month 3-6: Growth & Scale
- Advanced features
- Performance optimization
- Monetization prep

---

## Summary

**The opportunity is massive:** 500+ plugins, 50K+ developers, growing fast.

**The problem is real:** Developers waste hours on plugin discovery and integration.

**The solution is proven:** Rich metadata + curation + community (see npm, Product Hunt, DEV.to).

**Let's build the definitive Claude Code plugin directory.**
