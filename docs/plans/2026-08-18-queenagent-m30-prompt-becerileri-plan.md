# Madde 30 — Prompt üreten üç beceri · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m30-prompt-becerileri-design.md](../specs/2026-08-18-queenagent-m30-prompt-becerileri-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

Madde iki uçlu: **iki tur**, her turda önce yalnız testler (kırmızı), sonra uygulama.

---

## Tur 1 — Üç yönerge

### Adım 1 — Testler (kırmızı commit)

`test_skills.py`:

- **Altı** kimlik yönerge taşır (üçlü liste altıya çıkar); tanınmayan kimlik hâlâ boş dize.
- Düz yönerge: `PROMPTS = [` şekli, `-plain` adı, İngilizce kuralı, partili yazım; yapı dosyasını
  ve `build_prompts`'u kullanmadığını söyler.
- Yapılı yönerge: şemanın alan adları (`quality`, `characters`, `locations`, `shots`, `action`,
  `camera`), adı taşımak, **beşerli** partiler, iskelet, `build_prompts`, elle birleştirme yasağı,
  İngilizce.
- **Sıra:** yapılı yönergede kural defteri `build_prompts`'tan **önce** geçer.
- Kural defteri **tek metin**: aynı sabit hem yapılı yönergede hem Verify'da birebir geçer.
- Verify: düzeltmemek, dosya yazmamak, 3. kuralı kullanıcıya bırakmak.
- Defterin dördüncü maddesi **not** der, ihlal demez.

### Adım 2 — Uygulama

`domain/skills.py` — `RULEBOOK` sabiti ve üç metin.

---

## Tur 2 — Okuyucunun mono gövdesi

### Adım 1 — Testler (kırmızı commit)

- `FilePanel.test.jsx` — `.md` Markdown çizilir *(bugünkü davranış, kayıtta kalır)*; `.json` ve
  `.py` **birebir** gösterilir: girinti durur, `#` satırı başlık olmaz, `**kalın**` yıldızlarını
  korur.
- `workspace.css.test.js` — `.reader__code` mono yüz, `white-space: pre`, `overflow-x: auto` ve kod
  bloğunun ölçüleri; **çerçeve ve zemin yok**.

### Adım 2 — Uygulama

`FilePanel.jsx` · `workspace.css`.

---

## Kapanış denetimi

- Kural defteri tek yerde yazılı (`grep` iki yönergede de sabiti kullanıyor, metni kopyalamıyor).
- Arka uçta `skills.py` dışında değişiklik yok; ön uçta yeni istek yok.
- Karar dosyanın **adından** veriliyor, çipin üç harfinden değil.

## Risk

Yönergelerin modele uyduğu ve deneyin sonucu Madde 35'te görülür.
