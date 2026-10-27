"""Load a brand pack: brands/<client>/DESIGN.md front matter -> tokens, CSS variables, rule files."""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def load(client):
    d = ROOT / "brands" / client
    text = (d / "DESIGN.md").read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError(f"{d}/DESIGN.md has no YAML front matter")
    tokens = yaml.safe_load(m.group(1))
    tokens["dir"] = d
    tokens["critic_rules"] = [p for p in (d / "critic_rules.md", ROOT / "skill/critic_rules.md") if p.exists()]
    return tokens


def css_vars(tokens):
    """Flatten colors/rounded/spacing/typography into :root custom properties."""
    out = [f"--color-{k}: {v};" for k, v in tokens.get("colors", {}).items()]
    out += [f"--radius-{k}: {v};" for k, v in tokens.get("rounded", {}).items()]
    out += [f"--space-{k}: {v};" for k, v in tokens.get("spacing", {}).items()]
    for name, t in tokens.get("typography", {}).items():
        out += [f"--font-{name}-family: '{t['fontFamily']}';", f"--font-{name}-size: {t['fontSize']};",
                f"--font-{name}-weight: {t['fontWeight']};", f"--font-{name}-line: {t.get('lineHeight', 1.3)};"]
    return ":root {\n  " + "\n  ".join(out) + "\n}"


def palette(tokens):
    """Hex colours (6-digit, alpha dropped) the brand allows, by token name."""
    return {k: v[:7].upper() for k, v in tokens.get("colors", {}).items() if str(v).startswith("#")}
