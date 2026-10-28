# Bölüm 7 — Arayüz incelemesi: üç geçişli metodoloji

**Tarih:** 2026-08-04 · **Durum:** onay bekliyor
**Beslediği spec:** [2026-08-04-queen-editor-bolum7-arayuz-design.md](../specs/2026-08-04-queen-editor-bolum7-arayuz-design.md)
**Amaç:** o spec'teki eleman envanterini eksiksiz hâle getirmek ve `? tasarımdan doğrula`
satırlarını kapatmak.

## Neden üç geçiş

Tek yönlü bir karşılaştırmanın kör noktası vardır ve kör nokta yöne bağlıdır. Tasarımdan koda
bakan **bizde olmayanı** bulur, bizim **uydurduğumuzu** göremez — tasarımda karşılığı olmadığı için
oraya hiç bakmaz. Koddan tasarıma bakan tam tersini yaşar. İkisi de statik olduğu için, doğru
görünüp yanlış zamanlanan şeyi (tepkisiz buton, temizlenmeyen hata) hiçbiri görmez.

Üç geçiş bu üç kör noktayı kapatır. Geçişler **birbirinden bağımsız** yürütülür: biri diğerinin
bulgusuna bakmaz, yoksa ikinci geçiş birincinin doğrulaması hâline gelir ve bağımsızlığın verdiği
güven kaybolur.

## Ön koşul

**A ve B tasarım kaynağı olmadan çalışmaz.** Gereken dosyalar: `Queen Editor Basit v1.html` ve
onun içe aktardıkları — `simple-screens.jsx`, `simple-app.jsx`, `wireframe-kit.jsx`, `styles.css`,
`design-canvas.jsx`, `tweaks-panel.jsx`.

Şu an erişim yok: `claude_design` MCP sunucusu bu oturumda bağlı değil ve tasarım linki kimlik
doğrulaması istiyor (HTTP 403). Kaynak ya MCP bağlanarak ya da dosyalar `queen-editor/design/`
altına konarak sağlanmalı. **C bu koşula bağlı değildir, hemen koşabilir.**

---

## Geçiş A — Tasarımdan koda

**Birim:** tasarımdaki her görsel eleman.

**Yürüyüş:** `simple-screens.jsx` ekran ekran, yukarıdan aşağı. Her elemanda durulur ve bizim
kodda karşılığı aranır. Sıra tasarımın sırasıdır, bizim dosya düzenimiz değil.

**Her eleman için sorulan:** bizde var mı · aynı yerde mi · aynı biçimde mi (renk, boyut, boşluk,
metin) · tasarımın çizdiği **bütün durumlarda** var mı (boş, dolu, yükleniyor, hatalı, pasif).

**Kayıt:** `ekran · eleman · tasarımdaki hâli · bizdeki karşılığı veya "yok" · fark`.

**Bulur:** eksik elemanlar, eksik durumlar, yanlış renk/yerleşim/metin.
**Kördür:** bizim uydurduğumuz, tasarımda hiç bulunmayan şeylere.

## Geçiş B — Koddan tasarıma

**Birim:** bizim kodumuzdaki her görsel karar.

**Yürüyüş:** `frontend/src/` altındaki dokuz `.jsx` dosyası tek tek. Her `style={...}`, her
`className`, her koşullu render için tek soru: **"bunun tasarımda dayanağı ne?"**

**Ayrıca:** her sabit değer (renk, boşluk, yazı boyu) bir tasarım token'ına mı bağlı yoksa elle mi
yazılmış. `vendor/kit.jsx` ve `vendor/styles.css`'in hangi parçalarının hiç kullanılmadığı da
buraya yazılır — kullanılmayan bir ilkel çoğu zaman "elle yeniden yazılmış" demektir.

**Kayıt:** `dosya:satır · ne yapıyor · tasarımdaki dayanağı veya "dayanaksız" · karar`.

**Bulur:** uydurulmuş desenler, token yerine elle yazılmış değerler, tasarımın konuşmadığı yerde
aldığımız sessiz kararlar.
**Kördür:** hiç yazmadığımız koda — yani eksik elemanlara.

## Geçiş C — Durum ve tepki yürüyüşü

**Birim:** iki tür çift — `(ekran, durum)` ve `(kullanıcı eylemi, anında tepki)`.

**Durumlar:** her ekran için ilk açılış · veri geliyor · boş · dolu · hata · yeniden deneme.
**Eylemler:** uygulamayı aç · projeye gir · yeni proje · Üret · Durdur · yenile (F5) · sunucu
öldüğünde.

**Her çift için sorulan:** bugün ekranda ne oluyor · kullanıcı bundan ne anlıyor · anladığı şey
doğru mu · beklerken bir işaret var mı.

**Kayıt:** `ekran veya eylem · durum · bugün ne oluyor · kullanıcı ne anlıyor · doğru mu`.

**Bulur:** eksik yükleniyor durumları, yanlış mesajlar, tepkisiz butonlar, temizlenmeyen hatalar,
çift gönderim.
**Kördür:** salt görsel sapmalara — durum doğru ama rengi yanlışsa C bunu görmez.

---

## Karşılaştırma

Üç geçiş bittikten sonra bulgular tek tabloda birleştirilir ve şu kovalara ayrılır:

| Kova | Anlamı | Ne yapılır |
|---|---|---|
| A ∩ B ∩ C | Üç bağımsız geçişin de gördüğü | Tartışmasız iş |
| A ∩ B | Kesin görsel fark | Alınır |
| Yalnız A | Muhtemel eksik eleman | Doğrulanıp alınır |
| Yalnız B | Muhtemel bizim fazlamız | **Karar gerekir** — tasarıma mı çekilecek, yoksa bilinçli sapma olarak mı kalacak |
| Yalnız C | Davranış boşluğu | Alınır; tasarımın hiç çizmediği bir şey olabilir |
| **Çelişki** | A "tasarımda var" derken B "dayanaksız" diyorsa | Biri yanlış okumuştur — o satır elle açılıp bakılır |

"Yalnız B" kovası özellikle önemli: gerçek bir uygulama artboard değil, bazı sapmalar **kalmalı**.
Kaydırma davranışı, SPA yönlendirmesi ve sabit üst bar bunun örnekleri. Bu kovada varsayılan
"tasarıma çek" değil, "sor".

Çelişki sayısı ayrıca bir kalite ölçüsüdür: sıfıra yakınsa üç geçiş de güvenilir okumuş demektir.

## Çıktı

Tek dosya: birleştirilmiş bulgu tablosu + kova ayrımı. Bu tablo spec'in §1 envanterinin yerine
geçer ve `? tasarımdan doğrula` satırlarının hepsini kapatır. Spec o tabloya göre güncellenir.

## Maliyet

Üç geçiş, en pahalı seçenek. C tek başına kısa (kod zaten okundu). A ve B tasarım kaynağının
tamamını okumayı gerektirir — asıl yük orada. Karşılığında elde edilen, tek geçişin veremeyeceği
şey: bir bulgunun kaç bağımsız yoldan doğrulandığını bilmek.

## Sıra

1. **C şimdi koşar** — tasarım kaynağı gerekmiyor.
2. Tasarım kaynağı gelir.
3. **A koşar**, ayrı geçiş olarak.
4. **B koşar**, A'nın bulgusuna bakmadan.
5. Karşılaştırma ve kova ayrımı.
6. Spec güncellenir, sonra uygulama planına geçilir.
