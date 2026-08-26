# Madde 83 — Mesajın damgası altına iner · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 4, Madde 83 ·
**Üstüne geldiği:** [Madde 76](2026-08-26-queenagent-m76-tuketim-istenir-uygulama-design.md) —
sayının ekrana geldiği yer.
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz, ve tur kırmızı
commit'lenir.

---

## Bugün bir mesaj neye benziyor

Cevap iki not taşıyor ve ikisi mesajın iki ucunda duruyor:

```
QUEENAGENT · 11:05        ← .msg__label,  üstte, BÜYÜK HARF
⏺ list_files
  ⎿ No files
Here it is.
Stopped
[dosya kartları]
13.2k tokens              ← .token-count, altta, ayrı satır
```

Kullanıcının mesajı da aynı `.msg__label`'ı taşıyor ama içinde yalnız saat var — `QueenAgent`
yazmıyor, çünkü baloncuğun sağda oluşu kimin yazdığını zaten söylüyor.

Üç şey birden yanlış duruyor:

1. **`QueenAgent` her cevapta tekrarlanıyor.** Kenar çubuğunda zaten yazılı, ve cevabın solda
   oluşu onu ikinci kez söylüyor. Üçüncüsü fazla.
2. **Tek işi olan iki satır var.** Üstte saat, altta sayı. İkisi de aynı şeyin notu: bu tur ne
   zaman oldu ve neye mal oldu.
3. **Damga üstte.** Bir notun yeri anlattığı şeyin altıdır; üstte durduğunda okumaya başlamadan
   önce okunuyor.

## Ne olacak

Üstteki satır siliniyor, alttaki onun taşıdığını da alıyor:

```
⏺ list_files
  ⎿ No files
Here it is.
Stopped
[dosya kartları]
11:05 · 13.2k tokens      ← .msg__stamp, tek satır, en altta
```

Kullanıcının mesajı:

```
              [baloncuk]
                  11:04  ← .msg__stamp, altta, sağa yaslı
```

## Kararı verilmiş

**Kullanıcının mesajının saati de alta iner** *(kullanıcı kararı, 26 Ağustos)*. İki taraf da
damgasını altında taşıyor. Bir sohbette birinin damgası üstte, diğerininki altta olsaydı kaza gibi
okunurdu.

**`tokens` kelimesi açık kalıyor.** Kullanıcı `500 t` çizdi; `t` tek başına neyin kısaltması olduğunu
söylemiyor, ve satır bir kelimeyi taşıyacak kadar geniş. Kullanıcıya söylendi.

## Kararlar

**Tek eleman, tek metin.** İki eleman yan yana koymak yerine damga tek bir `div` ve içinde tek bir
cümle: `11:05 · 13.2k tokens`. Ayırıcı ` · ` — bugün `QueenAgent` ile saatin arasında duran işaretin
ta kendisi, yani yeni bir şey icat edilmiyor.

**Sayı yoksa yalnız saat.** `11:05`, sonunda ayırıcı kalmadan. Bu üç durumda oluyor ve üçü de
olağan: sayı gelmeden önceki kayıtlar, kullanıcının kendi mesajı, ve cevap daha akarken — sayı tek
karede, en sonda geliyor *(76)*.

**Damga her zaman mesajın son çocuğu.** Kural tek cümle olduğu için hem saklanmış mesajda hem
bekleyen kutuda hem akan kutuda aynı yeri buluyor: dosya kartlarının, `Stopped` satırının ve doğmakta
olan dosyanın altında.

**Büyük harf gidiyor.** `.msg__label` bugün `text-transform: uppercase` taşıyor. Bir isim için
anlamı vardı, `11:05` için yok. Damga üstündeki `Stopped` ile aynı sesi alıyor: `var(--font-mono)`,
`var(--muted)`, 11.5px — turun üç notu, tek ses.

**İki sınıf adı düşüyor, biri geliyor.** `.msg__label` ve `.token-count` yerine `.msg__stamp`. Yeni
ad ailesine uyuyor (`msg__text`, `msg__bubble`, `msg__stopped`), ve eski iki ad artık var olmayan
iki şeyi anlatıyor.

**Damgası olmayan bir kutu damga çizmiyor.** Bekleyen kutunun saati ilk çizimde henüz yok; `null`
bir saat için boş bir satır çizmek yerine hiçbir şey çizilmiyor.

## Kırmızıya dönecek testler

**`ChatScreen.test.jsx` — dokuz:**

