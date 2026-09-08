# Madde 199 · uygulama turu — şerit ve kalem tek satırda

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 199, ve
[test turu](2026-09-08-queenagent-m199-tek-satir-testler-design.md) — 6 kırmızı.

---

## Ne yazılacak

### `ChatScreen.jsx`

Bugün mesajın altında iki ayrı çocuk var: ternary'nin içindeki kalem, ve onun dışındaki
`<Versions />`. İkisi de kaldırılıp **tek bir satıra** giriyor.

- Yeni bir bileşen, `MessageFoot`. İçinde önce `<Versions />`, sonra kalem.
- **Kalemin varlığını çağıran taraf söylüyor:** `onEdit` verilmişse kalem var, verilmemişse yok.
  Bileşenin içinde *"bu bir kullanıcı mesajı mı, düzenleniyor mu"* diye ikinci bir karar yeri
  açmıyor — o karar zaten mesajın çizildiği yerde veriliyor.
- **Boşsa `null` dönüyor:** şerit tek sürümde çizilmiyor *(`Versions`'ın kendi kuralı)*, ve kalem de
  yoksa satır hiç doğmuyor.
- Kalem `<>…</>` parçasından çıkıyor, yani ternary'nin kullanıcı dalı yalnız bubble'ı bırakıyor.

### `workspace.css`

- Yeni `.msg__foot`: `display: flex`, `align-items: center`, ve aralarında `gap`.
- `.versions`'ın `margin-top: 6px`'i **kalkıyor**. Sütunun çocuğuyken kendi payına ihtiyacı vardı;
  satırın içinde o pay `.msg`'in `gap`'inin üstüne binerdi.

## Ne değişmiyor

- **Bubble sarmalanmıyor.** 197'nin kapattığı kusur bubble'ın bir satır sarmalayıcısına girmesiydi;
  buradaki satır yalnız altındaki notları taşıyor, bubble `.msg`'in doğrudan çocuğu kalıyor.
- `Versions`'ın kendi içi, okların adları, `EditMessage`'ın hiçbir şeyi.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir: **933 · 648 · 739 · 591**. Sonra `dist` derlenir ve
kaynakla **aynı commit'te** iner — ön yüz değişikliği aksi hâlde bitmiş sayılmaz.
