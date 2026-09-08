# Madde 196 · uygulama turu — sistem promptunun ikinci parçası

**Kaynağı:** [test turu](2026-09-08-queenagent-m196-ikinci-parca-testler-design.md), ve onun
kaynağı [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 196.

Kırmızı: arka uçta 5.

---

## `prompt.py`

İki şey: **boş** doğan `SYSTEM_PROMPT_SUFFIX`, ve ikisini birleştiren `system_prompt()`.

Birleştirme burada, motorda değil. Sebebi katman: iki metnin **yan yana nasıl okunduğu** bir metin
kuralı, ve 189 bütün metin kurallarını bu modüle topladı. `xai_engine` bir taşıma katmanı — orada
durursa, ayırıcının ne olduğu deponun metinlerinden uzakta, kimsenin bakmadığı bir yerde yaşar.

Boşken `SYSTEM_PROMPT`'un **kendisi** dönüyor: aynı nesne, aynı baytlar. Doluyken araya boş bir
satır giriyor — iki metin arasındaki tek ayırıcı, ve `SYSTEM_PROMPT`'un kendi paragrafları da öyle
ayrılıyor.

## `xai_engine.py`

`_for_xai` sabit yerine **işlevi** çağırıyor. `staticmethod` kalıyor; değişen tek şey, metnin
istek kurulurken okunması — sabit `import` anında değerini alıp donduğu için, oradan okumak
kullanıcının yazdığı bir cümleyi bir sonraki koşuya kadar geciktirirdi.

`write_once` kımıldamıyor: onun sistem metni çağıranın *(Madde 175)*, ve bu maddenin metni oraya
girmiyor.

## Yeşilin nasıl görüleceği

Dört sabit satır. Arka uçta 926, ve ön yüz ile `queen-editor` yerinde: **634 · 739 · 591**. `dist`
yok — bu madde ön yüze hiç dokunmuyor.
