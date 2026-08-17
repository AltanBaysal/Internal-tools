# Madde 19 — Sohbet ve dosya silme onaya geçer · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 19](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 24, 27, 29, 31 · **karar 16, 17** · `HANDOFF.md` §6
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 1 · Tek bir silme dili

Bugün üç ayrı dil var: proje Madde 18'in kutusuyla, sohbet **tarayıcının** kutusuyla, dosya ise
**hiç sormadan** siliniyor ve arkasından "File deleted. / Undo" şeridi bırakıyor.

Karar 16 ve 17 bunu tek dile indiriyor: **hepsi sorar, hiçbirinde geri alma yoktur.**

| Ne | Bugün | Bundan sonra |
|---|---|---|
| Proje | Madde 17'nin kutusu | değişmiyor |
| Sohbet | `window.confirm` | Madde 17'nin kutusu |
| Dosya | sormadan siler, Undo sunar | Madde 17'nin kutusu, Undo yok |

**Diskte hiçbir şey kaybolmuyor** — üçü de `trash/`e taşıyor. FOUNDATION'ın "ya onay ya geri alma,
asla ikisi de değil" kuralı onay tarafından karşılanıyor.

**Sohbet bugün gerçekten siliniyor.** `FileChatStore.delete` dosyayı diskten kaldırıyor ve
yanındaki yorum sebebini "tasarım geri almayı dosyaya, onayı sohbete veriyor" diye yazıyor. O
gerekçe karar 16 ile ortadan kalktı, ve geriye kullanıcının **kendi yazdığı** cümlelerin kalıcı
olarak yok edilmesi kaldı — QueenAgent'ın ürettiği dosya çöpte dururken. FOUNDATION ilke 1
("kullanıcının emeği kutsaldır", "silinen taşınır, yok edilmez") bunu yasaklıyor ve yol haritası da
"ikisi de `trash/`e taşımayı sürdürür" diyor. **Sohbet de `trash/`e taşınıyor**, dosyayla aynı
klasöre ve aynı `unique_name` kuralıyla.

---

## 2 · Cümleler

**Sohbet:** `Delete this chat?` · `Its files stay in the project.` · "Delete chat"
Cümle bugünkü tarayıcı kutusundan olduğu gibi geliyor; söylediği şey doğru ve tasarım onu
değiştirmiyor.

**Dosya:** `Delete "plan.md"?` · `The file is moved out of the project. This can't be undone.` ·
"Delete file"
Tasarım dosya için bir cümle yazmıyor — silmeyi onaysız kurguladığı için ihtiyacı da yoktu. Bu
yüzden proje kutusunun cümlesi dosyaya uyarlanıyor: **ne olduğu** ve **geri alınamayacağı**. Uydurma
bir sebep yok; söylenen şey gerçekten olan şey.

---

## 3 · Ne sökülüyor

- **`FileStrip` bileşeni tümüyle gidiyor** (fark 31 düşüyor). Şeridin rengi ve yarıçapı üzerine olan
  fark artık konusuz: şerit yok.
  **Şeridin ikinci işi kalıyor:** başarısız bir silmenin hata satırı. Şerit onu da taşıyordu; onunla
  birlikte atılsaydı silme sessizce başarısız olurdu. Yerinde tek satırlık bir hata kalıyor —
  teklif değil, sunucunun cümlesi.
- **`useFiles`'ın `deleted` ve `undo`'su gidiyor.** Çöpteki ad artık hiçbir yerde tutulmuyor — onu
  tutmanın tek sebebi geri alma teklifiydi.
- **Arka uçta geri yükleme sökülüyor:** `POST …/trash/<trashed>/restore` yolu, `restore_file`
  kullanım senaryosu, `FileStore.restore` portu ve uygulaması.
- **`NameTaken` hatası** yalnız geri yüklemede kullanılıyorsa o da gidiyor.

**Çöpteki adı artık kimse okumuyor**, ama silme cevabı onu döndürmeye devam ediyor: diskte ne olduğunu
söyleyen tek cümle o, ve Madde 18'in proje silmesi de aynı biçimi kullanıyor.

---

## 4 · Sohbet satırının "×"i (fark 24)

Bugün saydam duruyor, hover ya da odakla beliriyor → tasarımda **her zaman görünür** (`#B5ADA2`),
üstüne gelince kırmızıya döner ve arkasında yuvarlatılmış bir zemin belirir.

Bu, kenar çubuğundaki ⋯ ile çelişmiyor: araştırma bunu ayrıca not ediyor — tasarım iki denetimi
bilerek ayırmış. Sohbet satırındaki × bir listenin kendi işi, ⋯ ise bir menü kapısı.

---

## 5 · Onay kimin işi

Kutuyu App açıyor, Madde 18'deki `confirming` yuvasının aynısıyla. `ProjectScreen` ve `FileRail` gibi
ekranlar yalnız "sil" diye haber veriyor; ne soruyorlar ne siliyorlar.

Bu, silme çağrısının **tek yerde** durmasını sağlıyor: üç silme de App'te aynı yuvadan geçiyor,
dolayısıyla dördüncüsü eklendiğinde soracak yer de belli.

---

## 6 · Katman denetimi

Arka uçta **eksiltme** var: bir yol, bir kullanım senaryosu, bir port yöntemi ve bir hata gidiyor.
Yön değişmiyor.

Ön yüzde bir bileşen siliniyor, bir kanca sadeleşiyor, App bir yuvayı daha kullanıyor.

---

## 7 · Kabul ölçütü

1. Sohbetteki "×" kutuyu açar; `window.confirm` uygulamada hiçbir yerde çağrılmaz.
2. Dosyadaki "×" kutuyu açar ve onaylanana kadar hiçbir istek gitmez.
3. Onaydan sonra dosya listeden düşer, diskte `trash/` altındadır.
4. Hiçbir yerde "Undo" yoktur; `FileStrip` diye bir bileşen yoktur.
5. Geri yükleme adresi `url_map`'te yoktur.
6. Sohbet satırının "×"i hover beklemez.

## 8 · Risk

Geri alma sökülüyor, yani yanlışlıkla silinen bir dosya artık uygulamadan geri gelmiyor. Karşılığı
onay kutusu ve `trash/` klasörü: dosya diskte duruyor, kullanıcı onu dosya yöneticisinden geri
koyabilir. Karar 16 bu takası açıkça yapıyor.
