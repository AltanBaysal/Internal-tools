# Madde 140 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-09-02-queen-editor-m140-modeller-testler-design.md](2026-09-02-queen-editor-m140-modeller-testler-design.md)
**Kırmızı commit:** `92e0eea` — 6 kırmızı, 726 yeşil; ön yüz 28 dosya / 587 yeşil.
**Dal:** `feat/v6`

## Ne yeşile dönecek

Altı test. Beşi ek model mekanizmasını *(kutu, satır, eşleşme, süzme, disk toplamı, indirilen
dosya)*, altıncısı 138'in bıraktığı custom node sayısını.

## Tek dosya: `queeneditor.ipynb`

Üç hücre değişiyor, ve üçü de metin — çalışan kod bu turda yalnız defterin içinde.

### 1. CONFIG hücresi — kutu

Üç üretici kutusunun **altına**, kendi bloğunda:

```python
PHOTO_NOVAORANGE = False  #@param {type:"boolean"}
```

Üstünde neden kapalı geldiğini söyleyen yorum: her ek model **her açılışta** yeniden iniyor
*(`/content` runtime ile ölüyor)*, yani bedeli tek seferlik değil.

### 2. İndirme hücresi — satır, süzme, toplam

`PHOTO_EXTRA` listesi `CIVITAI_PHOTO`'nun **üstünde** duruyor, çünkü ikincisi birincisini okuyor:

```python
PHOTO_EXTRA = [
    (PHOTO_NOVAORANGE, 7, 2945776, "novaOrangeXL_rexV10.safetensors", "Nova Orange XL REX v1.0"),
]
```

Seçilenler `CIVITAI_PHOTO`'nun **kendi tanımına** ekleniyor:

```python
CIVITAI_PHOTO = [
    ...
] + [(vid, CKPT, fn, label) for on, _gib, vid, fn, label in PHOTO_EXTRA if on]
```

**Neden burada ve `civitai_jobs` satırında değil.** O satır `CIVITAI_PHOTO if INSTALL_PHOTO else []`
diye okunuyor ve bir bekçi bu cümleyi birebir arıyor — grubun listesine başka bir yoldan
ulaşılabiliyorsa, grubun anahtarı atlanabiliyor demektir. Ekleme tanımda yapılınca foto kutusu
kapalıyken ek modeller de zaten hiç denenmiyor: tek kapı, tek anahtar.

Disk toplamı aynı listeden:

```python
PHOTO_GIB = 8 + sum(gib for on, gib, *_rest in PHOTO_EXTRA if on)
```

`8` taban grubun kendisi — bugünkü sayı, olduğu gibi kalıyor. Değişen, üstüne eklenen.

### 3. Metin hücreleri — üç sayı düzeliyor

- **Giriş hücresi:** `(19 custom node)` → `(20 custom node)`. **138'in bıraktığı hata**; o koşuda
  alttaki başlık düzeltilmiş, giriş kaçmıştı, çünkü bekçi yalnız başlığa bakıyordu. Artık ikisine
  de bakıyor.
- **Giriş hücresi ve CONFIG yorumu:** foto grubunun boyutu artık değişken, o yüzden sabit `~8 GiB`
  yerine tabanı ve ek model başına bedeli birlikte söylüyor.
- **Modeller başlığı:** aynı sebep.

## Ne değişmiyor, ve neden

- **Taban model kutusuz.** Grafiğin export'u onu adıyla taşıyor, uygulama model seçilmemiş kareyi
  onunla üretiyor, panel onu grubun şartı sayıyor. Üçü de aynı dosyayı gösteriyor — kutu takmak
  üçünü birden yalanlardı.
- **LoRA kutusuz.** Grafikte sabit açık; madde yalnız Illustrious tabanlı model alıyor.
- **`model_groups.py`, uygulama, grafik, ön yüz, `dist`.** Model listesi ComfyUI'ye soruluyor;
  `checkpoints/`'a inen dosya kendiliğinden görünüyor.
- **`CIVITAI_VIDEO` / `OPEN_*` demetlerinin şekli.** `PHOTO_EXTRA` beş alanlı, ama
  `CIVITAI_PHOTO`'ya dört alanlı olarak giriyor — yani indirme döngüsünün gördüğü demet
  bugünküyle aynı, ve video yolu hiç ellenmiyor.

## Bilinen sonuç: iki model, iki ayar değil

Grafik 28 adım / CFG 6 ile sabit; yeni modelin kendi önerisi 20 adım / CFG 4.5. Örnekleyici
tutuyor *(`euler_ancestral` = Euler a)*, CFG tutmuyor, ve arayüzde CFG alanı yok. Yani ilk
karşılaştırmada yeni model bugünkünün ayarında koşacak.

Kayda geçiyor çünkü ileride *"yeni model neden daha sert çıktı"* diye sorulursa cevabın bir
parçası burada — ve düzeltmesi ayrı bir maddenin işi.

## Colab'da görülecek

Takım defterin **ne dediğini** söyler. İndirdiğini söyleyen tek şey koşu: foto ve yeni model
kutuları işaretli bir Run all, indirme özetinde `checkpoints/` altında **iki** dosya, arayüzün
**Model** listesinde **iki** satır. Sonra aynı prompt iki modelle üretilip yan yana konuyor.
