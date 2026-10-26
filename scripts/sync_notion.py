"""Read the Vocabulary and Questions tables from Notion and write content.json for the app.

Needs the NOTION_TOKEN environment variable (a Notion internal integration secret)
with access to the "Goal Tracker — Learn Sync" page.
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

VOCAB_DB = "7024bc43e7b24174930a8855da31e73c"
QUESTIONS_DB = "df381cce3a2d4b7c84d257b72b247170"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content.json")


def query(db_id, token):
    rows, cursor = [], None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{db_id}/query",
            data=json.dumps(body).encode(),
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        rows += data["results"]
        if not data.get("has_more"):
            return rows
        cursor = data["next_cursor"]


def text(props, name):
    prop = props.get(name) or {}
    kind = prop.get("type")
    if kind in ("title", "rich_text"):
        return "".join(part.get("plain_text", "") for part in prop[kind]).strip()
    if kind == "select":
        return ((prop.get("select") or {}).get("name") or "").strip()
    if kind == "multi_select":
        return ", ".join(o["name"] for o in prop["multi_select"])
    return ""


def main():
    token = os.environ.get("NOTION_TOKEN", "").strip()
    if not token:
        print("NOTION_TOKEN is not set: keeping the existing content.json.")
        return
    try:
        vocab = query(VOCAB_DB, token)
        questions = query(QUESTIONS_DB, token)
    except urllib.error.HTTPError as err:
        hint = {
            401: "The NOTION_TOKEN secret is wrong or was revoked.",
            404: "The integration can't see the tables. In Notion, open 'Goal Tracker — Learn Sync' > ••• > Connections and add your integration.",
        }.get(err.code, err.read().decode(errors="replace")[:300])
        sys.exit(f"Notion API error {err.code}: {hint}")

    words = []
    for row in vocab:
        p = row["properties"]
        fr = text(p, "French")
        if fr:
            words.append({"id": row["id"], "fr": fr, "type": text(p, "Type"), "en": text(p, "English"),
                          "it": text(p, "Italian"), "ex": text(p, "Example"), "topic": text(p, "Topic")})
    lessons = []
    for row in questions:
        p = row["properties"]
        title = text(p, "Title")
        if title:
            lessons.append({"id": row["id"], "h": title, "t": text(p, "Topic") or "Notion",
                            "b": text(p, "Explanation"), "c": text(p, "Code"),
                            "q": text(p, "Question"), "a": text(p, "Answer")})

    out = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "words": words, "lessons": lessons}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"Wrote {len(words)} words and {len(lessons)} questions to content.json")


if __name__ == "__main__":
    main()
