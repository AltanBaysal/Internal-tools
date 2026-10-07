# Görev 31 — "Kare" dili genele · Uygulama planı

> **Ajanlar için:** GEREKLİ ALT BECERİ: bu planı superpowers:executing-plans ile görev görev uygula.

**Amaç:** Arayüzde içerik birimini her yerde "kare" yapmak ve üç silme onayını fark belgesindeki
metinlere geçirmek.

**Mimari:** Yalnız ön yüz metni. Tek yeni parça, seçilen karelerin katmanlarını sayıp onayın alt
satırını kuran saf bir yardımcı; galerinin rozet kuralını (`OWNED`) paylaşır.

**Tasarım:** [spec](../specs/2026-08-12-queen-editor-v5-gorev-31-kare-dili-design.md)

## Genel kısıtlar

- Arayüz metni **Türkçe**, kod/yorum/test **İngilizce**.
- Sıfır olan katman türü yazılmaz; ikisi de sıfırsa ilk cümle hiç yazılmaz *(karar 2)*.
- Pencere genişlikleri bu görevde değişmez *(karar 8)* — madde 105 Görev 33'ün.
- Testler: `npm test --prefix queen-editor/frontend -- --run`.
- Ön yüz değiştiği için commit'te `dist/` yeniden üretilir.

---

### Task 1: Katman sayan alt satır ve üç onay metni

**Dosyalar:**
- Oluştur: `queen-editor/frontend/src/features/photo_generation/layer_words.js`
- Değiştir: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`
- Test: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Arayüz:**
- Üretir: `OWNED` — `[{ layer, word }]`, katman sırasında; `lostLayers(frames)` — seçilen üretilmiş
  karelerin listesini alır, alt satırın ilk cümlesini döndürür ya da hiç katman yoksa `""`.

- [ ] **Adım 1: Düşen testleri yaz** — boş galeri "henüz kare yok"; üç onayın metinleri; sıfır
      türün atlanması; katmansız seçimde tek cümle; tekil "Karenin"; karışık seçimde alt satır yok;
      bar butonu üç senaryoda da "Sil".
- [ ] **Adım 2: Testleri koş, düştüklerini gör** — `npm test --prefix queen-editor/frontend -- --run`
- [ ] **Adım 3: Yardımcıyı ve metinleri yaz**

```jsx
// The layers a selection would take with it, in the confirm's own words. Counted the way the tile
// badges count (OWNED): a layer that blew up is not one the frame has, so it is not promised here.
function lostLayers(frames) {
  const held = OWNED.map(({ layer, word }) => ({
    word,
    count: frames.filter((frame) => (frame.layers || {})[layer]
      && !(frame.failed || []).includes(layer)).length,
  })).filter(({ count }) => count > 0);
  if (!held.length) return "";
  const owner = frames.length === 1 ? "Karenin" : "Karelerin";
  const named = held.map(({ word }) => (word === "video" ? "videosu" : "sesi")).join(" ve ");
  // "da" after video, "de" after ses -- the last word decides.
  const also = held[held.length - 1].word === "video" ? "da" : "de";
  const counts = held.map(({ word, count }) => `${count} ${word}`).join(" · ");
  return `${owner} ${named} ${also} birlikte silinir (${counts}). `;
}
```

- [ ] **Adım 4: Testleri koş, geçtiklerini gör**

---

### Task 2: Kuyruk, ilerleme ve proje ekranı metinleri

**Dosyalar:**
- Değiştir: `QueuePanel.jsx` ("Üretilmiş kareler galeride kalır."),
  `ProgressPanel.jsx` ("{failed} kare üretilemedi — diğerleri devam ediyor"),
  `features/projects/ProjectsScreen.jsx` ("İlk projeni oluştur, karelerin burada toplansın")
- Test: aynı adlı `.test.jsx` dosyaları

- [ ] **Adım 1: Üç düşen testi yaz**
- [ ] **Adım 2: Koş, düştüklerini gör**
- [ ] **Adım 3: Üç metni değiştir**
- [ ] **Adım 4: Koş, geçtiklerini gör**

---

### Task 3: Detay ekranının kendi silme onayı

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`
- Test: `PhotoDetail.test.jsx`

Task 1'in yardımcısı burada da gerekiyor. İkisi de aynı özelliğin içinde, o yüzden ortak yer aynı
klasörde yeni bir modül: `layer_words.js` hem `OWNED`u (katman + sözcük) hem `lostLayers`ı tutar.
`Gallery.jsx` rozet çizimi için gereken glyph'leri kendi yanında `GLYPH = { video, audio }` olarak
eşler; `PhotoDetail.jsx` yalnız `lostLayers([frame])` çağırır. Metin kopyalanmaz.

- [ ] **Adım 1: Düşen testi yaz** — "Bu kare silinsin mi?" ve videosu olan bir karede
      "Karenin videosu da birlikte silinir (1 video). Bu işlem geri alınamaz."
- [ ] **Adım 2: Koş, düştüğünü gör**
- [ ] **Adım 3: Onayı, "Kare bulunamadı" ve "Kare silinemedi" metinlerini yaz; 70. satırdaki
      "Görev 31'e kadar" notunu kaldır** — koddaki not artık geçersiz.
- [ ] **Adım 4: Koş, geçtiğini gör**

---

### Task 4: Tam takım ve commit

- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `python -m pytest queen-editor -q`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] Commit (spec, plan, kaynak ve `dist/` aynı commit'te)
