# Madde 38 — Sessiz tur meşru · Test Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 38](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Kaynak:** [test bulguları, bulgu 4](../research/2026-08-18-queenagent-test-bulgulari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

Bu belge **yalnız testlerin** turuna aittir: hangi davranış çivileniyor, nereden bakılıyor. Kodun
nasıl değişeceği burada yazmıyor — uygulama turunun kendi belgesi var. Ayrılmasının sebebi kuralın
kendisi: birlikte yazılan test, kodun körlüklerini miras alır.

---

## 1 · Bulgu ve gerçek sebep

Kullanıcının gördüğü: "Generate prompts+" her kullanıldığında ekranda **"Couldn't get a response.
network error"**. Dosyalar diske yazılmış oluyor, üretim gerçekten çalışıyor — yanlış olan tek şey
kart.

Sebep tahmin değil, okunarak bulundu:

1. Model o turda hiç konuşmuyor, yalnız tool çağırıyor. `stream_answer` boyunca `said` boş kalıyor.
2. Tur sonunda [`stream_answer.py:90`](../../../queen-agent/backend/features/workspace/domain/usecases/stream_answer.py)
   `append_message(..., "".join(said), ...)` çağırıyor.
3. [`append_message.py:14`](../../../queen-agent/backend/features/workspace/domain/usecases/append_message.py)
   boş metni `EmptyMessage` ile reddediyor.
4. Bu çağrı `stream_answer`'ın `try` bloğunun **dışında**, yani `EngineFailed`'a çevrilmiyor; `_sse`
   de yalnız `EngineFailed` yakalıyor. İstisna üretecin dışına çıkıyor ve Flask akışı ortasından
   kopuyor.
5. Tarayıcı tarafında kopan akış `streamEvents`'in `reader.read()`'inde patlıyor, `useChat`'in
   `catch`'ine düşüyor ve **tarayıcının kendi cümlesi** karta yazılıyor: "network error".

Yani kart yalan söylüyor. Ağ sağlam; sunucu kendi kuralına takılıp bağlantıyı kopardı.

## 2 · Çivilenen kural

> **Bir cevap ya söylenmiş bir sözdür ya da yapılmış bir dosyadır.**

Bugünkü kural "bir mesajın metni olmalı" diyor. Bu kural **kullanıcının** mesajı için doğru: boş bir
mesaj gönderilemez, ve uçlar bunu 400 ile söylüyor. Modelin cevabı için aynı şey doğru değil —
model konuşmadan dosya üretmişse ortada bir cevap **vardır**, kullanıcı onu dosya kartı olarak
görür.

Kuralın sınırı da çiviliyor: ne söz ne dosya varsa ortada cevap **yoktur**. O zaman da bağlantı
kopmaz; olan biten akışın içinde, kendi cümlesiyle söylenir. Bu, "hata mesajında sebep uydurma"
kuralının gereği: uyduran taraf bugün ağ hatası diyen taraftır.

## 3 · Testler ne çiviliyor

**Kullanım durumu düzeyi** (`backend/tests/test_stream_answer.py`):

| # | Durum | Beklenen |
|---|---|---|
| 1 | Model konuşmadan `create_file` çağırır, sonraki turda da susar | Üretecin son parçası `Chat`; istisna yok |
| 2 | Aynı durum | Kaydedilen cevabın metni boş, `files` üretilen dosyayı taşır |
| 3 | Aynı durum | Sohbette hâlâ iki mesaj var — soru ve cevap; tool trafiği yazılmamış |
| 4 | Model konuşmadan yalnız `read_file` çağırır, dosya doğmaz | `EmptyMessage` — cevap yoktur |
| 5 | Tur limiti sessizce dolar, hiç dosya doğmaz | `EmptyMessage` — aynı kural, farklı yol |

**Uç düzeyi** (`backend/tests/test_chats_api.py`):

| # | Durum | Beklenen |
|---|---|---|
| 6 | Sessiz ama dosya üreten tur | Gövdede `event: file` ve `event: done` var, `event: error` **yok** |
| 7 | Aynı tur | Sunucunun yazdığı kayıtta cevap duruyor ve dosyayı hatırlıyor |
| 8 | Ne söz ne dosya üreten tur | Gövdede `event: error` var ve akış düzgün biter — kopmaz |
| 9 | Aynı tur | Sohbete hiçbir şey yazılmamış: yarım cevap saklanmaz |

8. maddedeki cümle **"The model returned nothing."** — olanı söylüyor, sebep uydurmuyor. Arayüz
dili İngilizce olduğu için cümle de İngilizce.

## 4 · Testlerin bakmadığı yer

Testler `append_message`'ın kuralı **nasıl** gevşettiğine bakmıyor; oradan bakmak, uygulamayı
testin içine yazmak olurdu. Bakılan yer davranışın göründüğü yer: kullanım durumunun ürettiği
parçalar, diske yazılan sohbet, ve uçtan çıkan çerçeveler.

Ön yüz bu maddede sınanmıyor. `useChat` `error` çerçevesini zaten işliyor ve dosya olaylarını zaten
biliyor; arka uç akışı düzgün kapattığı anda bugünkü kart kendiliğinden doğru olanı gösterir. Boş
metinli bir cevabın ekranda nasıl durduğu ayrı bir sorudur ve bu maddenin konusu değil.

## 5 · Testler için gereken sahne

`ScriptedEngine` bugün her turu bir parça listesi olarak veriyor; sessiz bir tur zaten
`[{"tool_calls": [...]}]` ve ardından `[]` ile kurulabiliyor — **yeni bir sahte gerekmiyor**.

Uç düzeyinde `FakeEngine` tek bir metin parçası veriyor ve tool çağıramıyor. Sessiz turu uçtan
görebilmek için orada betiklenebilir bir motor gerekiyor; bu, testin kendi malzemesi olduğu için
test turuna dahildir.

## 6 · Kabul ölçütü — kırmızının doğru olması

Bu turun çıktısı **yeşil değil, doğru kırmızıdır**. Takım koşulduğunda:

1. 1, 2, 3, 6, 7 numaralı testler **düşer** — sebep `EmptyMessage`, başka bir şey değil.
2. 8 ve 9 numaralı testler **düşer** — bugün istisna üretecin dışına çıkıyor, akışta `error`
   çerçevesi doğmuyor.
3. 4 ve 5 numaralı testler **geçer** — bugünkü davranış zaten bu; onlar kuralın sınırını, sonraki
   turda yanlışlıkla silinmesin diye tutuyor.
4. `skip` ya da `xfail` yok. Kırmızı, kırmızı olarak commitlenir.
5. Başka hiçbir test düşmez: kod bu turda değişmiyor.

## 7 · Risk

4 ve 5 numaralı testler bugün de geçtiği için bu turda bir şey kanıtlamıyorlar; değerleri sonraki
turda, kural gevşetilirken fazla gevşetilmediğini göstermekte. Belgeye yazılmasının sebebi bu —
yoksa "neden yeşil bir test ekledin" sorusu haklı olurdu.
