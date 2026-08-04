# Bölüm 12 — Silme + Onaylar Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Seçim modu + toplu silme, proje silme ve Projeden çık onayı — yıkıcı her işlem onaylı.

**Architecture:** Silme tek uca iner (`POST /api/projects/<p>/photos/delete`, dosya listesi alır); Bölüm 11'in tekil ucu buna dönüşür ve detay sayfası tek elemanlı liste gönderir. Proje silme `DELETE /api/projects/<ad>` ile klasörü içeriğiyle kaldırır. Frontend'de dört onay kutusu tek `shared/ConfirmModal.jsx`'e iner; galeri seçim modunu kendi durumunda tutar.

**Spec:** [2026-08-05-queen-editor-bolum12-silme-onaylar-design.md](../specs/2026-08-05-queen-editor-bolum12-silme-onaylar-design.md)

## Global Constraints

- **TDD:** önce düşen test, sonra kod. Test koşuları: `Set-Location d:\code\github\internal-tools\queen-editor; python -m pytest -q` ve `npm --prefix d:\code\github\internal-tools\queen-editor\frontend test`.
- **Commit:** bölüm sonunda tek commit + push (mesaj Bash aracıyla, PowerShell `<` karakterinde tökezliyor).
- Tasarım değerleri birebir (spec §2): ✓ dairesi 18×18 `top:6 left:6`; seçili `outline:"2px solid var(--accent)"` + örtü `rgba(167,139,250,.18)`; çubuk `left:"50%" bottom:20 translateX(-50%)`, `padding:"10px 18px"`, `gap:14`, `borderColor: var(--accent)`; çöp `Btn sm ghost` `top:10 right:10` `padding:"4px 8px"` `color: var(--danger)`.
- Onay kutusu genişlikleri: toplu silme 320, proje silme 340, çıkış 320.
- Ekran metni Türkçe, kod/yorum İngilizce. CRLF korunur.

---

### Task 1: Toplu silme ucu (tekil uç buna dönüşür)

**Files:** `domain/usecases/delete_photo.py` → `delete_photos`; `presentation/routes.py`; `main.py`; testler: `test_photo_usecases.py`, `test_photo_routes.py`.

**Interfaces:** `delete_photos(record, store, order_store, now, project, files) -> list[str]` (silinenler); `InvalidFiles` (gövde liste değil). Tekil `delete_photo` kaldırılır.

- [ ] **Step 1: Testleri yaz** — çoklu silme siler ve silinenleri döner; bilinmeyen ad atlanır (hata yok, listede de yok); liste olmayan gövde `InvalidFiles`; olmayan proje `ProjectMissing`; rota `POST /api/projects/düğün/photos/delete` 200 + `{"deleted": [...]}`, 400 ve 404 halleri; silinen numara geri kullanılmaz (mevcut test yeni uca göre güncellenir).
- [ ] **Step 2: Koştur, düştüğünü gör.**
- [ ] **Step 3: Use case'i yaz** — dosya başına: `store.delete` → `record.mark_deleted` → sıra budama; kayıtta olmayan ad atlanır; tek `order_store.write` ile kapanır (N kez yazmak yerine bir kez).
- [ ] **Step 4: Rotayı ve `main.py`'ı güncelle**, tekil rotayı kaldır.
- [ ] **Step 5: Koştur** → yeşil.

### Task 2: Proje silme ucu

**Files:** `services/drive/storage.py` (`delete_dir`), `features/projects/data/project_store.py` (`delete`, `exists`), `features/projects/domain/usecases/delete_project.py` (yeni), `presentation/routes.py`, `main.py`; testler: `test_drive_storage.py`, `test_project_store.py`, `test_project_usecases.py`, `test_projects_routes.py`.

**Interfaces:** `delete_project(store, name)` → yoksa `ProjectMissing`; `DriveProjectStore.delete(name)`, `.exists(name)`.

- [ ] **Step 1: Testleri yaz** — klasör içeriğiyle silinir; olmayan proje 404; `DELETE /api/projects/<ad>` 204; OS hatası 500 + sistemin metni.
- [ ] **Step 2: Koştur, düştüğünü gör.**
- [ ] **Step 3: Kodu yaz** — `delete_dir` `shutil.rmtree`; eksik klasör `FileNotFoundError` → use case `ProjectMissing`'e çevirir (kontrol + silme arasında yarış olabilir).
- [ ] **Step 4: Koştur** → yeşil.

### Task 3: `ConfirmModal` ortaklaştırma

**Files:** `shared/ConfirmModal.jsx` (yeni), `features/photo_generation/PhotoDeleteModal.jsx` (silinir), `PhotoDetail.jsx`; test: `shared/ConfirmModal.test.jsx`.

