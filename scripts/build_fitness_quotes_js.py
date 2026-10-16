"""Genera el módulo local que consume la rutina autocontenida."""

from pathlib import Path
import json


root = Path(__file__).resolve().parents[1]
target = root / "data" / "rutinas_autocontenidas" / "frases_fitness" / "fitness_quotes.js"
MAX_QUOTE_LENGTH = 220
EDITORIAL_QUOTES = (
    "Una repetición controlada vale más que una repetición hecha con prisa.",
    "La técnica se mantiene también cuando aumenta la carga.",
    "Registra cada serie: el progreso se construye con constancia.",
    "Entrena con intención y descansa para volver a rendir.",
    "No persigas el peso de otra persona; construye tu siguiente paso.",
    "Hoy no hace falta un récord: hace falta una serie bien hecha.",
    "Controla la bajada. Gana cada centímetro del recorrido.",
    "Aumenta la carga solo cuando puedas repetir la técnica.",
    "El descanso también forma parte de tu entrenamiento.",
    "La fuerza se construye con esfuerzo y ejecución consistente.",
    "Calidad en cada repetición; progreso sesión tras sesión.",
    "Una carga adecuada te reta sin obligarte a compensar.",
    "Vuelve a intentarlo con control, no con impulso.",
    "Tu mejor referencia es tu propio registro.",
    "La siguiente repetición empieza con una buena postura.",
    "Entrena fuerte. Muévete con control.",
    "La paciencia también cuenta entre una sesión y otra.",
    "Una serie a la vez, con atención en cada movimiento.",
    "Técnica sólida hoy; progreso sostenible mañana.",
    "No tienes que impresionar a nadie: completa bien tu serie.",
    "Respeta el recorrido y deja que la fuerza se acumule.",
    "Cada entrenamiento suma cuando cuidas la ejecución.",
    "La constancia pesa más que la prisa.",
    "Haz que cada serie tenga un propósito.",
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
def compact_payload() -> dict:
    """Publish original strength-training messages plus only source-backed external quotes."""
    selected = [
        {
            "author": "Gymratik",
            "quoteEs": quote,
            "authorContext": "Entrenamiento de fuerza · mensaje original",
        }
        for quote in EDITORIAL_QUOTES
    ]
    if any(not quote or len(quote) > MAX_QUOTE_LENGTH for quote in EDITORIAL_QUOTES):
        raise ValueError("Cada frase editorial debe ser no vacía y caber en el espacio de la tarjeta")
    arnold = [
        {
            **item,
            "portrait": ARNOLD_PORTRAIT,
            "photoSourceUrl": ARNOLD_PHOTO_SOURCE,
            "photoCredit": ARNOLD_PHOTO_CREDIT,
        }
        for item in ARNOLD_QUOTES
    ]
    for item, position in zip(arnold, (6, 15, 24), strict=True):
        selected.insert(position, item)
    return {"schemaVersion": 1, "language": "es", "count": len(selected), "quotes": selected}


def main() -> None:
    payload = compact_payload()
    target.write_text(
        "window.fitnessQuotesData = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"QUOTES_JS_OK quotes={payload['count']} authors={len({item['author'] for item in payload['quotes']})} bytes={target.stat().st_size} output={target}")


if __name__ == "__main__":
    main()
