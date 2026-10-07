# Mira Faz 14 (Durumlar ve doğrulama) — Uygulama Planı

**Hedef:** İskeletler (Madde 29), çevrimdışı şeridi (Madde 30), 1100px altı (Madde 31); ardından
uçtan uca tur kullanıcıya bırakılır (Madde 32).

**Mimari:** Arka uç değişmiyor. "Yükleniyor" bir alan olarak doğar; çevrimdışı hâli var olan
"cevap bekleyen sohbet" kuralına tek bir koşul ekler.

**Kaynak spec:** [Faz 14](../specs/2026-08-09-mira-faz-14-durumlar-design.md)

## Global Kısıtlar

- Boş-durum cümlesi yükleme bitmeden çizilmez.
- Çevrimdışıyken mesaj yine de gönderilir; istenmeyen tek şey cevaptır.
- Test komutları: `python -m pytest d:\code\github\internal-tools\mira -q` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend test`.

---

### Task 1: İskeletler

**Dosyalar:** Oluştur `features/workspace/Skeleton.jsx` · Değiştir `shared/useList.js`,
`useProjects.js`, `useChatLists.js`, `useFiles.js`, `HomeScreen.jsx`, `ProjectScreen.jsx`,
`ChatScreen.jsx`, `App.jsx`, `workspace.css` · Test `Skeleton.test.jsx`, `HomeScreen.test.jsx`,
`ProjectScreen.test.jsx`, `ChatScreen.test.jsx`

**Arayüzler:** Üretir `useList → {items, reload, loading}` · `<Skeleton rows={n} />`

- [ ] **Adım 1:** testleri yaz · **Adım 2:** kırmızı · **Adım 3:** yaz · **Adım 4:** yeşil.

---

### Task 2: Çevrimdışı

**Dosyalar:** Oluştur `shared/useOnline.js`, `features/workspace/OfflineStrip.jsx` · Değiştir
`useChat.js`, `App.jsx`, `workspace.css` · Test `useOnline.test.jsx`, `App.test.jsx`

**Arayüzler:** Üretir `useOnline() -> boolean` · `useChat(projectId, chatId, onFileCreated, online)`

`useChat`'in cevap isteyen etkisine tek koşul: `if (!online) return;`. Bağlantı dönünce etki
yeniden koşar ve sohbet hâlâ cevap beklediği için cevap istenir.

- [ ] **Adım 1:** testleri yaz · **Adım 2:** kırmızı · **Adım 3:** yaz · **Adım 4:** yeşil.

---

### Task 3: 1100px altı ve kapanış

**Dosyalar:** Değiştir `workspace.css` · Test yok (CSS; jsdom stil hesaplamaz)

```css
@media (max-width: 1100px) {
  .sidebar { width: 208px; }
  .chat-layout, .screen-layout { flex-direction: column; }
  .rail, .rail--open, .panel { width: auto; border-left: none; border-top: 1px solid var(--line); }
  .project-grid, .project-grid--reading { grid-template-columns: minmax(0, 1fr); }
}
```

- [ ] **Adım 1:** yaz · **Adım 2:** takımı koş · **Adım 3:** derle · **Adım 4:** commit ·
      **Adım 5:** kullanıcıya Madde 32 listesini bırak.

---

## Öz-denetim

**Spec kapsaması.** §1 Task 1 · §2 Task 2 · §3 Task 3 · §4 kullanıcıya kalıyor. Yedi testin altısı
Task 1-2'ye düşüyor; yedincisi (çevrimdışıyken mesaj yine gider) Task 2'de.

**Ad tutarlılığı.** `loading` üç hook'ta da aynı ad; `online` tek yönlü — `true` bağlıyken.

**Risk.** `useChat`'e dördüncü bir parametre ekleniyor; `onFileCreated` üçüncü sırada duruyor, sıra
karışırsa cevap hiç istenmez. Testte ikisi birden var.
