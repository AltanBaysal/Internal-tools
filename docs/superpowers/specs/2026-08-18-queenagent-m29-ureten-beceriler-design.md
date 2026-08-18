# Madde 29 — Üreten üç beceri: senaryo, karakter, kareler · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 29](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** [beceriler tasarım kararları](../research/2026-08-18-queenagent-beceriler-tasarim-kararlari.md) §2, §2b, §5b, §9b
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 1 · İki iş birden

Bu maddede hem **mekanizma** hem de ilk **üç yönerge** doğuyor. Ayrılmadılar, çünkü mekanizma tek
başına sınanamaz: bir yönerge olmadan "talimat konuşmaya bir kez girdi" cümlesinin doğrulanacak bir
karşılığı yok.

Madde 27 seçimi kaydetmişti ve orada açıkça yazıyordu: *beceri seçili olmak cevabı değiştirmez*. Bu
madde o sınırı kaldırıyor.

---

## 2 · Talimat konuşmaya nasıl girer (§2b)

Anthropic'in kademeli açılımı okundu ve kullanıcı haklıydı: gövde her istekte sistem yönergesine
enjekte edilmiyor, **bir kez konuşmaya düşüyor**. QueenAgent'ın uyarlaması:

| Kural | Neden |
|---|---|
| Talimat, o beceriyle gönderilen **kullanıcı mesajının hemen önüne** `system` rolüyle konur | Model kuralı, uygulanacağı cümleden hemen önce görür |
| Aynı beceriyle art arda giden mesajlarda **tekrarlanmaz** | Aynı metni her turda yeniden göndermek konuşmayı böler ve şişirir |
| Beceri **değişirse** yenisi bir kez girer; bırakılıp geri dönülürse yine bir kez girer | Kural bağlamda ne kadar geride kalırsa o kadar zayıflar |
| Talimat **kayda yazılmaz** | Transkriptte yalnız kullanıcı ve model cümleleri durur (fark yok, kural aynı) |

Yürütme sırası mesajların kendi sırası: konuşma kurulurken **kullanıcı mesajları** takip edilir; bir
mesajın becerisi yürüyen beceriden farklıysa yürüyen beceri değişir ve yeni becerinin metni araya
girer. Model cevapları beceri taşımaz ve sırayı bozmaz — bozsaydı her cevap araya girip talimatı her
turda yeniden yazdırırdı.

**Tanınmayan kimlik hiçbir şey eklemez.** Diskte duran eski bir kayıt yeniden adlandırılmış bir
beceri taşıyabilir; o mesaj yönergesiz akar, çökmez.

Bir yan kazanç: önceki adımların kuralları bağlamda kaldığı için
`Create scenario → Split into shots → Generate prompts+` zinciri akarken model önceki adımın da ne
dediğini görüyor.

---

## 3 · Yönergelerin dili ve kipi

Metinler **İngilizce** (§9b: uygulamanın kuralı yönerge metinlerini de kapsar) ve hepsi
**"bu işi şöyle yaparsın"** kipinde yazılır, **"şunu yap"** kipinde değil. Sebebi mekanik: beceri
seçimi mesajdan sonra **seçili kalıyor** (§2b). Emir kipinde yazılmış bir talimat, kullanıcı
"teşekkürler" yazdığında bile bir üretim tetiklerdi. Ne yapılacağını kullanıcının mesajı söyler;
yönerge yalnız nasıl yapılacağını söyler.

**Senaryonun dili kullanıcının dilidir.** §9b senaryoya dil dayatmıyor; ama uygulamanın sistem
yönergesi "in English" diyor, yani susmak İngilizceyi dayatmak olurdu. Bu yüzden senaryo yönergesi
dili açıkça kullanıcıya bırakır. Üretilen promptlar ve yapı JSON'u bunun dışında — onlar zorunlu
İngilizce ve o kural Madde 30'un yönergelerinde duruyor.

---

## 4 · Üç yönerge

### 4.1 Create scenario → `scenario.md`

- Kısa örgü: **10-15 cümle**, düz nesir, baştan sona. Sayı yönergeye yazılır, dilek olarak değil.
- Kare listesinin alanına girmez: numaralı kare yok, kamera/ışık dili yok, sahne başlığı yok,
  uzun betimleme yok. Detay sonraki adımların işi.
