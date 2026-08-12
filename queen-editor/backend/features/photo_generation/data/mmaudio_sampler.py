"""MMAudio itself: weights on the GPU, one clip in, a wav out.

This is the outside world, like the ComfyUI client and the ffmpeg exporter -- it has no tests,
because a fake torch would only be testing the fake. Everything decidable was pulled out into
`mmaudio_generator` (which piece, which words, which seed) and `audio_chunks` (where the cuts go),
and those are covered.

Every setting is collab-toolbox's mmaudio notebook's, to the number: the same architecture, the same
NSFW weights, 40 steps at cfg 5.5 with the euler solver, in float16 because a T4 has no bfloat16.

torch and mmaudio are imported inside the first render, never at module level: the app has to start,
and its suite has to run, on machines where neither is installed.
"""
import os
import tempfile
from pathlib import Path

MODEL = "large_44k"      # the architecture the NSFW fine-tune was trained on
STEPS = 40               # the notebook's override of the default 25 -- cleaner sound, ~60% slower
CFG_STRENGTH = 5.5       # the notebook's override of 4.5 -- holds the negative better
SOLVER = "euler"         # fixed step count, predictable
SYNC_FPS = 25.0          # what Synchformer reads, so a frame count converts to seconds by it


class MMAudioSampler:
    def __init__(self, weights, device="cuda"):
        self._weights = weights
        self._device = device
        self._engine = None

    def render(self, video, prompt, negative, seed, duration):
        """One clip's sound as wav bytes. The first call pays for loading the weights; every call
        after it finds them already on the card, which is why the queue's sound jobs run together."""
        import torch
        import torchaudio
        from mmaudio.eval_utils import generate, load_video

        engine = self._load()
        seq_cfg = engine["seq_cfg"]
        net, fm, rng = engine["net"], engine["fm"], engine["rng"]

        seq_cfg.duration = duration
        net.update_seq_lengths(seq_cfg.latent_seq_len, seq_cfg.clip_seq_len, seq_cfg.sync_seq_len)

        info = load_video(Path(video), duration)
        # load_video quantises to whole frames, so what came back can be shorter than what was
        # asked for; the model is told the length it actually got, or its own assertion fails.
        actual = info.sync_frames.shape[0] / SYNC_FPS
        if abs(actual - duration) > 0.01:
            seq_cfg.duration = actual
            net.update_seq_lengths(seq_cfg.latent_seq_len, seq_cfg.clip_seq_len,
                                   seq_cfg.sync_seq_len)
        info.clip_frames = _fit(torch, info.clip_frames, seq_cfg.clip_seq_len)

        dtype = engine["dtype"]
        clip = info.clip_frames.unsqueeze(0).to(self._device, dtype)
        sync = info.sync_frames.unsqueeze(0).to(self._device, dtype)
        rng.manual_seed(seed)
        with torch.inference_mode():
            audios = generate(clip_video=clip, sync_video=sync,
                              text=[prompt or ""], negative_text=[negative],
                              feature_utils=engine["features"], net=net, fm=fm, rng=rng,
                              cfg_strength=CFG_STRENGTH)
        audio = audios.float().cpu()[0]

        # torchaudio writes to a path; the bytes are what the caller wants, so the file is a step
        # rather than a result.
        handle, path = tempfile.mkstemp(suffix=".wav")
        os.close(handle)
        try:
            torchaudio.save(path, audio, seq_cfg.sampling_rate)
            with open(path, "rb") as opened:
                return opened.read()
        finally:
            os.remove(path)

    def _load(self):
        """The weights, loaded once and kept. Loading is minutes of work, and the queue sends its
        sound jobs one after another -- paying it per job would tax every sound for nothing."""
        if self._engine is not None:
            return self._engine

        import torch
        from safetensors.torch import load_file
        from mmaudio.eval_utils import all_model_cfg, setup_eval_logging
        from mmaudio.model.flow_matching import FlowMatching
        from mmaudio.model.networks import get_my_mmaudio
        from mmaudio.model.utils.features_utils import FeaturesUtils

        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        setup_eval_logging()

        dtype = torch.float16
        model_cfg = all_model_cfg[MODEL]
        # The base weights (vae, synchformer, vocoder) come from the library's own store; only the
        # fine-tune is ours to point at.
        model_cfg.download_if_needed()

        net = get_my_mmaudio(model_cfg.model_name).to(self._device, dtype).eval()
        net.load_weights(load_file(self._weights, device=self._device))
        features = FeaturesUtils(
            tod_vae_ckpt=model_cfg.vae_path,
            synchformer_ckpt=model_cfg.synchformer_ckpt,
            enable_conditions=True,
            mode=model_cfg.mode,
            bigvgan_vocoder_ckpt=model_cfg.bigvgan_16k_path,
            need_vae_encoder=False,
        ).to(self._device, dtype).eval()

        self._engine = {
            "net": net,
            "features": features,
            "fm": FlowMatching(min_sigma=0, inference_mode=SOLVER, num_steps=STEPS),
            "rng": torch.Generator(device=self._device),
            "seq_cfg": model_cfg.seq_cfg,
            "dtype": dtype,
        }
        return self._engine


def _fit(torch, frames, length):
    """The clip frames, at exactly the count the model was told to expect: short is padded with the
    last frame, long is trimmed. The sync frames are left alone -- their encoder compresses in time,
    so their raw count is not the sequence length."""
    if frames.shape[0] < length:
        padding = frames[-1:].expand(length - frames.shape[0], *frames.shape[1:])
        return torch.cat([frames, padding], dim=0)
    return frames[:length] if frames.shape[0] > length else frames