**Interfaces:** `ConfirmModal({ title, body, confirmLabel, busyLabel, danger, busy, onCancel, onConfirm, width })`.

- [ ] **Step 1: Testi yaz** — başlık ve gövde basılır; onay düğmesi `danger` iken kırmızı dolgu, değilken `wf-btn--hl`; `Esc` iptal eder, `busy` iken etmez; scrim tıklaması iptal eder, `busy` iken etmez.
- [ ] **Step 2: Koştur, düştüğünü gör.**
- [ ] **Step 3: Bileşeni yaz**, `PhotoDetail`'ı ona geçir, `PhotoDeleteModal.jsx`'i sil (`PhotoDetail.test.jsx` metinleri aynı kaldığı için değişmemeli).
- [ ] **Step 4: Koştur** → yeşil.

### Task 4: Galeride seçim modu

**Files:** `Gallery.jsx`, `shared/app.css`, `api.js` (`deletePhotos`), `useGeneration.js` (silme sonrası liste tazeleme), `ProjectScreen.jsx`; testler: `Gallery.test.jsx`, `api.test.js`.

- [ ] **Step 1: Testleri yaz** — hover halkası tıklanınca mod açılır ve kare seçilir; modda tıklama seçer/kaldırır ve **detaya gitmez**; çubuk "2 seçili" yazar; Tümünü seç hepsini seçer, ikinci basış temizler; Vazgeç ve `Esc` modu kapatır; Sil onay ister, onayda `onDelete(files)` çağrılır; modda sürükleme sıralama yapmaz.
- [ ] **Step 2: Koştur, düştüğünü gör.**
- [ ] **Step 3: Kodu yaz** — `selecting` + `selected` durumları galeride; ✓ dairesi `qe-check` sınıfıyla, hover görünürlüğü `app.css`'te (`.qe-tile:hover .qe-check{opacity:1}`); çubuk `wf-card` + accent kenar; galeri altına çubuk payı; `draggable={!selecting}`.
- [ ] **Step 4: Koştur** → yeşil.

### Task 5: Proje kartı çöpü + Projeden çık onayı

**Files:** `ProjectCard.jsx`, `ProjectsScreen.jsx`, `useProjects.js` (silme), `api.js` (`deleteProject`), `ProjectScreen.jsx`; testler: `ProjectsScreen.test.jsx` (yeni), `ProjectScreen.test.jsx` (ekleme).

- [ ] **Step 1: Testleri yaz** — çöpe basmak projeyi açmaz, onay kutusu açar; onaylayınca `deleteProject` çağrılır ve liste tazelenir; Projeden çık önce sorar, Vazgeç ekranda tutar, Çık `navigate("/")` çağırır.
- [ ] **Step 2: Koştur, düştüğünü gör.**
- [ ] **Step 3: Kodu yaz** — `ProjectCard` çöp düğmesi (`stopPropagation`), `ProjectsScreen` onay + silme + `reload`, `ProjectScreen` çıkış onayı; `ProjectCard` yol üretimini `projectPath`'e geçir.
- [ ] **Step 4: Koştur** → yeşil.

### Task 6: Kapanış

- [ ] **Step 1: Bozma turu** — çöp düğmesinden `stopPropagation` kaldır → "çöpe basmak projeyi açmaz" testi düşmeli; geri al.
- [ ] **Step 2:** iki test paketi + `npm run build`.
- [ ] **Step 3:** commit + push.

## Bulgu defteri

- **Çöp düğmesi `stopPropagation` ile değil, kardeş öğe olarak çözüldü.** Plan olayı durdurmayı
  söylüyordu; uygularken proje kartının zaten bir `<button>` olduğu görüldü — içine ikinci buton
  koymak geçersiz HTML. Kart ile çöp artık `position:relative` bir sarmalayıcının iki kardeşi;
  tıklama zaten karta ulaşmıyor, ek koda gerek kalmadı.
- **Bozma turu ilk denemede boşa çıktı ve testi düzeltti.** "Modda kareye tıklamak detaya gitmez"
  testi karenin sarmalayıcısına tıklıyordu; oysa kullanıcı görsele (bağlantıya) basar. Koruma
  kaldırıldığında test yeşil kalınca fark edildi, test gerçek jeste çevrildi — sonra koruma
  kaldırılınca doğru şekilde düştü.
- **`ConfirmModal` ortaklaştırması Bölüm 11'in sözünü tuttu:** dört kullanım (foto silme, toplu
  silme, proje silme, projeden çık) tek bileşene indi, `PhotoDeleteModal.jsx` silindi.
- Backend 232, frontend 60 test yeşil; `dist/` yenilendi.
