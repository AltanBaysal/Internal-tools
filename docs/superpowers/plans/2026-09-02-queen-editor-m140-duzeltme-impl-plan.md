# Madde 140 · Düzeltme · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-02-queen-editor-m140-duzeltme-uygulama-design.md](../specs/2026-09-02-queen-editor-m140-duzeltme-uygulama-design.md)
**Dal:** `feat/v6`
**Kırmızı commit:** `4d8af7f`
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. CONFIG — kutular ve kontrol.

Bugünkü tek kutunun yerine ikisi, ve altına kontrol:

```python
# Hangi foto modellerinin ineceğini buradan seç — hepsi boş gelir, istediğini işaretle. Her biri
# ~7 GiB, ve /content runtime ile öldüğü için her açılışta yeniden iner: bedeli tek seferlik değil.
# Fotoğraf kutusu kapalıyken hiçbiri dikkate alınmaz.
PHOTO_NOVA3DCG   = False  #@param {type:"boolean"}
PHOTO_NOVAORANGE = False  #@param {type:"boolean"}

# Photo ticked with every model box empty is a renderer with nothing to render with. Asked here
# like every other gate: a second in CONFIG beats ten minutes after ComfyUI's install.
assert not INSTALL_PHOTO or PHOTO_NOVA3DCG or PHOTO_NOVAORANGE, (
    "❌ Fotoğraf seçildi ama hiç model işaretlenmedi — yukarıdaki model kutularından "
    "en az birini işaretle ve hücreyi tekrar çalıştır."
)
```

**Hizalamaya dikkat:** desen `False` ile `#@param` arasında **iki boşluk** istiyor. `=` öncesi
hizalama serbest.

→ A1, A2 ve B testleri yeşile döner.

## B. İndirme hücresi — liste, ekleme, toplam.

`PHOTO_EXTRA` bloğu `PHOTO_MODELS` olur ve taban modeli alır:

```python
# Every photo checkpoint, each behind its own CONFIG box: which ones come down is the user's pick,
# and CONFIG stops the run when none of them was picked.
# Illustrious-based only -- the graph's lora is switched on for good and would not load onto
# another base, so a checkpoint from another family is its own item rather than a row here.
# (switch, gib, version_id, filename, label)
PHOTO_MODELS = [
    (PHOTO_NOVA3DCG,   7, 2744564, "nova3DCGXL_ilV90.safetensors",    "Nova 3DCG XL IL v9.0"),
    (PHOTO_NOVAORANGE, 7, 2945776, "novaOrangeXL_rexV10.safetensors", "Nova Orange XL REX v1.0"),
]
```

`CIVITAI_PHOTO`'da yalnız LoRA kalır:

```python
# The lora is not one of the choices above: the graph has it switched on, so it comes with the
# group like the three open files do.
CIVITAI_PHOTO = [
    (1552087, LORA, "USNR_STYLE_ILL_V1_lokr3-000024.safetensors", "USNR STYLE ILL v1.0"),
# Appended to the list itself rather than to civitai_jobs below: that line reads
# `CIVITAI_PHOTO if INSTALL_PHOTO else []`, and a group whose rows can be reached by a second
# route is a group whose switch can be walked around.
] + [(vid, CKPT, fn, label) for on, _gib, vid, fn, label in PHOTO_MODELS if on]
```

Toplam:

```python
# The checkpoints are the user's pick, so only what the group always takes is in the base: the
# lora, the upscaler, the detector and the SAM, together under 1.5 GiB and rounded up like
# everything else here.
PHOTO_GIB = 2 + sum(gib for on, gib, *_rest in PHOTO_MODELS if on)
```

→ A3, C ve D testleri yeşile döner.

## C. Metin hücreleri.

Giriş hücresi ve modeller başlığı foto tarafını yeniden anlatır: model başına kutu, hepsi boş,
hiçbiri seçilmezse durur. **Custom node sayısına dokunulmaz** — bir önceki turda düzeldi ve testi
onu tutuyor.

## D. Koşuldu: **733 yeşil, 0 kırmızı.**

`python -m pytest queen-editor -q` — beş kırmızının beşi döndü, tek seferde, ara kırmızı yok.
Adı geçen bekçilerin dördü de yeşil kaldı:
`test_every_file_the_panel_counts_is_fetched_by_the_notebook` *(`nova3DCGXL` defterde anılmaya
devam ediyor, yalnız hücre içindeki yeri değişti)*, `test_an_unticked_group_costs_no_bytes`
*(`civitai_jobs` satırı ellenmedi)*, `test_the_intro_agrees_with_the_custom_node_list` ve kardeşi,
ve `test_the_cookie_is_only_demanded_by_the_groups_that_are_gated`.

**Bir hata yazmadan yakalandı.** Spec'e kutular hizalı yazılmıştı — `PHOTO_NOVA3DCG   = False` —
ama testin deseni adla `=` arasında **tam bir** boşluk istiyor. Desen defter yazılmadan okundu,
spec düzeltildi, hizalama kaldırıldı.

`npm test --prefix queen-editor/frontend` — **28 dosya, 587 yeşil.**

## E. Yeşil commit.

`queeneditor.ipynb` ve bu turun iki belgesi.

`dist` yeniden derlenmiyor: ön yüz değişmiyor.

## Bilerek yapılmayanlar

**`model_groups.py`, üretici, grafik, ön yüz, `dist`.**

**Panelin yalanı** — taban model seçilmezse **Üreticiler** paneli "kurulu değil" der. Bilerek
taşınıyor, yol haritasında ve iki spec'te yazılı, ayrı bir maddenin işi.

**Üçüncü model** — mekanizma sayıya bağlı değil; adresi geldiğinde bir satır, bir kutu, ve
kontrole bir isim.
