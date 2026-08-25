# Madde 66 — Tool call'lar sohbette görünür · **uygulama turu**

**Tarih:** 2026-08-25 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Madde 66 ·
**Önceki tur:** [test tasarımı](2026-08-25-queenagent-m66-tool-satiri-testler-design.md) — yirmi
test `2be8d6e`'de kırmızı commit'lendi.
**Tur:** ikiden ikincisi.

---

## Testlerin istediği

Bir çağrı üç yerden geçecek: **koştuğu an bir parça olarak yayılacak**, **cevabın kaydına
yazılacak**, ve **ekranda bir satır olarak çizilecek** — hem akarken hem kayıttan.

`ToolCall` tipi önceki turda doğdu. Geri kalan her şey bu turda.

## Zincir

Bir çağrının izlediği yol, uçtan uca:

1. **`tools.py`** — çalışan araç, sonucunun yanında **hedefini** de söyler. Adın nasıl
   temizlendiği ve çakışmanın nasıl çözüldüğü zaten burada yaşıyor; hedefi başka yerde hesaplamak o
   kuralın ikinci kopyası olurdu ve ilk değişiklikte ayrışırdı.
2. **`stream_answer`** — araç koştuktan **sonra** bir `ToolCall` yayar. Sonra değil önce olsaydı
   hedef henüz kesin olmazdı; dosya kartının adının neden çalıştıktan sonra belli olduğuyla aynı
   sebep. Yayılanların hepsi biriktirilir ve turun sonunda cevap mesajına verilir.
3. **`chat.py` / `append_message`** — mesaj `calls` diye bir alan kazanır. `files`'ın yanında, aynı
   kuralla: varsayılanı boş, boşken kimseyi ilgilendirmiyor.
4. **`file_chat_store`** — alan diske boşken **yazılmaz**, okunurken yoksa boş sayılır. Göç yok:
   bugünkü sohbetler alanı taşımıyor ve taşımadıkları için bozulmuyorlar. Hedefsiz çağrıda `target`
   de yazılmaz — aynı gerekçe bir kat daha.
5. **`routes.py`** — parça `call` olayı olarak çıkar, `file` olayının komşusu. Sohbetin JSON'u da
   mesajın `calls`'ını taşır.
6. **`useChat`** — akıştan gelen çağrılar toplanır ve akış biterken **bırakılır**: sunucunun kaydı
   aynı çağrıları taşıyor. Dosya kartlarının bugün yaptığı devrin aynısı, ve aynı sebeple — iki
   kaynaktan çizilen tek adım iki adım gibi okunur.
7. **`ChatScreen`** — kayıtlı mesaj kendi `calls`'ını çizer; akan cevap kendi topladığını çizer.

## Satırın şekli

Tasarım bu koşuda kodu takip ediyor *(koşunun kaydına bakılsın)*, yani görünüm burada kararlaşıyor
ve tasarım geldiğinde üstüne ikinci bir tur gelebilir.

Satır cevabın **üstünde** durur: çağrılar cevap yazılmadan önce oldu, ve sıra bunu söylemeli.
Mono, muted, tek satır — mesajın üstündeki mono etiketle aynı aile, çünkü ikisi de aynı işi yapıyor:
metnin kendisi değil, metin hakkında bir not.

Hedefi olmayan çağrı yalnız aracın adını yazar. Ayraç, iki yanı da dolu olduğunda çizilir — boş bir
ad için yer tutan ayraç, olmayan bir şeyi varmış gibi gösterir.

Vurgu rengi kullanılmaz: `#B5623C` birincil eylemi işaretliyor ve bir çağrı satırı eylem değil,
kayıt.

## Dokunulmayanlar

- **Dosya kartı.** `create_file` hem satır hem kart doğurmaya devam eder; ikisi ayrı soruya cevap
  veriyor — kart *dosya burada, aç*, satır *cevap şunu yaptı*.
- **Model bilgisi.** Araç trafiği hâlâ sohbete mesaj olarak yazılmıyor; kaydedilen şey adım, konuşma
  değil.
- **Tur sınırı**, **hata kartı**, **kesikli kart** — hiçbiri bu maddenin konusu değil.

## `dist`

`ChatScreen.jsx`, `useChat.js`, `App.jsx` ve `workspace.css` ön yüz kaynağı: `frontend/dist` **aynı
commit'te** derlenip commit'lenir.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Yirmi kırmızı yeşile döner; arka uçta 401, ön yüzde 481 test yeşil olur. Yeşil kalması gereken
komşular: **araç trafiğinin sohbete mesaj olarak yazılmaması**, **dosya kartlarının iki kez
duyurulması**, ve **`calls` taşımayan eski sohbetlerin okunabilmesi**.
