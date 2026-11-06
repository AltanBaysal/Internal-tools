# Yeni editör — 12. Test stratejisi

Neyin hangi katmanda, neyle taklit edilerek test edildiği. Tek tek testleri coder her maddenin
spec'inde, kodu okuduktan sonra yazar; reviewer ve QA onlara bakar (CLAUDE.md). Bu belge yalnız
çerçeveyi ve mutlaka sıkı test edilecekleri söyler.

## Kurallar

- **Bütün depo TDD'dir.** Davranışı değiştiren her değişiklik kırmızı bir testle başlar, hangi
  parçada olursa olsun: core, depo adaptörleri, MCP adaptörü, UI, notebook ve başlatıcı kodu. Birim
  testle sınanamayan şeyde de önce bir test yazılır (aşağıda); elle bakış ve Colab denemesi testten
  sonra gelir, onun yerine değil.
- Davranışı değiştirmeyen değişiklik yeni test istemez: yorum, belge, ad değiştirme, kodu davranışı
  aynı kalacak biçimde düzenlemek. Var olan testler yeşil kalır, o kadar.
- Testler kodu sınar, belge okumaz (CLAUDE.md).
- Hiçbir test gerçek bir saniye beklemez; saat dışarıdan verilir.
- Yarışlar zaman penceresiyle değil, taklit servislerdeki kancalarla kurulur; sonuç her koşuda
  aynıdır. queen-editor'da yarışların çoğunu test değil QA bulmuştu (512, 513, 522, 523).
- Maliyet de test edilir: her işlemin kaç Drive çağrısı yaptığı (4. adımın tablosu). queen-agent'ta
  446'yı hiçbir review görmemişti.
- Bilinen kırmızı test olmaz.

## Katmanlar

| Katman | Neyi sınar | Nerede |
|---|---|---|
| Kurallar | Alan modelinin kuralları, sorgu ayrıştırıcısı; taklit gerekmez | Bu makine |
| Depo sözleşmesi | Depo portu; aynı testler bellek içi adaptörde ve gerçek Drive'da. Drive adaptörünün kendi testleri taklit Drive API'yle | Bu makine; gerçek Drive ayrı bir deneme hesabıyla (token depoda durmaz), bir kez de Colab'da |
| API | Endpoint'ler, hatalar, anahtar, kuyruk; aynı depoda iki core | Bu makine |
| MCP adaptörü | Gerçek bir MCP oturumunda tek tool, liste, `retry`, resimler | Bu makine |
| UI | Vitest; `tsc`, `eslint` | Bu makine |
| Başlatıcı | Notebook'un çağırdığı modüller, makine taklit | Bu makine |
| Uçtan uca | Yazılı Playwright suite'i, taklitlerle açılmış core; üstüne QA'nın Playwright denemesi | Bu makine |
| Colab | Gerçek ComfyUI'yle fotoğraf, model indirme, export testleri, gerçek Drive'a karşı depo sözleşmesi, 10. adımın ölçümleri | Colab'ın ücretsiz katmanı (T4), Google'ın Colab CLI'ıyla, gerektiği her an; ücretli katman testte kullanılmaz. MCP adaptörü makinenin içinde, core'a karşı çalışır. CLI'ın bu makinede çalışması yapımın ilk maddesinde denenir (13. adım) |

Dış her şey bir kapının arkasındadır ve testte taklidi bağlanır: depo, Drive API, ComfyUI, indirme,
ekran kartı, saat, Colab diski, ikinci core. Taklitler hata da verebilir: yazmadan önce ya da sonra
düşmek, yavaşlamak, reddetmek. Export testleri gerçek ffmpeg'le koşar: bu makinede ffmpeg 9.0.2 kurulu
(winget, Gyan.FFmpeg). Colab'daki ffmpeg'in sürümü ve işletim sistemi farklıdır, bu yüzden export
testleri Colab'da da koşar. Ekran kartı fark yaratmaz: v1'de export işlemcide kodlanır (7. adım).

## Mutlaka sıkı test edilenler

Core'un kullanımını etkileyen her şey sıkı test edilir. Gözle fark edilmeyen ama performansı
düşürenler özellikle: fazladan Drive çağrısı, agent'ın bağlamına giren gereksiz veri, boşuna
beklemeler, büyüdükçe yavaşlayan işlemler. Bunlar ekranda bir hata göstermez, yalnız her şeyi
yavaşlatır ve pahalandırır; bu yüzden ancak testle yakalanır. Coder ve reviewer her maddede bunlara
bakar. Bugün bilinenler:

- **Resimler agent'a MCP resmi olarak gider, hiçbir zaman metin olarak** (8. adım). Test gerçek MCP
  oturumundan geçer; herhangi bir metin parçasında resim baytları ya da base64 görünürse düşer. API'nin
  hiçbir JSON cevabında da base64 olmaz.
- **Aynı istek iki kez yapılmaz:** `retry: last`, core yeniden başladıktan sonra ve `creates.json` dahil.
- **İki Colab aynı projede:** yazmadan önce bakmak, `resume` ile kuyruğun devri, 30 sn'lik bırakma.
- **Kuyruğun kendiliğinden durması,** her nedeniyle: nedeni görünür, iş kaybolmaz, `resume` sürdürür.
- **Maliyet:** Drive çağrılarının sayısı tam eşitlikle; hiçbir istek başka projeye dokunmaz; proje
  büyüdükçe çağrı sayısı artmaz (projeyi ilk yüklemek dışında); boştayken, yeni log da yoksa, Drive'a
  çağrı gitmez.
- **Agent'ın bağlamı:** `GET /api`'nin dizini, listelerin varsayılan alanları ve hata cevapları kısa
  kalır; boyutları kayıtlı bir sınırla karşılaştırılır, sınırı aşan test düşer.
- **Boşuna bekleme:** ilerleyemeyen kuyrukta `/wait` hemen döner; hiçbir istek gereksiz yere Drive'ı ya
  da GPU'yu beklemez.
- **Dört alanlı hata ve hint kuralı:** her hata cevabında kendiliğinden bakılır.
- **Projeyi silmek:** her şey çöpe gider; agent'a kapalıdır.

## Birim testle sınanamayanlar

İstisna değildir; değişiklik yine kırmızı bir testle başlar.

| Ne | Önce yazılan test | Sonra nasıl bakılır |
|---|---|---|
| ComfyUI'nin ürettiğinin kalitesi | Taklit ComfyUI'ye giden graf doğru (prompt, seed, LoRA, yön, uzunluk) | Fotoğrafa T4'te bakılır; gerçek videoyu kullanıcı sonda Pro'da dener (video modelleri T4'e sığmaz) |
| Gerçek Colab süreleri | Kodun dayandığı sayılar, depodaki kayıtlı ölçüm dosyasıyla tutar | 10. adımın ölçümleri |
| Drive'ın belgelenmemiş davranışı | Sözleşme testi taklide karşı | Aynı test gerçek Drive'da |
| Harness'ın davranışı | Gerçek MCP oturumunda resim testi | Claude Code'da elle |
| Export'un ve UI'ın görünüşü | ffmpeg'e giden komut; UI'ın davranışı | Gözle; UI'a tasarım reviewer'ı ve kullanıcı bakar |

## Nasıl koşulur

Bu makine 16 GB'tır; bir anda tek suite koşar, queen-editor'ın ve queen-agent'ın suite'leriyle de yan
yana değil (CLAUDE.md). Suite'ler: Python (core, adaptör, başlatıcı), UI, uçtan uca ve gerçek Drive'a
karşı depo sözleşmesi. Klasör adları ve suite komutları v1-3'ün spec'indedir.
