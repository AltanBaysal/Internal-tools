# Madde 160 — OpenRouter'ın kaydı düşülür · **tek tur**

**Tarih:** 3 Eylül 2026 · **Branch:** `feat/v6` · **Kaynak:** [v7 yol haritası, Madde
160](../plans/2026-09-03-v7-roadmap.md)

## Neden tek tur

Bu maddenin dosyası `docs/`, ve başka hiçbir şeye dokunmuyor. **Kırmızıya çevrilecek bir test yok:**
kod zaten temiz *(3 Eylül'de tarandı — depoda `openrouter` geçen tek dosya yok)*, yani yazılacak her
test **doğduğu anda yeşil** olurdu, ve doğduğu anda yeşil olan bir test tur değil.

Bir an düşünülüp bırakılan seçenek: *"kaynakta `openrouter` geçmiyor"* diye bir bekçi test. Depoda
emsali var *(`test_the_listing_tool_is_gone`)*, ama tuttuğu şey maddenin bulgusu değil — bulgu
reddin nereden geldiği, ve onu bir test tutamaz. Bekçinin engelleyeceği kaza da gerçekçi değil:
OpenRouter'ın kazayla geri gelmesi diye bir şey yok, bilerek geri getirilmesi var, ve o zaten bir
madde.

Bu, CLAUDE.md'nin iki tur kuralından bilerek ayrılan tek yer, ve sebebi burada yazıyor.

## Ne yazılıyor

`docs/superpowers/research/2026-09-03-deepseek-reddi-ve-ikinci-saglayici.md`.

Madde 149 altı commit'ti ve hepsi geri alındı; revert **docs'u da** geri aldığı için o koşunun
**ölçüsü** hiçbir yerde yazmıyor. Yazmadığı için aynı fikir yeniden önerilir — 149 tam olarak bu
bilinmediği için doğmuştu.

Belge iki bulguyu taşıyor:

1. **Ret sağlayıcıdan değil ağırlıklardan geliyor.** Aynı MIT ağırlığı DeepInfra üstünde koşuldu ve
   aynı ret geldi.
2. **Ama aynı model `start-a-scenario` akışının içinde işi yaptı.** Yani ret mutlak değil; isteğin
   çıplak mı çerçeveli mi geldiğine bağlı. Bu ikincisi uygulamayı nasıl kullandığıyla ilgili ve
   değerli olan yarısı.

Yanına, kaybolmasın diye: doğrulanmış fiyatlar, MIT lisansı ve sağlayıcı şartları, ortak havuzun
429'u *(Madde 155'in beşerli dalgası tam olarak bu bulgudan geliyor)*, ve depo dışında kalan tek şey
— Colab Secrets'taki `OPENROUTER_API_KEY`.

**Bir kod dosyasının adı geçmiyor.** Belge kodun söyleyemediğini söylüyor: depo dışında olanı, ve bir
denemenin ölçüsünü.

## Numara

149 kullanıldı ve düşürüldü. Geçmişte `feat(m149)` ve `test(m149)` commit'leri duruyor, ve bir daha
başka bir madde o adı taşımıyor.
