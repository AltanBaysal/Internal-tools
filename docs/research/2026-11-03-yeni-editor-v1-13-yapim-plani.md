# Yeni editör — 13. Yapım planı

Yapımın nasıl yürüdüğü. Ne yapılacağı roadmap'te, nasıl yapılacağı her maddenin spec'indedir; onları
kodu yazan agent kodu okuyarak kendi yargısıyla yazar (CLAUDE.md).

## Kod

- Bu depoda yeni bir klasör: `queen-studio/`. Ad şimdilik budur; kendini kanıtlarsa `queen-editor`
  olur ve onun sonraki sürümü olarak yerine geçer (kullanıcı, 6 Kasım). Ad kodda tek yerde yazılır,
  sonra değiştirmek ucuz kalsın.
- queen-editor'dan kod alınmaz; queen-studio yerine geçene kadar o yerinde kalır.
- CLAUDE.md dört aracı sayacak; queen-studio'nun komutları ve suite'leri eklenir. Değişen bölümler:
  Designs (queen-studio'nun ekranları bu repoda tasarlanır), Subagents (tasarımcı ve tasarım
  reviewer'ı), Style (queen-studio'nun UI'ı İngilizce).
- Bir madde yalnız queen-studio'nun suite'lerini koşar; dört aracın bütün suite'leri `main`'e
  birleşmeden önce bir kez koşar. queen-studio öbür araçlarla kod paylaşmaz.

## Roadmap

- `docs/roadmaps/<tarih>-queen-studio-v1-roadmap.md`, CLAUDE.md'deki biçimde, bu tasarım
  belgelerinden yazılır. Belgelerdeki kararlar kullanıcıyla konuşularak verildi; onlardan çıkan
  maddeler `ALIGNED` doğar ve dayandığı adımı gösterir (kullanıcı, 6 Kasım). Belgelerde olmayan bir
  madde kullanıcıya sorulur.
- Maddeler tek tek yürür, worktree açılmaz: makine 16 GB, tek tarayıcı, tek deneme Colab'ı.
- **İlk madde, kurulum,** kullanıcıyla adım adım: ücretsiz katman ve Drive testleri için ayrı bir
  Google hesabı (şirket hesabı hiçbir testte kullanılmaz), Drive API izni (token depoda durmaz),
  hesabın Colab Secrets'ı, Google'ın Colab CLI'ı ve ilk T4 denemesi.
- Maddeler sırayla, tek tek yürür; dalga yoktur. İlk maddeden sonra koşu durmaz, yalnız geri
  alınamayan ya da geri alması çok zor ve uzun olan bir karar için durur (Doğrulama); kullanıcı sonuca
  son maddede bakar (kullanıcı, 6 Kasım).
- **Ekrandaki sürüm:** [v1-3](../roadmaps/2026-11-06-queen-studio-v1-roadmap.md#v1-3) yalnız "Queen
  Studio V1" yazan bir yer tutucu sayfa gösterir; sürüm kuralı böyle tutar. Tasarlanan ekranlar sonda
  onun yerine geçer.
- **UI en sonda yapılır,** core ve MCP adaptörü bittikten sonra, Pro denemesinden önce; ekranların
  gösterdiği her şey o zaman vardır (kullanıcı, 6 Kasım).
- **Son madde, Pro'da tek deneme,** her şey ücretsiz katmanda yeşil olduktan sonra, kullanıcıyla:
  gerçek video, Claude Code'un tünelden core'a bağlanması, export'a gözle bakmak; Kabul koşullarının
  hepsine de bu madde bakar. Pro bir sorun bulursa düzeltme önce ücretsiz katmanda denenir.
- **En son madde, DeepSeek harness'ı,** kullanıcıyla birlikte (10. adım).

## Doğrulama

Agent yaparken kullanıcıya dönüp durmaz; her maddenin "bitti" ölçüsü spec'indedir ve ana agent ona
kendisi bakar. Katmanlar: testler (12. adım), reviewer ve QA, agent senaryoları, Colab.

- **Agent senaryoları:** gerçek Claude Code, günlük kullanılan modelle, bizim MCP adaptörümüzle,
  taklit ComfyUI'li bir core'a karşı bir iş yapar (ör. proje, 4 fotoğraf, bir video, edit, export).
  İşin bitip bitmediği, çağrı ve token sayısı, resimlerin resim olarak gidip gitmediği kaydedilir; bir
  sayı kötüleşirse madde geri döner. API'ye, `GET /api`'ye, hatalara ya da adaptöre dokunan maddeden
  sonra koşar.
- **Nerede:** UI bu makinede Playwright'la; core ve MCP adaptörü Colab T4'te gerçek ComfyUI'yle,
  Colab CLI üzerinden (ücretsiz katmanda SSH ya da tünel yok, kuralları yasaklar); tünel bağlantısı ve
  gerçek video yalnız Pro'daki son denemede.
- **Kullanıcıya gidilir:** yalnız kurulumda, Pro denemesinde, DeepSeek harness'ında ve geri alınamayan
  ya da geri alması çok zor ve uzun olan bir kararda; koşu yalnız bunun için durur. Yolda çıkan öbür
  kararları ana agent kendi yargısıyla verir; tutmayan bir ölçümde tasarımı düzeltip adımına yazar.
  Her kararı gerekçesiyle roadmap'in kararlar belgesine yazar; kullanıcıyla sonda onun üstünden
  geçilir.
- **Tasarımdan sapmak serbesttir:** bazı şeyler ancak kod yazılırken görülür. Kodu yazan agent bir
  şeyi tasarımdan ya da kurallardan farklı yapmanın daha doğru olduğunu görürse ana agent'a söyler;
  ana agent artısını ve eksisini tartar, uygunsa değiştirir, değişen adımı düzeltir ve sapmayı
  kararlar belgesinin "Sapmalar" bölümüne yazar: nerede, neyden neye, neden (kullanıcı, 6 Kasım).

## Kabul koşulları

Roadmap ancak bunların hepsi tutunca biter. Ana agent sonda hepsine kendisi bakar; son madde de
onları dener. Her birinin yanında nasıl gösterildiği yazar.

1. **Agent işi tek başına bitirir:** Pro'da, gerçek modellerle, Claude Code tünelden bağlanıp proje →
   fotoğraflar → video → edit → export'u bitirir; kullanıcı yalnız Colab'ın adresini verir. Son
   maddedeki denemeyle.
2. **Resimler resim olarak gider:** hiçbir resim bağlama metin olarak girmez. Gerçek MCP oturumundaki
   resim testiyle; Claude Code'da elle de: küçük boyutlu bir fotoğraf bağlamı on binlerce değil birkaç
   yüz token büyütür.
3. **Hiçbir şey iki kez yapılmaz ya da kaybolmaz:** core iş ortasında yeniden başlasa, cevap kaybolup
   liste yeniden gönderilse ya da Colab kapansa da kuyruk kaldığı yerden sürer. 4. adımın Dayanıklılık
   tablosunun her satırı için hata enjekte eden bir testle; bir kez de Colab'da gerçek Drive'la.
4. **Kuyruk kendiliğinden durunca nedenini söyler:** işin hatası, ComfyUI, model inemedi, Drive'da yer
   yok, ürün yüklenemedi; her birinde iş kaybolmaz ve `resume` sürdürür. Her neden için bir testle.
5. **Gerçek Drive'da çalışır:** gerçek Drive'a karşı sözleşme testleri yeşil; 4. adımın ölçülmemiş
   varsayımları ve 10. adımın Colab ölçümleri ölçüldü, sonuçları depoda. Tutmayan varsa tasarım
   düzeltildi.
6. **Maliyet ve hız bütçede:** her işlemin Drive çağrısı sayısı 4. adımın tablosuyla tam eşit;
   boştayken (istek, iş ve yeni log yokken) Drive'a çağrı gitmez; agent senaryolarının token ve çağrı sayıları kayıtlı sınırların
   altında. Testlerle ve son agent senaryosuyla.
7. **İki Colab aynı projeyi sırayla kullanır:** biri ötekinin değişikliğini silmez, `resume` kuyruğu
   bir Colab'dan ötekine geçirir. Aynı depoda iki core'lu testlerle; bir kez de gerçek Drive'da.
8. **Kullanıcı UI'ı onaylar:** agent'ın ne yaptığı ve şu an ne yaptığı görünür; kare, video ve proje silmek
   onayla çalışır; kuyruk durdurulup sürdürülür; bildirim gelir. QA'nın Playwright denemesinden sonra
   kullanıcının bakışıyla.
9. **Kullanıcı export'u onaylar:** ad kuralına uyar, Drive'da `exports/` altında doğru klasördedir,
   oynar. Export testleriyle (bu makinede ve Colab'da); görünüşüne Pro'da gözle bakılır.
10. **Bütün suite'ler yeşil:** queen-studio'nunkiler, Colab testleri ve `main`'den önce bütün araçlarınkiler;
    bilinen kırmızı test yok, "şu testler hariç" de yok.
11. **Şirket hesabına hiçbir test dokunmadı:** suite'ler, sözleşme testleri, ölçümler ve Colab testleri
    yalnız deneme hesabıyla koştu; ücretli katman ve şirket hesabı yalnız son maddedeki Pro
    denemesinde, kullanıcıyla kullanılır. Testlerin ve Colab CLI'ın hesap ayarı yalnız deneme hesabını
    gösterir.

## Tasarımcı subagent

`.claude/agents/designer.md` ve `.claude/agents/design-reviewer.md`, roadmap'te yazılır. Bir ekranı
tasarlamak ve core'a bağlamak hep iki ayrı maddedir (kullanıcı, 6 Kasım):

- **Tasarım:** tasarımcı → tasarım reviewer'ı → reviewer → QA → ana agent → commit. Reviewer
  tasarımcının kodunu her kod maddesindeki gibi okur. Tasarımcı ekranları gerçek UI
  kodunda (React, TypeScript) örnek veriyle kurar; istek, yoklama ve hata yakalama yazmaz. Örnek veri
  core'un OpenAPI'sinden çıkan türlerle yazılır, core'da olmayan alanı gösteren ekran derlenmez.
  Ekranların davranışı önce düşen bir testle başlar. `frontend-design` skill'ini ve UI UX Pro Max'ten
  kısa bir kontrol listesini kullanır, yeni yetenek eklemez (9. adım). Tasarım reviewer'ı deneyime
  bakar; QA ekranları örnek veriyle Playwright'la dener.
- **Bağlantı:** her madde gibi coder → reviewer → QA → ana agent → commit. Coder örnek veriyi gerçek
  endpoint'lerle değiştirir, görünüş aynı kalır. Ekranın ne sıklıkla yokladığı ve kaç istek yaptığı
  burada; UI'ın tazelemesi Drive kotasının en büyük kalemi olduğu için (4. adım) reviewer bu maliyete
  bakar.

v1'in bütün ekranları tek tasarım maddesidir, tutarlı kalsınlar; ardından üç bağlantı maddesi gelir.
