# Madde 196 · test turu — sistem promptunun ikinci parçası

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 196.

---

## Bugün ne oluyor

Bestecinin sistem mesajı tek bir sabit: `xai_engine._for_xai` her isteğin başına `SYSTEM_PROMPT`'u
koyuyor, ve o metnin sonuna kullanıcının kendi ekleyebileceği bir yer yok. Eklemek isteyen
`prompt.py`'yi elle düzenliyor, yani deponun yazdığı metnin **içine** yazıyor — ve 190'ın okuma turu
oraya geldiğinde ikisi ayırt edilemiyor.

## Ne kurulacak

`prompt.py`'de ikinci bir sabit — `SYSTEM_PROMPT_SUFFIX` — ve bestecinin sistem mesajı
`SYSTEM_PROMPT`'un **arkasına** eklenerek kuruluyor.

### Boş doğuyor, ve içeriği bu maddenin işi değil

Sabiti madde boş bırakıyor. Ne yazılacağı kullanıcının kendi metni *(kullanıcı kararı, 8 Eylül)*, ve
o metin yazıldığı gün kod hiç değişmiyor.

### Boşken hiçbir şey değişmiyor

Boş bir son ek isteğe ne satır ne boşluk ekliyor: giden mesaj bugünküyle **bayt bayt aynı**. Sebebi
temizlik değil — sistem promptu servisin sabit önek olarak sakladığı baş *(`LAST_ROUND`'un kendi
yorumu bunu anlatıyor)*, ve fazladan bir boş satır o öneki daha ilk günden kaydırırdı.

### Nöbetçinin bunu bilmesi gerekiyor

`test_the_prompt_module_holds_the_texts_the_others_gave_up` listelediği her adın **dolu** olmasını
istiyor. Bu sabit o listeye girmiyor: girerse madde kendi testini kırmızı doğurur. Bunun yerine
sabitin **var olduğu** ve boş olmasına izin verildiği ayrı bir testte yazılı.

### Yalnız besteci

Kareyi yazan modelin sistem metni `write_once`'ın kendi parametresi *(Madde 175)* ve ona
dokunulmuyor — orası araçların değil, tek cümlelik bir işin metni.

## Testler

### `test_prompt.py`

1. **sabit var, ve boş olabilir** — `hasattr`, ve boş bir metin bu maddenin doğru doğuşu.
2. **nöbetçinin dolu olmalı listesinde değil** — o testin kendi listesi okunur; bu ad orada geçmez.

### `test_xai_engine.py`

3. **dolu bir son ek sistem mesajının sonunda durur** — mesaj `SYSTEM_PROMPT` ile başlar ve son ekle
   biter.
4. **boş bir son ek hiçbir şey eklemez** — mesaj `SYSTEM_PROMPT`'un **tam olarak kendisi**, sonunda
   ne satır ne boşluk.
5. **son ek yalnız sistem mesajına girer** — konuşmanın mesajları kımıldamaz.
6. **kareyi yazan modelin metnine karışmaz** — `write_once`'a verilen sistem metni ne ise o gider.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent` arka ucunda **5 kırmızı** —
`SYSTEM_PROMPT_SUFFIX` diye bir ad yok, ve `_for_xai` sistem mesajını tek parçadan kuruyor.

**Altıncısı doğduğu anda yeşil, ve bilerek öyle:** *"bu ad dolu olmalı listesinde değil"* bir
kırmızı değil, bir **nöbetçi** — bugün doğru olan bir şeyin yarın bozulmasını bekliyor. Kırmızı
veremez, çünkü listeye eklenmemiş bir ad zaten listede değil. Yazılma sebebi, listeye eklendiği gün
düşecek olması.

Ön yüz ve `queen-editor` kımıldamıyor: **634 · 739 · 591** yerinde.
