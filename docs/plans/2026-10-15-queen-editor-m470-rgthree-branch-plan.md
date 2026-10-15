# Madde 470 · rgthree `main` dalından klonlanır — plan

**Spec:** [m470](../specs/2026-10-15-queen-editor-m470-rgthree-branch-design.md) · **Dal:** `main`, ana
klasör — hotfix. Kapsam yalnız rgthree *(kullanıcı, 15 Ekim — "Yalnız rgthree")*.

## 1. Test — kırmızı

1. `backend/tests/test_colab_nodes.py` — `RGTHREE` adresi; `_github` sahtesiyle rgthree'nin klonunda
   `--branch main`, ComfyMath'inkinde `--branch` yok.
2. `backend/tests/test_notebook_installs_the_producer_groups.py` — `BRANCHES`'taki her adres
   `CUSTOM_NODES` hücresinde tırnaklı geçer (reviewer'ın bulgusu); anahtar bir kez bozularak kırmızı
   görülür.

`python -m pytest queen-editor/backend/tests/test_colab_nodes.py -q` bir kez: 1 kırmızı.

## 2. Kod

1. `colab/nodes.py` — `SKIPPED`'ın yanında `BRANCHES` ve nedenini söyleyen yorum; `install_node`
   adres tablodaysa klona `--branch <dal>` ekler; modülün ve `install_node`'un docstring'i.
2. `CODE-STANDARD.md` — *Notebook code*'a bir satır: bir node'un nasıl geldiği `colab/nodes.py`'de
   (`SKIPPED`, `BRANCHES`).
3. `docs/roadmaps/2026-10-05-queen-editor-v9-roadmap.md` — dalgaların altında 470'in satırı, tabloda
   470, başlıkta Durum 30/30.

## 3. Doğrulama

`python -m pytest queen-editor -q` bir kez, sonda.
