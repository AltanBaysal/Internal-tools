"""Model downloads for the notebook: every file comes down validated, and its line says where it came
from and how fast.

The lists of what to download stay in the notebook, next to the boxes that choose them -- addresses
live there (FOUNDATION 9), and so do how much room each group takes and which folders the summary
shows. What is here is how a file comes down, and the models cell's run around it -- hf_xet, the disk
check, the downloads, the folders and the table -- which a cell could not test (madde 438).

The Hugging Face token is here too: the notebook reads it once through use_hf_token, before anything
downloads, and every download and upload hands it over (madde 437).
"""
import glob
import json
import os
import shutil
import struct
import subprocess
import time

from colab.console import head_text, human, log, run
from colab.vault import read_secret

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
    # curl and aria2c write the .part straight into it.
    os.makedirs(target_dir, exist_ok=True)

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


def use_hf_token(read):
    """HF_TOKEN read with `read` -- the notebook's userdata.get -- trimmed, and put in the environment,
    where _token finds it.

    Without a token the run goes on, and a line says so with what the read raised: the public files
    come down without one, and civitai_fetch already takes a file the mirror refuses from Civitai."""
    token, problem = read_secret(read, "HF_TOKEN")
    if problem:
        _without_token(problem)
        return
    os.environ["HF_TOKEN"] = token
    log("HF_TOKEN okundu — Hugging Face'e token'la gidilecek", "OK")


def _without_token(said):
    """A token an earlier run of this kernel left in the environment goes, so the line saying the run
    goes without one holds."""
    os.environ.pop("HF_TOKEN", None)
    log(f"{said}\nHugging Face'e token'sız gidilecek: açık dosyalar iner ama HF 429 dönebilir; aynadan "
        "alma ve aynaya yükleme olmaz — Civitai dosyaları çerezle Civitai'den iner. Colab 🔑 "
        "Secrets'a 'HF_TOKEN' adıyla ekle.", "WARN")


def _token():
    """The token use_hf_token put in the environment, handed to huggingface_hub outright -- or False,
    its word for going without one (madde 437).

    Handed neither, huggingface_hub looks for a token itself, and in Colab it asks the vault first and
    keeps the answer for the session. On 9 Ekim that ask came mid-download and timed out, and H3 came
    down unauthenticated into a 429. A token handed over is used as it is, and nothing is asked."""
    return os.environ.get("HF_TOKEN") or False


# A download from HF sometimes drops halfway -- H3 Eros Max beta5 at 97%, a request to its chunk store
# failing (madde 432) -- and is tried again: three attempts in all, thirty seconds before each retry.
ATTEMPTS = 3
WAIT = 30
# HF's answer about the file itself: missing, or not ours. Asked again, HF answers the same, and the
# mirror's 404 is how civitai_fetch learns a file is not there (madde 311), which stays instant.
FINAL = (401, 403, 404)


def _chain(error):
    """The error and those it was raised from, the raised one first, linked the way Python prints
    them. huggingface_hub puts some of HF's answers under a sentence of its own, which carries no
    response; the answer is underneath. A chain that loops back ends there, and none runs past five."""
    chain = []
    while error is not None and error not in chain and len(chain) < 5:
        chain.append(error)
        error = error.__cause__ or (None if error.__suppress_context__ else error.__context__)
    return chain


def _response(error):
    """HF's response: the first one riding on an error of the chain, or None."""
    return next((e.response for e in _chain(error) if getattr(e, "response", None) is not None), None)


def _raw(error):
    """Each error of the chain as it was raised, its type and its whole message, and under them HF's
    response when one came: the status and the body, as sent (madde 432). A streamed body nobody read
    raises when asked for, and what it raised stands in its place: raised here, it would stop the
    cell with the reader's error instead of the drop's."""
    text = "\n".join(f"{type(e).__name__}: {e}" for e in _chain(error))
    response = _response(error)
    if response is not None:
        try:
            body = response.text or "(boş gövde)"
        except Exception as e:
            body = f"(gövde okunamadı — {type(e).__name__}: {e})"
        text += f"\n--- response: HTTP {response.status_code} ---\n{body}"
    return text


