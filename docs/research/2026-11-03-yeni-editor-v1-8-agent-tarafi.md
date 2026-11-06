# Yeni editör — 8. Agent tarafı

Agent'ın core'la nasıl konuştuğu: MCP adaptörü ve tool'u.

## MCP'de tek tool

MCP adaptörü her endpoint için ayrı bir tool sunmaz; tek bir tool sunar.

- Agent endpoint'leri `GET /api`'den öğrenir. Böylece kırk tool tanımı yerine tek bir tanım okur,
  birçok iş de tek çağrıda yapılır.
- Liste kod değildir, veri: her öğe bir fiil, bir adres ve gönderilecek şeydir. Adaptör kod
  çalıştırmaz; yalnız core'un adresine HTTP çağrısı yapar, bu yüzden bilgisayardaki dosyalara
  erişemez (Cloudflare'ın Code Mode'u incelendi; agent'ın yazdığı kodu çalıştırmak, dosyaların durduğu
  bir makinede risk olduğu için alınmadı). Çağrılar birbirinin sonucunu kullanmaz; buna ihtiyaç olan
  iş iki listeye bölünür.
- **Biçim:** agent `{"calls": [...]}` gönderir; her öğe `method`, `path`, istenirse `query` ve
  `body`'dir, endpoint'lerin kendi biçimiyle. Tool `{"results": [...], "stopped_at": …, "not_run":
  [...]}` döndürür: çalışan her çağrının cevabı sırasıyla, hata varsa listenin durduğu çağrı ve hiç
  çalışmayanlar.
- **Tek bekleme:** bir listede en çok bir `/wait` olur. İkincisini taşıyan liste hiçbir çağrı
  gönderilmeden `too_many_waits` ile döner; birden çok işi beklemek için `…/queue/wait` vardır
  (6. adım).
- **Anahtar:** adaptör her listeye kendisi bir anahtar verir; değiştiren her çağrının idempotency
  anahtarı bu anahtar ve çağrının sırasıdır. Yeni bir liste her zaman yeni anahtarlar alır.
- **Retry:** agent `{"retry": "last"}` gönderir; adaptör son listeyi aynı anahtarlarla yeniden
  gönderir. Yapılmış çağrılar ilk cevaplarını döndürür, yarıda kalan çağrı bittiyse ya da bitince
  onun cevabı döner, kalanlar yapılır; iş iki kez yapılmaz. "Yapıldı mı" sorusunu agent değil core
  cevaplar: cevap gelmediğinde istek core'da hâlâ sürüyor olabilir, agent'ın o an bakması yanıltır
  (core'un aynı anahtarla gelen, hâlâ süren isteği bekleyip onun cevabını vermesi 6. adımda yazılır).
  - Cevap alınamadıysa sonraki adım `retry` olmalıdır: arada başka liste gönderilirse "son liste"
    odur.
  - Adaptör yeniden başladıysa bellekteki liste gitmiştir; "yeniden denenecek liste yok" der, agent
    bakıp gönderir.
- **Core'un adresi:** tool her listenin başında `GET /health` ile adresin bizim core'umuz olduğunu
  doğrular; değilse hiçbir çağrı gönderilmez. Adres bulunamazsa ya da core cevap vermezse tool bunu
  hemen, adresiyle ve kullanıcıya sorulması gerektiğini söyleyerek döner. Adres
  sohbetin klasöründeki bir dosyadadır (10. adım).
- **Birden çok Colab:** her Colab için ayrı klasörde ayrı bir sohbet açılır; her sohbet kendi
  core'uyla konuşur.
- **Hata olunca:** liste sırayla çalışır ve ilk hatada durur. Cevap, hatadan önce yapılan çağrıların
  cevaplarını, hata veren çağrıyı ve hatanın kendi sözünü, ve hiç çalışmayan çağrıları söyler.
  Yapılanlar geri alınmaz. Agent hatayı düzeltip kalan çağrıları yeni bir liste olarak gönderir.
- **Proje silmek agent'ın değildir:** adaptör `DELETE /projects/{id}`'yi göndermez; o çağrı "proje
  silmek kullanıcının işidir, UI'dan silinir" hatasıyla döner (kullanıcı, 5 Kasım). Bu bir güvenlik
  sınırı değil, agent'ın yanlışlıkla silmesine karşı bir korumadır: adresi bilen herkes core'a
  doğrudan istek atabilir (10. adım).
- **Resimler:** cevabı resim olan çağrı (ör. karenin fotoğrafı, videonun bir saniyesi) agent'a MCP'nin
  resim parçası olarak gider, metin olarak değil; model resmi görür, ücreti piksele göredir (512
  px'lik resim ~200 token). Hiçbir resim JSON'un içinde dolaşmaz. `results`'ta resim çağrısının
  sonucu `{"status": 200, "image": k}`'dır; `k`, çağrıların sırasıyla sayılan MCP resim parçasının
  sırasıdır. Video agent'a gönderilmez; yalnız türü ve boyutu söylenir. Bir çağrının cevabı durumu ve
  gövdesidir, başlıkları değil.
- **Resim alamayan harness:** harness'ın resim alıp almadığı yapımda denenir (10. adım). Alamıyorsa
  adaptör resmi göndermez ve sonuçta bunu söyler; resmi hiçbir zaman metne çevirmez.
- **Sıkı test edilir** (12. adım): bir resim yanlışlıkla metin olarak bağlama girerse tek resim on
  binlerce token tutar ve agent'ın her işi yavaşlar ve pahalanır (kullanıcı, 5 Kasım — "burası
  özellikle sıkı test edilsin, çünkü core özellik bu ve burası yanlış olursa acayip performans düşüşü
  olur").
