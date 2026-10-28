# Queen Editor — Frontend build/dağıtım stratejisi (karar spec'i)

**Tarih:** 2026-07-25 · **Durum:** onaylandı · **Tür:** mimari karar kaydı (ADR)
**Şemsiye tasarım:** [2026-07-24-queen-editor-v1-design.md](2026-07-24-queen-editor-v1-design.md)
**İlgili:** [2026-07-25-queen-editor-b2-baglanti-design.md](2026-07-25-queen-editor-b2-baglanti-design.md) — Bölüm 2 bunu uygular

## Soru

Derlenmiş React arayüzü Colab'a nasıl ulaşır? İki yol var: geliştirici derleyip `frontend/dist`'i
**commit'ler** (Colab yalnız klon+servis), ya da **Colab** her Run all'da `npm ci && npm run build`
ile derler (dist commit'lenmez). Bu, tek seferlik değil duran bir karar — her bölümde frontend
büyüdükçe geçerli.

## Karar

**A — Geliştirici derler, `frontend/dist/` commit'lenir; Colab yalnız klonlar ve servis eder.**
Colab çalışma zamanında build çalıştırmaz.

## Gerçek sektör standardı ve neden A

Frontend artifact'ı için altın kural: **kontrollü bir ortamda derle, artifact'ı deploy et —
çalışma zamanında hedef makinede derleme.** Standart kurulumda o kontrollü ortam bir **CI/CD
pipeline**'dır: CI derler → artifact'ı yayınlar (CDN/registry/container) → hedef yalnız servis eder.
"Build çıktısını repoya koyma" kuralı da tam olarak **bu pipeline'ın var olduğunu varsayar**.

**Bizde CI yok; Colab hem runtime hem deploy hedefi.** Bu varsayım düşünce iki gerçekçi seçenek
kalıyor:

| | Nerede derlenir | Runtime riski | Repo | Hata biçimi |
|---|---|---|---|---|
| **A — dev derler, dist commit** | Kontrollü (geliştirici makinesi) | ~Sıfır: Colab statik servis | Küçük artifact taşır | Yumuşak: dist bayatsa eski ama çalışan UI |
| **B — Colab derler** | Son-kullanıcının Colab'ı | Var: npm registry, Node sürümü, ~30-60 sn | Temiz (dist ignore) | Sert: build patlarsa hiçbir şey açılmaz |

Colab'ı çoğunlukla geliştirici olmayan biri "Run all" yapıp çalışsın diye açar. B'de build o an
ağa ve Colab'ın toolchain'ine bağımlı; kırılırsa sert hata (hiçbir şey açılmaz, debug zor). A'da
build bir kez kontrollü ortamda olur, Colab'da kırılacak bir şey kalmaz — bu yüzden A **CI'siz bir
Colab aracı için operasyonel olarak daha sağlam.** ComfyUI da aynısını yapar (frontend'ini ayrı
pakette derlenmiş ship eder); fark: onunki ayrı repo, bizimki aynı repo — ama dağıtım mantığı aynı.

Not: A'yı seçmenin **yanlış** bir gerekçesi de vardı (bir dönem `package-lock.json` yoktu, Colab
`npm ci` yapamıyordu). O kısıt sonra çözüldü; A yine de **doğru** gerekçeyle (runtime sağlamlığı)
duruyor.

## Kabul edilen bedeller

1. **Bayat-dist:** geliştirici `frontend/src/`'i değiştirip yeniden derlemeyi/commit'i unutursa
   Colab eski UI'yi servis eder. Azaltma: (a) `CLAUDE.md` + `CODE-STANDARD.md`'de "commit'ten önce
   `npm run build`" kuralı; (b) notebook klon hücresi `dist/index.html`'in **varlığını** fail-loud
   doğrular (güncelliğini değil). Hata yumuşak (eski ama çalışan UI), sert değil.
2. **Repoda derlenmiş artifact:** `frontend/dist/` (bir `index.html` + bir hash'li `.js` + bir
   hash'li `.css`) versiyon kontrolünde durur. Küçük; CI olmadığında git tek artifact-taşıma
   kanalı.
3. **Gitignore istisnası:** kök [.gitignore](../../../.gitignore) satır 11'deki `dist/`
   (PyInstaller/flet çöpü için, isim bazlı) `frontend/dist`'i de yutuyor;
   [queen-editor/.gitignore](../../../queen-editor/.gitignore)'daki `!frontend/dist/` bunu
   daraltır. "Hack" değil — kapsamı düzelten, yorumla belgelenmiş tek satırlık config.

## B neden reddedildi

Repo daha temiz olurdu ve bayat-dist riski hiç olmazdı; ama build'i son-kullanıcının runtime'ına
taşımak, ağ/Node bağımlılığını en kötü anda (kullanıcı sadece çalıştırmak isterken) devreye sokar
ve sert hataya açar. CI olmadığından B'nin "temizlik" avantajı, A'nın runtime sağlamlığından daha
az değerli.

## Etki (mevcut durumla uyumlu)

Bu karar zaten Bölüm 2 kodunda uygulanmış durumda; spec onu kayda geçirir, yeni implementasyon
istemez:

- `queen-editor/.gitignore` — `!frontend/dist/` (dist commit'lenir; `node_modules/` commit'lenmez).
- `queen-editor/CODE-STANDARD.md` → `## Stack` — "frontend geliştiricide derlenir, `dist/` repoda
  ship edilir; Colab npm/build çalıştırmaz."
- `CLAUDE.md` → `## queen-editor` — "Build before commit" kuralı.
- `queen-editor/app.ipynb` — klon hücresi `frontend/dist/index.html`'i fail-loud doğrular; **build
  hücresi yok**; Flask hazır dist'i servis eder.
- `queen-editor/frontend/package-lock.json` — commit'lenir (lockfile kaynaktır; geliştirici
  derlemesini tekrar-üretilebilir kılar). `dist` türetilmiştir ama CI yokluğunda yine commit'lenir.

## Doğrulama

- `queen-editor/.gitignore` `!frontend/dist/` içerir; `git check-ignore frontend/dist/index.html`
  **eşleşmez** (izlenir).
- `CODE-STANDARD.md` `## Stack` ve `CLAUDE.md` `## queen-editor` A ile tutarlı.
- Colab Run all → klon (dist ile) → Flask servis → **"sunucuya bağlı ✓"**; runtime'da build yok.

## Yeniden gözden geçirme koşulu

Projeye bir CI (ör. GitHub Actions) eklenir ve dist'i derleyip bir artifact kanalına yayınlarsa, bu
karar tazelenir: o zaman "build çıktısını commit'leme" standardına dönmek (dist'i CI üretsin, repo
temiz kalsın) mümkün ve tercih edilir olur.
