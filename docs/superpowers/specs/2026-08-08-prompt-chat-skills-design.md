# prompt-chat — Skill'ler (Tasarım)

**Ekliyor:** [ilk spec](2026-08-08-prompt-chat-design.md) ve
[sohbet listesi](2026-08-08-prompt-chat-sohbet-listesi-design.md). Hiçbir kararlarını geri almaz.

**Öncesine geçiyor:** [agent iskeleti](2026-08-08-prompt-chat-agent-iskeleti-design.md). O belge
geçerli ama **sonraki aşama** — araçlar, döngü, dosyalar, projeler, modlar oraya ait. Bu belgede
hiçbiri yok.

## Amaç

prompt-chat bugün genel bir sohbet: yazarsın, cevap gelir, kopyalarsın. Modele "nasıl yazacağını"
her seferinde elle anlatmak gerekiyor — aynı talimatı herkes kendi kopyala-yapıştır defterinde
taşıyor.

Bu sürüm o talimatı repoya alıyor. **Skill**, agent'ın değil senin çağırdığın bir talimat dosyası:
`/sahne-yazma` yazıyorsun, o skill'in metni konuşmaya giriyor, model ona göre davranıyor.

Kazanç şu: talimat bir kişinin defterinden çıkıp **sürüm kontrollü ortak bir dosyaya** dönüşüyor.
İyileştiren commit'liyor, `git pull` yapan iyileşmiş hâlini alıyor.

Agent yok, döngü yok, dosya yazma yok. Bunlar bilerek ertelendi: en küçük işe yarar adım bu, ve
skill metinlerinin iyi olup olmadığını agent kurmadan da öğrenebiliriz.

## Ne çalışır

1. **Skill'ler repoda durur.** `prompt-chat/skills/<ad>/SKILL.md`, Vite build sırasında
   uygulamanın içine gömer. Ağ yok, backend yok.
2. **`/` yazınca liste açılır.** Yazı kutusunun başında `/` görünce skill adları ve tarifleri
   listelenir; yazdıkça süzülür, seçince mesajın başına yerleşir.
3. **Mesaj skill ile gider.** `/sahne-yazma sahneleri yaz` → skill'in tam metni, konuşmaya o
   mesajın önünde girer.
4. **Talimat sohbette kalır.** Bir kez çağırdığın skill sonraki mesajlarda da görülür — sistem
   mesajını değiştirmediğimiz için model önceki talimatı unutmaz.
5. **Model hangi skill'lerin olduğunu bilir.** Sistem mesajında hepsinin adı ve tarifi durur, tam
   metni durmaz — böylece model *"bunun için `/prompt-yazma` kullanmak isteyebilirsin"* diyebilir.

## Skill formatı — standarda uyar

