# Madde 350 — Dosya listesinde yazılı Refresh, başlığın satırında · uygulama turu

**Kaynak:** [yol haritasının 350'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2m);
tasarım: `queen-agent-v3`'ün 154'ü ve 175'i. **Testler:**
[test turunun spec'i](2026-09-29-queenagent-m350-liste-refresh-testler-design.md), kırmızısı `c1842c6d`.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne yapılır

Üç dosya, üçü de `queen-agent/frontend/src/features/workspace/` altında:

1. **`FileRail.jsx`**
   - `RefreshFiles` yalnız düğmeyi çizer: `<button type="button" className="ghost file-list__refresh"
     onClick={onRefresh}>Refresh</button>`. Kendi satırı (`file-list__bar`) ve `aria-label`'ı kalkar:
     yazı düğmenin adı. İki ekran aynı düğmeyi paylaşmaya devam eder; nerede duracağını yeri söyler.
   - Başlık — `rail__head` düğmesi ya da `rail__head--still` etiketi — bir
     `<div className="rail__bar">`'ın içine girer; açıkken yanında `RefreshFiles`, katlıyken yalnız
     başlık. Genişlik yüzünden katlanmak hep katlı demek (`App.jsx`: `railCollapsed ||
     railFoldedByWidth`), o yüzden koşul yalnız `collapsed`.
   - `FileList` `RefreshFiles`'ı çizmez ve `onRefresh`'i almaz: kutu doğrudan spinner'la, hata
     satırlarıyla ya da ilk dosyayla başlar.
   - Madde 192'nin yorumu düğmenin neden listenin içinde durduğunu anlatıyordu (bir düğme bir düğmenin
     içinde duramaz); artık yanında durduğu için yorum bugünkü nedeni söyler.
2. **`ProjectScreen.jsx`** — kutusunun sağ üstündeki yeri korur: `<div className="file-list__bar">
   <RefreshFiles onRefresh={onRefresh} /></div>`. Böylece o ekranın `Refresh`'i de yazılı ve
   çerçeveli olur; ekran v9-2n'de kalkar.
3. **`workspace.css`**
   - Yeni `.rail__bar`, `.rail__head--still`'in önünde: `display: flex`, `align-items: center`,
     `gap: 8px`, `margin-bottom: 12px` — tasarımın `kit.css`'indeki gibi.
   - `.rail__head`: `width: 100%` ve `margin-bottom: 12px` kalkar, `flex: 1` gelir. Satırı `Refresh`'le
     paylaşır; katlıyken satırı tek başına doldurur.
   - `.rail__head--still`: `margin-bottom: 12px` kalkar; boşluk satırın.
   - `.file-list__refresh` ve `.file-list__refresh:hover` kalkar: görünüş `ghost`'un, açık dosyanın
     `Refresh`'i gibi. Tasarımda da kendi kuralı yok.
   - `.file-list__bar` kalır, yalnız proje ekranının; yorumu buna göre düzelir.

## Dokunulmayanlar

- `FilePanel.jsx` ve `.reader__*` kuralları (342): açık dosyanın `Refresh`'i olduğu gibi.
- Başka lanelerin kuralları; `workspace.css`'te yalnız yukarıdaki kurallar değişir, sıraları
  korunur.
- CODE-STANDARD.md: dosya eklenmiyor, kalkmıyor.
- `dist` derlenmez: birleştirirken conductor derler.

## Nasıl görülür

Dört satır: `npm test --prefix queen-agent/frontend` yeşil (695 + 8); öteki üç süit yeşil.

Tarayıcıda: bir projenin sohbetinde sağ panelin üst satırında solda `PROJECT FILES 5 ›`, sağda
çerçeveli `Refresh`; altındaki kutunun ilk satırı ilk dosya. `›`'e basınca panel katlanır ve
`Refresh` gider; açılınca geri gelir.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m350-liste-refresh-uygulama-plan.md).
