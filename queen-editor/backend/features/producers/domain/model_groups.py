"""Which model files each producer needs, by folder and name -- or by folder and kind.

A **reading** list, not an installing one: the app never downloads a model. Where the files come
from and how they are fetched is the notebook's business (FOUNDATION 9), and the addresses live
there so that two places never claim to know them. What this file answers is the one question the
app still asks -- is this producer's group on the machine?

A row has one of three shapes, and which one says what it is asking:
  {"folder", "name"}   -- exactly this file, because the graph loads it by that name
  {"folder", "suffix"} -- any file of this kind, because which one is the user's pick
  {"any": [rows, ...]} -- one of these lists, each of rows of the two shapes above, all of them
                          here: two kinds of model, either of which a producer renders with

The names are inherited from collab-toolbox as knowledge, not as a dependency: they are the names
the graphs load by, so a rename here has to follow the graph rather than the source.
"""
HF_MMAUDIO_NSFW = "mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors"

# What Krea 2 Turbo's graph loads (madde 482), every one by name: the int8 DiT, its Qwen3-VL encoder,
# Qwen Image's VAE and SNOFS, which the graph switches on -- and Translucent Penetration's Krea
# version, which its lora box lays over SNOFS (madde 499).
KREA2_FILES = [
    {"folder": "diffusion_models", "name": "krea2_turbo_int8_convrot.safetensors"},
    {"folder": "text_encoders", "name": "qwen3vl_4b_fp8_scaled.safetensors"},
    {"folder": "vae", "name": "qwen_image_vae.safetensors"},
    {"folder": "loras", "name": "snofs_krea_v1_5.safetensors"},
    {"folder": "loras", "name": "translucent_penetration_v5_krea2.safetensors"},
]

# What Qwen Image 2.1 Turbo's graph loads (madde 499): the official template's int8 Turbo DiT, its
# Qwen3-VL 8B encoder and its VAE -- and Translucent Penetration's Qwen version, its lora box's one.
QWEN_FILES = [
    {"folder": "diffusion_models", "name": "qwen_image_2.1_turbo_int8_convrot.safetensors"},
    {"folder": "text_encoders", "name": "qwen3vl_8b_int8_convrot.safetensors"},
    {"folder": "vae", "name": "qwen_image_2.1_vae_bf16.safetensors"},
    {"folder": "loras", "name": "translucent_penetration_v5_qwen_image_2_1.safetensors"},
]

GROUPS = {
    # What the photo graphs read. The model and the loras are the render itself; the other three
    # are branches of the checkpoints' graph -- the default-on FaceDetailer loads the detector and
    # SAM at startup, and the bypassed Ultimate SD Upscale reads Remacri the moment it is switched
    # on. Counting only the render's files would make "the photo producer is installed" a lie.
    "photo": [
        # Which model is here is the user's pick since Madde 140 -- the notebook draws a box per
        # model and every one of them is empty by default. A checkpoint is a kind rather than a
        # file: the graph renders with whichever it was handed, and the panel asks whether there is
        # anything to hand it. Naming one made the panel call the producer uninstalled for anyone
        # who picked a different model. Krea (madde 482) and Qwen (madde 499) are the other kinds:
        # each a graph of its own, whose files all have to be here.
        {"any": [[{"folder": "checkpoints", "suffix": ".safetensors"}], KREA2_FILES, QWEN_FILES]},
        # Both loras come down whichever models were ticked: either can go over any checkpoint, and
        # hanging the panel's count on the choice would make "installed" mean a different set of
        # files on every machine. A Krea-only or Qwen-only run takes them too (~2 GiB with the
        # three below). DaSiWa's two futa loras (madde 501) come down with DaSiWa's box alone, so
        # they are not counted here, as no one checkpoint is; a run that ticked DaSiWa and did not
        # get them stopped in the notebook's download cell.
        {"folder": "loras", "name": "USNR_STYLE_ILL_V1_lokr3-000024.safetensors"},
        {"folder": "loras", "name": "translucent_penetration_v5.safetensors"},
        {"folder": "upscale_models", "name": "4x_foolhardy_Remacri.pth"},
        # UltralyticsDetectorProvider lists this one as "bbox/<name>", so the folder is nested.
        {"folder": "ultralytics/bbox", "name": "face_yolov9c.pt"},
        {"folder": "sams", "name": "sam_vit_b_01ec64.pth"},
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
        # Mutlu son's lora (madde 426), which the producer puts in the stack when a video asks for
        # it. Counted although most videos never load it: a switched-on video does, and the panel
        # says installed only when every video this producer can be handed can be made.
        {"folder": "loras", "name": "HMCumshot_V1.0.safetensors"},
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
