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
    # What the photo graph reads. The checkpoint and the lora are the render itself; the other
    # three are branches of the same graph -- the default-on FaceDetailer loads the detector and
    # SAM at startup, and the bypassed Ultimate SD Upscale reads Remacri the moment it is switched
    # on. Two of five would make "the photo producer is installed" a lie.
    "photo": [
        # Which checkpoint is here is the user's pick since Madde 140 -- the notebook draws a box
        # per model and every one of them is empty by default. So the row names a kind rather than
        # a file: the graph renders with whichever it was handed, and the panel asks whether there
        # is anything to hand it. Naming one made the panel call the producer uninstalled for
        # anyone who picked a different model.
        {"folder": "checkpoints", "suffix": ".safetensors"},
        {"folder": "loras", "name": "USNR_STYLE_ILL_V1_lokr3-000024.safetensors"},
        {"folder": "upscale_models", "name": "4x_foolhardy_Remacri.pth"},
        # UltralyticsDetectorProvider lists this one as "bbox/<name>", so the folder is nested.
        {"folder": "ultralytics/bbox", "name": "face_yolov9c.pt"},
        {"folder": "sams", "name": "sam_vit_b_01ec64.pth"},
    ],
    "video": [
        # The name is what the graph's VAELoader asks for, which is not what the file is called at
        # the source: ComfyUI looks a model up by its name on disk, so it lands under that one.
        {"folder": "vae", "name": "Wan2_1_VAE_fp32.safetensors"},
        {"folder": "text_encoders", "name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors"},
        {"folder": "loras", "name": "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"},
        {"folder": "loras", "name": "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors"},
        # The graph loads SmoothMix twice over: the checkpoint pair as diffusion models, and the
        # Animations pair as loras the Power Lora Loader has switched on.
        {"folder": "diffusion_models", "name": "SmoothMix_I2V_v2_High.safetensors"},
        {"folder": "diffusion_models", "name": "SmoothMix_I2V_v2_Low.safetensors"},
        {"folder": "loras", "name": "SmoothMix_Animations_XXX_High.safetensors"},
        {"folder": "loras", "name": "SmoothMix_Animations_XXX_Low.safetensors"},
        # Only the first-last graph reads this one, and only through its CLIPVisionLoader. It is in
        # the video group all the same: one producer, and a producer is installed or it is not.
        {"folder": "clip_vision", "name": "clip_vision_h.safetensors"},
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
