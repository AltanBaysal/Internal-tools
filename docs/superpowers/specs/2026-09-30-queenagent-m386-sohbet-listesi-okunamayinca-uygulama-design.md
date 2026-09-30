# Madde 386 — Kenar çubuğu okuyamadığı sohbet listesine "yok" demez · uygulama turu

**Kaynak:** [yol haritasının 386'sı](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); davranış ve
kararlar [test turunun spec'inde](2026-09-30-queenagent-m386-sohbet-listesi-okunamayinca-testler-design.md).
Kırmızı commit edilen testler: `Sidebar.test.jsx`'in 386 bölümü, `workspace.css.test.js`'in üç
kilidi, `App.test.jsx`'in *"a chat list that could not be read says so in the sidebar…"*'si.

**Kullanıcıdan gereken:** hiçbir şey.

## Yollar

1. **Kenar çubuğunun kendi işaretlemesi, var olan parçalarla (seçilen).** `Sidebar.jsx`
   `.sidebar__chats`'in içinde, hata varken satırların yerine küçük bir kutu çizer: cümle, altında
   `failure__retry` sınıflı `Try again` ve app'in tek `CopyButton`'ı. Yeni bileşen yok.
2. **`ProjectsFailure`'ı genelleştirmek** (`what` ve çerçeve sınıfı prop'la). Reddedildi: onun
   çerçevesi `.empty`, ekranın ortasına yerleşen bir sütun; kenar çubuğununki bir liste satırı. Tek
   bileşende iki çerçeve ve iki cümle, üç satırlık bir işaretlemeden fazla parça — ve 364'ün
   bileşenine, adına ve testlerine dokunur. Paylaşılan asıl parça, davranışı olan `CopyButton`,
   iki yolda da ortak.

## Değişenler

- **`useChatLists.js`** — `useProjectChats` `useList`'in `error`'unu bırakmaz:
  `projectChatsError: projectId ? error : null`, ötekiler gibi proje yokken boş. `Try again` için
  ayrı bir iş yok: `reloadProjectChats` zaten listeyi yeniden okur.
- **`App.jsx`** — `Sidebar`'a `error={projectChatsError}` ve `onRetry={reloadProjectChats}`.
- **`Sidebar.jsx`** — `error` ve `onRetry` prop'ları. `error` varken `shown` boştur (Enter bir şey
  açmaz, satır çizilmez) ve `.sidebar__chats`'in içinde:

  ```jsx
  <div className="sidebar__failure">
    <p className="sidebar__error">Couldn&apos;t load chats.</p>
    <div className="sidebar__actions">
      <button type="button" className="failure__retry" onClick={onRetry}>Try again</button>
      <CopyButton text={error} className="sidebar__copy" />
    </div>
  </div>
  ```

  Sıra: hata, sonra satırlar, sonra `No chats match "…".` / `No chats yet.`. Katlanmış hâl değişmez.
- **`workspace.css`** — `.sidebar__empty`'nin yanında: `.sidebar__failure` (`padding: 10px 12px`,
  `.sidebar__empty`'ninki), `.sidebar__error` (`margin: 0`, `font-size: 13px`, `color: #8a5237`,
  `line-height: 1.5`), `.sidebar__actions` (`display: flex`, `flex-wrap: wrap`, `gap: 8px`,
  `margin-top: 10px`), `.sidebar__copy[data-said="yes"]` accent, `[data-said="no"]` destructive.

## Tutulmayan

- Okuma sürerken ne göründüğü (test spec'inin Karar 7'si) — `useList` değişmez.
- `dist` — koşuyu yöneten derler.

## Nasıl görülür

Dört satır paralel; hepsi yeşil. Adım adım dökümü
[uygulama turunun planında](../plans/2026-09-30-queenagent-m386-sohbet-listesi-okunamayinca-uygulama-plan.md).
