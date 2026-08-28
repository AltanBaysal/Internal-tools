# Madde 113 — prompt+ var olanı da düzenler · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 113.
**Sebep:** prompt+'ın metni yalnız baştan kurmayı anlatıyor — açılışı *"this is the skill that
builds them"*, gövdesi iskeletten listeye giden yol. *"Bu promptu beğenmedim, üçüncü kareyi
değiştir"* hiçbir yerde geçmiyor; metinde görmediği işi zayıf model ya reddeder ya baştan kurar.
Madde 94'ün kaydı prompt+'ın işini zaten *"var olanı güncellemek"* diye yazmıştı, ve o cümle
metne hiç geçmemiş.

**108 ile ilişkisi:** 108 kullanıcıyı buraya yolluyor; burası da onu karşılayabilmeli.

## Testler

### `test_skills.py` — iki yeni

1. **İki işi birden söylüyor:** açılışta `"or changed"`, ve düzenleme yolunda
   `"build_prompts again"` — yani değişiklikten sonra liste yeniden kuruluyor.
2. **Değişiklik dosyadan geçiyor:** `"rebuilt rather than patched"` — türev `.py` elle yamanmaz.

### `skills.test.js` — bir yeni

Seçicideki satır düzenlemeyi de söylüyor: `detail` içinde `change`. *(Var olan `already have`
pini korunur.)*

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_skills.py` | 2 |
| `skills.test.js` | 1 |

Defter çifti bu maddenin değil.

## Bilerek yapılmayanlar

- **Kod ve metin yazılmaz** — tur kırmızı commit'lenir.
- **Akış metni ellenmez** — 108 kapandı.
- **Şema ellenmez** *(109, 110, 111)*.
- **`dist` bu turda derlenmez** — ön yüz kaynağı tur 2'de değişiyor.
