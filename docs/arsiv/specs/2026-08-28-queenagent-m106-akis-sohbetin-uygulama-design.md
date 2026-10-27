# Madde 106 — Akan cevap kendi sohbetinin ekranında kalır · Tur 2 (uygulama) tasarımı

**Test turu:** [testler tasarımı](2026-08-28-queenagent-m106-akis-sohbetin-testler-design.md) —
üç kırmızı `4eaa527`'de. Üç yüzün üçü de `useChat.js`'te kapanır; başka dosya değişmez.

## Dört parça

1. **Akış hedefi ekrana çıkar.** `streamingInto` ref'inin yanına `streamingChatId` state'i gelir —
   kapı bir render oynatmak zorunda, ref oynatamaz. İkisi birlikte yazılır: gönderimde ekranın
   sohbeti, ilk karede doğanın adı, `finally`'de null.
2. **Dönüşün kapısı.** Hook'un döndürdüğü akış demeti *(thinking, streamingText, creatingFile,
   createdFiles, streamingCalls, permission)* yalnız `streamingChatId === chatId` iken görünür —
   taslak burada kendi sohbetidir: ilk kare doğanı adlandırana kadar null null'a eşittir, adres
   taşınınca ikisi birlikte yeni ada geçer. Başka sohbette hepsi susar; dönünce yeniden konuşur.
3. **Biten tur yalnız kendi ekranını giydirir.** Tur sonu okuması *(Madde 89)* her durumda atılır —
   kayıt tek evinden okunmaya devam eder — ama `setChat` yalnız `landed === live.current` iken
   uygulanır *(live: her render güncellenen "ekran şu an hangi sohbette" ref'i)*. Akış içi `error`
   karesi ve okunamayan kayıt hatası aynı kapıdan geçer: turun hatası koştuğu sohbetindir.
   `finally` `streamingInto`'yu temizler — akış biterken state'ten, bittikten sonra diskten okunur;
   dönüş bu yüzden taze kaydı bulur.
4. **En yeni gönderim ekranın sahibi.** Gönderim başına bir `owner` jetonu: eski bir akışın
   kareleri artık ne çizer ne siler *(`finally`'si yenisinin akışını süpüremez)*; diske inmeye
   devam eder ve kaydı dönülünce okunur. Tek istisna `file` karesi — doğan dosya her ekran için
   gerçek, listeler tazelenir. Turun indiği yer gönderimin kendi yereli `target` olur:
   sahipliği kaybetmiş bir gönderim bile kendi sohbetini bilir.
5. **Doğum koruması daralır.** Yükleme etkisinin `chatId === streamingInto` atlaması yalnız elde
   duran kayıt buraya aitken kalır *(ayağa kaldırılmış taslak kaydı ya da bu sohbetin kendisi)* —
   başka sohbetten dönüşte elde öteki sohbetin kaydı vardır ve döküm diskten yüklenir.

## Bilerek böyle

- **Eşzamanlı ikinci gönderim engellenmez** — sunucu değişmiyor; ekran en son gönderimi çizer,
  eskisinin kaydı ziyaretinde diskten gelir.
- **Arkada biten sohbetin kenar çubuğu önizlemesi tazelenmez** — doğum çengeli yalnız doğum için;
  liste tazeliği bu maddenin sözü değil.
- **Sahipsiz akışın hatası ekrana yazılmaz** — kayıttaki cevapsız mesaj dönüşte kendini gösterir.

## Görülür hâli

Üç kırmızı yeşerir; 560 test yeşil, defter çifti dışında kırmızı yok. `dist` aynı commit'te.
