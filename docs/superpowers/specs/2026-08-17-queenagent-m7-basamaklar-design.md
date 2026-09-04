# Madde 7 — Kenar çubuğu daralma basamakları · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 7](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 10 (`değişecek` · görsel · **kesin**, Y1·Y2·Y3) · `HANDOFF.md` §8
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 0 · Açık soru yok, ama testin cinsi karara bağlanıyor

Fark 10 sayıları tek tek veriyor: **280 → 226 → 198 → 172px**, iç boşluk yalnız en dar basamakta
sıkışıyor. Eşikler `HANDOFF.md` §8'in kendi üç eşiği: **1000px**, **780px**, **640px**.

**Bu maddenin davranışı yok, ölçüsü var.** jsdom medya sorgularını hesaplamaz ve stil dosyasını hiç
yüklemez, dolayısıyla "pencere daralınca kenar çubuğu 198px olur" diye bir birim testi yazılamaz.
İki dürüst seçenekten biri gerekiyordu: testsiz bırakıp Madde 35'in elle turuna bırakmak, ya da
**ölçüleri stil dosyasının kendisinden okuyan bir kilit testi** yazmak.

**Karar: kilit testi yazılıyor.** Gerekçe: bu sayılar bir tasarım sözleşmesinden geliyor ve tek
koruyucuları yorum satırı olurdu. Test bir davranış kanıtlamaz — sayıların yazılı olduğu yerle
uygulandığı yerin ayrışmasını engeller. Ne olduğu testin adında açıkça durur ve **gerçek doğrulama
Madde 35'in elle turudur**.

---

## 1 · Ne değişir

| Genişlik | Kenar çubuğu | İç boşluk |
|---|---|---|
| varsayılan | 280px | 18px 14px |
| ≤ 1000px | 226px | 18px 14px |
| ≤ 780px | 198px | 18px 14px |
| ≤ 640px | 172px | **16px 10px** |

Bugün tek bir `@media (max-width: 1100px)` bloğu hem genişliği 208px'e indiriyor hem iç boşluğu
sıkıştırıyor. O bloktan **yalnız `.sidebar` kuralı** çıkar; bloğun geri kalanı (ray alta iner, ızgara
tek sütuna düşer, yatay dolgu daralır) **olduğu gibi kalır** — yerleşimin eşiklerini yeniden kurmak
Madde 33'ün işi ve burada ona dokunulmaz.

Bu, geçici olarak iki eşik ailesinin yan yana durması demektir: yerleşim 1100px'te, kenar çubuğu
1000/780/640'ta. Bilerek: bu maddenin kapsamı kenar çubuğu, Madde 33 ikisini tek ölçüde birleştirir.

---

## 2 · Katman denetimi

Yalnız `frontend/src/features/workspace/workspace.css`. Yeni bileşen, yeni prop, yeni bağ yok;
bağımlılık yönü ve üç yasak bu maddede hiç anılmıyor.

---

## 3 · Kabul ölçütü

1. `.sidebar` varsayılan genişliği 280px'tir.
2. Üç medya sorgusu sırasıyla 1000, 780 ve 640px'te 226, 198 ve 172px verir.
3. İç boşluk yalnız 640px bloğunda değişir.
4. 1100px bloğu artık `.sidebar`'a dokunmaz, geri kalanı aynen durur.

## 4 · Risk

Kilit testinin biçime duyarlı olması: stil dosyası yeniden biçimlendirilirse test kırılabilir. Bu
yüzden test tam metin değil, **her bloğun içindeki `.sidebar` genişliğini** arar.