[agentskills.io](https://agentskills.io/specification) açık standardı. Uydurmuyoruz: aynı format
Claude Code, Cursor, Copilot, Codex, Gemini CLI dahil kırktan fazla araçta çalışıyor, yani yazdığın
skill'i olduğu gibi başka bir araca taşıyabilirsin.

```
prompt-chat/skills/
└── sahne-yazma/
    └── SKILL.md
```

```markdown
---
name: sahne-yazma
description: Hikâyeyi fotoğraf karelerine böler. Kullanıcı sahne, kare, çekim
             listesi ya da storyboard'dan söz ettiğinde kullanılır.
---

(talimat metni)
```

| Alan | Kural |
|---|---|
| `name` | zorunlu; en fazla 64 karakter; yalnız küçük harf, rakam, tire; başta/sonda tire yok, arka arkaya iki tire yok; **klasör adıyla aynı** |
| `description` | zorunlu; en fazla 1024 karakter; **ne yaptığını ve ne zaman kullanılacağını** yazar |
| gövde | serbest markdown; 500 satırı geçmemesi önerilir |

Standardın isteğe bağlı alanları (`license`, `compatibility`, `metadata`, `allowed-tools`) ve alt
klasörleri (`scripts/`, `references/`, `assets/`) **okunmaz ve yok sayılır** — geçersiz değil,
sadece bu sürümün işine yaramıyor. Dosya standarda uygun kalır.

`description`'ın iyi yazılması bu sürümün tek gerçek kalite kaldıracı: modelin skill'i doğru
uygulaması ve senin listede doğru olanı bulman aynı cümleye bağlı.

## Bu sürümle gelen iki skill

| Skill | Ne yapar |
|---|---|
| `netlestirme` | Belirsiz bir isteği alır, başlamadan önce cevaplanması gereken soruları listeler |
| `plan-yazma` | Bir hedefi alır, numaralı adımlara böler; her adımda ne gerektiğini yazar |

İkisi de **genel amaçlı**: konu fark etmez, ekipte herkesin işine yarar. Bilerek böyle seçildi —
hikâye/sahne gibi işe özel bir skill yazmak, henüz konuşmadığımız zanaat hakkında varsayım yapmak
olurdu.

Seçimin üç sebebi var:
1. **Fark gözle görünür.** Biri soru listesi, diğeri adım listesi, skill'siz cevap ise düzyazı —
   makinenin çalıştığı bir bakışta anlaşılır.
2. **Birbirini tamamlarlar.** Önce netleştir, sonra planla. Aynı sohbette ikisini arka arkaya
   çağırmak, `/ad`'ın birikmesini de sınar.
3. **Atılacak örnek değiller.** İkisi de gerçekten kullanılacak.

Senin işine özel skill'ler (hikâye, sahne, prompt) bu sürümde **yok**. Onlar bir sonraki turun
konusu ve içeriklerini beraber yazacağız.

## Mesaj nasıl gider

Skill metni **saklanmaz**, gönderilirken açılır. Üç ayrı temsil:

| | İçerik |
|---|---|
| **Saklanan** (localStorage) | `{ role: "user", content: "sahneleri yaz", skill: "sahne-yazma" }` |
| **Ekranda görünen** | küçük bir etiket `sahne-yazma`, altında `sahneleri yaz` |
| **xAI'a giden** | skill'in tam gövdesi + boş satır + `sahneleri yaz` |

Neden böyle: skill metni build'in içinde zaten var, kayda ikinci kez yazmak hem `localStorage`'ı
şişirir hem de ikinci bir gerçek kaynağı olur — repodaki skill değiştiğinde eski sohbetler eski
metni taşırdı. Ekranda ham metni göstermemek de ayrı bir kazanç: üç bin kelimelik talimat duvarı,
kendi yazdığın cümleyi görünmez yapar.

Açılımı yapan yer `toRequestBody`. Bugün `{role, content}` çiftine indirgeyen o fonksiyon, artık
`skill` alanını da genişletir. Saf bir fonksiyon olduğu için testi ağsız yazılır.

Aynı skill'i iki kez çağırırsan metni **iki kez** gider. Tekrarı ayıklamıyoruz: ikinci çağırma
"bunu tekrar uygula" demenin yolu, ve sessizce ayıklamak modelin gördüğü şeyi senden habersiz
değiştirirdi. Bedeli görünür — alışkanlıkla her mesaja `/ad` yazmak parayı katlar.

Sistem mesajı sabittir ve tek işi var: cevabın Türkçe olması, ve mevcut skill'lerin adı + tarifi.
Skill'lerin tam metni orada durmaz — model neyin var olduğunu bilir, ne yaptığını çağrılınca öğrenir.

**Skill'siz yolda değişen tek şey budur ve bilerek kabul ediliyor:** bugün hiç sistem mesajı
gitmiyor, bundan sonra iki satırlık bir tane gidecek. Ekran aynı kalır, ama modelin gördüğü paket
aynı kalmaz. Karşılığı: model kendisine ne sorulduğunda hangi skill'in işe yarayacağını
söyleyebilir — *"bunun için `/plan-yazma` kullanabilirsin"*. Bu olmadan skill'ler ancak adını
bilenlerin bulabileceği gizli bir özellik olurdu.

## Veri

`chats` içindeki mesajlara **tek bir isteğe bağlı alan** eklenir:

```js
{ role: "user", content: "sahneleri yaz", skill: "sahne-yazma" }
```

`skill` yoksa mesaj bugünkü gibi davranır. Yeni `localStorage` anahtarı yok, yeni ekran yok, veri
göçü yok — eski sohbetler olduğu gibi çalışmaya devam eder.

## Hatalar

Bugünkü kural sürer: **servisin kendi sözü aktarılır, sebep uydurulmaz.**

| Durum | Ne olur |
|---|---|
| `/olmayan-skill` yazıldı | Mesaj **gönderilmez**; kutunun altında hata: bulunamadı, ve mevcut adlar listelenir |
| `SKILL.md` frontmatter'ı bozuk | O skill listeye hiç girmez; ayarlar panelinde hangi dosya ve neden diye yazar. Diğerleri çalışmaya devam eder |
| Kayıtlı bir mesaj, artık var olmayan bir skill'e atıf yapıyor | Mesaj **içeriğiyle** gider, skill metni olmadan. Ekrandaki etiket kalır. Çökme yok, uyarı yok |
| HTTP hatası | bugünkü `formatHttpError` — `HTTP <kod> — <gövde>` |

Bozuk bir skill'in tüm listeyi düşürmemesi bilinçli: skill'ler elle yazılan dosyalar, biri
bozulduğunda uygulama çalışmaya devam etmeli.

## Kapsam dışı

Hepsi [agent iskeleti spec'ine](2026-08-08-prompt-chat-agent-iskeleti-design.md) ait:

- **Araçlar ve tool calling** — model hiçbir şey çağırmaz, düz metin döner
- **Döngü** — bir istek, bir cevap; bugünkü davranışın aynısı
- **Dosya yazma, projeler, dosya ağacı, düzenleyici**
- **Modlar, geri alma, durdurma, tur tavanı**

Ayrıca bu sürümde olmayan, sonra bakılacaklar:
- **Uygulama içinde skill yazma** — skill'ler repoda yazılır, `git pull` ile dağılır
- **`references/` alt dosyaları** — standardın üçüncü kademesi; tek dosya yeterli
- **Skill'in kendi modelini seçmesi** — tek model alanı, bugünkü gibi

## Kararlar

| Karar | Gerekçe |
|---|---|
| Loop yok, araç yok | En küçük işe yarar adım. Skill metinlerinin kalitesini agent kurmadan da ölçebiliriz — ve asıl değer orada |
| Skill seçimi mesaj başına `/ad` | Aynı sohbette hikâye → sahne → prompt yapılabilsin; sohbet başına tek skill bunu keserdi |
| Metin sistem mesajına değil **konuşmaya** girer | Sistem mesajını her mesajda değiştirmek, modele önceki talimatı unutturur. Konuşmaya giren talimat birikir |
| Skill metni saklanmaz, gönderilirken açılır | Kayıt şişmez; repodaki skill değişince eski sohbetler de yeni metni kullanır |
| Ekranda ham metin yerine etiket | Üç bin kelimelik talimat, kendi yazdığın cümleyi görünmez yapar |
| agentskills.io standardı | Format zaten var ve kırktan fazla araçta çalışıyor; yazdığın skill taşınabilir olur |
| Adlar ASCII — `netlestirme`, `hikaye` | Standart `a-z0-9` diyor. Türkçe harfe izin vermek adları güzelleştirirdi ama taşınabilirliği bitirirdi — ki formatı seçmemizin tek sebebi oydu. Yazım hatası görünümü bilerek kabul edildi; `/` ile çağırırken Türkçe klavye gerekmemesi de yan kazanç |
| Standardın fazla alanları okunmaz | YAGNI — dosya uyumlu kalır, kod sadece ihtiyacı okur |
| Bozuk skill listeyi düşürmez | Elle yazılan dosyalar bozulur; biri yüzünden uygulama durmamalı |

## Doğrulama

**Önce bozmadığımızı kanıtla.** Sıra bilerek böyle: yeni özelliği denemeden önce eskisinin ayakta
olduğunu gör.

1. **Skill'siz çalışıyor mu:** hiç `/` yazmadan sıradan bir mesaj at → cevap gelir, ekran bugünküyle
   birebir aynıdır. Etiket yok, hata yok, fazladan bir şey yok.
2. **Eski sohbetler:** yenilemeden önce açılan bir sohbete dön → hiçbir davranış değişmemiş olmalı.
3. **Kalıcılık:** sayfayı yenile → sohbetler, anahtar ve model yerinde.

**Sonra yeniyi dene.**

4. **Liste:** yazı kutusuna `/` yaz → iki skill'in adı ve tarifi görünür; yazmaya devam edince süzülür.
5. **Çağırma:** `/plan-yazma hafta sonu taşınacağım` gönder → ekranda `plan-yazma` etiketi ve senin
   cümlen görünür, ham talimat metni görünmez; cevap numaralı adımlar hâlinde gelir.
6. **Fark görünüyor:** aynı cümleyi skill'siz gönder → cevap düzyazı gelir, biçim belirgin şekilde
   farklıdır.
7. **İkisi ayrışıyor:** aynı cümleyi `/netlestirme` ile gönder → adım değil **soru** listesi gelir.
8. **Talimat birikiyor:** `/netlestirme` ile başla, sonra sade bir mesaj at ("ilk üçünü cevapla") →
   model hâlâ netleştirme kipinde davranır; ardından `/plan-yazma` çağır → ikisini de görmüş olur.
9. **Bilinmeyen ad:** `/yok-boyle-bir-sey` gönder → istek atılmaz, hata ve mevcut adlar görünür.
10. **Bozuk dosya:** bir `SKILL.md`'nin frontmatter'ını boz → o skill listeden düşer, diğeri
    çalışmaya devam eder, ayarlarda hangi dosya ve neden yazar.
11. **Etiket kalıcı:** sayfayı yenile → skill etiketli eski mesajlar etiketiyle beraber görünür.
12. **Testler:** `npm test` yeşil, sayı bugünkü 69'un üstünde.
