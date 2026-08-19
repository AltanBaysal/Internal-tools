# QueenAgent v3 Yol Haritası

**Tarih:** 2026-08-18 · **Branch:** `fix/mira`
**Kaynak:** [test bulguları](../research/2026-08-18-queenagent-test-bulgulari.md) — kullanıcının
elle turundan çıkan 14 bulgu; her bulgu bir madde. Numaralar v2'den devam eder.
**Örnek yapı:** [2026-08-18-ornek-yapi.json](../research/2026-08-18-ornek-yapi.json)

Sıranın mantığı: Madde 38 her becerinin turunu bitiren sahte hatayı öldürür; 39-40 yapıyı kurar,
yönergeler (41-44) o yapıya yazılır; gerisi bağımsız, sona. Kullanıcının toplu testi en sonda.

---

## Faz 1 — Motor ve yapı

### Madde 38 — Sessiz tur meşru *(bulgu 4)*

- **Ne çalışır:** model konuşmadan yalnız dosya üretirse bu bir cevaptır — boş metin `EmptyMessage`
  ile patlamaz, akış hatasız kapanır.
- **Nasıl görülür:** prompts+ turu "Couldn't get a response. network error" göstermeden biter.

### Madde 39 — Shot düşer, frame gelir *(bulgu 9)*

- **Ne çalışır:** JSON alanı `"frames"`, hata mesajları "frame 3: …", dosya eki `-frames`; beceri
  adları **Split into frames** ve **Verify prompts**. Yönerge metinlerinde geçen alan adı ve "shot"
  kelimesi de değişir. Eski `"shots"` alanı okunmaya devam eder.
- **Nasıl görülür:** menüde yeni adlar; eski dosyadan `build_prompts` hâlâ üretir.

### Madde 40 — Yapıya kıyafet giriyor *(bulgu 6)*

- **Ne çalışır:** üst seviye `outfits` haritası; karede karakter alanı harita olur
  (`{"aylin": ["gecelik"]}`), kıyafetsiz `[]`, eski liste hâli okunur. `build_prompts` kimlik +
  kıyafeti bitişik birleştirir; bilinmeyen ad isimli hata. Verify'a kıyafet kuralları: kıyafet
  etiketi `characters`'ta ya da `action`'da → ihlal. **Generate prompts+ ve Verify prompts
  yönergelerindeki yapı tarifi de bu maddede güncellenir** — yapı ile yönerge aynı anda değişir,
  arada çelişik bir hâl kalmaz.
- **Nasıl görülür:** örnek yapıdaki dört kare doğru promptları verir; kıyafeti map'te değiştir →
  bütün kareler döner.

---

## Faz 2 — Beceriler

### Madde 41 — Senaryo kısa ve madde madde *(bulgu 7)*

- **Ne çalışır:** senaryo ana hatlarıyla, **madde madde** yazılır ("10-15 cümle, akan metin" düşer);
  hem sohbete hem dosyaya, ad konudan türer (`bar-sahnesi.md`); sohbette düzeltilince dosya
  `edit_file` ile güncellenir.
- **Nasıl görülür:** senaryo iste → kısa maddeli metin + dosya; "şurayı değiştir" → ikisi de değişir.

### Madde 42 — Karakter dosyaya, sayı kullanıcıya *(bulgu 5)*

- **Ne çalışır:** kaç aday istendiği söylenmediyse model sorar; çıktı sohbete değil **dosyaya** —
  yapıdaki `characters` şekliyle JSON, adı karakterden (`aylin.json`). Yapıştırılan beğenilmiş
  prompt biçim örneği alınır; kareye ait olanlar (poz, mekân, kamera, kalite) ayıklanır.
- **Nasıl görülür:** "3 aday" → `aylin.json`'da üç girdi; sayı söylenmezse model soruyor.

### Madde 43 — Kare açıklaması 1-2 cümle *(bulgu 10)*

- **Ne çalışır:** Split into frames'te her kare **1-2 cümle**; sayı yönergeye açıkça yazılır.
- **Nasıl görülür:** kare listesinde uzun paragraf yok.

### Madde 44 — Kare listesi konuşulan dilde ve dosyada *(bulgu 11)*

- **Ne çalışır:** liste konuşulan dilde gelir (İngilizceye çeviriyi prompt üreten beceriler yapar;
  JSON ve `PROMPTS` İngilizce kalır); hem sohbete hem md'ye yazılır (`bar-sahnesi-frames.md`),
  düzeltmeler dosyaya işler.
- **Nasıl görülür:** Türkçe sohbette Türkçe kare listesi + dosyası; üretilen promptlar İngilizce.

---

## Faz 3 — Küçükler

### Madde 45 — Varsayılan model `grok-4.3` *(bulgu 12)*

- **Ne çalışır:** varsayılan `grok-4.5` → `grok-4.3`; kendi modelini seçmiş sohbetler etkilenmez.
- **Nasıl görülür:** yeni sohbetin düğmesi Grok 4.3 der.

### Madde 46 — `grok-4.5` menüden kalkar *(bulgu 13)*

- **Ne çalışır:** fiyatı `grok-4.6` ile aynı olduğu için listeden düşer; onu seçmiş eski sohbette
  düğme ham id'yi gösterir ve çalışır.
- **Nasıl görülür:** menüde altı satır kalır.

### Madde 47 — "project file" yazısı kalkar *(bulgu 1)*

- **Ne çalışır:** okuyucunun altındaki "· project file" ibaresi gider.
- **Nasıl görülür:** dosya açıkken alt satır sadeleşir.

### Madde 48 — Seçim menüyü kapatır *(bulgu 14)*

- **Ne çalışır:** model ya da beceri menüsünden satır seçince menü kendiliğinden kapanır.
- **Nasıl görülür:** seç → menü yok; ikinci tıklama gerekmez.

---

## Faz 4 — Arayüz

### Madde 49 — Rayda dosya silme *(bulgu 8)*

- **Ne çalışır:** sohbetin sağındaki dosya listesinde de satırın ×'i var — aynı onay kutusu, aynı
  çöp.
- **Nasıl görülür:** sohbetten çıkmadan `bar-shots-2.json` silinebiliyor.

### Madde 50 — Sağ kenar sürüklenerek ayarlanır *(bulgu 2)*

- **Ne çalışır:** dosya bölümü kenarından sürüklenerek yatayda genişler/daralır; kapanıp açılma
  kalır.
- **Nasıl görülür:** kenarı çek → genişlik değişir ve kalır.

### Madde 51 — Sol kenar kapanıp açılır *(bulgu 3)*

- **Ne çalışır:** proje kenar çubuğu sürüklenmez; tek düğmeyle sola toplanır, aynı düğmeyle açılır —
  claude.ai davranışı.
- **Nasıl görülür:** kapat → sohbet genişler; aç → çubuk geri gelir.

---

## Kapanış

Maddeler durmadan spec → plan → test → uygulama ile gider; kullanıcının toplu testi **en sonda**
(38-51 bitince, v2 Madde 35'in turu bu değişikliklerle birlikte koşulur).
