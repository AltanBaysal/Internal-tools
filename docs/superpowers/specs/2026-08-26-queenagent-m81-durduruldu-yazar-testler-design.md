# Madde 81 — Durdurulan tur durdurulduğunu söyler · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 4, Madde 81 ·
**Üstüne geldiği:** [Madde 67](2026-08-25-queenagent-m67-durdurma-uygulama-design.md) —
durdurmanın kendisi.
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz, ve tur kırmızı
commit'lenir.

---

## İki delik

**Bir:** durdurulan cevabın bugünkü tek işareti metnine çekilen gri bir sol çizgi
*(`workspace.css`, `.msg--stopped .msg__text`)*. Hiçbir yerde kelime yok. O çizgi orada olduğunu
bilene bir şey söylüyor, bilmeyene hiçbir şey.

**İki:** ilk kelime gelmeden durdurulursa **diske hiçbir şey yazılmıyor**. Basıyorsun, akış
kapanıyor, ekran hiçbir şey olmamış gibi duruyor. Kaydın olmadığı yerde çizginin de yeri yok.

İkincinin arkasında üçüncü bir şey duruyor: kayıt yazılmayınca sohbetin son mesajı kullanıcınınki
kalıyor, yani sohbet hâlâ bir cevap borçlu görünüyor. Bunu tutan tek şey tarayıcıdaki `stopped`
bayrağı ve o bayrak yenilemede sıfırlanıyor — **bugün durdurup sayfayı yenileyince cevap kendi
kendine baştan başlıyor**.

## Kararı verilmiş: boş kayıt yazılır

*(kullanıcı kararı, 26 Ağustos)* — kelimeden önce durdurulan tur da diske yazılıyor: metni boş,
`stopped` işaretli bir cevap.

Bedeli önden biliniyor ve kabul edildi. 67'nin *"cevap ya vardır ya yoktur"* kuralı esniyor. Kural
yeni hâliyle şu:

> Bir mesaj ya bir söz, ya bir dosya, **ya da bir durdurma** taşır.

Bu üçüncüsü keyfi bir gevşetme değil: durdurma da olmuş bir şey, ve olmuş bir şeyin kaydı olur.
Kural zaten bir kez esnemişti — 67 yarım metni saklamaya karar verdiğinde.

**Kullanıcının boş mesajı hâlâ reddediliyor.** Kapıyı açan şey `stopped`, ve kullanıcının mesajı
hiçbir zaman `stopped` taşımıyor.

## Ekranda ne yazacak

Metnin hemen altında tek kelime: **`Stopped`**.

- **İngilizce**, çünkü QueenAgent'ın arayüzü bilerek İngilizce *(CLAUDE.md)*.
- **Metnin altında**, çünkü açıkladığı şey metnin neden yarıda bittiği. Dosya kartları ve token
  sayısı onun altında kalıyor — ikisi de turun kendisi hakkında notlar, bu ise metnin sonu.
- **İşaretsiz.** `⎿` tool call satırının işareti ve *"üstündekinin sonucu"* demek; durdurma bir
  çağrının sonucu değil. Ayırt eden şey yazı tipi: not kaydında, cevabın gövdesinde değil.
- **Sebep uydurulmuyor.** Kim durdurduysa o bir tanedir — kullanıcı — ve `Stopped` bunu zaten
  söylüyor. *"Interrupted by the network"* gibi bir cümle uydurmak CLAUDE.md'nin yasağına girer.

Metin boşken **metin bloğu hiç çizilmiyor**: boş bir `.msg__text` ile gri sol çizgi, yanında hiçbir
şey olmayan iki piksellik bir çubuk olurdu.

Gri çizgi kalıyor. Kelime onu okunur yapıyor, yerini almıyor.

## Kırmızıya dönecek testler

**Arka uç — iki:**

1. `test_append_message.py` · **yeni** — durdurulmuş bir cevap boş olabilir: `text=""`,
   `stopped=True` ile yazılıyor ve kayda giriyor.
2. `test_stream_answer.py` · **ters çevrilen** — bugünkü `test_stopping_before_a_word_writes_no_message`
   tam tersini söyleyecek: kelimeden önce durdurulan tur `["user", "ai"]` bırakıyor, son mesajın
   metni boş ve `stopped` işaretli.

**Ön yüz — üç:**

3. `ChatScreen.test.jsx` · **yeni** — durdurulan cevabın altında `Stopped` yazıyor.
4. `ChatScreen.test.jsx` · **yeni** — kelimeden önce durdurulan cevap ekranda yine de bir mesaj:
   `Stopped` var, ve boş metin bloğu **yok**.
5. `workspace.css.test.js` · **yeni** — `.msg__stopped` not kaydında: `var(--muted)` ve
   `var(--font-mono)`, tıpkı üstündeki adımlar ve altındaki token sayısı gibi.

Toplam **beş kırmızı**.

## Günü geçiren iki test

İkisi ilk günden yeşil, ve bilerek yazılıyorlar — ikisi de bugün var olmayan bir durumu kilitliyor,
yani yarın kırılabilecek bir şeyi bugünden tutuyorlar:

| Nerede | Ne tutuyor |
|---|---|
| `ChatScreen.test.jsx` | Sonuna kadar giden cevabın altında `Stopped` **yok** |
| `App.test.jsx` | Son mesajı boş bir `stopped` cevap olan sohbet **yeniden sorulmuyor** |

İkincisi bu maddenin asıl kazancı. Bugün geçiyor çünkü bugün öyle bir sohbet **kurulamıyor** — kayıt
hiç yazılmadığı için. Yarın kurulabilir olacak, ve o gün bu test onun doğru davrandığının tek
kanıtı.

## Dokunulmayan yeşiller

| Ne | Neyi kanıtlıyor |
|---|---|
| `test_an_empty_message_is_refused_and_the_chat_is_untouched` | Kullanıcının boş mesajı hâlâ reddediliyor |
| `test_what_was_already_said_is_kept` | Yarım metin hâlâ saklanıyor |
| `test_a_stopped_answer_says_it_was_stopped` | `stopped` işareti hâlâ kayda giriyor |
| `test_a_stop_ends_the_answer_without_asking_the_model_again` | Kalan turlar hâlâ koşmuyor |
| `ChatScreen.test.jsx` — `.msg--stopped` çizgisi | Gri çizgi duruyor |
| `App.test.jsx` — akarken durdurulan cevap yeniden sorulmuyor | 67'nin canlı koruması duruyor |

## Kapsam dışı

- **Durdurmanın kendisi.** 67 ve 79 nasıl bıraktıysa öyle; bu madde yalnız kaydın ve ekranın ne
  söylediğine dokunuyor.
- **Diskte yarım kalan dosyalar.** Durdurma bir geri alma değil: koşmuş bir araç dosyayı yazmıştır
  ve yazılı kalır. Bu bilerek böyle *(kullanıcı, 26 Ağustos: "sorun yok o konuda")*.
- **Turkçe metin.** Arayüz İngilizce.
- **Tur sınırına dayanan cevap.** O da bir son ama durdurma değil; kimse basmadı.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur** — birlikte koşturulduğunda vitest bu makinede zaman aşımına düşüyor.

Arka uçta **4 failed, 441 passed** beklenir: ikisi bu maddenin, ikisi defterin dalı. Ön yüzde
**3 failed, 509 passed** — üç yeni testle toplam 512.

`dist` bu turda derlenmiyor: kaynak değişmiyor, yalnız testler yazılıyor.
