"""Extract structured item data from the downloaded wiki pages.

Keeps only content that applies to Repentance+, based on the wiki's DLC codes
(see https://bindingofisaacrebirth.wiki.gg/wiki/Template:Dlc).

Input:  data/raw/wiki_pages.json (from fetch_wiki.py)
Output: data/wiki_items.json
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN = ROOT / "data" / "raw" / "wiki_pages.json"
OUT = ROOT / "data" / "wiki_items.json"
WIKI = "https://bindingofisaacrebirth.wiki.gg/wiki/"

SECTION_NAMES = {
    "effects": {"effects", "effect"},
    "synergies": {"synergies", "syngergies", "combinations"},
    "interactions": {"interactions", "interaction"},
}

# Templates that link to a game entity: {{i|Name|dlc}}, {{c|Character}}, ...
ENTITY_TEMPLATES = {"i", "c", "e", "t", "tf", "p", "card", "pill", "rune", "curse", "s", "trinket", "chal", "ch"}
DLC_TOKEN = re.compile(r"(n?)(a\+|a|r\+|r)")
DLC_TAG = re.compile(r"\{\{\s*dlc\s*\|\s*([anr+]+)\s*\}\}", re.I)


def valid_in_rplus(code):
    """A DLC code is a list of range boundaries; 'n' closes a range.

    The range is still open in Repentance+ (the latest version) unless the
    last boundary is a negated one, e.g. 'nr' (removed in Repentance) or
    'anr+' (Afterbirth until Repentance+).
    """
    code = (code or "").strip().lower()
    if not code:
        return True
    tokens = DLC_TOKEN.findall(code)
    if not tokens or "".join(n + v for n, v in tokens) != code:
        return True  # unknown code: keep, it is shown with its raw text anyway
    return tokens[-1][0] != "n"


def strip_dlc_blocks(text):
    """Handle {{dlc+|code}} ... {{dlc-}} blocks, which can span several lines."""
    pattern = re.compile(r"\{\{\s*dlc\+\s*\|\s*([anr+]+)\s*\}\}(.*?)\{\{\s*dlc-\s*\}\}", re.I | re.S)
    while True:
        new = pattern.sub(lambda m: m.group(2) if valid_in_rplus(m.group(1)) else "", text)
        if new == text:
            return text
        text = new


def strip_dlc_inline(text):
    """Drop text that follows an invalid {{dlc|code}} tag, up to the next tag.

    Also handles {{dlc|code|content}}. Returns (text, starts_invalid).
    """
    text = re.sub(
        r"\{\{\s*dlc\s*\|\s*([anr+]+)\s*\|([^{}]*)\}\}",
        lambda m: m.group(2) if valid_in_rplus(m.group(1)) else "",
        text,
        flags=re.I,
    )
    parts = DLC_TAG.split(text)
    # parts = [before, code1, after1, code2, after2, ...]
    starts_invalid = not parts[0].strip() and len(parts) > 1 and not valid_in_rplus(parts[1])
    kept = [parts[0]]
    for code, segment in zip(parts[1::2], parts[2::2]):
        if valid_in_rplus(code):
            kept.append(segment)
    return "".join(kept), starts_invalid


def template_args(inner):
    args = [a.strip() for a in inner.split("|")]
    positional = [a for a in args[1:] if "=" not in a]
    named = dict(a.split("=", 1) for a in args[1:] if "=" in a)
    return args[0].strip().lower(), positional, {k.strip(): v.strip() for k, v in named.items()}


def head_entities(text):
    """Entities named before the first ':' of a synergy bullet, with their DLC code."""
    head = text.split(":", 1)[0] if re.search(r"\}\}\s*:", text) or ":" in text else ""
    found = []
    for inner in re.findall(r"\{\{([^{}]*)\}\}", head):
        name, pos, named = template_args(inner)
        if name in ENTITY_TEMPLATES and pos:
            dlc = named.get("dlc") or (pos[1] if len(pos) > 1 else "")
            found.append({"name": pos[0], "kind": "item" if name == "i" else name, "dlc": dlc})
    return found


def to_plain(text):
    """Turn wikitext into readable plain text."""
    text = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    text = re.sub(r"<math>(.*?)</math>", r"\1", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)

    def repl(m):
        name, pos, named = template_args(m.group(1))
        if name in ENTITY_TEMPLATES and pos:
            return pos[0]
        if name in {"transformation contribution"} and pos:
            return f"Counts towards the {pos[0]} transformation."
        if name in {"code"} and pos:
            return pos[0]
        return ""

    for _ in range(3):
        text = re.sub(r"\{\{([^{}]*)\}\}", repl, text)
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"'{2,}", "", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_bullets(section_text):
    """Parse a bulleted section into a tree of {raw, children}."""
    roots, stack = [], []
    for line in section_text.split("\n"):
        m = re.match(r"^(\*+)\s*(.*)$", line)
        if not m:
            if line.strip() and stack:
                stack[-1][1]["raw"] += " " + line.strip()
            continue
        depth, raw = len(m.group(1)), m.group(2)
        node = {"raw": raw, "children": []}
        while stack and stack[-1][0] >= depth:
            stack.pop()
        (stack[-1][1]["children"] if stack else roots).append(node)
        stack.append((depth, node))
    return roots


def filter_node(node, is_synergy, inherited_heads=None):
    """Return Repentance+ nodes for this bullet (a list: the bullet itself, or
    its valid children promoted when the bullet itself is invalid)."""
    raw = node["raw"]
    text, starts_invalid = strip_dlc_inline(raw)
    heads = head_entities(text) if is_synergy else []
    if is_synergy and heads:
        valid_heads = [h for h in heads if valid_in_rplus(h["dlc"])]
        heads_invalid = not valid_heads
    else:
        valid_heads, heads_invalid = [], False

    if starts_invalid or heads_invalid:
        # The bullet only applies to older versions. Keep children that are
        # explicitly tagged as valid for Repentance+ (e.g. "** {{dlc|r}} ...").
        promoted = []
        for child in node["children"]:
            m = DLC_TAG.match(child["raw"].strip())
            if m and valid_in_rplus(m.group(1)):
                promoted += filter_node(child, is_synergy, heads or inherited_heads)
        return promoted

    children = []
    for child in node["children"]:
        children += filter_node(child, is_synergy, valid_heads or inherited_heads)
    out = {"text": to_plain(text), "raw": raw}
    if is_synergy:
        out["with"] = [h["name"] for h in (valid_heads or inherited_heads or [])]
    out["children"] = children
    if not out["text"] and not children:
        return []
    return [out]


def sections(wikitext):
    found = {}
    parts = re.split(r"^==\s*([^=].*?)\s*==\s*$", wikitext, flags=re.M)
    for title, body in zip(parts[1::2], parts[2::2]):
        key = next((k for k, names in SECTION_NAMES.items() if title.strip().lower() in names), None)
        if key and key not in found:
            found[key] = body
    return found


def infobox(wikitext):
    m = re.search(r"\{\{\s*infobox (passive|activated) collectible\s*\n(.*?)\n\}\}", wikitext, re.S | re.I)
    if not m:
        return None
    fields = {}
    for line in m.group(2).split("\n"):
        f = re.match(r"^\s*\|\s*([a-z ]+?)\s*=\s*(.*)$", line)
        if f:
            fields[f.group(1)] = f.group(2).strip()
    fields["_type"] = m.group(1).lower()
    return fields


def extract(page):
    box = infobox(page["wikitext"])
    if not box:
        return None
    text = strip_dlc_blocks(page["wikitext"])
    secs = sections(text)
    item = {
        "id": int(box["id"]) if re.fullmatch(r"-?\d+", box.get("id", "")) else box.get("id"),
        "name": page["title"],
        "type": box["_type"],
        "quality": box.get("quality"),
        "tags": box.get("tags", "").split(),
        "dlc": box.get("dlc", ""),
        "available_in_rplus": valid_in_rplus(box.get("dlc", "")),
        "description": to_plain(box.get("description", "")),
        "source": WIKI + page["title"].replace(" ", "_"),
        "revid": page["revid"],
    }
    for key in SECTION_NAMES:
        nodes = []
        for node in parse_bullets(secs.get(key, "")):
            nodes += filter_node(node, key != "effects")
        item[key] = nodes
    return item


def main():
    pages = json.loads(IN.read_text())
    items = [i for i in (extract(p) for p in pages) if i]
    items.sort(key=lambda i: (i["id"] if isinstance(i["id"], int) else 10**6, i["name"]))
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1))
    print(f"Extracted {len(items)} items "
          f"({sum(not i['available_in_rplus'] for i in items)} not available in Repentance+) -> {OUT}")


if __name__ == "__main__":
    main()
