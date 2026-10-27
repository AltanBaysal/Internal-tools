# Madde 380 — Sohbetin sonuna gelen kart görünür · uygulama turu

**Kaynak:** [yol haritasının 380'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-29-queenagent-m380-kart-gorunur-testler-design.md), kırmızı commit
`9936310b`.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne yeşile dönecek

`ChatScreen.test.jsx`'in Madde 380 bölümündeki dört kırmızı test: dipteki okuyan hata kartına, ret
kartına, 220'den uzun izin kartına ve dosya kartına iner. Beşinci test (yukarıdaki okuyan yerinde
kalır) ve bugünkü üç kaydırma testi yeşil kalır.

## Yol

Denenen üç yol:

1. **Bugünkü cevap kuralını kartlara da uygulamak** — içerik eklendikten sonra dibe uzaklığa bakmak.
   Uzun izin kartında düşer (test 3): dipteki okuyan kartın kendi boyu yüzünden "yukarıda" sayılır.
2. **Okuyanın yerini kaydırdığında not etmek** — seçilen yol. Liste bir `scroll` olayında okuyanın
   dibe `STICK_WITHIN` kadar yakın olup olmadığını bir ref'e yazar. İçeriğin büyümesi `scroll` olayı
   atmaz, bu yüzden ref kart gelmeden önceki yeri tutar.
3. **Render sırasında DOM'dan okumak** — render'ı saf olmaktan çıkarır; reddedildi.

## Değişen

Yalnız `queen-agent/frontend/src/features/workspace/ChatScreen.jsx`:

- `following` ref'i, başta `true`: sohbet açılınca liste dipten başlar (yeni mesaj etkisi).
- `.chat__scroll`'a `onScroll`: `following.current = scrollHeight - scrollTop - clientHeight <=
  STICK_WITHIN`.
- Cevabın etkisi yerine tek bir izleme etkisi: `following.current` doğruysa `toBottom()`. Bağımlılıkları
  sohbetin altına bir şey ekleyen her şey: `streamingText`, `createdFiles.length`, `permission`,
  `refused`, `error`. `createdFiles`'ın uzunluğu, dizinin kendisi değil: prop verilmeyince varsayılan
  `[]` her render'da yeni bir dizidir.
- Yeni mesaj etkisi (`useEffect(toBottom, [chat?.messages.length])`) olduğu gibi kalır: gönderilen
  mesaj her zaman görülür. Programla verilen `scrollTop` tarayıcıda bir `scroll` olayı atar, ve ref
  kendiliğinden "dipte"ye döner.

**Cevap da aynı kuralı kullanır.** Böylece "dipte" tek bir yerde karar verilir; cevabın bugünkü
davranışı küçük parçalarda aynı, büyük bir parçada (220'den uzun) artık dipteki okuyanı bırakmıyor.
Bugünkü iki cevap testi bunu değiştirmeden tutar.

## Tutmaz

- Pencere boyutu değişince `scroll` olayı gelmeyebilir; ref son kaydırmadaki yeri tutar. Madde bunu
  sormuyor.
- Yeni mesajın her zaman dibe inmesi değişmez.
- `workspace.css` değişmez. `dist` derlenmez: birleştirirken conductor derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, dördü de yeşil. Tarayıcıda: bir sohbetin dibindeyken cevap gelmeyince
kahverengi kart yazma kutusunun üstünde bütünüyle duruyor; yukarı kaydırılmışken liste yerinde kalıyor.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m380-kart-gorunur-uygulama-plan.md).
