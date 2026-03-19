#!/usr/bin/env python3
"""
recipe-formatter.py — Converts raw grep/text output into professional Markdown recipes.
Usage: python3 recipe-formatter.py <input_file> <output_file>
"""

import re
import sys
from pathlib import Path

# --- Dish type classification ---
DISH_GROUPS = {
    "Suppen & Eintöpfe": [
        r"suppe", r"eintopf", r"brühe", r"bouillon", r"chowder", r"bisque", r"minestrone",
    ],
    "Braten & Fleisch": [
        r"braten", r"schmorbraten", r"schmorbrat", r"gulasch", r"kotelett", r"steak",
        r"roastbeef", r"lammkeule", r"schweinebraten", r"rinderbraten",
    ],
    "Geflügel": [
        r"huhn", r"hähnchen", r"hühnchen", r"pute", r"ente", r"gans", r"geflügel",
    ],
    "Fisch & Meeresfrüchte": [
        r"fisch", r"lachs", r"forelle", r"thunfisch", r"garnelen", r"meeresfrüchte",
        r"calamari", r"muscheln",
    ],
    "Pasta & Getreide": [
        r"pasta", r"nudeln", r"spaghetti", r"risotto", r"reis", r"couscous",
        r"gnocchi", r"lasagne", r"penne",
    ],
    "Gemüse & Salate": [
        r"salat", r"gemüse", r"vegan", r"vegetarisch", r"ratatouille", r"gratin",
    ],
    "Backen & Desserts": [
        r"kuchen", r"torte", r"tarte", r"dessert", r"pudding", r"mousse",
        r"eis", r"sorbet", r"cookie", r"muffin", r"brot", r"brötchen",
    ],
    "Soßen & Beilagen": [
        r"soße", r"sauce", r"dip", r"marinade", r"dressing", r"chutney",
        r"beilage", r"püree",
    ],
}


def classify_dish(title: str) -> str:
    title_lower = title.lower()
    for group, patterns in DISH_GROUPS.items():
        if any(re.search(p, title_lower) for p in patterns):
            return group
    return "Sonstige Gerichte"


def parse_recipes(text: str) -> list[dict]:
    """Parse one or more recipes from raw text. Returns list of recipe dicts."""
    recipes = []

    # Split on recipe boundaries: "rezept:", "## Rezept", blank-line separated blocks
    blocks = re.split(
        r"(?mi)(?=^(?:rezept|##\s*rezept|\*\*rezept\*\*)[\s:]+)",
        text,
    )

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        recipe = _parse_block(block)
        if recipe and recipe.get("title"):
            recipes.append(recipe)

    return recipes


