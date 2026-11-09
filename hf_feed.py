"""Build feed.xml: newest model repos from a watchlist of Hugging Face orgs."""
import datetime as dt
import json
import urllib.request
from xml.sax.saxutils import escape

ORGS = ["Qwen", "mistralai", "allenai", "deepseek-ai", "zai-org", "moonshotai",
        "NousResearch", "google", "meta-llama", "microsoft", "nvidia"]
PER_ORG = 15      # newest repos pulled per org
KEEP = 100        # items kept in the feed


def newest(org):
    url = (f"https://huggingface.co/api/models?author={org}"
           f"&sort=createdAt&direction=-1&limit={PER_ORG}")
    req = urllib.request.Request(url, headers={"User-Agent": "hf-feed/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def rfc822(iso):
    d = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return d.strftime("%a, %d %b %Y %H:%M:%S +0000")


models = [m for org in ORGS for m in newest(org)]
models.sort(key=lambda m: m["createdAt"], reverse=True)

items = []
for m in models[:KEEP]:
    link = f"https://huggingface.co/{m['id']}"
    tags = ", ".join(t for t in m.get("tags", []) if ":" not in t)[:300]
    body = f"{m.get('pipeline_tag') or 'no pipeline tag'} · {tags}"
    items.append(
        "<item>"
        f"<title>{escape(m['id'])}</title>"
        f"<link>{escape(link)}</link>"
        f"<guid>{escape(link)}</guid>"
        f"<pubDate>{rfc822(m['createdAt'])}</pubDate>"
        f"<description>{escape(body)}</description>"
        "</item>"
    )

feed = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<rss version="2.0"><channel>'
    "<title>HF watchlist: new models</title>"
    "<link>https://huggingface.co</link>"
    f"<description>Newest repos from {escape(', '.join(ORGS))}</description>"
    + "".join(items) +
    "</channel></rss>\n"
)
open("feed.xml", "w", encoding="utf-8").write(feed)
print(f"wrote feed.xml with {len(items)} items")
