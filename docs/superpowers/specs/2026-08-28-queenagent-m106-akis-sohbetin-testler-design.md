# Madde 106 — Akan cevap kendi sohbetinin ekranında kalır · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 106.
**Belirti** *(kullanıcı, 28 Ağustos)*: bir sohbet çalışırken başka sohbete geçince eski sohbetin
akışı görünüyor.

## Kök neden (koşuda bulundu — 104'le aynı mahalle)

`useChat` tek örnek, ve akışın çizdiği her şey *(streamingText, thinking, çağrı kartları,
izin kartı)* **sohbete anahtarsız** state. Üç yüzü var:

1. **Akış öteki ekrana taşınıyor.** B'ye geçince B'nin kaydı yüklenir ama akan metin state'te
   durur — B'nin dökümünün üstünde A'nın akışı çizilir.
2. **Arkada biten tur ekranı boyar.** Tur sonu okuması *(Madde 89)* `landed`'ın kaydını koşulsuz
   `setChat` eder — kullanıcı B'de dururken ekran A'nın bitmiş dökümüne döner.
3. **Akan sohbete dönüş yanlış dökümü bulur.** Yükleme etkisi `chatId === streamingInto` görünce
   atlar *(Madde 88'in doğum koruması)*; ama B'ye gidip dönünce elde duran B'nin kaydıdır — A'nın
   ekranında B'nin dökümü, üstünde A'nın akışı.

## Testler — `App.test.jsx`, üç yeni *(hepsi `gatedSse` ile, iddia akış sürerken)*

1. `an answer streaming in one chat does not show in another`: c1'de akış tutulmuşken c2'ye
   geçiliyor — c2'de akan satır ve düşünme göstergesi yok *(bugün var — kırmızı)*; c1'e dönünce
   akan satır yerinde; kapı bırakılınca tur c1'de kapanıyor.
2. `a turn that ends in a left chat does not repaint the one the user is standing in`: c1'in turu
   kullanıcı c2'deyken bitiyor — tur sonu okuması yapılır ama c2'nin ekranı A'nın bitmiş cevabını
   giymez *(bugün giyiyor — kırmızı)*; c1'e dönünce bitmiş cevap orada.
3. `coming back to a streaming chat finds its transcript and its stream`: c1 akarken c2'ye gidilip
   dönülüyor — c1'in kendi dökümü diskteki hâliyle ekranda *(bugün B'nin dökümü duruyor —
   kırmızı)* ve akan satır üstünde.

*(2. testin sinyali okumanın kendisi: tur sonu okuması iki dünyada da atılır — düzeltme okuduğunu
uygulamayı ekranın sohbetine bağlar, okumayı kesmez. Kayıt tek evinden okunmaya devam eder.)*

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `App.test.jsx` | 3 yeni |

Defter çifti bu maddenin değil.

## Bilerek yapılmayanlar

- **Kod yazılmaz.**
- **İzin kartının taşınması ayrıca test edilmez** — kart akış demetinin parçası, aynı tek kapıdan
  geçecek; demeti mıhlayan akan-satır iddiası yeter.
- **Eşzamanlı iki gönderim test edilmez** — sunucu tarafı değişmiyor; ekran en son gönderimi
  çizer, bu maddenin sözü bu kadar.
- **`dist` derlenmez.**
