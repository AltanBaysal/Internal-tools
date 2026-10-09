# Madde 443 — Arşivdeki proje açılır, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** Archived'daki satıra basınca proje öteki projeler gibi açılır ve Archived'da kalır;
aramada Enter iki sekmede de çizilen ilk satırı açar.

**Yaklaşım:** Her görevde önce test, kırmızı görülür, sonra kod. Dosyalar Edit ve Write ile değişir.

**Spec:** [m443](../specs/2026-10-09-queen-agent-m443-arsivli-acilir-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları ve ekrandaki her söz İngilizce.
- Yol haritasına ve queen-editor'e dokunulmaz. Arka uçta kod değişmez, yalnız bir test eklenir.

---

## Görev 1: arka uç — sunucu arşivdekini reddetmiyor

- [ ] `test_pin_archive.py`: arşivlenmiş projede mesaj gönderilir, sohbetler ve sohbet okunur,
  diske konan bir dosya listelenir ve okunur; hiçbiri reddedilmez, proje sonunda hâlâ arşivde.
  Bugünkü kodla yeşil olmalı: test kuralı tutar, kod yazılmaz.

## Görev 2: `ProjectRow.jsx` — arşivdeki satır da düğme

- [ ] `ProjectRow.test.jsx`: *"an archived row is not a way into its project"* yerine arşivdeki
  satır `all-projects__row-open` düğmesi; sütunlar, `title`, basınca `onOpen("p2")`, ⋯ yanında.
  Üst yorum. Kırmızı.
- [ ] `ProjectRow.jsx`: arşivdeki gövde gider; `Columns` düğmenin içine döner; üst yorum. Yeşil.

## Görev 3: `AllProjectsScreen.jsx` — Archived satırı açılır, aramada Enter

- [ ] `AllProjectsScreen.test.jsx`: Archived testinde satır `row-open`, basınca `onOpenProject("p5")`;
  Enter testleri: Projects'te aramanın bıraktığı ilk satır (pinli önce), Archived'da ilk arşivli,
  boş kutuda sekmenin ilk satırı, eşleşme yokken ve yüklenirken hiçbir şey. Kırmızı.
- [ ] `AllProjectsScreen.jsx`: eşleşenler (`found`) ekranda hesaplanır, `ProjectList` onları alır;
  arama `onKeyDown`'da Enter `found[0]`'ı açar; üst yorum. Yeşil.

## Görev 4: `App.test.jsx` — uçtan uca

- [ ] Archived'daki satır son sohbeti açar, bar adını taşır, PATCH yok, mesaj o projeye gider;
  Exit project'ten sonra Projects'te yok, Archived'da var. Sohbeti olmayan arşivdeki proje taslakta
  açılır. Görev 2–3'ten sonra yeşil.

## Görev 5: CSS

- [ ] `workspace.css.test.js`: `.all-projects__row-text` testi çıkar.
- [ ] `workspace.css`: `.all-projects__row-text` kuralı silinir.

## Görev 6: derleme ve suite'ler

- [ ] `npm run build --prefix queen-agent/frontend`.
- [ ] Dört suite, sırayla: `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`,
  `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
