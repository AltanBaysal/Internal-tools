# Madde 469 · Yüz detailer'ı geri açılır — plan

**Spec:** [m469](../specs/2026-10-12-queen-editor-m469-yuz-detailer-geri-design.md) · **Dal:**
`feat/queen-editor-v9`, ana klasör. Açık soruların cevabı (ana ajan, 12 Ekim): `open_jobs`
konumsal ve varsayılansız; "her düğüm kaydedilen resme ulaşır" testi her çıkış düğümünden
yürüyecek biçimde değişir; madde v9 yol haritasına 469 olarak yazılır.

## 1. Testler — kırmızı

1. `backend/tests/test_workflow_asset.py` — iki 430 testi detailer'ı soran iki teste döner; ulaşma
   testi her çıkış düğümünden yürür; BREAK testinin docstring'i ToDetailerPipe'ı anar.
2. `backend/tests/test_producers.py` — fotoğraf grubu iki satırı geri bekler.
3. `backend/tests/test_notebook_installs_the_producer_groups.py` — detailer dosyalarını indiren
   satırlar, `OPEN_PHOTO` anahtar arkasında, `download_models` çağrısı `open_jobs`'la, on paket,
   `FOLDERS`'ta iki klasör; tahmin docstring'i.
4. `backend/tests/test_colab_downloads.py` — `download_models` üç listeyle, HF → adres → Civitai.
5. `backend/tests/test_colab_nodes.py` — docstring.

`python -m pytest queen-editor/backend/tests/<bu dört dosya> -q` bir kez: 9 kırmızı.

## 2. Kod

1. `assets/workflow_api.json` ← `git show 07f099ed^:queen-editor/assets/workflow_api.json`.
2. `backend/features/producers/domain/model_groups.py` — iki satır ve yorumlar.
3. `colab/downloads.py` — `download_models(hf_jobs, open_jobs, civitai_jobs, mirror, cookie)`.
4. `queeneditor.ipynb` — giriş ve başlık 10; Subpack; `BBOX`, `SAMS`; dedektör `HF_PHOTO`'da;
   `OPEN_PHOTO`; `open_jobs`; `FOLDERS`'ta iki satır; çağrı.
5. `comfy_photo_generator.py`, `colab/nodes.py` — yorumlar.
6. `docs/roadmaps/2026-10-05-queen-editor-v9-roadmap.md` — 469 satırı, başlık notu, Durum 29/29.

## 3. Doğrulama

`python -m pytest queen-editor -q` bir kez, sonda.
