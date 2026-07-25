"""When does a batch stop? One pure decision, so changing the rule touches one file.

Inherited from api.ipynb: a model loader failure means every remaining render would hit the
identical error, so it stops immediately; a render-specific failure only costs that frame, and a
run that keeps failing is broken rather than unlucky.
"""

MAX_CONSECUTIVE = 3


def stop_reason(consecutive, infra):
    """(consecutive failures, infra flag) -> user-facing reason, or None to keep going."""
    if infra:
        return "Altyapı hatası (model yükleyici) — üretim durduruldu"
    if consecutive >= MAX_CONSECUTIVE:
        return f"Üst üste {MAX_CONSECUTIVE} render başarısız — üretim durduruldu"
    return None
