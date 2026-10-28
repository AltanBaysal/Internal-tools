# Madde 110 — Kalite etiketleri koddan gelir · Tur 2 (uygulama) tasarımı

**Test turu:** [testler tasarımı](2026-08-28-queenagent-m110-kalite-testler-design.md) — beş kırmızı
`705bce4`'te.

## Kod — `build_prompts.py`

Modülün başına tek sabit, `DEFAULT_QUALITY`: kullanıcının kendi çalışan promptunun kalite zinciri
*([araştırma belgesi §5c](../research/2026-08-18-queenagent-beceriler-tasarim-kararlari.md))*. Yanına
neden orada durduğunu söyleyen yorum — model ailesi değişirse burası değişir, dosyalar değişmez.

İki kullanım yeri de aynı satıra döner: `structure.get("quality") or DEFAULT_QUALITY`
*(`build_prompts` ve `build_character_prompts`)*. Boş yazılmış bir alan da yazılmamış sayılır —
`or` bunu zaten yapıyor, ve *"boşluk bırakan bir alan"* ile *"alan yok"* aynı niyettir.

## Metin — `schema.py`

- Örnekten `"quality"` satırı çıkar. Kalan alanlar aynı sırada.
- Kalite paragrafı: zincir bu dosyada değil, kod her promptun **başına** koyuyor; `quality` alanı
  yalnız bu senaryo başka bir zincir istiyorsa yazılır, ve yazılmışsa onun yerine o kullanılır.
- Kural defterinin 3. maddesi yerinde: kalite etiketlerini karenin kendi alanına yazmak hâlâ
  ihlal, ve gerekçesi şimdi daha da net — kod zaten ekliyor.

## Değişmeyen

Birleştirme sırası *(kalite en başta, bir kez — Madde 95)*, kalan yedi kural, ve `quality` yazan
eski dosyalar: onlar kendi zincirlerini taşımaya devam ediyor.

## Görülür hâli

Beş kırmızı yeşerir; başka test kırılmaz *(defter çifti hariç)*. Ön yüz değişmiyor, `dist`
derlenmez.
