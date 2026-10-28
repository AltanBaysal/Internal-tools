# Madde 380 — Sohbetin sonuna gelen kart görünür · test turu

**Kaynak:** [yol haritasının 380'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); 349
tarayıcıda denenirken bulundu, 29 Eylül. Tasarımda karşılığı yok: `BEHAVIOUR.md` listenin kaymasını
anlatmıyor, `STICK_WITHIN`'in 220'si bugünkü kodun yorumunda "tasarımın sayısı" diye duruyor.

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalandı; kapsam ve okuyan kuralı kullanıcının.

## Ne kanıtlanacak

`ChatScreen`'de liste bugün iki anda aşağı iniyor:

- **Yeni mesajda** her zaman (`useEffect(toBottom, [chat?.messages.length])`).
- **Süren cevapta** yalnız okuyan dibe `STICK_WITHIN` (220) kadar yakınsa; bakılan an yazı eklendikten
  *sonra*.

Sohbetin altına çıkan kartlarda liste hiç kıpırdamıyor: hata kartı (`error`), ret kartı (`refused`),
izin kartı (`PermissionCard`, `permission`) ve oluşan dosya kartları (`createdFiles`). Kart eklenir,
yazma kutusunun altında yarım kalır.

Madde bittiğinde:

- **Okuyan dipteyken** bu dört karttan biri çıkınca liste yeni dibe iner, kart bütünüyle görünür.
- **Okuyan yukarıdayken** (dipten 220'den uzak) kart çıkınca liste yerinde kalır.

## Kararlar (kullanıcı yok, koşunun onayıyla verildi)

- **"Dipte" kart gelmeden önceki yere göre ölçülür.** İzin kartı modelin argümanlarını ham basar;
  `write_file`'da bu dosyanın bütün içeriği, ve kart 220'den kolayca uzun olur. Yazı eklendikten sonra
  ölçülürse dipteki okuyan, uzun kartın kendisi yüzünden "yukarıda" sayılır ve liste inmez. Bu yüzden
  izin kartı testinde içerik 600 büyür: dipteki okuyan yine dibe iner.
- **Okuyanın yeri, okuyanın kaydırmasıyla öğrenilir.** Testlerin yardımcısı (`scrollable`) listeyi
  bir yere koyduktan sonra bir `scroll` olayı atar — gerçek bir okuyanın kaydırması da böyle görünür.
  Bugünkü iki kaydırma testi bu yardımcıyı kullanıyor; olay bugünkü kodda hiçbir şeyi değiştirmez, o
  iki test yeşil kalır.
- **jsdom'da yerleşim yok:** `scrollHeight` ve `clientHeight` bugünkü testler gibi elle verilir; kartın
  gelişi `scrollHeight`'ın büyümesiyle anlatılır (`grow`).
- **Süren cevabın kuralı bu parçada test edilmez.** Uygulama kartlarla aynı kuralı kullanırsa cevap da
  ondan yararlanır; ama madde kartları istiyor, bugünkü iki cevap testi olduğu gibi kalır.

## Testler ne tutar

Hepsi `ChatScreen.test.jsx`'te, bugünkü kaydırma testlerinin yanında. Başlangıç: 1000 yüksek içerik,
300 yüksek pencere.

| # | Ne | Bugün |
|---|---|---|
| 1 | Dipteki (700) okuyan; cevap gelmedi, hata kartı çıkıyor, içerik 1100 → liste 1100'de | kırmızı |
| 2 | Dipteki okuyan; mesaj reddedildi, ret kartı çıkıyor, içerik 1100 → liste 1100'de | kırmızı |
| 3 | Dipteki okuyan; izin kartı çıkıyor, içerik 1600 (kart 220'den uzun) → liste 1600'de | kırmızı |
| 4 | Dipteki okuyan; cevap bir dosya oluşturdu, dosya kartı çıkıyor, içerik 1100 → liste 1100'de | kırmızı |
| 5 | Yukarıdaki (0) okuyan; dört kart birden çıkıyor → liste 0'da kalıyor | yeşil, bekçi |

5 bugün yeşildir: bugün hiçbir kart listeyi oynatmıyor. Uygulama yanlışlıkla her kartta dibe inerse
kırmızıya döner.

## Tutmaz

- Kartın ekranda tam göründüğü piksel ölçüsü jsdom'da görülmez; tarayıcıda görülür.
- Pencere yeniden boyutlanınca okuyanın yeri: madde bunu sormuyor.

## Bu turda yazılmayanlar

- `ChatScreen.jsx` değişmez; uygulama turunda.
- `dist` derlenmez: birleştirirken conductor derler.

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend` kırmızı: 1–4 düşer; 5 ve bugünkü
kaydırma testleri yeşil. Öteki üç süit bugünkü hâlinde. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m380-kart-gorunur-testler-plan.md).
