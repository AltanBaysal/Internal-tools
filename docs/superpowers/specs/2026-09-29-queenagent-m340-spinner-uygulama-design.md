# Madde 340 — Yüklenirken spinner, önce dosya listesinde · uygulama turu

**Kaynak:** [yol haritasının 340'ı](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2c);
tasarım: `queen-agent-v3`'ün 173'ü ve 181'i. **Testler:**
[test turunun spec'i](2026-09-29-queenagent-m340-spinner-testler-design.md), kırmızısı `1a3a498b`.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne yapılır

Üç değişiklik, üçü de `queen-agent/frontend/src/features/workspace/` altında:

1. **`Spinner.jsx`, yeni.** Tek bir `<span className="spinner" aria-hidden="true"
   data-testid="spinner" />` çizer. Halka yalnız halka: nerede duracağını, ne kadar boşlukla
   ortalanacağını yeri söyler — dosya listesinde `file-list__spinner`, sonra v9-2l'de
   `chat__spinner`, v9-2u'da `all-projects__spinner`. `data-testid` iskeletinki gibi: halka
   `aria-hidden`, rolüyle bulunamaz.
2. **`FileRail.jsx`'in `FileList`'i** yüklenirken `<Skeleton rows={3} />` yerine
   `<div className="file-list__spinner"><Spinner /></div>` çizer, ve `Skeleton` importu dosyadan
   kalkar. Başlık, `Refresh` ve hata satırları bugünkü yerlerinde kalır; yükleniş bitince satırlar ya
   da `No files yet` bugünkü gibi gelir.
3. **`workspace.css`**, iki yeni kural:
   - `.spinner` — `.msg__spinner`'ın hemen altında, onun halkası 20px'te: `flex: none`, `width` ve
     `height` 20px, `border: 1.5px solid var(--line)`, `border-top-color: var(--accent)`,
     `border-radius: 50%`, `animation: msg-spin 0.8s linear infinite`. Yeni bir `@keyframes` yok:
     `msg-spin` zaten var.
   - `.file-list__spinner` — `.file-list__empty`'nin altında: `display: flex`,
     `justify-content: center`, `padding: 24px 12px`.

**`.spinner` ayrı bir kural**, tasarımın `kit.css`'indeki gibi `.msg__spinner`'la aynı seçicide değil:
`.msg__spinner` sohbetin canlı satırının, ve bu dalgada sohbete başka parçalar dokunuyor. Tekrarlanan
beş satır, bir başkasının kuralını değiştirmekten ucuz.

## Dokunulmayanlar

- `Skeleton.jsx`, testi ve `.skeleton` kuralları: `App.jsx`, `ChatScreen.jsx` ve `ProjectScreen.jsx`
  hâlâ kullanıyor; onları v9-2l, v9-2n ve v9-2u kaldırır.
- `RefreshFiles`'ın yeri (v9-2m), açık dosyanın başlığı (342), `FilePanel.jsx`.
- CODE-STANDARD.md: ön ucun dosyaları bir tabloda sayılmıyor, ve yeni bir animasyon yok.
- `dist` derlenmez: birleştirirken conductor derler.

## Nasıl görülür

Dört satır: `npm test --prefix queen-agent/frontend` yeşil, 652'ye yeni testler eklenmiş olarak;
queen-editor'ün arka ucu 377'nin iki kırmızısıyla; öteki iki süit yeşil.

Tarayıcıda: bir projenin sohbetinde sağdaki dosya listesi yüklenirken `Project files` başlığı ve `↻`
yerinde, listenin kutusunda küçük, turuncu tepeli, dönen bir halka; gri bloklar yok.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m340-spinner-uygulama-plan.md).
