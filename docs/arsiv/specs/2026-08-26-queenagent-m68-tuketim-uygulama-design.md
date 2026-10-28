# Madde 68 — Token tüketimi okunur · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [test turu spec'i](2026-08-26-queenagent-m68-tuketim-testler-design.md) ·
**Testler:** `8892452` — arka uçta 10, ön yüzde 2 kırmızı.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder. Test yazılmaz.

---

## Sayının yolu

Beş durak, ve her birinde bir cümlelik iş var:

| Nerede | Ne yapıyor |
|---|---|
| `services/xai/client.py` | Karedeki sayıları görüyor ve **bizim kelimelerimize** çeviriyor |
| `domain/usecases/stream_answer.py` | Tur içinde en sonuncuyu tutuyor, turlar arasında topluyor |
| `domain/usecases/append_message.py` | Toplamı mesaja iliştiriyor |
| `data/file_chat_store.py` | Sıfır değilse diske yazıyor, yoksa sıfır okuyor |
| `presentation/routes.py` → `ChatScreen.jsx` | Her zaman gönderiyor; ekran tek sayıya indiriyor |

## İstemci: bir kare iki şey söyleyebilir

Bugünkü `_delta` bir kareden **tek bir şey** çıkarıyor — ya metin ya çağrı. Gerçek akışta sayılar
metinle aynı karede geliyor, yani tek şey yetmiyor. Fonksiyon üçe bölünüyor:

- `_parsed(raw)` — satırı kareye çeviriyor, ya da bitiş işareti, ya da hiçbir şey. Bozuk bir karenin
  bütün akışı düşürmemesi kuralı burada, olduğu gibi kalıyor.
- `_spoken(frame)` — `delta`'dan metin ya da çağrı. Bugünkü gövde, taşınmış hâli.
- `_spent(frame)` — `usage`'dan üç sayı, xAI'nin adlarından bizimkilere.

`stream` ikisini sırayla soruyor ve **önce söz, sonra sayı** veriyor: sayı sözün bedeli, ve bedel
sözden önce gelmiyor.

Bu bölme aynı zamanda dosyayı düzeltiyor — `_delta` bugün hem ayrıştırıyor hem yorumluyor, ve
ikinci bir okuyucu eklenince tek gövdede iki iş olduğu görünür hâle geliyor.

## Toplama kuralı

Tek cümle, iki yarısı var ve ikisi de gerekli:

> **Tur içinde en sonuncu geçerli, turlar arasında toplanır.**

Birinci yarı, servisin akış içinde artan bir toplam söylemesinden geliyor: her parça öncekini
kapsıyor, o yüzden toplamak faturayı gelen parça sayısıyla çarpardı. İkinci yarı, her turun ayrı bir
istek olmasından: on altı turluk bir cevapta sohbet on altı kez gönderiliyor, ve bu maddenin
görünür kılmak istediği büyüme tam olarak bu.

**Toplama, turun kesilip kesilmediğine bakmadan yapılır.** Kod bunu döngünün hemen ardında, durdurma
kontrolünden **önce** yapıyor — çünkü durdurulan turun girdisi de gönderilmiş ve ödenmiş.

## Diskte

`usage`, tamamen sıfır olmadıkça yazılıyor; okurken yoksa sıfır geliyor. `calls` ve `stopped` ile
aynı kural, aynı sebep: hiçbir eski kaydın dönüştürülmesi gerekmiyor.

Okuma `**` ile değil, üç alanı tek tek isteyerek yapılıyor. Diskteki bir dosya elle de düzeltilebilir
ve tanımadığı bir anahtar gören `**` `TypeError` atardı — depo, bilmediği bir alanı görmezden gelir.

## Ekranda

`ChatScreen`, cevabın en altına tek satır koyuyor: `13.2k tokens`. Sayı `sent + answered`.

- Bin ve üstü bir ondalıkla `k`'ya iniyor. Sayı "bu tur pahalı mıydı" sorusuna cevap veriyor ve o
  soruya dört anlamlı basamak yardım etmiyor.
- Sıfırsa satır hiç çizilmiyor. Ölçülmemiş bir cevabın altındaki boş satır, alınmamış bir ölçümü
  alınmış gibi gösterirdi.
- Görsel dil 66'nın tool call satırıyla aynı: mono, soluk, vurgusuz. Vurgu birincil eylemin, ve bu
  bir kayıt.

Kırılım ekrana çıkmıyor ama kayda giriyor *(kullanıcı kararı, 26 Ağustos)*. Madde 71 önbellek
payına bakarak yol seçecek; ekrana çıkmayan bir sayı saklanmazsa o soru cevapsız kalır.

## Port belgesi

`Engine.stream`'in üçüncü parça tipi `ports.py`'de yazılıyor — **şimdi**, çünkü artık doğru. Test
turunda kasten yazılmamıştı: koddan önce yazılan bir söz, belgeyi yalancı yapıyor.

## Kapsam dışı

Test turunun kapsam dışı listesi aynen geçerli. Ek olarak bu turda: `_delta`'nın bölünmesi dışında
istemcide düzeltme · sohbet listesinin özetine tüketim eklemek *(özet ne konuşulduğunu değil ne
zaman konuşulduğunu söylüyor)*.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Arka uçta 430, ön yüzde 489 — hepsi yeşil. `dist` **kaynağıyla aynı commit'te** derleniyor;
FOUNDATION'ın 3. kararı ve `test_dist_is_committed.py` bunu zaten zorluyor.
