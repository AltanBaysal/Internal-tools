# Madde 165 — `AT_ONCE` kalkar · **uygulama turu**

**Tarih:** 4 Eylül 2026 · **Branch:** `feat/v7` · **Kaynak:** [test turu
spec'i](2026-09-04-queenagent-m165-tek-dalga-testler-design.md) · **Yol haritası:** [Madde
165](../plans/2026-09-03-v7-roadmap.md)

Tek kırmızıyı yeşile çeviren kod.

## Değişen iki yer

- **`AT_ONCE = 5` gider**, ve onunla birlikte yanındaki yorumun ikinci yarısı: *"Five at once
  because a provider answers a full pool with a 429…"*. O cümle m149'un DeepInfra/OpenRouter
  denemesinin sonucuydu ve **o deneme geri alındı** — bugün ölçtüğü sağlayıcı bu uygulamada yok.
  CLAUDE.md'nin kuralı: bir yorum yalnız bugün doğru olanı söyler.
- **Havuz kare sayısına eşitlenir:** `ThreadPoolExecutor(max_workers=AT_ONCE)` →
  `ThreadPoolExecutor(max_workers=len(rest))`. `waiting[1:]` bir kez `rest` diye adlandırılır —
  aynı dilim üç yerde geçiyordu *(uzunluk, havuz, `map`)* ve üçünün aynı liste olduğu ancak
  okunarak anlaşılıyordu.

**`len(rest)` sıfır olamaz:** dal `if rest` ile korunuyor, ve `ThreadPoolExecutor(max_workers=0)`
`ValueError` atardı. Tavan da başıboş değil — `waiting` zaten `MOST_FRAMES_PER_CALL`'a kırpılmış,
yani en fazla 99 iplik.

## Bilerek yapılmayanlar

- **Yeniden deneme gelmiyor.** m155'in kararı. Boş kalan kare sayılıyor, cevapta yazıyor, ve araç
  yalnız boşu doldurduğu için yeniden çağırmak zaten yeniden denemek.
- **`AT_MOST` adını bu turda korur.** Adlandırma ayrı iş, ayrı iki tur.

## Doğrulama

1. `python -m pytest queen-agent -q` → **785 yeşil + defterin 2 kırmızısı.**
2. Dört sabit test satırı, sırayla, birebir.
3. `Grep` ile `AT_ONCE`: `queen-agent/` altında sıfır.
4. **Denemede bakılacak:** yüz istek birden gidince sağlayıcı 429 veriyor mu. Kod bunu ölçemez;
   ölçen şey gerçek bir dosya, ve cevabın *"N frames left empty"* satırı.
