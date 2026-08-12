# Görev 5 — Kurulum ekranı doğruyu söylesin

**Roadmap:** [v7](../plans/2026-08-13-queen-editor-v7-roadmap.md) · Blok 2

## Sorun

Kullanıcının bulduğu iki şikâyet — "Kur'a basınca anında tepki yok" ve "ilerleme çubuğu gerçekle
uyuşmuyor" — aynı kökten çıkıyor: **kurulum satırı, koşmayan bir koşuyu koşuyor gibi gösteriyor.**

`list_producers`, çalıştırıcının son durumunu türü tuttuğu sürece `installing` diye rapor ediyor —
durumun `running` mi, `done` mu, `error` mü olduğuna bakmadan. Sonuç:

- **Kurulum bitince kart kaybolmuyor.** Satır hâlâ "kuruluyor… bitince bu kart kaybolur" diyor,
  oysa iş bitmiş. Panel de `installing` gördükçe poll'a devam ettiği için bu sonsuza kadar sürüyor.
- **Kurulum patlayınca da aynı şey oluyor**, üstelik hatanın kendisi hiç görünmüyor: çalıştırıcı
  hata metnini tutuyor ama satır onu taşımıyor. Kullanıcı ekranda "kuruluyor…" görmeye devam
  ediyor.
- **İlerleme çubuğu bu durumda boş `done`/`total` ile çiziliyor** — yani "bilinmiyor" genişliğinde,
  hiç ilerlemeyen bir çubuk. Kullanıcının gördüğü tam olarak bu.

Anında geri bildirim eksikliği ise ayrı ve küçük: Kur'a basmak önce bir POST, sonra bir GET
istiyor; tünelin arkasında ikisi arasında ekranda hiçbir şey değişmiyor.

## Kararlar

1. **`installing` yalnız gerçekten koşan bir kurulum için raporlanır.** Kararın yeri sunucu: satırın
   ne dediği ekranın yorumuna bırakılamaz.
2. **Biten koşu satırı boşaltır.** Kurulum başarılıysa dosyalar yerinde olduğu için satır zaten
   "kurulu" der; ayrıca bir şey söylemesine gerek yok.
3. **Patlayan koşu satırda görünür.** Satır, son kurulumun hata metnini taşır ve panel onu
   çalıştırıcının kendi cümlesiyle gösterir — üstüne bir yorum eklemeden. Kur düğmesi de orada
   kalır: hata gördükten sonra tekrar denemek kullanıcının hakkı.
4. **İlerleme çubuğu kalkar.** Sayı yalan söylemiyordu, temsil ediyordu: bir grup dosya inerken
   `done`/`total` her dosyada sıfırlanıyor, çubuk geri sıçrıyor; `total` bilinmeyince de dolu ama
   soluk bir çubuk çiziliyor. Yerine **ne indiği** yazılır — çalıştırıcı dosyanın adını zaten
   raporluyor. Bir dosya adı, uydurulmuş bir yüzdeden daha fazla bilgi taşır.
5. **`done`/`total` satırdan tamamen çıkar.** Kimse çizmiyorsa taşımak, ilk okuyana çizilebilirmiş
   gibi görünen bir alan bırakır.
6. **Anında tepki ön yüzde verilir.** Kur'a basıldığı anda satır "kuruluyor…" der ve sunucunun
   cevabını beklemez; ilk okuma gelince yerini gerçeğe bırakır. Bu bir kural değil, çizim
   kararı — kuralı hâlâ sunucu söylüyor ([FOUNDATION madde 4](../../../queen-editor/FOUNDATION.md)).
   İstek reddedilirse (başka bir kurulum koşuyor) iyimser durum anında düşer.

## Testler

Sunucu:

- Koşan bir kurulum satırında `installing` var ve içinde indirilen dosyanın adı yazıyor.
- Biten bir kurulumdan sonra hiçbir satırda `installing` kalmaz.
- Patlayan bir kurulumdan sonra satır `installing` taşımaz, çalıştırıcının hata metnini taşır.
- Satırın `installing`'i `done`/`total` taşımaz.

Ön yüz:

- Kur'a basınca satır, sunucudan hiçbir cevap gelmeden "kuruluyor…" der.
- İstek reddedilince satır Kur'a geri döner.
- Kurulum kartlarının hiçbirinde ilerleme çubuğu yoktur.
- Koşan kurulum, inen dosyanın adını gösterir.
- Hatalı kurulum satırı, sunucunun cümlesini ve tekrar denemek için Kur'u gösterir.

## Öz eleştiri

- *Yüzdeyi tamamen atmak kayıp değil mi? 6 GiB inerken insan bir şey görmek ister.* — İstediği şey
  "ne kadar kaldı", ve bugünkü çubuk onu söylemiyordu: her dosyada sıfırlanan, çoğu zaman toplamı
  bilinmeyen bir çubuk, bilgi değil hareket. Dürüst bir yüzde için grubun toplam boyutunu önceden
  bilmek gerekir; onu bilmiyoruz. Bilirsek geri gelir.
- *İyimser durum yalan söylemez mi?* — Söyleyebilir, bir isteğin ömrü kadar. Karşılığı, kullanıcının
  Kur'a bir daha basması — ki bugün olan tam olarak bu. Reddedilen istekte iyimserlik anında
  düşüyor, ve sunucunun ilk cevabı her hâlükârda üstüne yazıyor.
- *Hata metnini satırda göstermek paneli kalabalıklaştırmaz mı?* — Kalabalıklaştırır. Alternatifi,
  kullanıcının hiç görmediği bir hata; bu koşuda bulunan en pahalı şey de zaten oydu.
