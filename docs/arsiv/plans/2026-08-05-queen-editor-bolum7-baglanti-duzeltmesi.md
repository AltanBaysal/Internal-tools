# Bölüm 7 — Bağlantı Düzeltmesi Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Colab öldüğünde donuk "üretiliyor" çubuğu kalmasın: her istek 10 sn'de zaman aşımına uğrar, üretim görünürken bağlantı hatası varsa çubuk soluklaşır ve kart son bilinen ilerlemeyi söyler.

**Architecture:** İki dosyalık frontend değişikliği. `shared/api.js`'teki tek `request()` sarmalayıcısına `AbortController` tabanlı zaman aşımı girer (bütün istekler oradan geçer, tek nokta yeter). `GeneratePanel.jsx`'in `running` dalı, hata varken `ProgressPanel`'i soluklaştırır ve mevcut `StatusErrorCard`'ın başlığına son bilinen ilerlemeyi ekler. Backend'e, `useGeneration`'a ve poll mantığına dokunulmaz — hata zaten poll'un catch'inde `error` state'ine düşüyor; eksik olan tek şey askıda kalan isteğin hiç hataya dönüşmemesiydi.

**Tech Stack:** React 18 + Vite (pre-built `dist/` commit edilir), `fetch` + `AbortController`. Test yok — frontend test altyapısı yol haritasında Bölüm 8 (bu düzeltmeden hemen sonra); bu senaryonun testi orada yazılacak.

**Spec:** [2026-08-04-queen-editor-bolum7-arayuz-design.md](../specs/2026-08-04-queen-editor-bolum7-arayuz-design.md) §4 "Bağlantı kopması — bayat 'üretiliyor' durumu".

## Global Constraints

- **Commit yok:** hiçbir görev commit atmaz. Tek commit en sonda, kullanıcı onayıyla (kullanıcı kuralı).
- **Yorum dili İngilizce, ekran metni Türkçe** (CLAUDE.md yorum sözleşmesi). Yorum WHY anlatır, WHAT değil.
- **Zaman aşımı tam 10 sn** (`10_000` ms) — spec §4'ün onaylanmış değeri.
- Zaman aşımı mesajı mevcut kalıba uyar: `"Sunucuya ulaşılamadı — bağlantıyı kontrol et.\n..."` — `GeneratePanel.describeError` bu ön eke bakarak "Sunucuya ulaşılamıyor" başlığını seçiyor, ön ek değişemez.
- **Yeni CSS yok, yeni bileşen yok** — soluklaştırma satır içi `opacity`, kart mevcut `StatusErrorCard`.
- Backend dosyalarına ve `useGeneration.js`'e dokunulmaz.
- Dosyalar CRLF satır sonlarıyla kalır (repo sözleşmesi).

---

### Task 1: `api.js` — her isteğe 10 sn zaman aşımı

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js` (yalnız `request()` fonksiyonu, satır 1-21)

**Interfaces:**
- Consumes: —
- Produces: `request()` davranışı — 10 sn cevapsız kalan istek `Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nZaman aşımı (10 sn)")` fırlatır. İmza ve tüm dışa açık fonksiyonlar aynı kalır; Task 2 bu hata metninin ön ekine güvenir.

- [ ] **Step 1: `request()`'i zaman aşımlı hâline getir**

Dosyanın başındaki mevcut blok:

```js
// Single fetch wrapper -- same-origin "/api", so no base URL and no CORS.
// On failure it throws the server's own message: the rules (and their Turkish wording) live in the
// backend, and the UI prints whatever comes back.
async function request(path, options) {
  let resp;
  try {
    resp = await fetch(path, options);
  } catch (err) {
    // fetch rejects with a browser-English TypeError when the tunnel is unreachable; say it in
    // Turkish and keep the raw text underneath (we never guess the cause).
    throw new Error(`Sunucuya ulaşılamadı — bağlantıyı kontrol et.\n${err.message}`);
  }
```

şununla değiştirilir (fonksiyonun geri kalanı — `body` okuma, `resp.ok` kontrolü — aynen kalır):

```js
// Single fetch wrapper -- same-origin "/api", so no base URL and no CORS.
// On failure it throws the server's own message: the rules (and their Turkish wording) live in the
// backend, and the UI prints whatever comes back.

// fetch has no timeout of its own; when the Colab runtime dies, the Cloudflare edge can hold a
// request open for minutes, so the poll's catch never fires and the screen freezes on stale state.
const TIMEOUT_MS = 10_000;

async function request(path, options) {
  let resp;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    resp = await fetch(path, { ...options, signal: controller.signal });
  } catch (err) {
    // fetch rejects with a browser-English TypeError (or AbortError on timeout) when the tunnel is
    // unreachable; say it in Turkish and keep the raw text underneath (we never guess the cause).
    const detail = err.name === "AbortError" ? `Zaman aşımı (${TIMEOUT_MS / 1000} sn)` : err.message;
    throw new Error(`Sunucuya ulaşılamadı — bağlantıyı kontrol et.\n${detail}`);
  } finally {
    clearTimeout(timer);
  }
```

