# Madde 444 — Copy başarıda komple yeşil, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** başarılı kopyalamada üç Copy düğmesinin tamamı tasarımın yeşiline döner, 2,5 saniye sonra
eski hâline; *"Could not copy"* kırmızı söz kalır; üçü de en az 116 px; soluk Copy hiç yeşil olmaz.

**Yaklaşım:** Her görevde önce test, kırmızı görülür, sonra kod. Dosyalar Edit ve Write ile değişir.

**Spec:** [m444](../specs/2026-10-09-queen-agent-m444-copy-yesil-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları ve ekrandaki her söz İngilizce.
- Yol haritasına, arka uca ve queen-editor'e dokunulmaz.

---

## Görev 1: `CopyButton.jsx` — söz kopyalanan metne bağlı

- [ ] `CopyButton.test.jsx` (yeni): başarıda *"Copied"* ve `data-said="yes"`; başarısızlıkta *"Could
  not copy"* ve `"no"`; 2,5 saniye sonra *"Copy"* ve `data-said` yok; söz sürerken metin boşalınca
  soluk, *"Copy"*, `data-said` yok; metin yokken soluk; söz sürerken başka metin gelince *"Copy"*,
  `data-said` yok. Metin boşalan ve başka metin gelen testler kırmızı.
- [ ] `CopyButton.jsx`: söz `{ word, text }` olarak tutulur, yalnız metin aynıyken gösterilir; yorum.
  Yeşil.

## Görev 2: `app.css` — yeşil aile

- [ ] `app.css.test.js`: `:root` `--success`, `--success-dark`, `--success-soft`'u taşır. Kırmızı.
- [ ] `app.css`: aile `--destructive`'in altına, neyi işaretlediğini söyleyen yorumla. Yeşil.

## Görev 3: `workspace.css` — tek kural, üç genişlik, iki yeşil

- [ ] `workspace.css.test.js`: `.ghost[data-said="yes"]` ve hover'ı aileden okur;
  `.ghost[data-said="no"]` `--destructive`; sınıf başına `data-said` kuralı yok; üç Copy de
  `min-width: 116px`; `.file-card__saved` ve `.msg__stamp-cached` değişkenden. Kenar çubuğunun ve
  proje listesinin `--accent`'li eski testleri gider. Kırmızı.
- [ ] `workspace.css`: altı kural silinir; `.ghost[data-said]` `.ghost`'un yanına; `min-width`
  üç seçiciye; iki yeşil değişkene. Yeşil.

## Görev 4: derleme ve suite'ler

- [ ] `npm run build --prefix queen-agent/frontend`.
- [ ] Dört suite, sırayla: `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`,
  `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
