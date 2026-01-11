#!/usr/bin/env python3
"""
Static site generator for PlugPack.

Generates a beautiful static site from scraped plugin data.
Output goes to docs/ for GitHub Pages deployment.

Usage:
    python -m generator.generate
    # or
    make generate-site
"""

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .utils import (
    format_date,
    format_number,
    get_category_info,
    get_maintenance_badge,
    group_by_category,
    sort_plugins,
    time_ago,
)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = Path(__file__).parent / "templates"
OUTPUT_DIR = PROJECT_ROOT / "docs"
DATA_FILE = PROJECT_ROOT / "scraped_plugins.json"


def load_plugins() -> list[dict]:
    """Load plugins from scraped_plugins.json."""
    if not DATA_FILE.exists():
        print(f"Warning: {DATA_FILE} not found. Run 'make scrape' first.")
        return []

    with DATA_FILE.open() as f:
        plugins = json.load(f)

    print(f"Loaded {len(plugins)} plugins from {DATA_FILE}")
    return plugins


def setup_jinja_env() -> Environment:
    """Set up Jinja2 environment with custom filters."""
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Add custom filters
    env.filters["format_date"] = format_date
    env.filters["time_ago"] = time_ago
    env.filters["format_number"] = format_number
    env.filters["maintenance_badge"] = get_maintenance_badge
    env.filters["category_info"] = get_category_info

    return env


def render_template(env: Environment, template_name: str, context: dict, output_path: Path):
    """Render a template and write to file."""
    template = env.get_template(template_name)
    html = template.render(**context)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        f.write(html)

    print(f"  Generated: {output_path.relative_to(PROJECT_ROOT)}")


def generate_index(env: Environment, plugins: list[dict]):
    """Generate the homepage."""
    # Get stats
    categories = group_by_category(plugins)
    featured = [p for p in plugins if p.get("is_verified")]

    context = {
        "plugins": sort_plugins(plugins, "stars")[:12],  # Top 12 for homepage
        "total_plugins": len(plugins),
        "total_categories": len(categories),
        "categories": sorted(categories.keys()),
        "category_counts": {cat: len(items) for cat, items in categories.items()},
        "featured_plugins": featured[:6],
        "generated_at": datetime.now(UTC).isoformat(),
    }

    render_template(env, "index.html", context, OUTPUT_DIR / "index.html")


def generate_plugin_pages(env: Environment, plugins: list[dict]):
    """Generate individual plugin pages."""
    # Find related plugins for each plugin
    categories = group_by_category(plugins)

    for plugin in plugins:
        # Get related plugins from same category
        category = plugin.get("category", "other")
        related = [p for p in categories.get(category, []) if p["slug"] != plugin["slug"]][:4]

        context = {
            "plugin": plugin,
            "related_plugins": related,
            "generated_at": datetime.now(UTC).isoformat(),
        }

        output_path = OUTPUT_DIR / "plugins" / f"{plugin['slug']}.html"
        render_template(env, "plugin.html", context, output_path)


def generate_category_pages(env: Environment, plugins: list[dict]):
    """Generate category listing pages."""
    categories = group_by_category(plugins)

    for category, cat_plugins in categories.items():
        context = {
            "category": category,
            "category_info": get_category_info(category),
            "plugins": sort_plugins(cat_plugins, "stars"),
            "total_plugins": len(cat_plugins),
            "all_categories": sorted(categories.keys()),
            "generated_at": datetime.now(UTC).isoformat(),
        }

        output_path = OUTPUT_DIR / "categories" / f"{category}.html"
        render_template(env, "category.html", context, output_path)

    # Generate categories index
    context = {
        "categories": {cat: len(items) for cat, items in sorted(categories.items())},
        "total_plugins": len(plugins),
        "generated_at": datetime.now(UTC).isoformat(),
    }
    render_template(env, "categories_index.html", context, OUTPUT_DIR / "categories" / "index.html")


def generate_all_plugins_page(env: Environment, plugins: list[dict]):
    """Generate the all plugins listing page."""
    categories = group_by_category(plugins)

    context = {
        "plugins": sort_plugins(plugins, "stars"),
        "total_plugins": len(plugins),
        "categories": sorted(categories.keys()),
        "category_counts": {cat: len(items) for cat, items in categories.items()},
        "generated_at": datetime.now(UTC).isoformat(),
    }

    render_template(env, "all_plugins.html", context, OUTPUT_DIR / "plugins" / "index.html")


def generate_data_files(plugins: list[dict]):
    """Generate JSON data files for client-side search."""
    data_dir = OUTPUT_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Full plugins data
    plugins_file = data_dir / "plugins.json"
    with plugins_file.open("w") as f:
        json.dump(plugins, f, indent=2)
    print("  Generated: docs/data/plugins.json")

    # Search index (lightweight version for client-side search)
    search_data = [
        {
            "slug": p["slug"],
            "name": p["name"],
            "description": p["description"],
            "category": p.get("category", "other"),
            "author": p.get("author_name", ""),
            "stars": p.get("github_stars", 0),
            "verified": p.get("is_verified", False),
        }
        for p in plugins
    ]
    search_file = data_dir / "search-index.json"
    with search_file.open("w") as f:
        json.dump(search_data, f)
    print("  Generated: docs/data/search-index.json")


def copy_static_assets():
    """Copy static assets to output directory."""
    static_src = TEMPLATES_DIR / "static"
    static_dest = OUTPUT_DIR / "static"

    if static_src.exists():
        if static_dest.exists():
            shutil.rmtree(static_dest)
        shutil.copytree(static_src, static_dest)
        print("  Copied static assets to docs/static/")


def generate_site():
    """Main function to generate the entire static site."""
    print("\n=== PlugPack Static Site Generator ===\n")

    # Load data
    plugins = load_plugins()
    if not plugins:
        print("No plugins found. Exiting.")
        return

    # Clean output directory
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    print(f"Output directory: {OUTPUT_DIR}\n")

    # Set up Jinja
    env = setup_jinja_env()

    # Generate pages
    print("Generating pages...")
    generate_index(env, plugins)
    generate_all_plugins_page(env, plugins)
    generate_plugin_pages(env, plugins)
    generate_category_pages(env, plugins)

    # Generate data files
    print("\nGenerating data files...")
    generate_data_files(plugins)

    # Copy static assets
    print("\nCopying assets...")
    copy_static_assets()

    # Generate .nojekyll for GitHub Pages
    (OUTPUT_DIR / ".nojekyll").touch()
    print("  Generated: docs/.nojekyll")

    print(f"\n=== Done! Generated {len(plugins)} plugin pages ===")
    print("Preview locally: python -m http.server -d docs 8080")
    print("Then open: http://localhost:8080\n")


if __name__ == "__main__":
    generate_site()
