# Madde 78 — Tool call satırı yeniden çizilir · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Madde 78 ·
**Tur:** ikiden birincisi — bu belge yalnız **testleri** tarif eder.

---

## Ne kanıtlanacak

Madde 66 çağrıları görünür kıldı ve kayda yazdı. Davranış doğru; **çizim beğenilmedi**
*(kullanıcı, 26 Ağustos)*. İstenen biçim Claude Code'unki:

```
⏺ read_file(aylin.json)
  ⎿  45 lines
```

İki iddia:

1. Satır **iki katmanlı** — üstte ne çağrıldığı, altında ne olduğu.
2. Alt satır **kayıtta kalıyor** — 66'nın kazanımı korunuyor, sayfa yenilendiğinde ikisi de duruyor.

## Karara bağlanan: alt satır ne söyleyecek

Yol haritasının açık sorusu buydu, ve cevabı bir ayrımda: **alt satır sonucun kendisi değil,
özeti.**

Bunun sebebi kayıtta yazılı. `ToolCall`'un yorumu şöyle diyor: *"Sonuç bilerek yok. Bir okumanın
döndürdüğü şey dosyanın kendisi, ve o zaten diskte; buraya kopyalamak aynı metni iki yerde
bırakırdı."* O kural duruyor — `read_file`'ın sonucu dosyanın tamamı, ve onu sohbet kaydına
yazmak hem kaydı şişirir hem ikinci bir bayatlama kaynağı açar.

Özet başka bir şey: **araç, ne yaptığını bir okuyucu için bir satırda söylüyor.** "45 lines",
"3 files", "Saved", "12 prompts". Kaç satır okunduğu diskte durmuyor — ve durmadığı için de
bayatlamıyor; o anın kaydı.

**Reddedilen çağrı da bir sonuçtur.** Olmayan bir dosyayı okumak, eşleşmeyen bir metni değiştirmek
— bunlar turun gerçekten yaptığı şeyler ve gizlenmiyor. Aracın modele söylediği cümlenin kısası
alt satıra çıkıyor.

## Kayıtta değişen

`ToolCall` üçüncü bir alan kazanıyor: `outcome`. Boşken diske yazılmıyor, taşımayan eski kayıt boş
okunuyor — `calls`, `stopped` ve `usage` ile aynı kural, dördüncü kez.

`ToolResult` de bir alan kazanıyor, aynı adla: her dal kendi özetini yazıyor. Özeti aracın kendisi
üretiyor çünkü ne olduğunu bilen o — dışarıdan `text`i ayrıştırmak kırılgan bir tahmin olurdu.

## Ekranda

| Bugün | Sonra |
|---|---|
| `read_file · aylin.json` | `⏺ read_file(aylin.json)` |
| *(alt satır yok)* | `  ⎿  45 lines` |

- **İşaretler biçimin kendisi.** İstenen şey Claude Code'un görünümü, ve onu tanınır kılan şey bu
  iki glif.
- **Konusu olmayan çağrı parantez taşımıyor.** Bir dizini listelemek gerçekten hiçbir dosya
  hakkında değil; boş parantez orada olmayan bir şeyi duyururdu. 66'daki kural, yeni kabuğunda.
- **Özeti olmayan çağrı alt satır çizmiyor.** Eski kayıtlar böyle, ve boş bir girinti alınmamış bir
  ölçümü alınmış gibi gösterirdi.
- **Renk ve tipografi değişmiyor:** mono, `var(--muted)`, vurgusuz. Vurgu birincil eylemin, ve bu
  bir kayıt.

## Yazılacak testler

### Arka uç

**`test_tools.py` — beş test.** Her aracın çağrısı kendi özetini taşıyor: listeleme kaç dosya
olduğunu, okuma kaç satır olduğunu, yaratma kaydedildiğini, düzenleme değiştirildiğini, prompt
kurma kaç prompt yazıldığını. Ayrıca reddedilen bir çağrının özeti reddi söylüyor.

**`test_stream_answer.py` — bir test.** Turun sakladığı çağrı özeti taşıyor. 66'nın testleri
`ToolCall(tool, target)` biçiminde eşitlik kuruyor; üçüncü alan varsayılanlı olduğu için o testler
kırılmıyor, ama bu tur onlardan birinin gerçekten özeti taşıdığını ayrıca soruyor.

**Depo — iki test.** Özet gidiş dönüş hayatta kalıyor. Boşken diske yazılmıyor.

**Rotalar — bir test.** Mesajın JSON'u her çağrının özetini taşıyor, boşken de.

### Ön yüz

**`ChatScreen.test.jsx` — beş test.** Satır işaretle başlıyor ve aracın adını parantezli konusuyla
yazıyor. Konusu olmayan çağrı parantez taşımıyor. Özeti olan çağrı ikinci bir satır çiziyor ve o
satır kendi işaretini taşıyor. Özeti olmayan çağrı ikinci satır çizmiyor. Akan cevapta da aynı
biçim.

## Kapsam dışı

Satırın açılıp kapanması *(Claude Code'da uzun sonuç katlanıyor; bizim özetimiz zaten tek satır)* ·
sonucun tamamının saklanması *(yukarıdaki karar)* · çağrının aldığı diğer değerler *(konusu
dışındakiler; 66'da da yoktu)* · dosya kartları *(ayrı bir şey ve duruyor)* · arka ucun araç
davranışı *(yalnız özet cümlesi ekleniyor; ne yaptıkları değişmiyor)*.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**İki suite ayrı ayrı koşulur.** Aynı anda koşturulduklarında vitest bu makinede zaman aşımına
düşüyor ve alakasız testler kırmızı görünüyor — Madde 77'de bir kez kovalandı.

Arka uçtaki bugünkü iki kırmızı defterin dalı; bu maddenin kırmızıları onlara eklenir.

Testlerin konuşabilmesi için gereken **ad** — `ToolCall.outcome` ve `ToolResult`'ın aynı adlı alanı
— bu turda doğar. Madde 66'nın dersi: içe aktarılamayan bir ad `pytest`i toplama hatasına düşürür
ve o zaman suite kırmızı değil bozuk olur.
