# diagram-picture-renamer — prima versione

Questo repository contiene una prima versione di uno strumento CLI che analizza un'immagine e restituisce un titolo e parole chiave (keywords) associate.

Principali punti:
- Linguaggio: Python
- CLI: `typer`
- Analisi immagine: Pillow + (opzionale) OCR con `pytesseract`
- Integrazione LLM: opzionale via OpenAI (se configurato)

Installazione (macOS, zsh):

Questo progetto usa `uv` per gestire l'ambiente e sincronizzare le dipendenze.

Prerequisiti:
- Python 3.10+
- `uv` installato (ad esempio via pip o pipx)

Installazione dipendenze:

```bash
# installa uv (se non è già disponibile)
pip install uv

# dalla root del repository: sincronizza l'ambiente e installa le dipendenze
uv sync
```

Nota: `uv sync` crea/sincronizza l'ambiente di lavoro e installerà i pacchetti elencati in `requirements.txt`.
Dopo `uv sync` puoi attivare l'ambiente creato (se presente) o eseguire direttamente il comando Python desiderato usando l'ambiente; ad esempio, per usare il CLI come prima:

```bash
# se uv ha creato una directory .venv puoi attivarla così (opzionale)
source .venv/bin/activate
python -m src.main analyze path/to/image.png
```


Uso:

```bash
python -m src.main analyze path/to/image.png
```

Esempio di output (JSON su stdout):

{
  "title": "Architecture_ServiceMesh_20251115",
  "keywords": ["service", "mesh", "diagram", "blue", "network"]
}

Note:
- Se `OPENAI_API_KEY` è impostata e `OPENAI_MODEL` definito, il tool proverà a usare l'LLM per migliorare titolo e keyword.
- In assenza di LLM, si usa una logica locale basata su OCR (se disponibile) e colori dominanti.
