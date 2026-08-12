"""What each producer needs on disk, and where.

Knowledge inherited from collab-toolbox, not a dependency on it: the names and addresses are copied
into our own file, so that folder can change without changing ours (CODE-STANDARD's independence
rule).

Two kinds of entry appear here:
  * a file with a `url` -- the app fetches it,
  * a file with `url: None` -- it needs credentials the app has no place for, so the notebook's
    setup cell installs it. The installer stops when it reaches one and says so, because a group
    half installed in silence would read as installed the next time anybody looked.

An empty group means the producer does not answer for itself through files at all: the photo
producer is set up by the notebook, and which checkpoint it holds is the user's own choice.
"""
HF_WAN22 = "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files"
HF_WAN21 = "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files"
HF_MMAUDIO_NSFW = "mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors"

GROUPS = {
    "photo": [],
    "video": [
        # The name is what the graph's VAELoader asks for, which is not what the file is called at
        # the source: ComfyUI looks the model up by its name on disk, so it lands under that one.
        {"folder": "vae", "name": "Wan2_1_VAE_fp32.safetensors",
         "url": f"{HF_WAN21}/vae/wan_2.1_vae.safetensors"},
        {"folder": "text_encoders", "name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
         "url": f"{HF_WAN21}/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"},
        {"folder": "loras", "name": "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
         "url": f"{HF_WAN22}/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"},
        {"folder": "loras", "name": "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",
         "url": f"{HF_WAN22}/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors"},
        # SmoothMix comes from Civitai behind a token; the notebook fetches it. The graph loads it
        # twice over: the checkpoint pair as diffusion models, and the Animations pair as loras the
        # Power Lora Loader has switched on.
        {"folder": "diffusion_models", "name": "SmoothMix_I2V_v2_High.safetensors", "url": None},
        {"folder": "diffusion_models", "name": "SmoothMix_I2V_v2_Low.safetensors", "url": None},
        {"folder": "loras", "name": "SmoothMix_Animations_XXX_High.safetensors", "url": None},
        {"folder": "loras", "name": "SmoothMix_Animations_XXX_Low.safetensors", "url": None},
    ],
    "audio": [
        # The fine-tune the sampler loads, and the only file that is ours to fetch: MMAudio's own
        # vae, synchformer and vocoder come down with the library, which knows where it keeps them.
        # It lands in ComfyUI's model tree although ComfyUI never reads it -- the installer, the
        # panel and the "is it there" check all hang off that one root, and a second root for a
        # single file would be the same machinery written twice.
        {"folder": "mmaudio", "name": HF_MMAUDIO_NSFW,
         "url": f"https://huggingface.co/phazei/NSFW_MMaudio/resolve/main/{HF_MMAUDIO_NSFW}"},
    ],
}


def audio_weights(files):
    """Where the sound weights sit, built from the row above rather than spelled out a second time:
    a renamed file then moves the panel and the sampler together."""
    row = GROUPS["audio"][0]
    return files.path(row["folder"], row["name"])
