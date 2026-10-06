"""Genera el módulo local que consume la rutina autocontenida."""

from pathlib import Path
import json
import re


root = Path(__file__).resolve().parents[1]
source = root / "data" / "rutinas_autocontenidas" / "frases_fitness" / "fitness_quotes.json"
target = root / "data" / "rutinas_autocontenidas" / "frases_fitness" / "fitness_quotes.js"
MAX_RUNTIME_QUOTES = 60
MAX_QUOTE_LENGTH = 220
PHYSICAL_FITNESS_TERMS = re.compile(
    r"\b(?:gym|gymnasium|workouts?|physical fitness|running|runner|run|swimming|swim|cycling|cyclist|bike|biking|"
    r"sports?|athlete|athletics|dance|dancing|yoga|cardio|marathon|bodybuilding|weightlifting|lifting weights|"
    r"physical exercise|exercise routine|walking|walk|gimnasio|rutina de ejercicio|ejercicio f[ií]sico|"
    r"correr|nataci[oó]n|ciclismo|deporte|m[uú]sculos? f[ií]sicos|levantamiento de pesas|pesas|atleta|"
    r"nadar|salud f[ií]sica|patinaje|patinar|surfear|tenis|voleibol|f[uú]tbol|b[aá]squetbol|baloncesto|"
    r"b[eé]isbol|golf|remo|rowing|esqu[ií]|escalar|senderismo|jogging|paddleboarding|sprint|sprinter|carrera)\b",
    flags=re.IGNORECASE,
)
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
OFF_TOPIC_MEDIA_CONTEXT = re.compile(r"\bmtv was such a great training\b", flags=re.IGNORECASE)
NON_PHYSICAL_CONTEXT = re.compile(r"\b(?:brain|imagination|leadership|sex without love|ps[aá]quic[oa]|psychiatr|vocal training)\b", flags=re.IGNORECASE)
SPORTS_SPECTATOR_CONTEXT = re.compile(
    r"\b(?:booing|boo|spectators?|football manager|f[uú]tbol de fantas[ií]a|fantasy sports?|"
    r"professional game|sporting event|game coverage|poker|jacket|tacones|clothes|ropa deportiva)\b",
    flags=re.IGNORECASE,
)


def compact_payload(data: dict) -> dict:
    """Keep a small, photo-backed, author-diverse offline rotation for the PWA."""
    selected: list[dict[str, str]] = []
    seen_authors: set[str] = set()
    for item in data.get("quotes", []):
        author = str(item.get("author", "")).strip()
        quote = str(item.get("quoteEs", "")).strip()
        source_quote = str(item.get("quoteOriginal", "")).strip()
        portrait = str(item.get("portrait", "")).strip()
        context = str(item.get("authorContext", "")).strip()
        portrait_file = root / "data" / "rutinas_autocontenidas" / "frases_fitness" / portrait
        if (
            not author
            or not quote
            or len(quote) > MAX_QUOTE_LENGTH
            or not PHYSICAL_FITNESS_TERMS.search(f"{quote} {source_quote}")
            or OFF_TOPIC_MEDIA_CONTEXT.search(f"{quote} {source_quote}")
            or NON_PHYSICAL_CONTEXT.search(f"{quote} {source_quote}")
            or SPORTS_SPECTATOR_CONTEXT.search(f"{quote} {source_quote}")
            or author in seen_authors
            or "arnold" in author.lower()
            or not portrait
            or not portrait_file.is_file()
        ):
            continue
        seen_authors.add(author)
        compact = {"author": author, "quoteEs": quote, "portrait": portrait}
        if context:
            compact["authorContext"] = context[:100]
        selected.append(compact)
        if len(selected) == MAX_RUNTIME_QUOTES - len(ARNOLD_QUOTES):
            break
    if len(selected) < 20:
        raise ValueError(f"El banco solo permite {len(selected)} frases ligadas explícitamente a actividad física; se requieren al menos 20")
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
