"""Which model files each producer needs, by folder and name -- or by folder and kind.

A **reading** list, not an installing one: the app never downloads a model. Where the files come
from and how they are fetched is the notebook's business (FOUNDATION 9), and the addresses live
there so that two places never claim to know them. What this file answers is the one question the
app still asks -- is this producer's group on the machine?

A row has one of two shapes, and which one says what it is asking:
  {"folder", "name"}   -- exactly this file, because the graph loads it by that name
  {"folder", "suffix"} -- any file of this kind, because which one is the user's pick

The names are inherited from collab-toolbox as knowledge, not as a dependency: they are the names
the graphs load by, so a rename here has to follow the graph rather than the source.
"""
HF_MMAUDIO_NSFW = "mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors"

GROUPS = {
    # What the photo graph reads. The checkpoint and the loras are the render itself, and Remacri
    # is read by the bypassed Ultimate SD Upscale the moment it is switched on. The graph runs no
    # detailer (madde 430), so no detector and no SAM is counted.
    "photo": [
        # Which checkpoint is here is the user's pick since Madde 140 -- the notebook draws a box
        # per model and every one of them is empty by default. So the row names a kind rather than
        # a file: the graph renders with whichever it was handed, and the panel asks whether there
        # is anything to hand it. Naming one made the panel call the producer uninstalled for
        # anyone who picked a different model.
        {"folder": "checkpoints", "suffix": ".safetensors"},
        # Both loras come down whichever models were ticked: either can go over any model, and
        # hanging the panel's count on the choice would make "installed" mean a different set of
        # files on every machine.
        {"folder": "loras", "name": "USNR_STYLE_ILL_V1_lokr3-000024.safetensors"},
        {"folder": "loras", "name": "translucent_penetration_v5.safetensors"},
        {"folder": "upscale_models", "name": "4x_foolhardy_Remacri.pth"},
    ],
    # What the MiniMax H3 graphs read (madde 243), the one video model since madde 435. MiniMaxH3/ is
    # part of the name rather than of the folder: the graph's loaders ask for "MiniMaxH3/<file>", and
    # that is also where the file sits.
    "video": [
        {"folder": "diffusion_models",
         "name": "MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors"},
        {"folder": "text_encoders", "name": "qwen3vl_32b_minimax_h3_int4_convrot.safetensors"},
        {"folder": "vae", "name": "MiniMaxH3/minimax_h3_video_vae_int8_convrot.safetensors"},
        {"folder": "vae", "name": "MiniMaxH3/minimax_h3_audio_vae_fp32.safetensors"},
        # The preview the graph samples through; a model node in its chain, so a render needs it too.
        {"folder": "vae_approx", "name": "taeh3.safetensors"},
        # Inside the lora stack's JSON, where a scan for model names cannot see it.
        {"folder": "loras", "name": "H3_Motion_BoosterV2.safetensors"},
    ],
    "audio": [
        # The fine-tune the sampler loads. MMAudio's own vae, synchformer and vocoder come down
        # with the library, which knows where it keeps them. This one sits in ComfyUI's model tree
        # although ComfyUI never reads it -- the panel and the sampler both hang off that root, and
        # a second root for a single file would be the same knowledge written twice.
        {"folder": "mmaudio", "name": HF_MMAUDIO_NSFW},
    ],
}


def audio_weights(files):
    """Where the sound weights sit, built from the row above rather than spelled out a second time:
    a renamed file then moves the panel and the sampler together."""
    row = GROUPS["audio"][0]
    return files.path(row["folder"], row["name"])
