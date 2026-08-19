# Madde 41 — Senaryo kısa ve madde madde · Uygulama Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 41](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Test turu:** [2026-08-19-queenagent-m41-senaryo-testler-design.md](2026-08-19-queenagent-m41-senaryo-testler-design.md) — kırmızı commit `9f946d3`
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 1 · Tek dosya değişiyor

`domain/skills.py`'daki `CREATE_SCENARIO`. Kod değişmiyor, çünkü değişen şey bir davranış değil bir
**yönerge**: `create_file` ve `edit_file` zaten var, adı modelin seçmesi zaten mümkün, dosyaya
yazmak zaten çalışıyor. Eksik olan tek şey, senaryonun bunları kullanmasının söylenmesi.

## 2 · Yeni metnin taşıdıkları

- **Ne olduğu:** kısa bir ana hat, madde madde. Sayı yok — "kısa" ve "ana hatlar" kuralın kendisi.
- **Neden kısa:** bu adım hikâyeyi yazmıyor, **ne anlaşıldığını gösteriyor**. Sebebi yazmak, kuralın
  kendisinden daha uzun ömürlü; sebebini bilen bir model sınırı da doğru çeker.
- **Nereye:** hem sohbete hem dosyaya. Dosya cevabın yerine geçmez.
- **Hangi adla:** konudan türeyen bir ad, örneğiyle (`bar-scene.md`). Sabit ad gitti.
- **Düzeltme:** sohbette düzeltilen şey `edit_file` ile dosyaya da işler — yoksa iki senaryo olur,
  biri ekranda biri diskte.

Kare listesinin alanına girmeme kuralı **duruyor**; Madde 39'da kelimesi güncellendi, içeriği değil.

## 3 · Kabul ölçütü

1. Test turunun altı testi de yeşil, başka hiçbir test düşmüyor.
2. İki komut da yeşil.
3. Elle: senaryo iste → kısa maddeli metin + konudan adını almış bir dosya; "şurayı değiştir" →
   ikisi de değişiyor.