- `create_file` ile `scenario.md` olarak diske iner — dosyaya inen tek üretici beceri budur.
- Dil kullanıcının dili.

### 4.2 Create character prompt → sohbet

- SDXL etiket dili: virgülle ayrılmış kısa öbekler, cümle değil.
- **Kareden kareye değişmeyen** ne varsa o girer: kim olduğu, saç, göz, yapı, kıyafet. Poz, mekân,
  kamera ve ruh hâli **girmez** — onlar karenin alanları (§4'ün alan ayrımı).
- Kalite/skor etiketi girmez: onu `build_prompts` bir kez ekler (§5.3).
- **İki üç aday** üretir ve aralarındaki farkı söyler. Kullanıcının deneme yapma hakkı buradan
  geliyor — belgedeki cümlesiyle: "ben direkt ilk oluşturulanı seçmeyebilirim."
- **Sohbette kalır.** Dosya yazmaz, yapı dosyasına da girmez. Hangi adayın tutulacağı ve adının ne
  olacağı kullanıcının ayrı bir cümlesidir.

### 4.3 Split into shots → sohbet

- Varsa senaryoyu `read_file` ile okur.
- Her kare **tek satır**, prompt dilinde: karede ne var, ne oluyor, hangi kameradan. Nesir değil.
- **Kare sayısı kullanıcıyla birlikte kararlaştırılır** (§11): model bir sayı önerir ve gerekçesini
  söyler, tek başına karar vermez.
- **Küçük partiler** (§5b): liste tek cevapta boca edilmez, birkaç kare hâlinde dökülür. Sebep iki
  yanlı — uzun tek üretimde kalite sona doğru düşer, ve kullanıcının aralarda düzelttirmesine yer
  açılır.
- **Sohbette kalır.** Dosya yazmaz.

---

## 5 · Katman denetimi

**Domain:** yeni `domain/skills.py` — kimlikten yönerge metnine. `prompt.py`'nin komşusu ve aynı
gerekçeyle domain'de: bir ürün davranışı, taşıma detayı değil. `domain/usecases/stream_answer.py`
konuşmayı kurarken talimatı araya koyar.

**Dokunulmayan:** `data/`, `presentation/`, ön uç. Yeni uç nokta yok, yeni ekran yok — beceri
kimliği Madde 27'de zaten uçtan uca akıyor.

**`prompt.py` değişmiyor.** Uygulamanın kendi sistem yönergesi her cevabın altında duruyor;
beceriler onun üstüne ek koyar, yerine geçmez.

---

## 6 · Kabul ölçütü

1. Bir beceriyle gönderilen mesajın **hemen önünde** o becerinin metni `system` rolüyle durur.
2. Aynı beceriyle giden ikinci mesajda metin **tekrarlanmaz**.
3. Beceri değişince yenisi bir kez girer; bırakılıp geri dönülünce yine bir kez girer.
4. Beceri seçilmemiş mesaj hiçbir şey eklemez.
5. Tanınmayan kimlik hiçbir şey eklemez ve çökmez.
6. Talimat **sohbet kaydına yazılmaz**; transkript kullanıcı ve model cümlelerinden ibaret kalır.
7. Senaryo yönergesi 10-15 cümleyi, `scenario.md`'yi ve kullanıcının dilini söyler.
8. Karakter ve kare yönergeleri **dosya yazmamayı** açıkça söyler.
9. Kare yönergesi hem **kullanıcıyla kararlaştırmayı** hem **küçük partileri** söyler.
10. Üç metnin hiçbiri emir kipinde bir üretim başlatmaz — hepsi "kullanıcı şunu isterse şöyle
    yaparsın" diye kurulur.

## 7 · Risk

Yönergelerin gerçekten çalıştığı ancak canlı modelde görülür; testler metnin **ne söylediğini** ve
konuşmanın **nereye konduğunu** sabitler, modelin ona uyduğunu değil. Uyum Madde 35'in elle turunda
görülecek. Bu, yönerge metinleri için kabul edilen bilinen sınır.