def _parse_block(text: str) -> dict:
    """Parse a single recipe block into a structured dict."""
    lines = [l.rstrip() for l in text.splitlines()]
    recipe: dict = {
        "title": "",
        "portions": "",
        "time": "",
        "ingredients": [],
        "steps": [],
        "source": "",
        "raw_lines": [],
    }

    mode = "header"  # header | ingredients | steps

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # --- Title ---
        m = re.match(r"(?i)^(?:##\s*)?(?:\*\*)?rezept[:\s*]+(.+?)(?:\*\*)?$", stripped)
        if m:
            recipe["title"] = m.group(1).strip().strip("*")
            mode = "header"
            continue

        # --- Portionen ---
        m = re.match(r"(?i)^portionen?[:\s]+(\d+)", stripped)
        if m:
            recipe["portions"] = m.group(1)
            continue

        # --- Zeit ---
        m = re.match(r"(?i)^(?:zeit|zubereitungszeit|kochzeit)[:\s]+(\d+)\s*(?:min(?:uten?)?|std|h)?", stripped)
        if m:
            recipe["time"] = m.group(1)
            continue

        # --- Quelle / Datei ---
        m = re.match(r"(?i)^(?:quelle|datei|file|source)[:\s]+(.+)$", stripped)
        if m:
            recipe["source"] = m.group(1).strip()
            continue

        # --- Section headers ---
        if re.match(r"(?i)^zutaten[:\s]*$", stripped):
            mode = "ingredients"
            continue
        if re.match(r"(?i)^(?:anleitung|zubereitung|schritte)[:\s]*$", stripped):
            mode = "steps"
            continue

        # --- Ingredients: lines starting with - or * or number+unit patterns ---
        if mode == "ingredients":
            cleaned = re.sub(r"^[-*•]\s*", "", stripped)
            if cleaned:
                recipe["ingredients"].append(cleaned)
            continue

        # --- Steps: numbered lines ---
        if mode == "steps":
            m = re.match(r"^(\d+)[.)]\s*(.+)$", stripped)
            if m:
                recipe["steps"].append(m.group(2).strip())
            elif stripped:
                recipe["steps"].append(stripped)
            continue

        # --- Auto-detect ingredient lines (outside explicit sections) ---
        if re.match(r"^[-*•]\s+\S", stripped) and mode == "header":
            cleaned = re.sub(r"^[-*•]\s*", "", stripped)
            recipe["ingredients"].append(cleaned)
            continue

        # --- Auto-detect numbered steps (outside explicit sections) ---
        if re.match(r"^\d+[.)]\s+\S", stripped) and mode == "header":
            m = re.match(r"^\d+[.)]\s+(.+)$", stripped)
            if m:
                recipe["steps"].append(m.group(1).strip())
            continue

        recipe["raw_lines"].append(stripped)

    return recipe


def format_recipe(recipe: dict) -> str:
    """Render a recipe dict as Markdown."""
    lines = []
    title = recipe["title"] or "Unbekanntes Gericht"

    lines.append(f"## Rezept: {title}")
    lines.append("")

    meta = []
    if recipe["portions"]:
        meta.append(f"👥 {recipe['portions']} Portionen")
    if recipe["time"]:
        meta.append(f"⏱️ {recipe['time']} Min")
    if meta:
        lines.append(" | ".join(meta))
        lines.append("")

    if recipe["ingredients"]:
        lines.append("**Zutaten:**")
        for ing in recipe["ingredients"]:
            lines.append(f"- [ ] {ing}")
        lines.append("")

    if recipe["steps"]:
        lines.append("**Anleitung:**")
        for i, step in enumerate(recipe["steps"], 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    if recipe["source"]:
        lines.append(f"*Quelle: {recipe['source']}*")
        lines.append("")

    return "\n".join(lines)


def build_document(recipes: list[dict], source_hint: str = "") -> str:
    """Assemble a full Markdown document, grouped by dish type."""
    if not recipes:
        return "<!-- Keine Rezepte gefunden -->\n"

    # Apply source hint if not set per recipe
    for r in recipes:
        if not r["source"] and source_hint:
            r["source"] = source_hint

    # Group by dish type
    groups: dict[str, list[dict]] = {}
    for r in recipes:
        group = classify_dish(r["title"])
        groups.setdefault(group, []).append(r)

    doc_lines = [
        "# Rezeptsammlung",
        "",
        f"> {len(recipes)} Rezept(e) gefunden",
        "",
        "---",
        "",
    ]

    for group, group_recipes in groups.items():
        doc_lines.append(f"# {group}")
        doc_lines.append("")
        for recipe in group_recipes:
            doc_lines.append(format_recipe(recipe))
            doc_lines.append("---")
            doc_lines.append("")

    doc_lines += [
        "---",
        "",
        "*Automatisch formatiert von recipe-formatter.py*",
    ]

    return "\n".join(doc_lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 recipe-formatter.py <input_file> <output_file>", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        text = input_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)

    recipes = parse_recipes(text)

    if not recipes:
        print("Warning: No recipes detected in input.", file=sys.stderr)

    source_hint = input_path.stem
    document = build_document(recipes, source_hint=source_hint)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(document, encoding="utf-8")
        print(f"✓ {len(recipes)} Rezept(e) → {output_path}")
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
