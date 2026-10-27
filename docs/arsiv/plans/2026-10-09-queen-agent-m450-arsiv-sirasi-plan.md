# Madde 450 — Arşivle Unarchive'ın sırası, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** Archive'la Unarchive arka arkaya basılınca son basılan kazanır: ekran onu hemen gösterir,
sunucu onu son yazar, ve sayfa yenilenince o durur.

**Yaklaşım:** Her görevde önce test, kırmızı görülür, sonra kod. Dosyalar Edit ve Write ile değişir.

**Spec:** [m450](../specs/2026-10-09-queen-agent-m450-arsiv-sirasi-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları ve ekrandaki her söz İngilizce.
- Arka uca, yol haritasına ve queen-editor'e dokunulmaz.

---

## Görev 1: `AllProjectsScreen.jsx` — son basış ekranda durur

- [ ] `AllProjectsScreen.test.jsx`: `onScreen`'in `onArchiveProject`'i her basışta bekleyen bir söz
  döner; yardımcıya `unarchive(id)` eklenir. Yeni testler: arşiv beklerken Unarchive projeyi o anda
  Projects'e getirir, arşivin cevabından sonra da orada, Unarchive'ın cevabıyla sunucunun listesi geçer;
  tersi sırada proje Archived'da kalır; Unarchive satırı beklemeden çıkarır, ret onu geri getirir.
  Kırmızı.
- [ ] `AllProjectsScreen.jsx`: `leaving` (dizi) → `asked` (id → son basış); `archive` her basışta
  kendi kaydını yazar, Archive'da odağı devreder, cevabı bekler, kaydı yalnız hâlâ kendisininse siler;
  `listed` `asked`'in istediğini çizer; yorumlar. Yeşil.

## Görev 2: `inTurn.js` — sıra

- [ ] `inTurn.test.js`: bir iş öncekinin sonucundan önce başlamaz, çağıran kendi sonucunu alır;
  reddeden ve fırlatan iş çağıranına reddini verir, sonraki yine koşar. Kırmızı.
- [ ] `inTurn.js`: `inTurn()` → `queued(task)`; sıra `run.catch(() => {})`'i bekler. Yeşil.

## Görev 3: `useProjects.js` — okumalar ve yazmalar sırada

- [ ] `App.test.jsx`: PATCH'lerin cevabını tutan sahte sunucu (`serverForRows`'un üstünde). Archive'dan
  hemen sonra Unarchive: ilk cevap gelmeden tek PATCH; ikincisi birincinin listesinden sonra; sonunda
  Projects'te, yeniden kurulan App'te de. Tersi sırada Archived'da. Arşiv beklerken onaylanan silme,
  arşivin listesinden sonra gider. Kırmızı.
- [ ] `useProjects.js`: sıra bir kez kurulur; `editProject` (PATCH + liste) ve `removeProject` birer
  iş; dışarı verilen `reloadProjects` sıradan geçer; ilk okuma, Try again ve yeni proje dışarıda;
  yorumlar. Yeşil.

## Görev 4: derleme ve suite'ler

- [ ] `npm run build --prefix queen-agent/frontend`; yeni `dist` dosyaları `git add` ile sahnelenir.
- [ ] Dört suite, birer birer: `python -m pytest queen-agent -q`, `npm test --prefix
  queen-agent/frontend`, `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
