"""Genera el módulo local que consume la rutina autocontenida."""

from pathlib import Path
import json


root = Path(__file__).resolve().parents[1]
source = root / "data" / "rutinas_autocontenidas" / "frases_fitness" / "fitness_quotes.json"
target = root / "data" / "rutinas_autocontenidas" / "frases_fitness" / "fitness_quotes.js"
MAX_RUNTIME_QUOTES = 120
MAX_QUOTE_LENGTH = 220
ARNOLD_QUOTES = (
    {
        "quoteEs": "No esperes a tener ganas. Empieza: la acción crea la motivación; cada repetición la fortalece.",
        "author": "Arnold Schwarzenegger",
        "authorContext": "Arnold's Pump Club · traducción al español",
        "sourceUrl": "https://www.schwarzenegger.com/fitness/post/you-dont-have-to-feel-like-it",
    },
    {
        "quoteEs": "El trabajo duro funciona. La constancia funciona.",
        "author": "Arnold Schwarzenegger",
        "authorContext": "Arnold's Pump Club · traducción al español",
        "sourceUrl": "https://www.schwarzenegger.com/fitness/post/build-a-foundation-that-no-one-can-tear-down",
    },
    {
        "quoteEs": "No esperes a que llegue la motivación; sal a buscarla.",
        "author": "Arnold Schwarzenegger",
        "authorContext": "Arnold's Pump Club · traducción al español",
        "sourceUrl": "https://www.schwarzenegger.com/index.php/fitness/post/the-spark",
    },
)
ARNOLD_PORTRAIT = "retratos/arnold-schwarzenegger-eu-2026.jpg"
ARNOLD_PHOTO_SOURCE = "https://commons.wikimedia.org/wiki/File:Arnold_Schwarzenegger_in_2026.jpg"
ARNOLD_PHOTO_CREDIT = "Alex Halada / Unión Europea, 2026 · CC BY 4.0"


def compact_payload(data: dict) -> dict:
    """Keep a small, photo-backed, author-diverse offline rotation for the PWA."""
    selected: list[dict[str, str]] = []
    seen_authors: set[str] = set()
    for item in data.get("quotes", []):
        author = str(item.get("author", "")).strip()
        quote = str(item.get("quoteEs", "")).strip()
        portrait = str(item.get("portrait", "")).strip()
        portrait_file = root / "data" / "rutinas_autocontenidas" / "frases_fitness" / portrait
        if (
            not author
            or not quote
            or len(quote) > MAX_QUOTE_LENGTH
            or author in seen_authors
            or "arnold" in author.lower()
            or not portrait
            or not portrait_file.is_file()
        ):
            continue
        seen_authors.add(author)
        compact = {"author": author, "quoteEs": quote, "portrait": portrait}
        context = str(item.get("authorContext", "")).strip()
        if context:
            compact["authorContext"] = context[:100]
        selected.append(compact)
        if len(selected) == MAX_RUNTIME_QUOTES - len(ARNOLD_QUOTES):
            break
    if len(selected) < MAX_RUNTIME_QUOTES - len(ARNOLD_QUOTES):
        raise ValueError(f"El banco solo permite {len(selected)} frases breves de autores con foto; se requieren {MAX_RUNTIME_QUOTES - len(ARNOLD_QUOTES)}")
    arnold = [
        {
            **item,
            "portrait": ARNOLD_PORTRAIT,
            "photoSourceUrl": ARNOLD_PHOTO_SOURCE,
            "photoCredit": ARNOLD_PHOTO_CREDIT,
        }
        for item in ARNOLD_QUOTES
    ]
    for item, position in zip(arnold, (24, 64, 104), strict=True):
        selected.insert(position, item)
    return {"schemaVersion": 1, "language": "es", "count": len(selected), "quotes": selected}


def main() -> None:
    payload = compact_payload(json.loads(source.read_text(encoding="utf-8")))
    target.write_text(
        "window.fitnessQuotesData = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"QUOTES_JS_OK quotes={payload['count']} authors={len({item['author'] for item in payload['quotes']})} bytes={target.stat().st_size} output={target}")


if __name__ == "__main__":
    main()
