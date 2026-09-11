# Sürümler — Queen Editor

**Güncel sürüm: v5** — dalı `feat/queen-editor-v5`.

Bir sürüm bir daldır. Dal açılır, koşu orada koşar, kullanıcı dener, dal main'e girer ve bir sonraki
sürüm yeni bir dalla başlar. **O dalın tek bir yol haritası olur**, ve koşu sürerken çıkan yeni işler
o yol haritasına madde olarak eklenir.

Bu dosya iki soruyu cevaplar: queen-editor v kaçta, ve elindeki yol haritası hangi sürüme ait.

## Sürümler ve koşuları

Bir belgenin adındaki numara onun sürümü **değildir**. Aşağıdaki tablo bağlayıcı olandır.

| Sürüm | Dal | Yol haritası |
|---|---|---|
| — | *bilinmiyor* | `2026-08-03-queen-editor-v2-roadmap.md` |
| v1 | `feat/queen-editor-v1` | `2026-08-08-queen-editor-v3-roadmap.md` |
| v2 | `feat/queen-editor-v2` | `2026-08-08-queen-editor-v4-roadmap.md` |
| v3 | `feat/queen-editor-v3` | `2026-08-12-queen-editor-v5-roadmap.md` |
| v3 | `feat/queen-editor-v3` | `2026-08-13-queen-editor-v6-roadmap.md` |
| v3 | `feat/queen-editor-v3` | `2026-08-13-queen-editor-v7-roadmap.md` |
| v3 | `feat/queen-editor-v3` | `2026-08-13-queen-editor-v8-roadmap.md` |
| v3 | `feat/queen-editor-v3` | `2026-08-13-queen-editor-v9-roadmap.md` |
| v3 | `feat/queen-editor-v3` | `2026-08-13-queen-editor-v11-roadmap.md` |
| v3 | `feat/queen-editor-v3` | `2026-08-14-queen-editor-v12-roadmap.md` |
| v3 | `feat/queen-editor-v3` | `2026-08-14-queen-editor-v13-roadmap.md` |
| v4 | `feat/queen-editor-v4` | `2026-08-20-queen-editor-v14-roadmap.md` |
| v5 | `feat/queen-editor-v5` | `2026-09-11-queen-editor-v5-roadmap.md` |

Belgeler [docs/superpowers/plans/](../docs/superpowers/plans/) altında, ve **adları değişmiyor**:
yazılmış spec'ler ile görev planları onlara adlarıyla atıf yapıyor.

**v10 diye bir yol haritası yok.** O numarada yalnız tek bir görev dosyası duruyor
(`2026-08-13-queen-editor-v10-gorev-1-uretim-kendi-baslamasin.md`), ve roadmap'i hiç yazılmamış.

**İlk belgenin dalı bilinmiyor, ve uydurulmadı.** `2026-08-03-queen-editor-v2-roadmap.md` hiçbir
yerinde dal adı taşımıyor. Onu ekleyen commit `01344b0`, `feat/queen-editor-v1`'in geçmişinde
duruyor — ama sonradan o dala girmiş bir commit de orada durur, yani bu onun orada yazıldığını
kanıtlamıyor. Üstüne bu koşu, v3'ün v1'i adlayarak açıldığı gün kapanmış.

## Ne yanlış gitti

**Koşan yol haritasına madde eklenecek yerde her koşuda yeni bir roadmap açıldı.** Her yeni belge bir
öncekine zincirlendi — v5'in başlığı *"yerini aldığı doküman: v4-roadmap"* diyor — ve numarası birer
birer arttı. Dal ise ancak öncekisi main'e girince kesildi. Böylece dört dala on üç belge düştü, ve
ikisi aynı harfi paylaştığı için tek bir sayaç sanıldı.

Bunun bedeli 11 Eylül 2026'da görüldü: *"queen-editor v kaçta"* sorusu soruldu ve **v14** diye
cevaplandı, çünkü en yüksek numaralı belge o. Doğrusu v4'tü.

Kayıt bunun için var: cevap bir daha belgelerden çıkarılmıyor, buradan okunuyor.
