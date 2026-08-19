# Madde 42 — Karakter dosyaya, sayı kullanıcıya · Uygulama Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 42](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Test turu:** [2026-08-19-queenagent-m42-karakter-testler-design.md](2026-08-19-queenagent-m42-karakter-testler-design.md) — kırmızı commit `e2742c2`
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 1 · Yine tek metin

`CREATE_CHARACTER_PROMPT`. Kod değişmiyor: `create_file` var, JSON yazmak sıradan bir dosya yazma
işi, ve modelin soru sorması zaten yapabildiği bir şey. Değişen, becerinin ne yapacağının
söylenmesi.

## 2 · Dosyanın şekli

Yapı dosyasının haritalarıyla **aynı**, çünkü varlık sebebi doğrudan yapıştırılabilmesi:

```json
{
  "characters": { "aylin": "1girl, pale skin, long black hair, green eyes" },
  "outfits": { "gunluk": "oversized black t-shirt, black thong" }
}
```

Birden çok aday istendiğinde adayların birbirinden ayrılması gerekiyor. Adları numaralanır
(`aylin-1`, `aylin-2`), ve aralarındaki farkın bir satırlık açıklaması sohbette söylenir — dosya
yapıştırılacak malzeme, açıklama ise seçimi yapacak kişiye ait.

## 3 · Kıyafet dosyada, kimlikte değil

Beceri kıyafeti üretmeye devam eder — kullanıcının istediği bu. Ama kıyafet `outfits` girdisi olur,
giysiye göre adlandırılır, ve kimliğin içine girmez. Madde 40 kuralı koydu; burası onu kullanan yer.

Kıyafet istenmemişse `outfits` hiç yazılmaz: boş bir harita, olmayan bir şeyi varmış gibi gösterir.

## 4 · Yapıştırılan prompt

Biçim örneği: etiket yoğunluğu, sıralama, dil oradan alınır. Kareye ait olanlar — poz, mekân,
kamera, kalite ve skor etiketleri — ayıklanır. Bu, kalite etiketlerini dışarıda tutma kuralının
zaten söylediği şeyin yapıştırma durumundaki hâli.

## 5 · Kabul ölçütü

1. Test turunun altı testi de yeşil, başka hiçbir test düşmüyor.
2. İki komut da yeşil.
3. Elle: "3 aday" → `aylin.json`'da üç kimlik girdisi; sayı söylenmezse model soruyor.
