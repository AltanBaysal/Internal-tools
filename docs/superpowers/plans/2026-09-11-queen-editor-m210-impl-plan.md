# Madde 210 — sürüm kaydı · uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-11-queen-editor-m210-surum-kaydi-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

> İlk deneme ayrı bir kayıt dosyası yazdı (`SURUMLER.md`, `b5eed21`); kullanıcı onu istemedi, çünkü
> **ad kayıt olacak.** Bu plan o karara göre yazıldı ve dosya `9a1c271`'de kaldırıldı.

## Adımlar

**1 · Tek belgeli sürümler yeniden adlandırılır.** `git mv`, içeriğe dokunmadan: eski *v14* → `v4`,
eski *v4* → `v2`. Çakışma yok — tarih öneki ikisini de ayırıyor.

**2 · v1 birleşir.** Eski *v2* ve *v3*, `2026-08-03-queen-editor-v1-roadmap.md` içinde *Koşu 1* ve
*Koşu 2* olur. Başlık seviyeleri bir kademe iner; birbirlerine giden bağlantılar bölüm adına döner.

v2'nin dalı **yazılmıyor, çünkü bilinmiyor** — belgede hiç geçmiyor ve ölçülemiyor. Kayıt bunu
söyler, ölçümü yanına koyar *(commit `01344b0`, `feat/queen-editor-v1`'in geçmişinde)*, ve uydurulmuş
bir dal adı yazmaz.

**3 · v3 birleşir — sekiz koşu.** Eski *v5, v6, v7, v8, v9, v11, v12, v13* →
`2026-08-12-queen-editor-v3-roadmap.md`, *Koşu 1*'den *Koşu 8*'e.

En büyük belge *(eski v5, 455 satır)* **`git mv` ile taşınır**, yani baytlarına hiç dokunulmaz;
başlığı birleşme başlığına çevrilir. Kalan yedisi elle eklenir. Sebebi: bin satırı yeniden yazmak bu
işin tek gerçek riski, ve yarısı hiç riske girmeden taşınabiliyor.

**4 · Bağlantılar çevrilir.** Eski adlara atıf yapan her `.md` — `docs/` altındakiler,
`queen-editor/*.md` ve `CLAUDE.md` — yeni ada geçer. On iki eski ad, düz metin değişimi; başka hiçbir
metne dokunulmuyor. *(Kullanıcı onayıyla tek komutta yapıldı: 157 dosya. Elle 130'dan fazla düzenleme
demekti ve mekanik bir ad değişikliğinde hata payı orada daha yüksek.)*

**5 · CLAUDE.md'nin kuralı düzelir.** *"one file per run, highest `vN` current"* gidiyor; yerine **bir
sürüm bir daldır, o dalın bir yol haritası olur ve adı sürümünü söyler** geliyor. Koşu sırasında çıkan
iş, açık olan yol haritasına madde olarak eklenir — ikinci bir belge değil.

**6 · Üçüncü iddia dürüst bilinmeyeni kabul eder.** Başlığında dal adı olmayan bir belge, kayıt onu
açıkça `bilinmiyor` diyorsa geçer; sessiz kalan belge hâlâ kırmızı. *(Ad kayıt olduktan sonra bu
iddia biçim değiştirdi: artık ad ile başlığın aynı dalı söylemesini tutuyor.)*

**7 · Yol haritaları `roadmaps/` klasörüne taşınır** *(kullanıcı kararı, 13 Eylül)*. 14 belge, üç tool
birden, `git mv` ile — içeriklerine dokunulmadan.

Bağlantılar bu kez ad değil **yol** olduğu için üç biçim ayrı ayrı çevrilir, her biri düz metin
değişimi: `../plans/<ad>` *(387 dosya)*, `docs/superpowers/plans/<ad>` *(18 dosya)*, ve `plans/`
içindeki görev planlarında çıplak `<ad>` *(24 dosya)*. Göreli yol **hesaplanmıyor** — üç biçim
sayılıp üçü tek tek değiştiriliyor, çünkü hesap yapan bir script okunamaz hâle geliyordu.

Kalan dört bağlantı testin listesinden elle düzeltildi: `docs/` kökünde `superpowers/plans/` diye
yazılmış üç tanesi, ve `plans/` içinden `../docs/superpowers/plans/` diye yazılmış bir tanesi — o
dördüncüsü **taşınmadan önce de kırıktı**, eski iddia ada baktığı için hiç görülmemişti.

**7b · Haritaların kendi dışa bakan bağlantıları.** Bir harita `plans/` içindeyken görev planlarına
çıplak adla gidiyordu; `roadmaps/` içinden o ad hiçbir şeye varmıyor. Altı haritada yedi bağlantı
`../plans/`'a çevrildi, biri de `../../../CLAUDE.md`'ye — o da zaten kırıkmış. Bu yön kolay
atlanıyor, çünkü `../specs/` ve `../../../queen-editor/` derinlik değişmediği için kendiliğinden
çalışmaya devam ediyor; onun için kendi iddiası yazıldı.

**7c · CLAUDE.md'nin klasör satırı** `roadmaps/`'i gösterir ve `plans/`'ın madde planlarının yeri
olduğunu söyler.

**8 · Takım koşulur.**

```bash
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

**9 · Yeşil commit edilir**, ve yol haritasının 210 satırı ✅ ile işaretlenip sayaç 1/7'ye çekilir.

## Sonuç

Arka uç **747 yeşil**, ön yüz **591 yeşil** ve hiç değişmedi — bu madde ön yüze dokunmuyor, `dist`
derlenmiyor.

On üç yol haritası beşe indi: v1 *(iki koşu)*, v2, v3 *(sekiz koşu)*, v4, v5; ve 14 haritanın hepsi
`docs/superpowers/roadmaps/` altına geçti. Hiçbir sürüm numarası iki belgede geçmiyor, hiçbir ad kendi
dalından başkasını söylemiyor, `plans/` altında tek bir harita kalmadı, ve iki yönün de bağlantısı
çözülüyor — haritaya gidenler de haritadan çıkanlar da.

**Taşınma iki eski kırığı ortaya çıkardı**, ikisi de bu maddede kapandı: bir görev planının kendi
klasörünü `../docs/superpowers/plans/` diye yazması, ve bir haritanın `CLAUDE.md`'ye hiçbir yere
varmayan çıplak adla bağlanması. İkisini de ad yerine yolu çözen iddia buldu.

## Dokunulmayanlar

- **Maddelerin metni.** Birleşme kopyalamadır; hiçbir görev yeniden yazılmadı.
- **Madde numaraları.** Her koşu görevlerini 1'den sayıyordu ve öyle kaldı; numara bölümüne ait.
- **QueenAgent'ın belgeleri.** Onun adları kendi sayacıyla tutarlı.
