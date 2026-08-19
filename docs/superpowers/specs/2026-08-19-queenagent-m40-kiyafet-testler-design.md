# Madde 40 — Yapıya kıyafet giriyor · Test Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 40](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Kaynak:** [test bulguları, bulgu 6](../research/2026-08-18-queenagent-test-bulgulari.md) ·
[örnek yapı](../research/2026-08-18-ornek-yapi.json)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

Bu belge **yalnız testlerin** turuna aittir.

---

## 1 · Çözülen problem

Aynı karakter farklı karelerde farklı kıyafette. Bugün iki yol var ve ikisi de bozuk:

- **Kıyafeti karaktere gömmek** — karakter tek bir kıyafete çakılır, ikinci bir kıyafet ikinci bir
  karakter girdisi doğurur ve kimlik ikiye ayrılır.
- **Kıyafeti action'a yazmak** — action her karede elle yazılıyor, yani kıyafet her karede yeniden
  yazılıyor. Tutarlılık ilk kopyada bozulur; yapının varlık sebebi tam da bu.

Karar: **kalıcı olan `characters`'ta, değişebilen `outfits`'te.** `outfits` üst seviyede,
`characters`'ın kardeşi — kıyafetler karakterler arasında ortak kullanılır, o yüzden giyene göre
değil **giysiye göre** adlandırılır.

## 2 · Şema

```json
"characters": { "aylin": "1girl, pale skin, long black hair" },
"outfits":    { "gecelik": "white nightgown", "gunluk": "black t-shirt" }
```

Karede karakter alanı **harita** olur — anahtar karakter, değer kıyafet listesi:

```json
"characters": { "aylin": ["gunluk", "atki"], "deniz": ["takim"] }
```

| Hâl | Anlamı |
|---|---|
| `{ "aylin": [] }` | Karakter var, kıyafet yok |
| `{}` | Karesiz kare — kimse yok |
| `["aylin"]` *(eski liste)* | Adlar, kıyafetsiz |
| `{ "aylin": "gunluk" }` | Tek kıyafet, listeye sarılmadan yazılmış |

## 3 · Birleştirme kuralı

Her karakterin bloğu **bitişik** kalır: kimlik, hemen ardından o karakterin kıyafetleri, yazıldıkları
sırayla. Sonra bir sonraki karakter.

```
quality, AYLIN, gunluk, atki, DENIZ, takim, location, action, camera
```

Bitişikliğin sebebi görüntü modelinin okuma biçimi: kimlikle kıyafeti araya başka bir karakter
girerek ayırmak, kıyafetin kime ait olduğunu belirsizleştirir.

## 4 · Testler ne çiviliyor

**`test_build_prompts.py`:**

| # | Durum | Beklenen |
|---|---|---|
| 1 | Tek karakter, tek kıyafet | `quality, kimlik, kıyafet, mekân, action, camera` |
| 2 | Bir karakterin iki kıyafeti | İkisi de kimliğin hemen ardında, yazıldıkları sırayla |
| 3 | İki karakter, ikisi de kıyafetli | Her bloğun bitişikliği korunur; ikinci kimlik ilk kıyafetlerden sonra gelir |
| 4 | `"aylin": []` | Kimlik var, kıyafet yok |
| 5 | `{}` | Karakter yok, kare yine üretilir |
| 6 | Eski liste hâli `["aylin"]` | Kimlik, kıyafetsiz |
| 7 | Değer liste değil dize (`"gunluk"`) | Tek kıyafet adı gibi okunur |
| 8 | Bilinmeyen kıyafet adı | `frame N: X is not in outfits; known: …` |
| 9 | Bilinmeyen karakter (harita hâlinde) | `frame N: X is not in characters; known: …` |
| 10 | Kıyafetsiz yapı (`outfits` hiç yok), eski dosya | Kırılmaz — kimlikler üretilir |

**`test_skills.py`:**

| # | Durum | Beklenen |
|---|---|---|
| 11 | Yapılandırılmış yönerge | Şemada `"outfits"` görünür; karede karakter alanının harita olduğu yazar |
| 12 | Yapılandırılmış yönerge | Kalıcı/değişebilen ayrımını söyler |
| 13 | `RULEBOOK` | Kıyafetin `characters` ya da `action` içine yazılmasını ihlal sayar |
| 14 | Karakter yönergesi | Kıyafeti kimliğin dışında tutar *(Madde 42'ye zemin değil — bugünkü cümle yapıyla çelişiyor)* |

14 numaralı test yol haritasının Madde 42'ye taşıdığı işin **bu maddeye düşen yarısı**: bugünkü
karakter yönergesi "what they are wearing" diyor ve Madde 40'ın yapısıyla açıkça çelişiyor. Çelişkiyi
bir sonraki maddeye bırakmak, arada yanlış çalışan bir ürün bırakmak olurdu.

## 5 · Testlerin bakmadığı yer

Karakter becerisinin kıyafeti **nasıl üreteceği** (dosyaya mı, kaç aday) Madde 42'nin işi. Burada
yalnız kimliğin kıyafet taşımadığı çiviliyor.

## 6 · Kabul ölçütü — kırmızının doğru olması

1. 1-5, 7-9, 11-14 **düşer**: harita hâli bugün hiç anlaşılmıyor, `outfits` diye bir şey yok.
2. 6 ve 10 **geçer**: eski liste hâli bugünkü tek hâl, ve `outfits`'siz yapı zaten bugünkü yapı.
3. `skip` yok, `xfail` yok.

## 7 · Risk

Eski liste hâlinin okunmaya devam etmesi, iki farklı şeklin aynı alanda yaşaması demek. Kod bunu tek
bir yerde çözer ve orada söyler; iki şeklin ikinci bir yere sızması bu maddenin asıl riski.
