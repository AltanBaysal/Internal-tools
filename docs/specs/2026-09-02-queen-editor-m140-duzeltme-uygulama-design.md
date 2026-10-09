# Madde 140 · Düzeltme · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-09-02-queen-editor-m140-duzeltme-testler-design.md](2026-09-02-queen-editor-m140-duzeltme-testler-design.md)
**Kırmızı commit:** `4d8af7f` — 5 kırmızı, 728 yeşil; ön yüz 28 dosya / 587 yeşil.
**Dal:** `feat/v6`

## Ne yeşile dönecek

Beş test: liste adı ve içeriği, kutu-satır eşleşmesi, anahtarla süzme, hiç model seçilmeme
kontrolü, ve disk tabanı.

## Tek dosya: `queeneditor.ipynb`, iki hücre

### CONFIG — iki kutu ve bir kontrol

`PHOTO_NOVA3DCG` kutusu doğuyor, `PHOTO_NOVAORANGE`'ın **üstünde**: sıra listedekiyle aynı kalıyor,
ve kontrol satırı kutuları o sırayla diziyor.

```python
PHOTO_NOVA3DCG = False  #@param {type:"boolean"}
PHOTO_NOVAORANGE = False  #@param {type:"boolean"}

assert not INSTALL_PHOTO or PHOTO_NOVA3DCG or PHOTO_NOVAORANGE, (...)
```

**Hizalanmıyorlar, ve sebebi test.** Deseni `^(PHOTO_\w+) = (?:True|False)  #@param`: adla `=`
arasında **tam bir** boşluk, `False` ile `#@param` arasında **iki**. İki adı `=` hizasına getirmek
kısa olanı desenin dışına atardı. *(Spec'e önce hizalı yazılmıştı; desen okununca düzeltildi.)*
Üstteki `INSTALL_*` üçlüsü de hizalı değil — adları aynı boyda olduğu için fark edilmiyor.

Kontrolün mesajı ne yapılacağını söylüyor, sebebi değil: kullanıcı kutuyu görüyor, eksik olanın ne
olduğunu değil ne yapacağını bilmesi gerekiyor.

### İndirme hücresi — `PHOTO_MODELS`, `CIVITAI_PHOTO`, `PHOTO_GIB`

`PHOTO_EXTRA` → `PHOTO_MODELS`, ve taban model satır olarak içine giriyor:

```python
PHOTO_MODELS = [
    (PHOTO_NOVA3DCG,   7, 2744564, "nova3DCGXL_ilV90.safetensors",    "Nova 3DCG XL IL v9.0"),
    (PHOTO_NOVAORANGE, 7, 2945776, "novaOrangeXL_rexV10.safetensors", "Nova Orange XL REX v1.0"),
]
```

`CIVITAI_PHOTO`'da artık **yalnız LoRA** kalıyor — o bir model değil, grafiğin sabit açık dalı —
ve seçilen checkpoint'ler aynı yerde ekleniyor:

```python
CIVITAI_PHOTO = [
    (1552087, LORA, "USNR_STYLE_ILL_V1_lokr3-000024.safetensors", "USNR STYLE ILL v1.0"),
] + [(vid, CKPT, fn, label) for on, _gib, vid, fn, label in PHOTO_MODELS if on]
```

Ekleme yeri değişmiyor ve sebebi de değişmiyor: `civitai_jobs` satırı
`CIVITAI_PHOTO if INSTALL_PHOTO else []` diye okunuyor, ve bir bekçi o cümleyi birebir arıyor.

Disk tabanı `8`'den `2`'ye:

```python
PHOTO_GIB = 2 + sum(gib for on, gib, *_rest in PHOTO_MODELS if on)
```

`2` grubun her hâlükârda aldığı dört dosya — LoKr, Remacri, yolov9c, SAM; ölçülen toplamları
1.5 GiB'ın altında, hücrenin kendi kuralı gereği yukarı yuvarlanıyor.

## Sayılar ne oluyor

| Seçim | `need` | Gereken boş disk |
|---|---|---|
| tek model | 9 | 14 GiB |
| iki model | 16 | 21 GiB |

Tek model bugünkü 8'in bir üstünde: tahmin **yukarı** kayıyor, ve bu doğru yön — düşük tahmin diski
doldurup yarım dosya bırakıyor, yüksek tahmin bir uyarıya mal oluyor.

## Metin hücreleri

Giriş ve modeller başlığı foto tarafını yeniden anlatıyor: kutular model başına, hepsi boş geliyor,
hiçbiri seçilmezse defter duruyor. Custom node sayısı ellenmiyor — o bir önceki turda düzeldi.

## Taşınan sonuç

Taban modelin kutusu boş bırakılırsa **Üreticiler paneli "kurulu değil" der, oysa üretim çalışır**:
`model_groups.py` o dosyayı foto grubunun şartı sayıyor. Defter doğru, panel yanlış. Düzeltmesi
uygulama kodu ve kendi maddesi; buraya karıştırılırsa hangi değişikliğin neyi bozduğu ayrılamaz.

## Değişmeyenler

- **`model_groups.py`, üretici, grafik, ön yüz, `dist`.**
- **`CIVITAI_VIDEO` / `OPEN_*` demetlerinin şekli** — `PHOTO_MODELS` beş alanlı ama
  `CIVITAI_PHOTO`'ya dört alanlı giriyor, yani indirme döngüsünün gördüğü demet aynı.
- **LoRA** — kutusuz, `CIVITAI_PHOTO`'da.

## Colab'da görülecek

Foto kutusu işaretli, model kutuları boş → defter **CONFIG'de durur** ve ne yapılacağını söyler.
Bir model işaretli → o iner. İkisi de → ikisi iner, ve **Model** listesinde iki satır çıkar.
