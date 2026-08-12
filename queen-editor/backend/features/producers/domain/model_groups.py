"""What each producer needs on disk, and where.

Knowledge inherited from collab-toolbox, not a dependency on it: the names and addresses are copied
into our own file, so that folder can change without changing ours (CODE-STANDARD's independence
rule).

Two kinds of entry appear here:
  * a file with a `url` -- the app fetches it,
  * a file with a `url` and an `auth` word -- the source wants a key, and the composition root is
    the only layer that holds one. The installer stops when it reaches a source it was given no
    key for, loudly: a group half installed in silence would read as installed the next time
    anybody looked.

Every file is fetchable from here. The notebook installs code, never a model (FOUNDATION 9).
"""
HF_WAN22 = "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files"
HF_WAN21 = "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files"
HF_MMAUDIO_NSFW = "mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors"

# Civitai serves gated files by model version id, behind a login cookie. The address and the
# cookie's name live together: if the source changes, one file changes.
CIVITAI = "civitai"
CIVITAI_DOWNLOAD = "https://civitai.red/api/download/models"
CIVITAI_COOKIE_NAME = "__Secure-civ-token"


def civitai_headers(cookie):
    """What a Civitai download must carry. This file knows the cookie's name, never its value --
    the secret is the composition root's to supply."""
    return {"Cookie": f"{CIVITAI_COOKIE_NAME}={cookie}"}

GROUPS = {
    # What the photo graph reads. The checkpoint and the lora are the render itself; the other
    # three are branches of the same graph -- the default-on FaceDetailer loads the detector and
    # SAM at startup, and the bypassed Ultimate SD Upscale reads Remacri the moment it is switched
    # on. Two of five would make "the photo producer is installed" a lie.
    "photo": [
        {"folder": "checkpoints", "name": "nova3DCGXL_ilV90.safetensors",
         "url": f"{CIVITAI_DOWNLOAD}/2744564", "auth": CIVITAI},
        {"folder": "loras", "name": "USNR_STYLE_ILL_V1_lokr3-000024.safetensors",
         "url": f"{CIVITAI_DOWNLOAD}/1552087", "auth": CIVITAI},
        {"folder": "upscale_models", "name": "4x_foolhardy_Remacri.pth",
         "url": "https://huggingface.co/FacehugmanIII/4x_foolhardy_Remacri/resolve/main/"
                "4x_foolhardy_Remacri.pth"},
        # UltralyticsDetectorProvider lists this one as "bbox/<name>", so the folder is nested.
        {"folder": "ultralytics/bbox", "name": "face_yolov9c.pt",
         "url": "https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov9c.pt"},
        {"folder": "sams", "name": "sam_vit_b_01ec64.pth",
         "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"},
    ],
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
        # SmoothMix comes from Civitai behind a login cookie. The graph loads it twice over: the
        # checkpoint pair as diffusion models, and the Animations pair as loras the Power Lora
        # Loader has switched on.
        {"folder": "diffusion_models", "name": "SmoothMix_I2V_v2_High.safetensors",
         "url": f"{CIVITAI_DOWNLOAD}/2513182", "auth": CIVITAI},
        {"folder": "diffusion_models", "name": "SmoothMix_I2V_v2_Low.safetensors",
         "url": f"{CIVITAI_DOWNLOAD}/2513186", "auth": CIVITAI},
        {"folder": "loras", "name": "SmoothMix_Animations_XXX_High.safetensors",
         "url": f"{CIVITAI_DOWNLOAD}/2376136", "auth": CIVITAI},
        {"folder": "loras", "name": "SmoothMix_Animations_XXX_Low.safetensors",
         "url": f"{CIVITAI_DOWNLOAD}/2376143", "auth": CIVITAI},
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
