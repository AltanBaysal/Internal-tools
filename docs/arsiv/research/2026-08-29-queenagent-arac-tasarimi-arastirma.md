# Yazdıktan sonra okuma: sorun, kimler yaşamış, nasıl çözmüşler

**Tarih:** 29 Ağustos 2026 · **Sebep:** yedinci denemede prompt+ turu 16 adım, 335k `sent`; her
`edit_file`'dan sonra bir `read_file`, ve sonunda aynı dosya üst üste üç kez.
**Neden yazıldı:** kullanıcının sözü — *"bunları yapmadan önce araştır, eminim başka insanlar da
benzer problemlerle karşılaşmıştır"*. Blok 11'in üç maddesi buradan çıkan sonuca göre yazıldı.

## 1 · Sorun bize özgü değil, ve ölçülmüş

Claude Code, Cursor ve Codex oturumları üzerinde yapılan bir ölçümde **21 milyon token'ın 8.8
milyonu (%42) kaçınılabilir işlemlere** gitmiş; baskın kalem, ajanların bağlamı korumak yerine
aynı dosyaları tekrar tekrar okuması
*([gotcontext.ai](https://gotcontext.ai/news/researcher-finds-42-of-coding-agent-tokens-are-wasted-on-repeated-file-reads))*.
Claude Code'un kendi deposunda aynı şikâyet bir hata kaydı olarak duruyor: tekrarlı okuma/yazma
denemeleri 100k+ token yakıyor
*([anthropics/claude-code#46968](https://github.com/anthropics/claude-code/issues/46968))*.

Yani QueenAgent'ın 335k'sı bir yapılandırma hatası değil, bu araç ailesinin bilinen davranışı.

## 2 · Kök neden hep aynı: string eşleşmeli düzenleme

Üç bağımsız kaynak aynı yere işaret ediyor:

- Model `old_string`'i **kelimesi kelimesine geri yazmak** zorunda; bu, dosyada zaten duran metnin
  en pahalı token sınıfında tekrarı — 15 satırlık tipik bir düzenlemede ~200 boşa çıktı token'ı
  *([WormBytes](https://www.wormbytes.ca/2026/03/04/trueline-mcp-announcement/))*.
- Eşleşme başarısız olunca — metin birden çok yerde geçiyorsa, ya da dosya okunduktan sonra
  değiştiyse — ajan **tam dosyayı yeniden okuyup** senkronizasyona dönüyor, ve içeriğin bedeli
  ikinci kez ödeniyor *(aynı kaynak)*.
- Aider'ın SEARCH/REPLACE bloğu da aynı yerden kırılıyor: benzer blokların olduğu büyük
  dosyalarda hizalama kayıyor ve yakınsamayan yeniden deneme döngüleri doğuyor
  *([Aider-AI/aider#3651](https://github.com/Aider-AI/aider/issues/3651),
  [fabianhertwig.com](https://fabianhertwig.com/blog/coding-assistants-file-edits/))*.

**Bizim durumumuza birebir oturuyor.** `edit_file`'ın *"old metin diskte tam olarak bir kez
geçmeli"* şartı + birbirine çok benzeyen kareler = modelin her batch'ten önce dosyayı görme
ihtiyacı. Madde 125 tanımdaki *okuma emrini* kaldırdı ama şartı yerinde bıraktı, ve model şartı
dinledi. Yasağı değil, şartı değiştirmek gerekiyor.

## 3 · İki çözüm ailesi

**a) Çapaya hash/satır kimliği takmak.** trueline-mcp her satırı kriptografik bir özetle
etiketliyor; model özeti geri veriyor, dosya değiştiyse düzenleme diske dokunmadan reddediliyor.
Kazanç: tam dosya yeniden okuması yerine **yalnız değişen aralığın** okunması *(WormBytes)*.

**b) String düzenlemeyi tamamen bırakıp yapılandırılmış eylem uzayına geçmek.** Amazon Science'ın
CODESTRUCT'ı tam olarak bunu savunuyor: ajan ham metin düzenlemesi üretmek yerine, kod değişimi
için **ayrık ve iyi tanımlı işlemler** çağırıyor; amaç belirsizliği kaldırmak ve güvenilirliği
artırmak *([arXiv 2604.05407](https://arxiv.org/pdf/2604.05407))*.

QueenAgent için (b) daha uygun, çünkü hedef dosya zaten yapılandırılmış: kareler bir JSON
listesi, ve eklenen şey serbest metin değil, şeması `schema.py`'de yazılı bir nesne. `add_frames`
bu ailenin bizdeki karşılığı — ve `build_prompts` ile `build_character_prompts` aynı yolu zaten
yürüyor *(FOUNDATION 5)*.

**Ekleme işleminin bilinen tuzağı:** ekleme idempotent değildir; aynı çağrı iki kez koşarsa
kareler iki kez girer *([agentpatterns.ai](https://www.agentpatterns.ai/agent-design/idempotent-agent-operations/))*.
İlacı basit: aracın cevabı **kaç kare eklendiğini ve dosyanın artık kaç kare tuttuğunu** söyler.
Model durumu cevaptan görür, ne tekrar ekler ne de kontrol için okur.

## 4 · Bayat sonuçları temizlemek: yapılabilir, ama bedava değil

Anthropic'in `clear_tool_uses_20250919` stratejisi tam olarak Madde 129'un yapmak istediği şey ve
tasarımın iki ayrıntısını doğruluyor: temizlenen sonuç **silinmez, yerine bir yer tutucu konur**
(model içeriğin düzenlendiğini bilir), ve temizlik **kronolojik** ilerler
*([Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/context-editing))*.

Ama aynı doküman maliyeti de yazıyor, ve bu bizim için belirleyici:

> Tool result clearing **önbelleklenmiş prefix'i geçersiz kılar**; her temizlemede cache write
> maliyeti doğar. `clear_at_least` parametresi tam bu yüzden var: temizliğin, geçersiz kıldığı
> önbelleğe **değmesi** için en az ne kadar token düşürüleceğini söyler.

Anthropic bunu **sunucu tarafında, cache lookup'tan sonra** uyguluyor — yani istemcinin geçmişi
bozulmuyor. Biz xAI'a istemci tarafından istek kuruyoruz; ortadaki bir mesajı kısaltmak, o
noktadan sonraki her şeyi Madde 124'ün yeni taktığı önbellek anahtarının dışına düşürür. Kazanç
ile kayıp aynı büyüklük mertebesinde olabilir, ve hangisinin ağır bastığı **ölçülmeden
bilinemez** *(FOUNDATION 3)*.

Bir de körlük eleştirisi: eşik bazlı temizleme, modelin şu anki akıl yürütmesinin hangi eski
sonuca dayandığını bilmez — *"asla ulaşılamaz olduğunu kanıtlamadığın şeyi serbest bırakma"*
*([conikeec](https://conikeec.substack.com/p/context-editing-looks-like-a-feature))*. Bizim
tasarımımız bu eleştiriden büyük ölçüde muaf: düşürülen şey **aynı dosyanın daha yenisi okunmuş
eski hâli**, yani gerçekten geçersiz bilgi. Kalan risk önbellek, ve o ölçülebilir.

## 5 · Sonuç: Blok 11 nasıl koşulur

1. **Madde 128 önce ve tek başına** — kaynakların ikisinin de işaret ettiği kök çözüm, ve
   önbellekle hiçbir alışverişi yok: daha az çağrı, daha az okuma, aynı prefix.
2. **Madde 130** yanında koşulur; metin işi, riski yok.
3. **Madde 129 ölçüme bağlanır.** 128'den sonra bir deneme koşulur: okumalar gerçekten
   bittiyse temizlenecek bayat sonuç da kalmamış demektir ve madde kendiliğinden düşer. Duruyorsa,
   Anthropic'in `clear_at_least` mantığıyla — yalnız kazanç önbellek kaybına değdiğinde —
   yazılır.
