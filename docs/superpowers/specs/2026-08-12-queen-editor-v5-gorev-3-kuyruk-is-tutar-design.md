# Queen Editor v5 · Görev 3 — Kuyruk kare değil iş tutar

**Tarih:** 2026-08-12 · **Yol haritası:**
[v5 Görev 3](../plans/2026-08-12-queen-editor-v5-roadmap.md) · **Kapsadığı maddeler:** 33, 36 ·
**Katman:** yalnız arka uç

## Amaç

Kuyruk bugün tek tür iş biliyor: bir kare üretmek. Tasarım v3'te foto, video ve ses **aynı kuyrukta
akıyor** (madde 33) ve motor **tür tür bitiriyor**: önce bütün fotolar, sonra videolar, sonra sesler
(madde 36).

Bu görevin işi kuyruğun kendisi. Video ve ses üreten bir şey henüz yok; kuyruk onları taşıyabilir
hâle geliyor ve sırayı doğru kuruyor, böylece Blok 5 geldiğinde ikinci bir kart kod değil **veri**
olarak doğuyor.

Dışarıdan görünen davranış değişmiyor — bugün kuyrukta yalnız foto işi var, dolayısıyla "tür
sırası" tek türden ibaret.

## Kapsam

**İçinde:** plan kaydının iş türü taşıması; kuyruk borcunun (kare, tür) çiftiyle sorulması; tür
sırasının motorun kuralı olması; döngünün işi türüne göre üreticisine vermesi; sayaçların iş
üstünden okunması.

**Dışında:** video ve ses üreticilerinin kendisi (Blok 5-6); üretici eksikken beklemek (Görev 13);
kuyruk panelinin tür başına karta bölünmesi (Görev 9); her türlü ekran dokunuşu.

---

## 1 · Plan kaydı iş olur

Plan bugün kare tutuyor. Artık **iş** tutuyor ve her iş türünü söylüyor:

```
{"id": "P11_3", "type": "photo", "number": 11, "variant": 3, "prompt", "negative", "seed", "model"}
{"id": "P11_3", "type": "video"}
{"id": "P11_3", "type": "audio"}
```

- **`id` işin hedef karesidir**, yeni bir kimlik değil. Foto işi kareyi doğurur; video işi var olan
  bir kareye katman takar. İkisi de aynı kareyi işaret ettiği için aynı alan.
- **Bir iş, bir yuva.** Aynı kareye iki video işi girmez — Görev 1'in yuva kuralı bunu zaten
  yasaklıyor; kuyruk o kuralın üstünde çalışır.
- Video ve ses işinin prompt'u kayıtta durmaz: sırası gelince dil modeli yazar (Görev 16, 21).

**Geriye uyum:** `type` alanı olmayan plan kaydı **foto işidir** — bugün başka tür yok. Drive'daki
projeler elle dokunulmadan çalışır.

## 2 · Borç artık (kare, tür) çiftine sorulur

Görev 1'de kuyruk `statuses` (yalnız foto yuvası) okuyordu. Artık **`slots`** okuyor ve borç şu:

```
açık  = işin yuvasının hiç satırı yok  ·  ya da son satırı queued
kapalı = son satırı done | failed | removed | deleted
```

Kural aynı kural — yalnız sorulduğu yer kareden yuvaya indi. Foto işleri için cevap harfi harfine
bugünküyle aynı kalıyor, dolayısıyla v4'ün "silinen fotoğrafın karesi kuyruğa dönmez" nöbetçisi
yerinde duruyor.

## 3 · Tür sırası motorun kuralı

Motor sıradaki işi seçerken **önce türe, sonra plan sırasına** bakıyor:

```
photo  →  video  →  audio
```

Bir tür bitmeden sonrakine geçilmiyor: kuyrukta açık foto işi varken video işi seçilmiyor. Aynı tür
içinde bugünkü kural aynen duruyor — hiç sırası gelmemişler plan sırasında, yeniden sıraya alınanlar
(Tekrar dene) onların arkasında.

**Neden tür tür.** Tasarımın kararı bu (madde 36) ve gerekçesi üretimin kendisinde: her tür kendi
üreticisini yükler, türler arasında gidip gelmek her seferinde model yükleme demektir. Ayrıca video
işi fotoğrafını bekler — foto işleri önde bitince video sırası geldiğinde kaynağı hazırdır.

## 4 · Döngü işi türüne göre veriyor

Bugün döngü tek bir üreticiye soruyor. Artık **tür → üretici** eşlemesine bakıyor ve işi sahibine
veriyor. Bu görevde eşlemede yalnız foto var; video ve ses kendi bloklarında ekleniyor.

Bir işin türünün üreticisi yoksa koşu **durur** ve sebebini söyler — sessizce atlanmaz. Bugün böyle
bir durum oluşamaz (foto dışında iş doğuran bir yol yok); kural yine de baştan konuyor, çünkü
sessiz atlama kullanıcının istediği işi kaybetmek olur.

## 5 · Sayaçlar iş üstünden okunuyor

`total`, `done`, `failed` ve `failures` bugünkü anlamlarını koruyor, yalnız kare yerine **iş**
sayıyorlar. Arayüz bugün tek tür gördüğü için sayılar aynı çıkıyor; tür başına ayrışmaları Görev
9'un işi.

`failures` **dosya adı** döndürmeyi sürdürüyor — ekran kırmızı karelerini dosya adıyla işaretliyor.

## 6 · Testler

**Full TDD**, arka uç `pytest`.

**Plan kaydı**
- `type` alanı olmayan kayıt foto işi sayılır.
- Foto işi, video işi ve ses işi aynı planda yan yana durur.

**Tür sırası**
- Kuyrukta foto ve video işi birlikteyken önce foto seçilir.
- Bütün foto işleri kapanınca video işine geçilir; videolar bitince sese.
- Aynı tür içinde plan sırası korunur ve yeniden sıraya alınan iş arkada bekler.

**Borç**
- Yuvası `done` olan iş kuyrukta görünmez.
- Aynı karenin foto işi kapalıyken video işi açık olabilir.
- Silinen fotoğrafın işi kuyruğa geri dönmez *(v4 nöbetçisi)*.

**Döngü**
- Foto işi foto üreticisine gider.
- Üreticisi olmayan bir tür koşuyu durdurur ve sebebi cevapta okunur.

## 7 · Kabul kriteri

`pytest` yeşil ve şu iki cümle testlerle kanıtlanmış:

1. Karışık türde işler atıldığında motor türleri sırayla bitiriyor — foto işleri bitmeden videoya
   geçmiyor.
2. Bugünkü davranış hiç değişmiyor: yalnız foto işi olan bir kuyruk bugünküyle aynı sırada, aynı
   sayılarla akıyor.
