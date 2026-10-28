"""Download the wikitext of every collectible page from the Isaac wiki.

Output: data/raw/wiki_pages.json, a list of {"title", "pageid", "revid", "wikitext"}.
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://bindingofisaacrebirth.wiki.gg/api.php"
OUT = Path(__file__).resolve().parent.parent / "data" / "raw" / "wiki_pages.json"
USER_AGENT = "tboi-tearstest/0.1 (https://github.com/MerrymanLyon/tboi-tearstest)"


def api_get(params):
    params = {**params, "format": "json", "formatversion": "2"}
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except OSError:
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))


def category_members(category):
    titles = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category,
        "cmtype": "page",
        "cmnamespace": "0",
        "cmlimit": "500",
    }
    while True:
        data = api_get(params)
        titles += [m["title"] for m in data["query"]["categorymembers"]]
        if "continue" not in data:
            return titles
        params.update(data["continue"])


def page_contents(titles):
    pages = []
    for i in range(0, len(titles), 50):
        data = api_get({
            "action": "query",
            "prop": "revisions",
            "rvprop": "ids|content",
            "rvslots": "main",
            "redirects": "1",
            "titles": "|".join(titles[i:i + 50]),
        })
        for p in data["query"]["pages"]:
            if "revisions" not in p:
                continue
            rev = p["revisions"][0]
            pages.append({
                "title": p["title"],
                "pageid": p["pageid"],
                "revid": rev["revid"],
                "wikitext": rev["slots"]["main"]["content"],
            })
        time.sleep(1)
    return sorted(pages, key=lambda p: p["title"])


def main():
    titles = category_members("Category:Collectibles")
    print(f"{len(titles)} pages in Category:Collectibles")
    pages = page_contents(titles)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(pages, ensure_ascii=False, indent=1))
    print(f"Saved {len(pages)} pages to {OUT}")


if __name__ == "__main__":
    main()
