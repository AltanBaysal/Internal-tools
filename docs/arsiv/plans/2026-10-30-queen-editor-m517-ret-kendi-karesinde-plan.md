# Madde 517 · Bir reddin cümlesi kalır, bir cevap kendi karesinde iş görür — plan

**Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-16), 517 · v11-16 ·
**Spec:** [2026-10-30-queen-editor-m517-ret-kendi-karesinde-design.md](../specs/2026-10-30-queen-editor-m517-ret-kendi-karesinde-design.md)

Önce test: testler yeni kuralı söyler (kırmızı), sonra kod (yeşil). Yalnız ekran.

## 1. Testler

- `frontend/src/features/photo_generation/PhotoDetail.test.jsx`, dosyanın sonuna "an answer stays with
  its frame (madde 517)" bloğu:
  - `deferred()` (cevabı testin vereceği istek) ve `mount(fid, frames, status)` (adımlamak için
    `rerender`) yardımcıları;
  - sıra başka karede çalışırken dört kart (Yeniden üret, katman silme, bekleyen katmanın Kuyruktan
    çıkar'ı, kare çıkarma) 2 sn'lik yoklamadan sonra da sunucunun cümlesini gösterir;
  - beş basışın (dördü ve ses) geç gelen reddi, basıştan sonra geçilen karede görünmez, ve basışın
    karesine dönülünce orada görünür (reviewer'ın bulgusu);
  - A'nın geç reddi B'nin ekrandaki kartını ezmez;
  - geç gelen başarı (ana ajanın eki): kare çıkarma `navigate` çağırmaz; Videoyu sil ve bekleyen
    katmanın Kuyruktan çıkar'ı B'nin sekmesini değiştirmez; Yeniden üret B'de "Kuyruğa eklendi"
    demez; B'nin kendi silmesi yoldayken A'nın başarısı B'nin penceresini kapatmaz.
- Kırmızılar çalıştırılıp görülür.

## 2. Kod

- `useGeneration.js`: `regenerate`, `removeLayer`, `dequeueLayer`, `removePhotos` reddedilince
  `{ error: failureText(err) }` ile döner (`refusal` yardımcısı); `setError` yerinde kalır.
- `PhotoDetail.jsx`:
  - `openFrame` ref'i, `useLayoutEffect` ile `fid`'den;
  - `refused`, `refusedAct`, `muteRefused` yerine `refusals` (`{ [fid]: { text, raw } }`), `refuse`
    ve `unrefuse`;
  - beş basışın cevabı: `null` ise (sayfa söküldü) hiçbir şey; ret her durumda `refuse(fid, …)`;
    ekrana dokunan işler (`busy`, pencere, `sent`, sekme, `navigate`) yalnız
    `openFrame.current === fid` iken; basış başlarken `unrefuse(fid)`;
  - `fid` efekti tabloya dokunmaz; tek `StatusErrorCard`, `refusals[fid]`'den.
- `npm test --prefix queen-editor/frontend`, `npm run build --prefix queen-editor/frontend`,
  `python -m pytest queen-editor -q`.

## 3. BACKLOG

- `queen-editor/BACKLOG.md`: iki iş silinir.