Dikkat:

- `finally { clearTimeout(timer) }` şart — başarılı cevapta zamanlayıcı sızmasın.
- `{ ...options, signal: controller.signal }` — `options` çağrıların çoğunda `undefined`; spread bunu sorunsuz karşılar (`{ ...undefined }` → `{}`).
- `photoUrl()` bir fetch değil (`<img>` yüklüyor), zaman aşımından etkilenmez — dokunma.

- [ ] **Step 2: Elle doğrula**

`request` dışında `fetch(` çağrısı kalmadığını doğrula:

```
Grep "fetch(" queen-editor/frontend/src/  →  yalnız api.js'teki tek çağrı çıkmalı
```

### Task 2: `GeneratePanel.jsx` — bayat "running" görünümü

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx` (yalnız `running` dalı, satır 130-134)

**Interfaces:**
- Consumes: `error` prop'u — poll başarısız oldukça `useGeneration` doldurur, ilk başarılı poll'da `null`'a döner (mevcut davranış, değişmiyor). `describeError()` başlığı Task 1'in hata ön ekinden türer.
- Produces: — (görsel değişiklik; dışarıya yeni arayüz yok)

- [ ] **Step 1: `running` dalını değiştir**

Mevcut:

```jsx
      {running ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <ProgressPanel job={job} stopping={stopping} onStop={onStop} />
          {errorInfo && <StatusErrorCard text={errorInfo.headline} raw={errorInfo.raw} />}
        </div>
      ) : (
```

Yeni:

```jsx
      {running ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {/* While polls fail, the bar shows the LAST KNOWN state, not the present — dim it so a
              frozen counter cannot read as live progress, and let the card carry the last-known
              numbers ("the screen never claims what it does not know"). */}
          <div style={errorInfo ? { opacity: 0.45 } : undefined}>
            <ProgressPanel job={job} stopping={stopping} onStop={onStop} />
          </div>
          {errorInfo && (
            <StatusErrorCard
              text={`${errorInfo.headline} — son bilinen: ${job.done ?? 0}/${job.total || "?"}`}
              raw={errorInfo.raw}
            />
          )}
        </div>
      ) : (
```

Dikkat:

- Başlık `errorInfo.headline`'dan türer, sabit yazılmaz: askıda/ölü tünelde "Sunucuya ulaşılamıyor — son bilinen: 7/48", sunucunun reddettiği istekte "İstek reddedildi — son bilinen: 7/48". Sebep uydurulmaz (FOUNDATION).
- `job.done ?? 0` ve `job.total || "?"` — Üret'e basıldığı andaki yerel `running` job'ında sayılar henüz yok; `undefined/0` görünmesin.
- Soluklaştırma sarmalayıcı `<div>`'le yapılır; `ProgressPanel`'e prop eklenmez (bileşen değişmez). Durdur butonu da soluklaşır ve bu doğru: bağlantı yokken durdurma isteği de gidemez, buton diri görünmemeli. Buton pasifleştirilmez — bağlantı her poll'da denenmeye devam ediyor, dönerse buton anında diri.

- [ ] **Step 2: Elle doğrula**

- `errorInfo` yokken görünüm bugünkünün aynısı (opacity sarmalayıcısı `undefined` stil alır).
- Idle daldaki (`:` sonrası) hata/kart zinciri değişmedi.

### Task 3: Build + doğrulama paketi

**Files:**
- Modify: `queen-editor/frontend/dist/` (üretilir, elle düzenlenmez)

**Interfaces:**
- Consumes: Task 1-2'nin kaynak değişiklikleri.
- Produces: Colab'ın servis edeceği güncel `dist/`.

- [ ] **Step 1: Build**

Run: `npm run build` (`queen-editor/frontend/` içinde)
Expected: hatasız biter, `dist/` yenilenir.

- [ ] **Step 2: Commit YOK — kullanıcı onayı bekle**

Değişen dosyalar (`api.js`, `GeneratePanel.jsx`, `dist/`) çalışma kopyasında bırakılır. Kullanıcı "commitle" deyince tek commit: `fix(queen-editor): ölü sunucuda donuk üretiliyor çubuğu — 10 sn zaman aşımı + soluk çubuk` (dist aynı commit'te — Colab testi push ister).

- [ ] **Step 3: Colab doğrulaması (kullanıcı, push sonrası)**

1. Üretim başlat, runtime'ı tamamen kapat → en geç ~12 sn içinde (poll 2 sn + zaman aşımı 10 sn) çubuk soluklaşır, kırmızı "Sunucuya ulaşılamıyor — son bilinen: X/Y" kartı gelir.
2. Runtime'ı yeniden başlat (aynı URL'yle tünel dönerse) → kart kaybolur, ekran gerçek duruma oturur.
3. Normal üretim + Durdur akışı eskisi gibi (regresyon kontrolü).
