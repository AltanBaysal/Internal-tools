# Madde 144 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-09-02-queen-editor-m144-form-testler-design.md](2026-09-02-queen-editor-m144-form-testler-design.md)
**Kırmızı commit:** `ffde8d1` — 3 kırmızı, 736 yeşil; ön yüz 28 dosya / 587 yeşil.
**Dal:** `feat/v6`

## Ne yeşile dönecek

Üç test: iki grubun arasındaki ayraç ve başlık, üretici başlığı, ve model adlarının **çizilen**
kısımda geçmesi.

## Tek hücre: CONFIG'in ilk otuz satırı

Bugünkü hâl — kutular ve üstlerinde `#` yorumları:

```python
# Ne kurulacağını buradan seç: Colab bu satırları ... çizer.
#   fotoğraf ~2 GiB + seçtiğin her model ~7 GiB · video ~39 GiB ...
INSTALL_PHOTO = False  #@param {type:"boolean"}
...
# Hangi foto modellerinin ineceğini buradan seç — hepsi boş gelir ...
#   nova3DCG: 3DCG / 2.5D · novaOrange: detaylı tenli anime · novaAnime: anime
PHOTO_NOVA3DCG = False  #@param {type:"boolean"}
```

Yeni hâl — aynı bilgi, iki okuyucuya bölünmüş:

```python
#@markdown ### Üreticiler
#@markdown En az birini işaretle. Video ~39 GiB · ses ~9 GiB.
INSTALL_PHOTO = False  #@param {type:"boolean"}
...

#@markdown ---
#@markdown ### Fotoğraf modelleri
#@markdown Hepsi boş gelir — istediğini işaretle, hiçbirini seçmezsen defter durur.
#@markdown Grubun ortak dosyaları ~2 GiB; her model ~7 GiB daha, üçü birden ~23 GiB (T4'te dar).
#@markdown - **nova3DCG** — 3DCG / 2.5D
#@markdown - **novaOrange** — detaylı tenli anime
#@markdown - **novaAnime** — anime
# Kapalı gelmelerinin sebebi formda yazmıyor, çünkü kullanıcının kararını değiştirmiyor:
# /content runtime ile ölüyor, yani her model HER AÇILIŞTA yeniden iniyor. Bedeli tek seferlik
# değil, ve bunu bilen kişi defteri düzenleyen kişi.
PHOTO_NOVA3DCG = False  #@param {type:"boolean"}
```

## Kopya bırakılmıyor

Kullanıcıya bakan her cümle `#`'ten **çıkıyor**, `#@markdown`'a giriyor. Geride kalan `#` yorumu
tek bir şey söylüyor ve o formda işi olmayan şey: `/content`'in runtime ile ölmesi.

İkisine birden yazmak bir kopya olurdu, ve kopya bayatlayan şeydir.

## Boyut cümlesi iki parçaya bölünüyor

Bugün tek satır: *"fotoğraf ~2 GiB + seçtiğin her model ~7 GiB · video ~39 GiB · ses ~9 GiB"*.

Bu satır iki soruyu birden cevaplıyor, ve tam olarak karışan şey o. Üretici başlığının altında
video ile ses kalıyor; fotoğrafın maliyeti model başlığının altına geçiyor, çünkü orada bir seçime
bağlı ve orada okunması gerekiyor.

## Değişmeyen

- **Hiçbir `assert`, liste, indirme ya da kutu adı.** `PHOTO_*` satırlarının kendisi harfi harfine
  aynı — desen `=` öncesinde tam bir boşluk istiyor ve hizalama yok.
- **Kutu sırası.** Kontrol satırı sırayı takip ediyor, ve testi onu ölçüyor.
- **Defterin geri kalanı, uygulama, grafik, ön yüz, `dist`.**

## Colab'da görülecek

Sağdaki form panelinde üstte **Üreticiler** başlığı ve üç kutu, altında yatay çizgi, altında
**Fotoğraf modelleri** başlığı, açıklama, hangi modelin ne olduğunu söyleyen üç maddelik liste ve
üç kutu.

**Takım bunu doğrulayamaz** — yalnız satırların doğru yerde durduğunu söyler. Çizimi gören tek
göz kullanıcının gözü.
