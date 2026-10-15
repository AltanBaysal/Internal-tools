# Madde 470 · rgthree `main` dalından klonlanır

**Tarih:** 15 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
470 · **Dal:** `feat/queen-editor-v9-m470` — hotfix, ana klasörde, worktree yok; Colab'da
denendikten sonra `main`'e ·
**Kurallar:** [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kullanıcının istediği

15 Ekim 2026: "abi şuan hot fix yapalım maine çöz bunu plan ver"; kapsam: "Yalnız rgthree" — DaSiWa'nın
`llama-cpp-python` zaman aşımı backlog'da kalır, bu maddeye girmez.

Görülecek sonuç: yeni bir oturumda ComfyUI hücresi rgthree'yi `main` dalından klonlar;
`comfyui.log`'da rgthree için `IMPORT FAILED` yoktur, ve fotoğraf üretimi `missing_node_type`
olmadan çalışır. Öteki her node bugünkü gibi kendi varsayılan dalından gelir.

## Ne oldu — 15 Ekim'de doğrulandı

- Colab'da fotoğraf üretimi düşüyor: `POST /prompt -> HTTP 400 missing_node_type: Node 'Power Lora
  Loader (rgthree)' not found` — `assets/workflow_api.json`'ın `27`'si.
- `/content/comfyui.log`: `IMPORT FAILED: /content/ComfyUI/custom_nodes/rgthree-comfy`; rgthree'nin
  `__init__.py`'sinin 271. satırında `AttributeError: module 'execution' has no attribute
  'recursive_output_delete_if_changed'`.
- rgthree-comfy GitHub'da varsayılan dalını `main`'den `dev`'e çevirdi (`default_branch: dev`, deponun
  `updated_at`'i `2026-10-15T13:11:51Z`).
- `dev` = `5f940ddf`, 20 Kasım 2023 tarihli bir commit: 17 node, Power Lora Loader yok, ve ComfyUI'nin
  `execution` modülüne — kendi `rgthree_config.json.default`'unda varsayılan açık — eski bir yama; bu
  ComfyUI'de yamanın aradığı fonksiyon yok.
- `main` = `d7297b42`, 6 Ekim 2026, güncel kod; `__init__.py`'si `.py.power_lora_loader`'ı import
  ediyor.
- `colab/nodes.py`'nin `install_node`'u `git clone --progress --depth 1 --recurse-submodules <adres>
  <hedef>` ile, `--branch`'sız klonluyor: varsayılan dalı, yani artık `dev`'i alıyor.
- ComfyUI'nin kendisi — bugün çıkan v0.40.0 — sebep değil: `recursive_output_delete_if_changed`
  v0.39.2'nin `execution.py`'sinde de yok.

## Değişen — `colab/nodes.py`

`SKIPPED`'ın yanında, onunla aynı biçimde bir sabit — varsayılan dalı çalıştırdığımız kod olmayan
node'un klonlandığı dal, klon adresine göre:

```python
BRANCHES = {"https://github.com/rgthree/rgthree-comfy.git": "main"}
```

Yorumu nedenini söyler: 15 Ekim'de rgthree `dev`'i, Power Lora Loader'sız 2023 ağacını, varsayılan dalı
yaptı. `install_node` adres tabloda varsa klona `--branch <dal>` ekler; yoksa komut bugünküyle aynı.
Docstring'i dalın nereden geldiğini söyler.

- **Anahtar klon adresi**, notebook'un `CUSTOM_NODES` listesindekiyle birebir:
  `"https://github.com/rgthree/rgthree-comfy.git"`. Node'u adres belirler; klasör adı notebook'un
  seçimi.
- **Yeri `nodes.py`:** hangi node'ların kurulduğu ComfyUI hücresinde kalır (CODE-STANDARD, *Notebook
  code*); bir node'un nasıl geldiği — atlanan requirement satırları gibi — `nodes.py`'de. Dal da nasıl
  gelişinin parçası; CODE-STANDARD'ın o bölümüne bunu söyleyen bir satır eklenir. Notebook'un
  `CUSTOM_NODES` listesi ve sayım testleri değişmez.
- **Dal, commit değil:** rgthree güncel kodunu `main`'de tutuyor; öteki node'lar gibi o da her yeni
  oturumda en son hâliyle gelir.

**Maliyet:** değişmez — node başına bir sığ `git clone`. `--branch` yalnız hangi dalın çekileceğini
söyler; ek bir ağ isteği ya da disk işlemi yok. Tabloya bakış O(1).

**Ne kırılabilir:**

- rgthree `main`'i silerse ya da adını değiştirirse git dalı bulamaz ve `run` hücreyi git'in kendi
  satırlarıyla durdurur — sessizce eski bir ağaç gelmez.
- Adres iki yerde yazılı: `BRANCHES`'ın anahtarı ve ComfyUI hücresinin `CUSTOM_NODES` satırı.
  Defterdeki adres değişirse bakış sessizce boşa düşer ve rgthree yine `dev`'den gelir;
  `test_notebook_installs_the_producer_groups.py`'deki
  `test_every_branch_colab_names_is_for_an_address_the_notebook_clones` `BRANCHES`'taki her adresin
  hücrede tırnaklı geçtiğini sorar.
- `install_node` yerinde duran node'a dokunmaz ("zaten var"). `dev`'den klonlanmış bir rgthree aynı
  oturumda yerinde kalır; ComfyUI `/content`'te, Colab'ın geçici diskinde durduğu için yeni oturum
  sıfırdan klonlar. Düzeltme yeni oturumda görülür.

## Test — önce kırmızı

`backend/tests/test_colab_nodes.py`'ye `test_rgthree_alone_is_cloned_from_the_branch_we_name`: var olan
`_github` sahtesi ve `commands`'iyle rgthree ve ComfyMath kurulur; rgthree'nin klonunda `--branch main`
vardır, ComfyMath'inkinde `--branch` yoktur. Kod gelmeden kırmızı — rgthree'nin klonunda `--branch`
yok —, kodla yeşil.

`backend/tests/test_notebook_installs_the_producer_groups.py`'ye
`test_every_branch_colab_names_is_for_an_address_the_notebook_clones`: `BRANCHES`'taki her adres
notebook'un `CUSTOM_NODES` hücresinde tırnak içinde durur. Anahtardan `.git` düşürülünce kırmızı,
geri konunca yeşil.

## Dokunulmayan

`queeneditor.ipynb` (`CUSTOM_NODES`, başlıktaki ve girişteki sayılar), sayım testleri, `SKIPPED`,
`colab/console.py`'nin `run`'ı, öteki node'lar, DaSiWa'nın `llama-cpp-python` zaman aşımı (backlog'da),
frontend ve `dist`.

## Bitti sayılır

Test kırmızıdan yeşile döner, `python -m pytest queen-editor -q` yeşil. Asıl görüş Colab'da, push'tan
sonra yeni bir oturumda: rgthree `main`'den klonlanır, `comfyui.log`'da rgthree için `IMPORT FAILED`
yoktur, fotoğraf üretimi `missing_node_type` olmadan çalışır.
