# Madde 457 — Geç gelen liste, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** `useList` cevabı ve düşüşü ait oldukları yolla tutar ve yalnız en son istediği okumanınkini
yazar; B açılırken kenar çubuğu ve dosya paneli A'nın hiçbir satırını çizmez, A'nın geç gelen cevabı
da B'nin listesinin üstüne yazılmaz.

**Yaklaşım:** Önce test, kırmızı görülür, sonra kod. Dosyalar Edit ile değişir.

**Spec:** [m457](../specs/2026-10-10-queen-agent-m457-gec-liste-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları İngilizce.
- Arka uca, `useFiles.js`'e, `OpenProject.jsx`'e, yol haritasına ve queen-editor'e dokunulmaz;
  `FileRail.jsx`'te yalnız başlığın sayısı.

---

## Görev 1: hook testleri — `useList.test.jsx`

- [ ] `Host` bir `path` alır (varsayılanı `/api/things`).
- [ ] Cevapları yol başına bir kuyrukta tutan, `nth` ile istenen sırada bırakan bir sahte `fetch`.
- [ ] Yedi test (spec, *Testler*). Kırmızı görülür.
- [ ] Kendi son cevabını tutan yol: A cevaplanır, kapanır, yine A, okuma yolda — A'nın satırları,
  beklemiyor. Var olan davranışı tutar, ilk koşuşta yeşil.

## Görev 2: kenar çubuğu ve ekran testleri — `Sidebar.test.jsx`, `App.test.jsx`

- [ ] Sidebar: `loading` iken ne satır ne *"No chats yet."*, Search chats yerinde.
- [ ] App, *"leaving before the project's chats arrive stays where the user went"*'in yanında: A'nın
  geç gelen sohbet listesi; ve B'nin listeleri bekletilirken kenar çubuğu ile dosya paneli.
  Kırmızı görülür.

## Görev 3: kod

- [ ] `useList.js`: `answer {path, items}` ve `failure {path, message}`; `useRef` sayaç, her `reload`'da
  — `enabled` yanlışken de — artar; `then` ve `catch` yalnız en son okumada yazar; `items`, `error`,
  `loading` çizimde şimdiki yoldan hesaplanır. `loading` durumu ve `finally` kalkar.
- [ ] `useChatLists.js`: `loadingChats`; `readChats`'in yorumu yeniden.
- [ ] `App.jsx`: `loading={loadingChats}` Sidebar'a.
- [ ] `Sidebar.jsx`: `loading` prop'u; `.sidebar__chats` hata yokken `loading` ise boş; `shown` boş;
  yorum yeniden.
- [ ] `FileRail.test.jsx`: spinner dönerken başlıkta sayı yok, açık, katlı, genişlik yüzünden katlı.
  Kırmızı. `FileRail.jsx`: `loading` iken `rail__count` çizilmez, iki başlıkta da.
- [ ] Bütün ön uç suite'i yeşil.

## Görev 4: derleme ve suite'ler

- [ ] `npm run build --prefix queen-agent/frontend`; `dist` `git add` ile sahnelenir.
- [ ] Dört suite, birer birer: `python -m pytest queen-agent -q`, `npm test --prefix
  queen-agent/frontend`, `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