| # | Test | Bugün | Yarın |
|---|---|---|---|
| 1 | cevabın damgası | `QueenAgent · 11:05` | `11:05`, sınıfı `msg__stamp`, `QueenAgent` yok |
| 2 | kullanıcı mesajının damgası | sınıfı `msg__label` | sınıfı `msg__stamp` |
| 3 | bekleyen kutunun saati | `QueenAgent · 14:32` | `14:32` |
| 4 | cevap akarken saat kaymıyor | `QueenAgent · 14:32` | `14:32` |
| 5 | cevap ne harcadı | `13.2k tokens` | `11:05 · 13.2k tokens` |
| 6 | küçük cevap büyük gösterilmiyor | `342 tokens` | `11:05 · 342 tokens` |
| 7 | kimsenin ölçmediği cevap | hiçbir satır yok | damga var, yalnız saat taşıyor |
| 8 | kullanıcının mesajı sayı taşımıyor | `.msg--user .token-count` yok | `.msg--user .msg__stamp` var ve içinde `tokens` yok |
| 9 | **yeni** — damga mesajı kapatıyor | son çocuk `.msg__text` | son çocuk `.msg__stamp`, iki mesajda da |

Yedincisi ters yönde kırılıyor ve bilerek: bugün ölçülmemiş cevabın altında **hiçbir** satır yok,
yarın saat taşıyan bir damga var. Sayının yokluğu satırın yokluğu demek değil artık — saat her zaman
var.

**`workspace.css.test.js` — iki:**

| # | Ne tutuyor |
|---|---|
| 10 | **yeni** — `.msg__stamp` not kaydında: `var(--font-mono)`, `var(--muted)`, ve `text-transform` **yok** |
| 11 | **yeni** — `.msg__label` ile `.token-count` stil dosyasında hiç geçmiyor |

Toplam **on bir kırmızı**. Sekizi var olan testin yeniden yazılması, üçü yeni.

## Dokunulmayan yeşiller

| Ne | Neyi kanıtlıyor |
|---|---|
| `Sidebar.test.jsx` — `QueenAgent` | Kelime uygulamadan silinmiyor; kenar çubuğundaki adı duruyor |
| `App.test.jsx` — üç `getByText("QueenAgent")` | Aynısı, uygulamanın bütünü içinde |
| `ChatScreen.test.jsx` — `.msg--stopped` çizgisi ve `Stopped` satırı | 81 aynen duruyor |
| `ChatScreen.test.jsx` — tool call satırları | 78 aynen duruyor |
| `ChatScreen.test.jsx` — dosya kartları, doğmakta olan dosya | Damganın altına inmesi onları kaydırmıyor |
| `time.test.js` — `clockTime` | Saatin biçimi değişmiyor; taşındığı yer değişiyor |

## Kapsam dışı

- **Sayının kendisi.** Neyin toplandığı *(gönderilen + cevaplanan)*, binden sonra kısaltılması,
  önbellek payının çizilmemesi — üçü de 68 ile 76'nın kararı ve aynen duruyor.
- **Saatin biçimi.** `clockTime` ne veriyorsa o. Kullanıcı örneğinde `16.27` yazdı, bugünkü biçim
  `16:27`, ve iki nokta deponun kendi biçimi.
- **Kenar çubuğundaki `QueenAgent`.** Uygulamanın adı orada, ve orada kalıyor.
- **Arka uç.** Hiçbir şey değişmiyor: damga zaten diskteki `at` ve `usage` alanlarından çiziliyor.
- **Türkçe metin.** Arayüz İngilizce *(CLAUDE.md)*.

## Uygulama turuna kalan bir yorum

`workspace.css` bugün `.msg--waiting` kuralının üstünde şunu diyor: *"The design measures the wait:
10px between the label and the dots"*. Etiket noktaların altına indiğinde o cümle yanlış olacak —
ölçtüğü boşluk artık noktalarla damganın arası. Yorum uygulama turunda koda uydurulur; bu turda
kaynağa dokunulmuyor.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur** — birlikte koşturulduğunda vitest bu makinede zaman aşımına düşüyor.

Arka uçta değişiklik beklenmiyor: bugünkü **2 failed, 430 passed** aynen kalır, ve o iki kırmızı
defterin `feat/queenagent-v5`'te duran dalı — deneme bitince `main`'e çevrilecek.

Ön yüzde bugün **494 passed**. Üç yeni testle toplam **497**, ve **11 failed, 486 passed** beklenir.

`dist` bu turda derlenmiyor: kaynak değişmiyor, yalnız testler yazılıyor.
