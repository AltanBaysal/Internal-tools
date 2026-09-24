"""Model downloads for the notebook: every file comes down validated, and its line says where it came
from and how fast.

The lists of what to download stay in the notebook, next to the boxes that choose them -- addresses
live there (FOUNDATION 9). What is here is how a file comes down, which a cell could not test.
"""
import json
import os
import struct
import subprocess
import time

from colab.console import head_text, human, log, run

# hf_hub_download writes the repo's folders and its own .cache under local_dir. Neither belongs among
# ComfyUI's models, so a file lands here and is moved into place: a rename on one disk, not a copy.
STAGE = "/content/hf_stage"


def check_safetensors(path):
    if not os.path.exists(path):
        return "invalid", "missing"
    size = os.path.getsize(path)
    if size < 8:
        return "invalid", f"too small ({human(size)})"

    with open(path, "rb") as f:
        header_len = struct.unpack("<Q", f.read(8))[0]
        if not (0 < header_len < 200_000_000):
            return "invalid", f"bad header length ({header_len})"
        if 8 + header_len > size:
            return "partial", f"header incomplete ({human(size)})"
        try:
            header = json.loads(f.read(header_len).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            return "invalid", f"header parse failed ({type(e).__name__}, {human(size)})"

    ends = [v["data_offsets"][1] for k, v in header.items()
            if k != "__metadata__" and isinstance(v, dict) and "data_offsets" in v]
    if not ends:
        return "ok", f"{human(size)}, no tensor offsets"

    expected = 8 + header_len + max(ends)
    if size == expected:
        return "ok", f"{human(size)}, {len(ends)} tensors"
    if size < expected:
        return "partial", f"{size:,} / {expected:,} bytes"
    return "invalid", f"too long: {size:,} / {expected:,} bytes"


def check_binary(path, min_bytes):
    if not os.path.exists(path):
        return "invalid", "missing"
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(16)
    if head[:1] in (b"<", b"{"):
        return "invalid", f"error page? ({human(size)})"
    if size < min_bytes:
        return "partial", f"{human(size)} < taban {human(min_bytes)}"
    return "ok", human(size)


def strip_unreferenced_tail(path, label):
    try:
        with open(path, "rb") as f:
            n = struct.unpack("<Q", f.read(8))[0]
            header = json.loads(f.read(n).decode("utf-8")) if 0 < n < 200_000_000 else {}
        end = 8 + n + max(v["data_offsets"][1] for k, v in header.items() if k != "__metadata__")
    except Exception:
        return
    if os.path.getsize(path) > end:
        with open(path, "rb") as f:
            f.seek(end)
            tail = f.read()
        os.truncate(path, end)
        log(f"{label}: kuyrukta {len(tail)} sahipsiz bayt vardı, atıldı → {tail[:200]!r}", "WARN")


def _judge(path, label, floor):
    """A file with a floor -- .pth, .pt -- has no header to read and is judged by its size. A
    safetensors first loses the stamp some quantizers leave after the last tensor (NOTEBOOK-STANDARD,
    section 3)."""
    if floor:
        return check_binary(path, floor)
    strip_unreferenced_tail(path, label)
    return check_safetensors(path)


def _settled(path, label, floor):
    """The verdict's message, or a RuntimeError showing how the file starts. A bad file is never
    passed on and never deleted: it stays where it is, for inspection."""
    state, msg = _judge(path, label, floor)
    if state != "ok":
        raise RuntimeError(f"{label}: {state} — {msg}\n{path}\n--- file head ---\n{head_text(path)}")
    return msg


def _landed(label, source, size, took, msg):
    """The file's line, and its row for the table the models cell ends with (madde 312)."""
    log(f"{label}: indirildi — {source}, {human(size)}, {took:.0f} sn, "
        f"{size / took / 2**20:.1f} MB/s ({msg})", "OK")
    return label, size, took


def fetch(url, target_dir, filename, label, *, parallel, headers=None, floor=None):
    """A file by its address. parallel=True is aria2c's sixteen connections. A gated file goes by
    curl: Civitai redirects to its store, the store answers 403 when the login cookie comes along,
    and curl drops the cookie when the host changes where aria2c carries it. Its row for the summary,
    or None when the file was already in place."""
    target = os.path.join(target_dir, filename)
    part = target + ".part"
    hdrs = f"/tmp/{filename}.headers"

    if os.path.exists(target):
        log(f"{label}: zaten var ({_settled(target, label, floor)})")
        return

    resume = False
    if os.path.exists(part):
        state, msg = _judge(part, label, floor)
        if state == "invalid":
            raise RuntimeError(f"{label}: .part {state} — {msg}\n{part}\n--- file head ---\n{head_text(part)}")
        if state == "ok":
            log(f"{label}: .part zaten tam ({msg}) — indirilmiyor")
        else:
            log(f"{label}: .part'tan devam ({msg})")
            resume = True

    start, before = time.perf_counter(), (os.path.getsize(part) if os.path.exists(part) else 0)
    if not os.path.exists(part) or resume:
        log(f"{label}: iniyor")
        if parallel:
            cmd = ["aria2c", "-x", "16", "-s", "16", "-k", "1M", "--continue=true",
                   "--console-log-level=warn", "--auto-file-renaming=false",
                   "--allow-overwrite=true", "-d", target_dir, "-o", os.path.basename(part)]
            if headers:
                cmd += ["--header", headers]
        else:
            cmd = ["curl", "-L", "-C", "-", "--fail-with-body", "--max-time", "7200",
                   "-D", hdrs, "-o", part]
            if headers:
                cmd += ["-H", headers]
        cmd.append(url)
        try:
            run(cmd, label, timeout=7200)
        except RuntimeError as e:
            raise RuntimeError(
                f"{e}\n{url.split('?')[0]}\n"
                f"--- response headers ---\n{head_text(hdrs)}\n"
                f"--- response body ---\n{head_text(part)}"
            ) from None

    state, msg = _judge(part, label, floor)
    if state != "ok":
        raise RuntimeError(f"{label}: {state} — {msg}\n{part}\n{url.split('?')[0]}\n"
                           f"--- response headers ---\n{head_text(hdrs)}\n"
                           f"--- file head ---\n{head_text(part)}")
    os.replace(part, target)
    return _landed(label, url.split("/")[2], os.path.getsize(target) - before,
                   time.perf_counter() - start, msg)


def hf_fetch(repo, path, target_dir, filename, label, *, floor=None):
    """A file by its repo and path, through Hugging Face's own downloader. With hf_xet behind it the
    file's Xet chunks come straight from storage in parallel; an address went through HF's bridge,
    which cuts a plain download to 8.7 MB/s on most of its servers (xet-core #821). Its row for the
    summary, or None when the file was already in place."""
    # Imported here: Colab ships it, and this module has to import where it is not installed.
    from huggingface_hub import hf_hub_download

    target = os.path.join(target_dir, filename)
    if os.path.exists(target):
        log(f"{label}: zaten var ({_settled(target, label, floor)})")
        return

    log(f"{label}: iniyor (HF)")
    start = time.perf_counter()
    try:
        got = hf_hub_download(repo, path, local_dir=STAGE)
    except Exception as e:
        raise RuntimeError(f"{label}: HF {repo}/{path} — {type(e).__name__}: {e}") from None
    msg = _settled(got, label, floor)
    os.replace(got, target)
    return _landed(label, "HF", os.path.getsize(target), time.perf_counter() - start, msg)


def civitai_url(version_id):
    return f"https://civitai.red/api/download/models/{version_id}"


def cookie_header(cookie):
    return f"Cookie: __Secure-civ-token={cookie}"


def _upload(mirror, path, target, label):
    """Up to the mirror. A refusal is printed, not raised: the file is already down and usable, and
    the next run tries again."""
    from huggingface_hub import HfApi

    start = time.perf_counter()
    try:
        HfApi().upload_file(path_or_fileobj=target, path_in_repo=path, repo_id=mirror,
                            commit_message=f"{label} (Civitai {path})")
    except Exception as e:
        log(f"{label}: aynaya yüklenemedi — {type(e).__name__}: {e}", "WARN")
        return
    size, took = os.path.getsize(target), time.perf_counter() - start
    log(f"{label}: aynaya yüklendi — {human(size)}, {took:.0f} sn, {size / took / 2**20:.1f} MB/s", "OK")


# Files on trial stay out of the mirror (madde 327): they come straight from Civitai and are never
# uploaded -- a file we may not keep has no business there. Keyed by file name, not by Civitai
# version: the version is the file's address, and addresses live in the notebook (FOUNDATION 9).
MIRRORLESS = set()


def civitai_fetch(mirror, version_id, target_dir, filename, label, cookie):
    """A Civitai file, from the user's Hugging Face mirror when it is there. When it is not -- or will
    not come down -- the mirror's own sentence is printed, the file comes from Civitai the way it
    always did, and it goes up to the mirror so the next run takes the fast road (madde 311). A file
    in MIRRORLESS skips the mirror both ways and comes straight from Civitai (madde 327). Either way
    the row is the download's; the upload has its own line. A file already in place asks nothing of
    anyone, the probe included."""
    path = f"{version_id}/{filename}"
    target = os.path.join(target_dir, filename)
    if os.path.exists(target):
        log(f"{label}: zaten var ({_settled(target, label, None)})")
        return
    mirrored = filename not in MIRRORLESS
    if mirrored:
        try:
            return hf_fetch(mirror, path, target_dir, filename, label)
        except RuntimeError as e:
            log(f"{label}: aynadan alınamadı, Civitai'den inecek — {e}", "WARN")
    else:
        log(f"{label}: aynası kapalı — Civitai'den aynasız iniyor (madde 327)")
    if len(cookie or "") <= 200:
        raise RuntimeError(
            f"❌ {label}: {'aynada yok' if mirrored else 'aynası kapalı'}, ve Civitai'den inmesi için "
            f"CIVITAI_COOKIE gerekiyor — Colab 🔑 Secrets'a 'CIVITAI_COOKIE' adıyla ekle: civitai.red → "
            f"giriş → F12 → Application → Cookies → __Secure-civ-token değeri (ES256 JWT)")
    civitai_probe(version_id, label, cookie)
    row = fetch(civitai_url(version_id), target_dir, filename, label, parallel=False,
                headers=cookie_header(cookie))
    if mirrored:
        _upload(mirror, path, target, label)
    return row


def civitai_probe(version_id, label, cookie):
    out = "/content/_probe.bin"
    done = subprocess.run(
        ["curl", "-sL", "--max-time", "20", "--limit-rate", "200k", "-r", "0-1023",
         "-H", cookie_header(cookie), "-w", "%{http_code}", "-o", out, civitai_url(version_id)],
        capture_output=True, text=True)
    if done.returncode not in (0, 28):
        tail = "\n".join((done.stderr or done.stdout or "").strip().splitlines()[-5:])
        raise RuntimeError(f"❌ probe {label}: curl exit {done.returncode}\n{tail}")
    code = (done.stdout or "").strip()[-3:]
    body = b""
    if os.path.exists(out):
        with open(out, "rb") as f:
            body = f.read(512)
        os.remove(out)
    if code.startswith("2") and not body.startswith(b"<") and not body.startswith(b'{"'):
        log(f"{label}: erişim OK", "OK")
        return
    raise RuntimeError(f"❌ {label}: HTTP {code} — Civitai yanıtı: "
                       f"{body.decode('utf-8', 'replace').strip() or '(boş gövde — binary değil)'}")


def _duration(seconds):
    minutes, seconds = divmod(round(seconds), 60)
    return f"{minutes} dk {seconds} sn" if minutes else f"{seconds} sn"


def download_summary(rows):
    """The table the models cell ends with (madde 312): every file that came down in this run -- one
    already in place hands back None and stays out -- and under them a Toplam, whose speed is the
    average of the whole download. The times are the downloads' own; the cell's own line, under the
    table, has the rest, uploads and probes included."""
    rows = [row for row in rows if row]
    if not rows:
        log("İndirme özeti: bu koşuda inen dosya yok")
        return
    rows.append(("Toplam", sum(size for _, size, _ in rows), sum(took for _, _, took in rows)))
    width = max(len(label) for label, _, _ in rows)
    print("\nİndirme özeti:")
    for label, size, took in rows:
        print(f"   {label:<{width}}  {human(size):>8}  {_duration(took):>11}  "
              f"{size / took / 2**20:6.1f} MB/s")
