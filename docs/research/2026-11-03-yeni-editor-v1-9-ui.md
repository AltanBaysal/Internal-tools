# Yeni editör — 9. UI

UI'ın v1'de ne yaptığı. Ekranlar `queen-design` reposunda çizilmez; bu repoda, yapımın içinde
tasarlanır (kullanıcı, 6 Kasım — "queen-design reposunda çizmesin, kendimiz yapalım"). Tasarlayan,
kullanıcının deneyimine odaklanan, UI'a özel bir tasarımcı subagent'tır (kullanıcı, 6 Kasım —
"tasarımcı bir subagent tasarlayabiliriz, koda odaklanmayan, deneyime odaklanan, UI'a özel").
Ekranların kodunu o yazar, gerçek UI kodunda ve OpenAPI türleriyle yazılı örnek veriyle; istek,
yoklama ve hata yakalama yazmaz. Tasarımına bir tasarım reviewer'ı, koduna her kod gibi reviewer
bakar. Ekranları core'a bağlamak ayrı maddelerdir, coder'ındır; görünüş aynı kalır (kullanıcı, 6 Kasım). UI en sonda, core ve MCP
adaptörü bittikten sonra yapılır. Anthropic'in `frontend-design` skill'ini kullanır;
tanımına UI UX Pro Max'in (MIT) işe yarayan UX kuralları küçük bir kontrol listesi olarak eklenir
(ör. silmeden önce onay, uzun beklemede iskelet ekran, boş ve hata durumları). Eklentinin kendisi
kurulmaz: ağa çıkan ve API anahtarı okuyan yan skill'ler getiriyor. Taste Skill alınmadı, yalnız
pazarlama sitesi kuruyor (kullanıcı, 6 Kasım). Tanımı yapım planında yazılır (13. adım).

## Ne yapar

UI yalnız kritik olanları yapar, basit ve yalın kalır. Dili İngilizcedir, queen-agent'ınki gibi (kullanıcı, 6 Kasım).

- **Görmek:** kullanıcı agent'ın ne yaptığını, şu an ne yaptığını ve şu an ne olduğunu görüp
  anlayabilir. Neyin nasıl gösterileceği tasarımda kararlaştırılır. Edit'ler export almadan
  izlenebilir.
- Ekran kendiliğinden güncellenir; başka bir Colab'daki değişiklik birkaç saniye geriden gelir
  (4. adım).
- **Silmek:** kare (`DELETE /projects/{p}/frames/{id}`) ve video
  (`DELETE /projects/{p}/frames/{id}/video`).
- **Projeyi silmek** yalnız UI'dandır, bir onayla (`DELETE /projects/{id}`); agent proje silmez
  (kullanıcı, 5 Kasım — "agent'lar proje silemesin"; "Yalnız UI'dan, bir onayla").
- **Kuyruğu durdurmak ve sürdürmek:** UI'da durdurma ve sürdürme butonları (ekranda İngilizce: Pause, Resume); agent'ın kullandığı aynı
  `POST /projects/{p}/queue/pause` ve `…/queue/resume`'u çağırır (kullanıcı, 6 Kasım). Kuyruk
  kendiliğinden durduğunda nedeni görünür; kullanıcı sorunu düzeltip agent'a yazmadan sürdürür.
- **v1'de yok:** üretmek, prompt değiştirmek, edit değiştirmek.
- **Neyin nasıl gösterildiği tasarımcı subagent'ın kararıdır** (ör. telefonda kullanım, modellerin
  durumu, history'den agent'ın ne yaptığı, onaylar); kullanıcıya sorulmaz (kullanıcı, 6 Kasım).
  UI'ın yapabildikleri yukarıdaki listedir; koşunun ortasında yeni bir yetenek eklenmez, gerekirse
  `queen-studio/BACKLOG.md`'ye yazılır.

## Birden çok Colab

Her core kendi UI'ını sunar, queen-editor'daki gibi. Bütün projeler görünür. Projenin kuyruğu ve
onu bu Colab'ın mı başka bir Colab'ın mı çalıştırdığı görünür; hangi Colab olduğu söylenmez.

## Bildirim

- Kuyruk bittiğinde ya da durduğunda UI tarayıcı bildirimi gösterir (queen-editor madde 509, 518);
  `GET /projects/{p}/queue/wait` ile bekler.
- Şimdilik yalnız UI. İleride aynı bilgi agent'a da gönderilebilir (ör. bir hook ile); bu, kullanılan
  agent'a bağlıdır.