def hf_fetch(repo, path, target_dir, filename, label, *, floor=None):
    """A file by its repo and path, through Hugging Face's own downloader. With hf_xet behind it the
    file's Xet chunks come straight from storage in parallel; an address went through HF's bridge,
    which cuts a plain download to 8.7 MB/s on most of its servers (xet-core #821). Its row for the
    summary, or None when the file was already in place.

    A download that drops is tried again, up to ATTEMPTS, and each drop prints what was raised.
    Neither HF's answer about the file (FINAL) nor a file that came down whole but bad is asked for
    again: both would come back the same. The error that stops the cell carries what the last attempt
    raised, and HF's response with it."""
    # Imported here: Colab ships it, and this module has to import where it is not installed.
    from huggingface_hub import hf_hub_download

    target = os.path.join(target_dir, filename)
    if os.path.exists(target):
        log(f"{label}: zaten var ({_settled(target, label, floor)})")
        return

    log(f"{label}: iniyor (HF)")
    start = time.perf_counter()
    for attempt in range(1, ATTEMPTS + 1):
        try:
            got = hf_hub_download(repo, path, local_dir=STAGE, token=_token())
            break
        except Exception as e:
            where = f"{label}: HF {repo}/{path}, deneme {attempt}/{ATTEMPTS}"
            answer = getattr(_response(e), "status_code", None)
            if answer in FINAL or attempt == ATTEMPTS:
                raise RuntimeError(f"{where}\n{_raw(e)}") from None
            log(f"{where} — {WAIT} sn sonra yeniden\n{_raw(e)}", "WARN")
        time.sleep(WAIT)
    msg = _settled(got, label, floor)
    os.makedirs(target_dir, exist_ok=True)
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
                            commit_message=f"{label} (Civitai {path})", token=_token())
    except Exception as e:
        log(f"{label}: aynaya yüklenemedi — {type(e).__name__}: {e}", "WARN")
        return
    size, took = os.path.getsize(target), time.perf_counter() - start
    log(f"{label}: aynaya yüklendi — {human(size)}, {took:.0f} sn, {size / took / 2**20:.1f} MB/s", "OK")


# Files on trial stay out of the mirror (madde 327): they come straight from Civitai and are never
# uploaded -- a file we may not keep has no business there. Keyed by file name, not by Civitai
# version: the version is the file's address, and addresses live in the notebook (FOUNDATION 9).
MIRRORLESS = {
    # H3's Mystic XXX lora, while the user tries it (madde 328).
    "MysticXXX_MMH3-V4.safetensors",
}


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


def install_hf_xet():
    """hf_xet, behind hf_fetch: without it huggingface_hub goes back to HF's bridge with nothing but a
    log line."""
    run(["pip", "install", "-q", "-U", "hf_xet"], "pip install hf_xet")


# GiB the disk check asks to stay free past the models themselves.
HEADROOM = 5


def check_disk(sizes):
    """The choice and the free disk on one line, and the run stopped before anything downloads when
    the chosen groups and HEADROOM do not fit. `sizes` is the notebook's (ticked, GiB, name) rows."""
    need = sum(gib for on, gib, _ in sizes if on)
    free = shutil.disk_usage("/content").free / 1024**3
    log(f"Seçim: {', '.join(name for on, _, name in sizes if on)} — ~{need} GiB "
        f"| Diskte boş: {free:.1f} GiB")
    if free < need + HEADROOM:
        raise RuntimeError(
            f"❌ Disk yetmiyor: ~{need} GiB model + {HEADROOM} GiB pay gerekiyor, "
            f"{free:.1f} GiB boş. Daha az üretici ya da daha az foto modeli seç, ya da diski daha "
            f"büyük bir runtime aç."
        )


def download_models(hf_jobs, civitai_jobs, mirror, cookie):
    """The Hugging Face files, then the Civitai ones. Every file's row, in that order, for
    download_summary."""
    rows = []
    for repo, path, folder, filename, label, floor in hf_jobs:
        rows.append(hf_fetch(repo, path, folder, filename, label, floor=floor))
    for version_id, folder, filename, label in civitai_jobs:
        rows.append(civitai_fetch(mirror, version_id, folder, filename, label, cookie))
    return rows


def show_folders(folders):
    """What each ticked folder holds, with sizes: the notebook's (ticked, title, folder, pattern)
    rows."""
    for on, title, folder, pattern in folders:
        if not on:
            continue
        print(f"\n📂 {title}/")
        for path in sorted(glob.glob(f"{folder}/{pattern}", recursive=True)):
            print(f"   {human(os.path.getsize(path))}  {os.path.relpath(path, folder)}")


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
