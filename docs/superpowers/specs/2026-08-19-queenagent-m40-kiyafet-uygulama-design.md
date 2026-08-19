# Madde 40 — Yapıya kıyafet giriyor · Uygulama Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 40](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Test turu:** [2026-08-19-queenagent-m40-kiyafet-testler-design.md](2026-08-19-queenagent-m40-kiyafet-testler-design.md) — kırmızı commit `f66c20f`
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 1 · İki şekli tek yerde çözmek

Karedeki `characters` alanı iki şekil taşıyabiliyor: yeni harita, eski liste. Bu ikilik **tek bir
yerde** çözülür ve orada biter — küçük bir yardımcı, karenin alanını `(ad, kıyafet listesi)`
çiftlerine çevirir:

```
{"aylin": ["gunluk"]}   →  [("aylin", ["gunluk"])]
["aylin"]               →  [("aylin", [])]
{"aylin": "gunluk"}     →  [("aylin", ["gunluk"])]
{}  ·  []               →  []
```

Kırmızıda görüldüğü gibi harita hâlinin **kimlik** kısmı bugün zaten kazara çalışıyor: sözlük
üzerinde dönmek anahtarları veriyor. Buna güvenmek olmaz — kazayla doğru olan bir şey, ilk
değişiklikte sessizce yanlış olur. Yardımcı bunu bilerek yapar.

Dizeyi tek ad gibi okumak da bilerek: yönerge liste istiyor, ama tek adı listeye sarmadan yazan bir
model **tek ad** demek istiyordur, ve dizeyi harf harf gezmek anlamsız bir hatayla cevap verirdi.

## 2 · Bitişiklik

Her karakterin bloğu tek seferde yazılır: önce kimlik, sonra o karakterin kıyafetleri. Sonra bir
sonraki karakter. Görüntü modeli için kıyafetin kime ait olduğunu söyleyen tek şey bu komşuluk;
bütün kimlikleri önce, bütün kıyafetleri sonra yazmak bilgiyi kaybettirir.

## 3 · Kıyafet de aranır

Bilinmeyen kıyafet, bilinmeyen karakterle aynı cümleyi alır — aynı `_looked_up`, alan adı
`outfits`. Yeni bir hata biçimi icat etmeye gerek yok: kullanıcı zaten bu cümleyi tanıyor.

`outfits` haritası hiç yoksa boş harita gibi davranır. Kıyafetsiz eski dosyalar bu yüzden kırılmaz;
kıyafet **isteyen** bir kare varsa zaten isimli hata alır.

## 4 · Yönergeler aynı anda değişir

Yapı ile yönergeyi ayrı maddelere bölmek, arada yapıyı bilen ama yönergesi bilmeyen bir ürün
bırakırdı. Üçü birden burada değişir:

- **Generate prompts+** — şemaya `outfits` girer, karedeki `characters` harita olarak gösterilir,
  ve ayrımın sebebi bir cümleyle yazılır: kalıcı olan `characters`'ta, karelere göre değişen
  `outfits`'te.
- **RULEBOOK** — yeni kural: kıyafetin kimliğin içine ya da karenin `action`'ına yazılması. İkisi de
  aynı şeyin iki yüzü: adını vermek yerine metnini kopyalamak. Kural listesinin **ikinci sırasına**
  girer, çünkü birinci kuralın kardeşi; sonrakiler bir kayar ve kullanılmayan ad notu sonda kalır.
- **Create character prompt** — "what they are wearing" kimlikten düşer, yerine kıyafetin `outfits`
  girdisi olduğu yazılır. Bu cümle bugün Madde 40'ın yapısıyla açıkça çelişiyor; çelişkiyi Madde
  42'ye ertelemek, arada yanlış çalışan bir ürün bırakmak olurdu.

## 5 · Örnek yapı belgesi

[2026-08-18-ornek-yapi.json](../research/2026-08-18-ornek-yapi.json) listesini hâlâ `shots` altında
taşıyor — Madde 39'dan önce yazıldı. Şemanın gerçek olduğu madde burası olduğu için alan adı burada
`frames`'e çekilir. Belgenin geri kalanı (kıyafet kararı, örnek kareler) kullanıcının onayladığı
hâliyle durur.

## 6 · Değişen dosyalar

| Dosya | Ne |
|---|---|
| `domain/build_prompts.py` | `outfits` okunur; karedeki iki şekli çözen yardımcı; bitişik birleştirme |
| `domain/skills.py` | Şema, ayrım cümlesi, `RULEBOOK`'un yeni kuralı, karakter yönergesi |
| `docs/…/2026-08-18-ornek-yapi.json` | `shots` → `frames` |

Ön yüz değişmiyor: yapı dosyası ekranda ham JSON olarak görünüyor, ve yeni alanı çizmek için bir
şey yapmasına gerek yok.

## 7 · Kabul ölçütü

1. Test turunun on testi de yeşil, başka hiçbir test düşmüyor.
2. İki komut da yeşil.
3. Elle: örnek yapıdaki dört kare doğru promptları veriyor; `outfits`'te bir kıyafeti değiştirmek
   onu giyen bütün kareleri döndürüyor.
