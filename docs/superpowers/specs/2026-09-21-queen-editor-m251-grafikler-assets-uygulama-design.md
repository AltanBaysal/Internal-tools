# Madde 251 · Grafikler de `assets/` altına — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m251-grafikler-assets-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

**Beş dosya `git mv` ile taşınıyor** — `queen-editor/assets/` altına, disclaimer'ın yanına.
Kopyalanmıyor: kökte kalan bir kopya, bir sonraki düzenlemenin yanlış dosyaya gitmesi demek, ve
hangisinin gönderildiğini söyleyen hiçbir şey olmaz.

**`config.py`'nin beş sabiti `assets`'i geçiyor.** Yolu kuran tek yer orası, ve taşımanın uygulama
tarafındaki tamamı bu.

**Defterin Clone hücresi yeni yere bakıyor** — `os.path.join(CLONE_DIR, "queen-editor", "assets",
_name)`. Beş adı saymaya devam ediyor; değişen yalnız klasör. Hücreye yorum girmiyor.

**`test_producer_contract.py` kendi yollarını bırakıyor.** Üç grafiği bugün kökten kendisi kuruyor;
artık `config`'in sabitlerini kullanıyor. Yeni bir olgu değil — aynı yolun ikinci evinin kapanması,
ve taşımanın onu kırması bunun zamanının geldiğini söylüyor.

## Bu turda değişen

- `queen-editor/workflow_api.json` → `queen-editor/assets/workflow_api.json`, ve diğer dördü.
- `backend/config.py`: beş sabit.
- `queeneditor.ipynb`: Clone hücresinin grafik yolu.
- `backend/tests/test_producer_contract.py`: üç yol `config`'ten.

Davranış hiç değişmiyor, ön yüz de `dist` de yerinde. **Defter değişti, yani bu maddenin görünür
olması push'a bağlı** — defter depoyu klonluyor.
