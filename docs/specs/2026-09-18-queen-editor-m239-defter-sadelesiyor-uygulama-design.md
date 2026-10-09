# Madde 239 · Defter sadeleşiyor — uygulama turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-18-queen-editor-m239-defter-sadelesiyor-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Tasarım

On kod hücresinin her biri NotebookEdit ile yeniden yazılıyor. Kod satırları birebir aynı kalıyor;
yalnız yorumlar ve docstring'ler gidiyor. Kalanlar:

- `# === … ===` bölüm başlıkları,
- Colab'ın formu olan `#@markdown` ve `#@param` satırları,
- Türkçe markdown hücreleri, olduğu gibi.

Satır sonuna yazılmış yorumlar da gidiyor. Örneğin custom node listesindeki "ne sağlıyor" notları.

Defterin davranışı değişmiyor. Testler bunu defterin metninden okuyor: her dosyanın adı, her
grubun anahtarı, probe, disk ölçümü, tünelin biçimi. Tavan testi yeşile dönüyor.

**Markdown'daki geliştirici notları da gidiyor.** Yorumlar gittikten sonra defter 30.941 karakterdi,
tavanın üstünde. Kalan fazlalık markdown hücrelerinde, kullanıcıya değil defteri düzenleyene
yazılmış notlardı: *Model eklemek*, *LoRA eklemek*, *Diğer gruplara eklemek*, node kurulumunun ve
MMAudio ağırlıklarının gerekçeleri. Bunlar da yorum. Kurulum talimatları ve her hücrenin ne yaptığını
söyleyen cümleler kalıyor.

## Bu turda değişen

`queeneditor.ipynb`, ve bir test: `test_the_protocol_flag_says_what_it_is_standing_in_for`
siliniyor. O test `http2` bayrağının yanında bir açıklama yorumu şart koşuyordu; kullanıcının
kararıyla çelişiyor ve test turunda gözden kaçtı. Bayrağı `test_the_tunnel_is_opened_over_tcp_rather_than_quic`
tutmaya devam ediyor: bayrak silinirse o test kırılıyor ve mesajı sebebi söylüyor. Yani gerekçe
yorumdan testin mesajına taşınmış oluyor.
