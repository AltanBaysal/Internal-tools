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

GROUPS = {
    "photo": [],
    "video": [
        {"folder": "vae", "name": "wan_2.1_vae.safetensors",
         "url": f"{HF_WAN21}/vae/wan_2.1_vae.safetensors"},
        {"folder": "text_encoders", "name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
         "url": f"{HF_WAN21}/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"},
        {"folder": "loras", "name": "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
         "url": f"{HF_WAN22}/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"},
        {"folder": "loras", "name": "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",
         "url": f"{HF_WAN22}/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors"},
        # SmoothMix I2V comes from Civitai behind a token; the notebook fetches it.
        {"folder": "diffusion_models", "name": "SmoothMix_I2V_v2_High.safetensors", "url": None},
        {"folder": "diffusion_models", "name": "SmoothMix_I2V_v2_Low.safetensors", "url": None},
    ],
    "audio": [
        # MMAudio's node downloads its own weights on first use; nothing here is ours to fetch.
        {"folder": "mmaudio", "name": "mmaudio_large_44k_v2.pth", "url": None},
    ],
}
