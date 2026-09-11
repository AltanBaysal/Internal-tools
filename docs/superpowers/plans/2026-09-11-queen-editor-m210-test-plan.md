# Madde 210 — sürüm kaydı · test turunun planı

**Spec:** [test turu](../specs/2026-09-11-queen-editor-m210-surum-kaydi-testler-design.md) ·
**Madde:** [v5 yol haritası](2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. `SURUMLER.md`, CLAUDE.md'nin cümlesi ve eski belgelerin başlıkları
uygulama turunda düzelir.

## Adımlar

**1 · Tek dosya açılır:** `queen-editor/backend/tests/test_version_record.py`.

Komşusu `test_notebook_clones_its_branch.py` ile aynı türden: deponun kendi metnini okuyup bir olguyu
tutuyor, çünkü o olguyu başka hiçbir test fark etmiyor. Kendi dosyası, çünkü sorusu ne defterin ne
üreticilerin — o adların altına girseydi ad tutmadığı bir söz vermiş olurdu.

**2 · Yollar ve okuyucular.**

- `TOOL` → `queen-editor/`, `REPO` → deponun kökü *(komşu dosyadaki `os.path.dirname` zinciriyle
  aynı biçimde)*.
- `RECORD` → `queen-editor/SURUMLER.md`.
- `PLANS` → `docs/superpowers/plans/`.
- `_roadmaps()` → `*queen-editor-v*-roadmap.md` kalıbına uyan dosyalar, adlarıyla birlikte. Bu koşunun
  kendi belgesi de listeye dahil: o da kayda yazılmak zorunda.
- `_branch_in_header(text)` → bir yol haritasının ilk satırlarındaki `feat/queen-editor-vN` adını
  çıkarır. Hem `**Koşu dalı:**` hem `**Branch:**` yazan belgeler var, o yüzden etikete değil **dal
  adının kendisine** bakılır: metinde geçen `feat/queen-editor-` ile başlayan ad.

**3 · İddia 1 — kayıt var ve güncel sürümü adlıyor.**

`SURUMLER.md` okunur; içinde **Güncel** diye işaretlenmiş bir satır ve o satırda tek bir
`feat/queen-editor-vN` adı bulunur. Birden fazla ad varsa da kırmızı: güncel sürüm tekildir.

*Bugün kırmızı — dosya yok.*

**4 · İddia 2 — her yol haritası kayıtta geçiyor.**

`_roadmaps()`'in verdiği her dosya adı `SURUMLER.md`'nin metninde aranır. Eksik olan varsa kırmızı,
ve mesaj eksik olanları adlarıyla sayar.

*Bugün kırmızı — dosya yok.*

**5 · İddia 3 — kayıttaki dal, belgenin kendi başlığındaki dal.**

Her yol haritası için: belgenin başlığından dal adı okunur, kayıttaki o belgeye ait satırdan da dal
adı okunur, ikisi karşılaştırılır. Başlığında dal adı **hiç olmayan** belge de kırmızı verir — v2
bugün öyle, ve düzeltmesi uygulama turunun işi.

*Bugün kırmızı — hem dosya yok hem v2'nin başlığı dal adı taşımıyor.*

**6 · İddia 4 — CLAUDE.md artık yanlış tarifi vermiyor.**

`CLAUDE.md` okunur ve `highest \`vN\` current` ifadesi aranır; varsa kırmızı. Mesaj cümlenin neden
yanlış olduğunu söyler: en yüksek numaralı belge güncel sürüm değil.

*Bugün kırmızı — cümle yerinde duruyor.*

**7 · Takım koşulur.**

```bash
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: **dört kırmızı**, arka ucun geri kalanı yeşil, ön yüz süiti değişmemiş.

**8 · Kırmızı commit edilir.** `skip` ya da `xfail` yok — kırmızı görülmeden implementasyon turu
başlamaz.

## Sonra ne gelir

Uygulama turu: `SURUMLER.md` yazılır, CLAUDE.md'nin cümlesi düzelir, v2'nin başlığına dal adı girer
ve `Branch:` diyen iki belge `Koşu dalı:`na çekilir. Dosya adları ve yolları değişmez.
