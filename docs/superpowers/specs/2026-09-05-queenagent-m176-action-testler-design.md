# Madde 176 · test turu — `write_frame_prompt`, karenin action'ını yazan araç

**Kaynağı:** [yol haritası](../plans/2026-09-05-queenagent-v7-roadmap.md), Madde 176. Koşunun
tasarımının bütün sebebi bu madde: iki modelin işi burada bölünüyor.

Bu tur **yalnız testleri** yazıyor ve kırmızı commit'liyor.

---

## İşin bölünmesi

Ana ajan — Queen Flash ya da Queen Pro — senaryoyu kuruyor: kim var, ne giyiyor, nerede, hangi
sırayla. Tasarımın tespiti şu: **bu model kurmakta iyi, o cümleyi yazmakta değil** — kısıtı yüzünden
kaçamak yazıyor. Grok'un gücü tam da orada, ama karmaşık işi taşımıyor.

`write_frame_prompt(file, frame, note?)` bu bölünmenin tek geçidi. Ana ajan **neyin nereye
yazılacağını** söylüyor, yazan model **yalnız o cümleyi** yazıyor.

Yazılan tek alan `action`. Kamera da onun içinde — kullanıcının kararı: *"kamerayı kaldıralım, onu
da aksiyona yazalım."* Model iki alan arasında bölüşme yapmıyor, tek bir cümle yazıyor.

## Yazan modelin gördüğü

**Bütün dosya değil.** Kullanıcının kararı: *"burada bütün karakterleri vs almasın, sadece o sahnede
olan karakterleri ve senaryoyu alsın."* Ve *"etiket ve adlarını görsün"* — ad da etiket de, çünkü
notta geçen ad ile haritadaki etiketi eşleştirmesi gerekiyor.

```
Scene: she turns her head as the door opens
In frame:
- aylin: 1girl, long teal hair
  wearing gecelik: white nightgown
Place: bedroom: sunlit bedroom
Note: make it tenser, she is afraid
```

Öteki karelerin kadrosu, haritanın geri kalanı, konuşma, araç listesi, bağlam kabı — hiçbiri
gitmiyor. Bu isteğin ucuz olmasının sebebi bu.

**Not ana ajanın sesi.** Kullanıcı *"şurası kötü olmuş, düzelt"* dediğinde ana ajan bunu nota
koyuyor ve aynı kareyi yeniden çağırıyor — yeniden deneme diye ayrı bir şey yok, **aynı kareyi
yeniden çağırmak zaten odur.**

## Sistem promptu iki parçadan

`WRITE_FRAME_SYSTEM_PROMPT` + `SDXL_PROMPT_RULES`.

172 ölü şemayı ikiye bölmüştü: **girdi kuralları** altı harita aracının yanına gitti, **action ve
kamera kuralları** bu maddeye bırakıldı. İkinci yarı şimdi geliyor, ve 172'nin testi
*(`test_the_rules_say_nothing_about_a_frames_action`)* iki yarının birbirine karışmadığını hâlâ
bekliyor.

`SYSTEM_PROMPT` girmiyor: o QueenAgent'ın ajanına ne yapacağını anlatıyor, buradaki modelin ajanlığı
yok.

## Cevap düz metin

JSON değil — **yazılacak tek alan var.** Bir şema, tek alanlı bir nesne için modele fazladan bir iş
ve bozulacak fazladan bir şey verirdi. Gelen metin `frames[n].action`'a **her zaman üzerine**
yazılıyor: not ile ikinci çağrı düzeltme demek, ve düzeltme eskisini bırakmaz.

Metin **cevaba basılmıyor.** 130'un kuralı: derlenmiş prompt ekrana değil dosyaya gider. Makbuz tek
cümle: *Wrote frame 3 of bar-scene.json.*

## Reddettikleri

| Ne | Cümle |
|---|---|
| sahnesiz kare | `Frame 3 has no scene to write from.` |
| olmayan kare | 174'ün cümlesi |
| motor yok | `There is no model to write with.` |
| istek düştü | `The prompt model did not answer: {servisin kendi sözleri}` |
| boş cevap | `The prompt model answered with nothing; frame 3 is unchanged.` |

Son ikisinde **kare olduğu gibi kalıyor** ve araç bunu söylüyor. İçeride yeniden deneme yok: bir
raund kaybetmek, sessizce iki kere ödemekten iyidir — ve ana ajan zaten yeniden çağırabilir.

## Harcama damgaya ekleniyor

175'ten devrolan yarı. `ToolResult.spent` doluyor, `stream_answer` onu turun toplamına **ekliyor**.

`context` **eklenmiyor:** o alan son raundun isteğinin büyüklüğü — konuşmanın ne kadar şiştiği — ve
bu aracın isteği konuşma değil. Toplama girse, sohbetin ne zaman dolduğunu söyleyen tek sayı yalan
söylerdi.

## İki açıklamaya eklenen cümle

173 ve 174 `action`'dan söz etmemişti: o gün onu yazan araç yoktu, ve olmayan bir aracın adını
açıklamaya koymak modele çağıramayacağı bir yol göstermek olurdu. Bugün var. `add_scene` ve
`update_frame` artık `write_frame_prompt`'u adıyla anıyor.

---

## Koşarken çıkan tek şey — dördüncü kez aynı ders

`test_a_tools_request_does_not_change_how_big_the_conversation_got` ilk koşuda **yeşildi.** İddiası
`context == 1500`, ve bugün hiçbir şey eklenmediği için zaten 1500. 168, 173, 174 ve şimdi 176 —
**"X'e dokunulmadı" diyen test, dokunulan şeyi de görmek zorunda.** Aracın faturasının toplama
girdiğini ölçen satır eklendi.

## Çivilenen vak'alar — 21 kırmızı

**Bildirim (3):** araç listesinde var; `modes.py` kapıyı önünde tutuyor; iki komşu araç onu adıyla
anıyor.

**Sistem promptu (3):** girdi kurallarını taşıyor · action ve kamerayı anlatıyor · `SYSTEM_PROMPT`
taşımıyor.

**Giden mesaj (5):** sahne cümlesi · kadronun adları ve etiketleri · kıyafetlerin etiketleri · mekân
ve etiketi · not. Ve bir yasak: **öteki karelerin kadrosu gitmiyor.**

**Yazdığı (5):** `action`'a yazıyor · üzerine yazıyor · makbuz · metin cevapta yok · dosya
doğurmuyor.

**Harcama (2):** `ToolResult.spent` doluyor · turun damgasına ekleniyor, `context`'e dokunmadan.

**Reddettiği (5):** sahnesiz kare · olmayan kare · motor yok · düşen istek · boş cevap.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **21 kırmızı**, hepsi `queen-agent`'ta; hiçbiri `skip` ya da `xfail` değil.
3. Kırmızıların hepsi **yokluktan** — `There is no tool called write_frame_prompt.`
4. Öteki üç takım rakamlarını korudu: **586 · 739 · 591.** `dist` derlenmedi.
