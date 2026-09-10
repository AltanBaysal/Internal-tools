# Madde 183 · uygulama turu — prompt yazan model Grok 4.3 olur

**Kaynağı:** [test turu spec'i](2026-09-06-queenagent-m183-grok-testler-design.md).
Commit `8f48a6d` 5 kırmızı bıraktı.

---

## İki satır

`config.py`'de `MODELS`'in Grok satırı ve `PROMPT_MODEL`. Adres ve anahtar aynı kalıyor; değişen
yalnız kimlik.

`grok-build-0.1` **kalkıyor, taşınmıyor.** Kullanıcı kararı: onu kullanan tek yer `PROMPT_MODEL`'di
ve o da yeni adı gösteriyor, dolayısıyla kalan bir satır ölü yapılandırma olurdu. `engine_for`
bilinmeyen bir kimliği zaten varsayılana düşürüyor, yani eski adı taşıyan bir kayıt — sohbetin
modelini adlandıran kayıtlar; yazar hiçbir yere yazılmıyor — cevapsız kalmıyor.

## Yorumun düzeltilmesi

`MODELS`'in üstündeki yorum *"Madde 82 buraya tek model yazdı ve Madde 146 üç yaptı"* diyor. Sayı
üçte kalıyor, ama satırın hangi Grok olduğu değişti; yorum kimlik saymıyor, dolayısıyla dokunmuyor.

`PROMPT_MODEL`'in yorumu *"ne yazacağı için seçilir, nasıl akıl yürüttüğü için değil"* diyor — bu
maddeden sonra **daha da doğru**: xAI'ın listesinde `grok-4.5` ve `grok-4.6` da var, ikisi daha yeni
ve daha pahalı, ve seçilmeyen onlar. O gerekçe bir cümleyle yazılıyor, çünkü kod *"neden 4.3"*
sorusuna kendi başına cevap veremiyor.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **837 yeşil.** 5 kırmızının hepsi dönmeli.
3. Öteki üç takım: **589 · 739 · 591.** `dist` derlenmiyor — bu madde frontend'e dokunmuyor.
