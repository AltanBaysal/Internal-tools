# Madde 89 — Sohbetin şekli tek yerde kurulur · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5.5 yol haritası](../plans/2026-08-26-queenagent-v5-5-roadmap.md) — Madde 89 ·
**Üstüne geldiği:** [Madde 88](2026-08-26-queenagent-m88-cevabi-sunucu-baslatir-uygulama-design.md)
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder.

---

## Geriye ne kaldı

Yol haritası bu maddeyi yazdığında sohbetin JSON'unu **beş yer** üretiyordu: iki mesaj ucu, skill
ucu, okuma ucu ve akışın son karesi. Üçü zaten düştü — skill ucu 86'da, sohbet yaratan uç 87'de, ve
mesaj ucunun JSON gövdesi 88'de akışa dönüşünce.

Bugün **iki** kaldı: `get_chat` ve akışın `done` karesi. Bu madde ikinciyi kaldırıyor.

Yeni sohbetin id'sinin nasıl döneceği de 88'e devredilmişti ve orada çözüldü — akışın ilk karesi.
Yani 89'un işi tek cümleye indi: **`done` gövdesiz olur, ve tarayıcı kaydı okuma ucundan okur.**

## Neden

Kayda bir alan eklendiğinde bugün iki yer birden değişmek zorunda, ve ikisi ilk unutulduğunda
birbirinden ayrışıyor. Ayrıştığında da sessiz: akan gösterim ile okunan kayıt aynı ekranda farklı
şeyler söyler ve kimse hangisinin doğru olduğunu söylemez.

Tek yer kalınca ayrışacak ikinci bir şekil yok.

## Ne olur

`_sse`'nin son karesi `event: done` ve boş bir gövde. Akışın hiçbir karesi kaydı taşımaz.

Tarayıcı, akış **nasıl biterse bitsin** kaydı okur: cevap yazıldıysa da, hata karesiyle bittiyse de.
Hata hâlinde okunacak bir şey yine var — kullanıcının kendi cümlesi diske yazılmıştı, ve ekranda
kalması gerekiyor.

Hangi sohbetin okunacağını ilk kare söylüyor. Yeni doğan bir sohbette de bu yüzden çalışıyor: id
akışın başında geldi.

## Sıra önemli

Okuma, akan durumu temizlemeden **önce** biter. Tersi olursa ekran bir an boşalıyor: akan metin
silinmiş, kayıt henüz gelmemiş.

## Okuma düşerse

Ekran okunanı çizemiyor demektir, ve bunu söylemesi gerekiyor. Hata kartı okumanın **kendi
sözleriyle** yazar — sebep uydurulmaz. Cevabın kendisi diske yazılmıştı; kayıp olan gösterim.

## Bedeli

Her turdan sonra fazladan bir okuma isteği. Yerelde ihmal edilebilir, ve karşılığında kaydın şekli
tek yerde duruyor.

## Bir testin iddiası değişiyor

88'in `the draft streams its first answer and moves to the new address` testi *"akış sürerken adres
değişti ve hiçbir şey diske geri gitmedi"* diyor ve bunu `/chats/c1`'in **hiç** okunmamasıyla
kanıtlıyor. 89'dan sonra o okuma bir kere yapılıyor — turun sonunda.

İddia korunuyor, ölçüsü değişiyor: `/chats/c1` **tam bir kere** okunuyor. İki kere okunması,
yükleme efektinin akan cevabı silmek üzere devreye girdiği anlamına gelirdi, ki 88'in koyduğu bekçi
tam olarak onu engelliyor.

## Kırmızıya dönecek testler

**Arka uç — iki:**

1. `done` karesinin gövdesi boş.
2. Akışın hiçbir yerinde kayıt yok: gövdede `"messages"` diye bir şey geçmiyor.

**Ön yüz — dört:**

3. Tur bitince tarayıcı kaydı okuma ucundan okuyor ve orada yazanı çiziyor — akışın söylediğini
   değil.
4. Yeni doğan bir sohbet de aynı şekilde okunuyor; okunan id ilk kareden geliyor.
5. Hata karesiyle biten bir tur da okunuyor: kullanıcının cümlesi ekranda kalıyor.
6. O okuma düşerse ekran bunu okumanın kendi sözleriyle söylüyor.

Toplam **altı kırmızı**, ve 88'in bir testinin ölçüsü değişiyor.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `_chat_json` ve `_chat_summary` | Kalıyorlar; değişen yalnız kaç yerden çağrıldıkları |
| `get_chats` listesi | Satır şekli sohbet kaydı değil, ayrı bir şey |
| İlk kare | 88'in işi, yerinde |
| `stream_answer` | Ne ürettiği değişmiyor |
| `/stop` | 90'ın işi |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` bu turda derlenmiyor.
