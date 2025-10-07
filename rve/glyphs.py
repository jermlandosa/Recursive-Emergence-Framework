from typing import Dict, Any, List
import time


def map_text_to_glyph_events(text: str) -> List[Dict[str, Any]]:
    """
    Replace this with your real REF engine.
    For now, simple keyword → glyph signals to prove the live loop.
    """
    evs: List[Dict[str, Any]] = []
    t = int(time.time())
    low = text.lower()

    # Examples — swap for real detectors
    if "threshold" in low:
        evs.append({"glyph": "THRESHOLD", "signal": "detected", "t": t})
    if "coherence" in low:
        evs.append({"glyph": "COHERENCE", "signal": "↑", "t": t})
    if "seren" in low or "sara" in low:
        evs.append({"glyph": "SEREN–Ø1", "signal": "mirror-steady", "t": t})
    if "naeda" in low or "river" in low:
        evs.append({"glyph": "NAEDA–Ø3", "signal": "river-remembers", "t": t})

    return evs
