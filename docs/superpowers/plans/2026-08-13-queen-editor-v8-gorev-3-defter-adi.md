# v8 · Görev 3 — Defterin ve README'nin adı bugünü anlatsın (uygulama planı)

**Spec:** [2026-08-13-queen-editor-v8-gorev-3-defter-adi-design.md](../specs/2026-08-13-queen-editor-v8-gorev-3-defter-adi-design.md)
**Amaç:** Defteri ilk kez açan biri ne yaptığını başlıktan doğru anlasın; README bugünü söylesin.

**Komut:** `python -m pytest queen-editor -q` (metin değişikliği, ama defterin JSON'u bozulmasın)

## Global kısıtlar

- Defterdeki markdown **Türkçe**, README **İngilizce** (bugünkü hâli öyle, dili değişmiyor).
- Yorum/metin kod ile çelişemez.
- Görev tek commit; commit mesajında çift tırnak yok.

## Adım 1 — Defterin başlığı ve girişi

**Dosya:** `queen-editor/app.ipynb`, hücre `34c9ff58` (NotebookEdit ile)

- [ ] **1.1** Başlık: `# Queen Editor — Colab kurulumu`
- [ ] **1.2** Giriş paragrafı defterin işini sayar (bağla → klonla → ComfyUI → Flask → link) ve
      üretimin uygulamada olduğunu söyler. "Tek foto" dili kalkar.
- [ ] **1.3** Kullanım adımları duruyor; 3. adımın sonu zaten Üreticiler panelini gösteriyor.

## Adım 2 — README

**Dosya:** `queen-editor/README.md`

- [ ] **2.1 Giriş** — iki cümle: proje içinde kareler, her karede foto → video → ses katmanları,
      export diziyi birleştirir; ComfyUI foto ve video, MMAudio ses; Colab'da koşar.
- [ ] **2.2 "Built in cumulative parts…"** — Part 1…4 sayımı yerine `docs/superpowers/plans/`
      altındaki yol haritalarına tek işaret.
- [ ] **2.3 §2'ye üçüncü secret** — `XAI_API_KEY`, video prompt'u için; yoksa foto yine çalışır.
- [ ] **2.4 §3** — "and the sound library" çıkar (Görev 2'de silindi); üretimin ne olduğu
      cümlesi kareler/katmanlar diliyle yazılır.
- [ ] **2.5 Geliştirici notu** duruyor: `dist/` derleyip commit'lemek hâlâ şart.

## Adım 3 — Kapanış

- [ ] **3.1 Koş** — `python -m pytest queen-editor -q`
- [ ] **3.2 Commit** — defter + README + spec + plan.
- [ ] **3.3 Yol haritasını kapat** — v8'in durumu "3/3 bitti, Colab turu bekliyor".

## Kendi kontrolüm

- README'nin Colab bölümündeki adımlar (token, secrets, Run all) değişmiyor — onlar bugün de
  doğru; yalnız eskimiş cümleler dokunuluyor. ✓
- `XAI_API_KEY`'i eklemek kapsam genişletmesi değil: spec'te gerekçesi yazılı, aynı eskimenin
  parçası. ✓
- Defterin JSON'u NotebookEdit ile değişiyor, elle değil — testin dosyayı okuyabilmesi buna bağlı. ✓
