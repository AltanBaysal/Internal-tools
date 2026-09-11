# Madde 210 — queen-editor'ün sürüm kaydı · test turu

**Kaynak:** [yol haritasının Madde 210'u](../plans/2026-09-11-queen-editor-v5-roadmap.md).

## Ne kanıtlanacak

*"Queen-editor v kaçta"* sorusunun bugün iki cevabı var ve ikisi de belgelerden çıkarılıyor: dal
sayacı **v4** diyor, yol haritalarının adları **v14**. Soru bu sabah soruldu ve yanlış cevaplandı.

Hata, koşan yol haritasına madde ekleyecek yerde her koşuda yeni bir roadmap açmaktı: bir sürüm bir
daldır, ve o dalın **tek** yol haritası olur. Dört dal kesilmiş, on üç roadmap yazılmış.

Bu tur, cevabın tek yerden okunmasını ve o yerin belgelerle çelişememesini tutar.

## Kayıt nerede durur

`queen-editor/SURUMLER.md` — tool'un kendi kapısının yanında, `README.md`, `FOUNDATION.md` ve
`BACKLOG.md` ile aynı klasörde.

**`docs/` altında değil**, çünkü orası koşuların kendi belgelerinin yeri ve kayıt tam da onların
üstünde duran şey — orada dursaydı on dördüncü bir roadmap gibi görünürdü. **CLAUDE.md'de değil**,
çünkü CLAUDE.md kural söyler, olgu tutmaz; bir sürüm numarası her koşuda değişir, kural değişmez.
**QueenAgent'ın kaydı bu dosyaya girmiyor:** her tool kendi kurallarını kendi taşıyor, ve queen-agent
sürümünü zaten başka bir yerde tutuyor *(`frontend/src/shared/version.js`, madde 209)*.

## Testler ne tutar, ne tutmaz

**Sürüm numarasını tutmaz.** `GUNCEL == "v5"` diye bir iddia, elle verilen bir kararı ikinci bir yere
kopyalar; v6 geldiğinde ikisini birden değiştirmek gerekir ve biri unutulursa süit koşuyu değil
kendini korur. Numara bir karar, davranış değil.

**Tutarlılığı tutar.** Kaydın söylediği ile belgelerin söylediği aynı olmak zorunda. Bu bir kararı
kopyalamıyor; **iki kaydın ayrışamamasını** söylüyor — bu maddenin bütün derdi de o ayrışma.

**Dalın var olduğunu tutmaz.** Git'e sorulmuyor: bir klonda dal olur, başkasında olmaz, ve süit
hangi makinede koştuğuna göre renk değiştiremez.

## Dört iddia

| # | Nerede | Ne |
|---|---|---|
| 1 | `test_version_record.py` | `SURUMLER.md` var, ve güncel sürümü tek bir `feat/queen-editor-vN` dalıyla adlıyor |
| 2 | `test_version_record.py` | queen-editor'ün **her** yol haritası kayıtta geçiyor |
| 3 | `test_version_record.py` | her yol haritasının kayıttaki dalı, o belgenin kendi başlığındaki dal |
| 4 | `test_version_record.py` | CLAUDE.md sürümü artık *"en yüksek vN"* diye tarif etmiyor |

**İkincisi yeni roadmap'i yakalar.** Bir sonraki koşu dosyasını açıp kayda yazmayı unutursa, kayıt
sessizce bayatlamaz — süit kırmızı verir. Bugünkü karmaşa tam olarak böyle birikti.

**Üçüncüsü asıl iddia.** Her yol haritası başlığında `**Koşu dalı:** \`feat/queen-editor-vN\`` yazıyor
ve on üçünün onikisi bunu zaten taşıyor; v2 taşımıyor, v3 ile v4 `**Branch:**` diyor. Kayıt ile
başlık ayrışırsa hangisinin doğru olduğu yine bilinmez, yani iddia ikisini birbirine bağlıyor.

**Dördüncüsü hatanın kaynağını tutar.** CLAUDE.md bugün *"one file per run, highest `vN` current"*
diyor. Bu sabahki yanlış cevap o cümleden çıktı: en yüksek numaralı belge güncel sürüm değil. Cümle
düzelmeden kayıt düzelse bile bir sonraki okuyan aynı yere düşer.

## Bu turda yazılmayanlar

- **`SURUMLER.md` yazılmıyor.** Dosyanın kendisi, CLAUDE.md'nin düzeltilmesi ve eski belgelerin
  başlık satırları uygulama turunun işi. Bu tur yalnız testleri koyuyor.
- **Dosya adları değişmiyor** — ne bu turda ne öbüründe. Yazılmış spec'ler ve görev planları bu
  adlara atıf yapıyor; v5–v13'ün dokuzu aynı dalda koştuğu için yeniden adlandırma zaten dokuz
  dosyayı tek ada yığardı.
- **Eski koşuların metni birleştirilmiyor.** Yüz elliden fazla madde tek belgeye yığılırdı ve
  gerçekten olmuş koşu sınırları silinirdi — kaydı düzeltmek için kaydı bozmak olurdu.
- **QueenAgent'ın kaydı kapsam dışı.** Onun sayacı ayrı ve kendi yerinde duruyor.
- **`dist` derlenmiyor:** bu madde ön yüze hiç dokunmuyor.

## Nasıl görülür

```bash
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

**Dört kırmızı**, arka ucun geri kalanı yeşilde durur; ön yüz süiti hiç etkilenmez. Kırmızı hâliyle
commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-11-queen-editor-m210-test-plan.md).
