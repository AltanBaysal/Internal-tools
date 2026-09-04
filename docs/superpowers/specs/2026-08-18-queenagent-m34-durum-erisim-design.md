# Madde 34 — Durum ekranları ve erişilebilirlik · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 34](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 64, 65, 69 · [tasarım v2 farkları](../research/2026-08-14-mira-tasarim-farklari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 1 · İlk yükleme tek iskelet (fark 65)

Bugün bekleyen her liste kendi iskeletini çiziyor, ekranın geri kalanı gerçek hâliyle duruyor.
Tasarım tersini istiyor: **ana bölgenin tamamı tek bir iskelete bırakılır**, kenar çubuğu dolu
görünür ki gezinme kilitlenmesin.

Bloklar: **280×38** bir çubuk, **104px** bir blok, **180×16** bir çubuk. Tasarımın dört kartlık
ızgarası Madde 3'te silindi (ızgara yok), o yüzden üç blok kalıyor.

**Ne zaman çıkar:** proje listesinin **ilk** cevabı gelene kadar. O an ekranın hangisi olacağı
bilinmiyor; bugün orada iki ayrı yanlış var —

1. Çatal (`/`) hiçbir şey çizmiyor: boş bir ana bölge, "yükleniyor" demeden.
2. Doğrudan `/p/<id>` ile açılan bir adres, liste gelmeden **"That project does not exist."**
   diyor. Ekran, henüz sormadığı bir soruya "yok" cevabı veriyor — Madde 32'de listeler için
   kapatılan yanlışın aynısı, bu sefer ekran seviyesinde.

İkisi de tek kuralla kapanıyor: **ilk yükleme sürerken ana bölge iskelettir**, hiçbir ekran çizilmez.

**Yanıp sönme 1.4s ve kademeli.** Bugünkü blok 1.6s'te sönüp yanıyor; sayı tasarımdan gelmiyor.
Uygulamada tek bir yanıp sönme var ve o da tasarımın verdiği süreye çekiliyor. Kademeli gecikme
yalnız bu ekranın bloklarında: tasarım onu bu ekran için söylüyor, listelerin iskeletine
genelleştirmek uydurma olurdu.

## 2 · Çevrimdışı şeridi kızılımsı olur (fark 64)

| Ne | Bugün | Olacak |
|---|---|---|
| zemin | `#fbf6ec` | `#F5E9E3` |
| alt çizgi | `#eadfc8` | `#E7D3C8` |
| yazı | `#8a6a37` | `#8A5237` |
| metin | "You're offline. Messages are saved; QueenAgent will answer when the connection is back." | "You're offline — messages are saved and will send when you reconnect." |

Cümlenin solunda **7px'lik dolu bir nokta** durur.

**Noktanın rengi şeridin kendi mürekkebidir (`#8A5237`), vurgu rengi değil.** Fark 64 "vurgu rengi
bir nokta" diyor, ama aynı belgenin fark 74'ü ve `CODE-STANDARD.md` tek bir kural yazıyor: **vurgu
rengi yalnız birincil eylemi işaretler.** Çevrimdışı olmak bir eylem değil bir durum. İki cümle
çelişiyor; yazılı kural kazanıyor ve seçim burada kayda geçiyor — Madde 35 gözle bakar.

Metin de düzeliyor çünkü bugünkü cümle yanlış bir şey söylemiyor ama uzun; tasarımın cümlesi kısa ve
aynı iki şeyi söylüyor: mesaj kayıtlı, bağlantı gelince gider.

## 3 · Satırlar gerçek düğme olur (fark 69)

Bugün proje ekranındaki **sohbet satırı** ve **dosya satırı** tıklanabilir `div`. Sekmeyle sıraya
girmezler, Enter/Boşluk açmaz, odak halkası almazlar. Klavyeyle bu uygulamada bir dosya açmanın yolu
yok.

Düzeltme, kenar çubuğunun Madde 6'da kurduğu deseni ödünç alır: **satır bir kutudur, içinde iki
düğme durur** — açan düğme ve `×`. Düğme içine düğme koymak geçersiz HTML olurdu, bu yüzden `×` bir
kardeş olarak durur ve kutunun kendisi tıklanabilir olmaktan çıkar.

- Dolgu satırdan **açan düğmeye** taşınır: tıklanabilir alan küçülmesin.
- Hover zemini kutuda kalır: `×`'in üstündeyken de satır aydınlanır, bugünkü davranış korunur.
- `×` zaten `aria-label` taşıyor; üstüne **`title`** eklenir — fark 69'un ikinci yarısı, fareyle
  bekleyene de okunan bir ad.

Odak halkası uygulamanın tek kuralından geliyor (`app.css`), satır kendi halkasını yazmaz.

## 4 · Katman denetimi

**Ön uç:** `Skeleton.jsx` (yeni `screen` biçimi), `App.jsx` (ilk yüklemede ekran yerine iskelet),
`OfflineStrip.jsx`, `FileRow.jsx`, `ProjectScreen.jsx` (sohbet satırı), `workspace.css`.

**Arka uç:** dokunulmuyor.

## 5 · Kabul ölçütü

1. İlk yükleme sürerken ana bölge tek iskelet; hiçbir ekran çizilmez ve kenar çubuğu çalışır.
2. İskelet üç blok: 280×38, 104, 180×16; yanıp sönme 1.4s; blokların gecikmesi kademeli.
3. Liste geldiğinde iskelet gider ve doğru ekran çizilir.
4. Yükleme sürerken **"That project does not exist." çıkmaz**; liste geldikten sonra, gerçekten yoksa
   çıkar.
5. Şerit yeni üç rengi ve yeni cümleyi taşır, solunda 7px nokta durur.
6. Nokta vurgu rengi **değildir**.
7. Sohbet ve dosya satırı gerçek `button`; sekmeyle sıraya girer, Enter açar.
8. `×` satırın içinde değil kardeşidir ve `title` taşır; ona basmak satırı açmaz.
9. Satır hover'ı `×`'in üstündeyken de durur.

## 6 · Risk

Odak halkasının gerçekten çizildiği ve sekme sırasının okunur olduğu jsdom'da kısmen görülür
(`toHaveFocus`), tam olarak Madde 35'te. Şeridin rengi ve noktanın seçimi göz işi.
