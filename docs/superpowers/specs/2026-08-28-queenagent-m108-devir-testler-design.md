# Madde 108 — Devir beşinci adım olur · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 108.
**Gözlenen** *(28 Ağustos, ikinci deneme)*: akış sahne listesinden sonra durmadı — Generate
prompts+'ı hiç göstermedi, frame'leri *"yazayım mı?"* diye kendisi teklif etti, ve istenince onunu
tek `edit_file`'da yazdı.

## Sebep

- Devir cümlesi numaralı listenin **dışında** ve emir kipinde değil *("the closing message
  names…" — tarif)*. Zayıf model listeyi bitirince durur.
- 4. adım *"what the frames will be written from"* diyerek devamı ima ediyor; listeye en yakın
  cümle kazanıyor.
- Sınır yalnız gerekçeyle anlatılıyor *("would be doing its work twice")*, kural olarak değil.

## Bu maddenin sınırı

Yalnız **akış metni**. prompt+'ın düzenleyici olması ayrı bir problem ve ayrı bir madde
*(113)*; burada ona dokunulmuyor.

## Testler — `test_skills.py`, iki yeni

1. **Devir numaralı adım:** metinde `"Five steps"` ve `"5. The handoff"` var, ve `"5. The
   handoff"` metindeki son `"Generate prompts+"` geçişinden önce geliyor — yani devir adımın
   içinde, sonuna iliştirilmiş bir cümle değil.
2. **Israr edilse de yazmıyor:** `"never written here"` ve `"not even when the user asks"`.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_skills.py` | 2 |

Defter çifti *(`test_notebook`, 2)* bu maddenin değil.

## Bilerek yapılmayanlar

- **Kod yazılmaz** — tur kırmızı commit'lenir.
- **prompt+ metnine ve seçici satırına dokunulmaz** *(113)*.
- **Ritüel cümlelerine dokunulmaz** *(107 koşulmuyor)*.
- **`dist` derlenmez** — ön yüz değişmiyor.
