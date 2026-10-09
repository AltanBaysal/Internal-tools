# Görev 33 — Pencere ve yerleşim cilası · Uygulama planı

> **Ajanlar için:** GEREKLİ ALT BECERİ: bu planı superpowers:executing-plans ile görev görev uygula.

**Amaç:** Sekiz onay penceresine kendi genişliğini vermek, yatay taşmayı kapatmak, seçim barını
yüzdürmek.

**Mimari:** Genişlik çağıran ekranın; `ConfirmModal` yalnız 320 varsayılanını taşır. Taşma
düzeltmesi `shared/app.css`'e yazılır — `vendor/styles.css` elle düzenlenmez.

**Tasarım:** [spec](../specs/2026-08-12-queen-editor-v5-gorev-33-pencere-yerlesim-design.md)

## Genel kısıtlar

- Genişlikler: proje silme 340, kurulum ve iptali 360, kuyruk boşaltma 380, export çıkışı 380,
  yeni proje 400, bekleyen çıkarma 400, karışık silme 420, kare silme 320 (varsayılan).
- Katman silme pencereleri 400'de kalır *(madde 80)*.
- Testler: `npm test --prefix queen-editor/frontend -- --run`.
- Ön yüz değiştiği için commit'te `dist/` yeniden üretilir.

---

### Task 1: Her pencere kendi genişliğinde

**Dosyalar:**
- Değiştir: `features/photo_generation/Gallery.jsx`, `QueuePanel.jsx`, `ExportScreen.jsx`,
  `features/producers/ProducersPanel.jsx`, `features/projects/NewProjectModal.jsx`
- Test: aynı adlı `.test.jsx` dosyaları

Ölçüm penceredeki kart kutusundan okunur; testler onu başlıktan yukarı çıkarak bulur:
`screen.getByText(<başlık>).closest(".wf-card")`.

- [ ] **Adım 1: Düşen testleri yaz** — altı pencere, altı genişlik.
- [ ] **Adım 2: Koş, düştüklerini gör**
- [ ] **Adım 3: `width` özelliklerini geç** — Gallery'nin üç onayı genişliğini `confirm` nesnesiyle
      taşır, böylece metin ve ölçü yan yana durur.
- [ ] **Adım 4: Koş, geçtiklerini gör**

---

### Task 2: Seçim barı yüzer

**Dosyalar:**
- Değiştir: `features/photo_generation/Gallery.jsx`
- Test: `Gallery.test.jsx`

- [ ] **Adım 1: Düşen testi yaz** — barın rayı `bottom: 28px`.
- [ ] **Adım 2: Koş, düştüğünü gör**
- [ ] **Adım 3: `BAR_RAIL`i ve altındaki boşluğu güncelle**
- [ ] **Adım 4: Koş, geçtiğini gör**

---

### Task 3: Yatayda taşma yok

**Dosyalar:**
- Değiştir: `shared/app.css`, `features/photo_generation/SidePanel.jsx`,
  `features/photo_generation/ProjectScreen.jsx`

Testi yok *(spec karar 7)*: jsdom yerleşim hesaplamıyor.

- [ ] **Adım 1: `app.css`'e belge güvencesini yaz** — `html, body { max-width: 100%; overflow-x:
      hidden; }` ve uzun sözcükleri kıran kural.
- [ ] **Adım 2: Yan paneli ve başlık çubuğunu `min-width: 0` ile daraltılabilir yap**
- [ ] **Adım 3: Takımı koş** — hiçbir test kırılmamalı.

---

### Task 4: Tam takım ve commit

- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `python -m pytest queen-editor -q`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] Commit (spec, plan, kaynak ve `dist/` aynı commit'te)
