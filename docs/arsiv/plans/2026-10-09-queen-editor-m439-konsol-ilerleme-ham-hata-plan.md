# Madde 439 — Konsol ilerlemeyi gösterir, ve her hata ham hâliyle, bütün basılır, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** apt düşerse bütün çıktısı hatada; git clone ve pip ilerlemeyi gösterir; bir sunucuyu
beklemek `colab/wait.py`'de bir kez yazılır, ve Flask cevap vermezse son bakışın hatası ve log'u
hatada; cloudflared'ın, wget'in ve Civitai denemesinin hataları kesilmez, saklanmaz.

**Yaklaşım:** Davranış değişen her görevde önce test, kırmızı görülür, sonra kod. Dosyalar Edit ve
Write ile değişir.

**Spec:** [m439](../specs/2026-10-09-queen-editor-m439-konsol-ilerleme-ham-hata-design.md)

## Her yere geçerli kurallar

- Yorumlar, docstring'ler ve test adları İngilizce; konsola ve `assert`'e giden metin Türkçe.
- Testler modülü fixture'da `importlib` ile alır.
- Yol haritasına ve notebook'a dokunulmaz.

---

## Görev 1: `colab/console.py` — `log_tail`

- [ ] `backend/tests/test_colab_console.py`: `log_tail` 40 satırlık log'da başlık + son 30 satır.
  Kırmızı.
- [ ] `console.py`: `LOG_LINES = 30`, `log_tail(path)` — `comfy._tail` buraya, `head_text`'in yanına
  taşınır. Yeşil.

## Görev 2: `colab/wait.py` — `wait_for`

- [ ] `backend/tests/test_colab_wait.py`: cevapta süre; 45 bakıştan sonra üç parçalı hata; ölü
  sürecin cevabı sayılmaz; biten süreç beklemeyi hemen durdurur. Kırmızı.
- [ ] `wait.py`: `LOOKS`, `STEP`, `_asked` (`comfy._asked`'dan), `wait_for`. Yeşil.
- [ ] `CODE-STANDARD.md`'nin `colab/` listesine `wait.py`.

## Görev 3: `colab/comfy.py` — bekleme ve ilerleme

- [ ] `test_colab_comfy.py`: `Machine` `urllib.request.urlopen`'u kendisi değiştirir; kurulum testi
  `git clone --progress …` ve `pip install --progress-bar on …` (`-q`'suz) bekler. Kırmızı.
- [ ] `comfy.py`: `start_comfy` `wait_for(…, process)` çağırır; `LOOKS`, `STEP`, `_asked`, `_tail`,
  `LOG_LINES` çıkar; komutlara bayraklar. Yeşil.

## Görev 4: `colab/server.py` — Flask, cloudflared, wget

- [ ] `test_colab_server.py`: Flask'ın hatası `❌ Flask 90 sn içinde cevap vermedi — <adres>\nURLError: …\n---
  <log> · son 30 satır ---\n…`; tünelin hatası cümle + log'unun son 30 satırı, bütün, ve hiçbir şey
  ayrıca basılmaz; cloudflared `wget -nv` ile. Kırmızı.
- [ ] `server.py`: `wait_for`, `log_tail(TUNNEL_LOG)`, `-nv`; `LOOKS`, `STEP`, `LOG_LINES` çıkar.
  Yeşil.

## Görev 5: `colab/system.py` — bütün çıktı

- [ ] `test_colab_system.py`: düşen adımın hatası komut, çıkış kodu ve bütün çıktı. Kırmızı.
- [ ] `system.py`: hata `done.stdout`'un tamamını taşır; `TAIL` import'u çıkar. Yeşil.

## Görev 6: `colab/downloads.py` — Civitai denemesi

- [ ] `test_colab_downloads.py`: curl düşerse `-sS` ve bütün stderr; Civitai reddederse 512 bayttan
  uzun yanıt bütün; bayt gelirse, 0'la da 28'le de, "erişim OK"; 28'le `000` gelirse curl'ün
  stderr'i hatada; ayrıştırılamayan başlık `Tür: mesaj` ile. Kırmızı.
- [ ] `downloads.py`: `PROBE`, `-sS`, `done.stderr`, `head_text`; reddin hatasına curl'ün stderr'i;
  `check_safetensors`'ın mesajı. Yeşil.

## Görev 7: nodes, sound, downloads — ilerleme

- [ ] `test_colab_nodes.py`, `test_colab_sound.py`, `test_colab_downloads.py`: klon `--progress`, pip
  `--progress-bar on` ve `-q`'suz. Testlerin docstring'leri yalnız neyi denetlediklerini söyler.
  Kırmızı.
- [ ] `nodes.py`, `sound.py`, `downloads.py`: bayraklar. Yeşil.
- [ ] `console.run`'ın docstring'i, kendi paragrafında, bayrakların nedenini söyler.

## Görev 8: suite'ler

- [ ] Dört suite, sırayla: `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`,
  `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
