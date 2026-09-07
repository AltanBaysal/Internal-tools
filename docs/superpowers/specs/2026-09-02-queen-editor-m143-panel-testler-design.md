# Madde 143 — Panel seçilen modeli sayar · Tur 1 (test) — Tasarım

**Kaynak:** [v6 yol haritası](../plans/2026-09-01-v6-roadmap.md), Madde 140'ın bıraktığı sonuç
**Dal:** `feat/v6`
**Bu tur yalnız test yazar.**

## Problem

Madde 140 her foto checkpoint'ini kullanıcının seçimine çevirdi. **Panel bu değişikliği kaçırdı:**
[model_groups.py](../../../queen-editor/backend/features/producers/domain/model_groups.py) foto
grubunun şartı olarak hâlâ **tek bir dosyayı adıyla** sayıyor —
`nova3DCGXL_ilV90.safetensors`.

Sonucu: `PHOTO_NOVA3DCG` kutusunu boş bırakıp yalnız Orange ya da Anime alan bir kullanıcı,
**Üreticiler panelinde "kurulu değil" görüyor, oysa üretim çalışıyor.**

140'ta bilerek taşındı, çünkü uygulama kodu ve maddenin konusu defterdi. Bu madde onu kapatıyor.
Numarası **143** — 142 tüketilmiş durumda *(açıldı ve düşürüldü)*, ve belgenin kuralı numaraların
kaymaması.

## Sorunun kökü: grup tek bir soru sorabiliyor

`list_producers` her satır için **aynı** soruyu soruyor: *"bu dosya bu klasörde var mı?"* Bu, foto
grubunun dört destek dosyası için doğru soru — LoRA, Remacri, dedektör ve SAM adlarıyla yükleniyor,
ve biri eksikse grafiğin bir dalı çalışmıyor.

Checkpoint için **yanlış** soru. Doğrusu: *"bu klasörde çalışabileceğim bir model var mı?"*

## Çözüm: satırın iki şekli olur

Bir grup satırı bundan sonra ikisinden biri:

| Şekil | Anlamı | Örnek |
|---|---|---|
| `{"folder", "name"}` | **tam olarak bu dosya** | LoRA, Remacri, dedektör, SAM |
| `{"folder", "suffix"}` | **bu türden herhangi bir dosya** | foto checkpoint'i |

Bilgi tek yerde kalıyor — ikinci bir yapı, aynı şeyi iki belgeye bölmek olurdu. Ve satırın hangi
soruyu sorduğu satıra bakınca görülüyor.

`ModelFiles` portu bunun için ikinci bir soru kazanıyor: `has_any(folder, suffix)`.

## `suffix`, çünkü yarım indirme model değil

*"Klasörde bir şey var mı"* yetmiyor: defter dosyaları `<ad>.part` olarak indirip **ancak
doğruladıktan sonra** gerçek adına taşıyor, yani yarıda kesilen bir koşu `checkpoints/` içinde bir
`.part` bırakıyor. Uzantıya bakmayan bir kontrol onu model sayar ve panel yine yalan söylerdi —
bu sefer ters yönde.

`.safetensors` ile biten dosya aranıyor; `nova.safetensors.part` **`.part` ile bitiyor**, yani
kendiliğinden dışarıda kalıyor. Uzantı satırda yazılı, kodun içinde saklı değil: grafiğin yüklediği
şey o, ve bunu bilen yer grubun kendisi.

## Kaybolan bir kontrol var, ve yerini almış durumda

`test_every_file_the_panel_counts_is_fetched_by_the_notebook` grubun saydığı her dosyanın defterde
anıldığını arıyor. Checkpoint satırı adını bırakınca o kontrol checkpoint'leri kapsamıyor.

**Kayıp değil, taşınma:** aynı dosyada `test_the_notebook_offers_every_photo_model` üç modeli de
adıyla ve version id'siyle çiviliyor — üstelik daha sıkı, çünkü sürüm numarasını da tutuyor.

## Kırmızıya dönecek iddialar

1. **Foto grubunun checkpoint satırı ad taşımıyor**, uzantı taşıyor.
2. **Hangi model seçilmiş olursa olsun üretici kurulu sayılıyor** — klasörde bir `.safetensors`
   varsa yeter.
3. **Boş klasör kurulu değil.**
4. **Yarım indirme model sayılmıyor** — `.part` kurulu demek değil.
5. **Grup satırının iki şekli var, ve ikisi de adres taşımıyor** — bugünkü tek şekil iddiası
   genişliyor. Adres yasağı duruyor: adresler defterde.
6. **Defter kontrolü adsız satırda patlamıyor** — bugün `row["name"]` diyor, ve adsız bir satırda
   `KeyError` verir.

## Kapsam dışı

- **Grafiğin fallback'i.** Model seçilmemiş eski bir kare grafiğin export'undaki checkpoint'i
  istiyor; o inmemişse render ComfyUI'nin kendi *"model bulunamadı"* hatasıyla düşüyor. Ayrı bir
  soru, ve **davranışı yanlış değil** — yüksek sesle ve doğru sebeple düşüyor. Değiştirilecekse
  değişecek şey mesaj, davranış değil.
- **Video ve ses grupları.** İkisinde de her dosya adıyla yükleniyor; seçim yok, soru değişmiyor.
- **Defter, grafik, ön yüz, `dist`.**
