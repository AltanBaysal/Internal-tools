"""SageAttention for ComfyUI, on the cards that can run it (madde 409).

The owner's trial: a CONFIG box, ticked by default, to be taken out again if it does not pay ("iyi
çalışmıyorsa silicem"). It changes what comes out. SDXL's attention and WAN's run through it, so a
photo or a WAN video from the same seed comes out very close to, not the same as, one made without
it. H3's graphs pick their own attention backend, and MMAudio runs outside ComfyUI.
"""
import subprocess

from colab.console import log, run

# The build PyPI holds: a 20 kB wheel of Triton kernels that leaves torch alone. 2.x is not on PyPI,
# and would be compiled from source on every fresh machine.
PACKAGE = "sageattention==1.0.6"

# Ampere and later, the cards the kernels are written for: A100 is 8.0, L4 8.9, H100 9.0; a T4 is 7.5.
LOWEST = 8.0


def sage_attention_flags(wanted):
    """What ComfyUI's command gets on top of today's: --use-sage-attention, or nothing.

    The flag comes only after pip said yes. Given it without the package, ComfyUI exits while it
    starts (comfy/ldm/modules/attention.py), so a failed install costs the speed-up and never the
    session."""
    if not wanted:
        log("SageAttention: atlandı (SAGE_ATTENTION kapalı)")
        return []
    card = subprocess.run(["nvidia-smi", "--query-gpu=name,compute_cap", "--format=csv,noheader"],
                          capture_output=True, text=True)
    name, capability = card.stdout.strip().rsplit(", ", 1)
    if float(capability) < LOWEST:
        log(f"SageAttention: atlandı — {name}, compute capability {capability} "
            f"(en az {LOWEST} gerekiyor)")
        return []
    log(f"SageAttention kuruluyor — {name}, compute capability {capability}…")
    try:
        run(["pip", "install", PACKAGE], "pip install sageattention", timeout=300)
    except RuntimeError as failure:
        log(f"SageAttention kurulamadı — ComfyUI onsuz başlayacak:\n{failure}", "WARN")
        return []
    log("SageAttention kuruldu — ComfyUI --use-sage-attention ile başlayacak", "OK")
    return ["--use-sage-attention"]
