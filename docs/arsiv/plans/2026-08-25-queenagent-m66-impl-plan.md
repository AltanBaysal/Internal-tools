# Madde 66 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-25-queenagent-m66-tool-satiri-uygulama-design.md](../specs/2026-08-25-queenagent-m66-tool-satiri-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sıra

Zincirin başından sonuna; her adım bir öncekinin ürettiğini tüketiyor.

**1. `tools.py` — sonuç hedefini söyler.**
`ToolResult` üçüncü bir alan kazanır: `target`. Her dal kendi hedefini verir — okuma ve düzenleme
temizlenmiş adı, yaratma **yazılan** adı, kurma kaynak dosyasını, listeleme boşu. Hatalı dallar da
hedefi verir: olmayan bir dosyayı istemek de olmuş bir adımdır.

**2. `chat.py` — mesaj `calls` taşır.**
`files`'ın yanına `calls: tuple = ()`. Yorumu neden orada olduğunu söyler, ne olduğunu değil.

**3. `append_message` — `calls` alır.**
`files` gibi, varsayılanı boş. Boş mesaj kuralı değişmez: bir çağrı yapmış olmak konuşmuş olmak
değildir, yani `calls` tek başına mesajı ayakta tutmaz.

**4. `stream_answer` — yayar ve biriktirir.**
Araç koştuktan sonra `ToolCall(tool, result.target)` yayılır ve bir listeye eklenir; tur bitince
liste cevap mesajına verilir. Dosyalardaki tekrar ayıklaması buraya taşınmaz.

**5. `file_chat_store` — diske yazar ve okur.**
`calls` boşken yazılmaz; `target` boşken yazılmaz. Okurken yoksa boş. Deseni `files` ve `skill`
zaten kurmuş durumda.

**6. `routes.py` — dışarı çıkarır.**
`_sse` içinde `ToolCall` için `call` olayı — `FileWritten` dalının komşusu, `Chat`'e düşen `else`
dalından **önce**. `_chat_json` mesaja `calls` ekler.

**7. `useChat.js` — akıştan toplar, sonunda bırakır.**
`call` çerçevesi `streamingCalls`'a eklenir; `finally` içinde `createdFiles` ile birlikte boşaltılır.

**8. `App.jsx` — geçirir.** `streamingCalls` ChatScreen'e verilir.

**9. `ChatScreen.jsx` — çizer.**
Kayıtlı mesaj `message.calls`'ını, akan cevap `streamingCalls`'ı çizer. Liste boşken hiçbir kap
çizilmez. Hedefsiz satır yalnız adı yazar, ayraç çizmez.

**10. `workspace.css` — satırın görünümü.**
`.tool-calls`, `.tool-call`, `.tool-call__name`, `.tool-call__target`. Mono, muted, vurgu rengi yok.

**11. İki suite koşulur**, yirmi kırmızının yeşile döndüğü görülür.

**12. `dist` derlenir** ve kaynağıyla aynı commit'e girer.

**13. Commit.**

## Beklenen yeşil

`python -m pytest queen-agent -q` → 401 · `npm test --prefix queen-agent/frontend` → 481.

Yeşil kalması gereken komşular: araç trafiğinin sohbete mesaj olarak yazılmaması, dosya kartının iki
kez duyurulması, `calls` taşımayan eski sohbetin okunabilmesi.

## Turda çıkan iki şey

**Satır dosya kartının arkasına geçti.** İlk yazılışta `ToolCall` karttan **önce** yayılıyordu ve
iki eski test düştü — ikisi de dosyanın "kendini iki kez duyurduğunu" sıradaki *yerine* bakarak
tutuyor. Sıra değiştirildi: önce kart, sonra satır. Ekranda bir farkı yok, ikisi ayrı yerlere
çiziliyor; kazancı, dolu kartın yerini aldığı kesikli kartın hemen ardında kalması. Eski testlere
dokunulmadı.

**Kendi testimin biri akışı hiç koşturmuyormuş.** `test_the_stored_chat_hands_back_the_calls`
cevabı istiyor ama gövdeyi okumuyordu; cevabı yazan şey üreteç olduğu için hiçbir şey çalışmıyor ve
kayıt boş kalıyordu. Test gövdeyi okuyacak şekilde düzeltildi — iddiası değişmedi, yalnız iddia
ettiği şeyi gerçekten çalıştırır oldu. Kırmızı turda bu görülmemişti, çünkü test zaten kırmızıydı ve
**doğru sebeple kırmızı olduğu doğrulanmamıştı.**

## Bu turda yapılmayan

Durdurma *(Madde 67)* · tüketim sayacı *(68)* · dosya kartının kaldırılması · başarısız çağrının
ayrıca işaretlenmesi · çağrının aldığı bütün değerlerin gösterilmesi.
