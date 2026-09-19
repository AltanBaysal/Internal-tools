# Madde 210 · QueenAgent'ın dalları — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-13-queen-editor-m210-queenagent-dallari-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı `5664ecb`'de duruyor. Bu tur belgeleri düzeltir; teste dokunulmaz.

## Adımlar

**1 · v2'nin başı yeniden yazılır.** Belge başlığı `(KAPANDI)` alır; başlık bloğu `**Branch:**
`fix/mira`` ile 15–18 Ağustos aralığını ve `**Sonrası:** v4`'ü verir *(v3 diye bir belge kalmıyor)*.
Ardından birleşmeyi anlatan `>` notu: iki koşu tek dal, ve **v3 numarası boş kalıyor** — sebebi dal
adlarının numara taşıması. Sonra `---`.

**2 · Eski gövde Koşu 1 olur.** Var olan metnin başına
`# Koşu 1 — 15 Ağustos *(o zamanki adıyla "v2")*` giriyor. Gövdenin kendisine dokunulmuyor; `##`/`###`
zaten `#`'in altına giriyor.

**3 · v3'ün gövdesi Koşu 2 olarak eklenir.** `2026-08-18-queen-agent-v3-roadmap.md` okunur, `# QueenAgent
v3 Yol Haritası` satırı `# Koşu 2 — 18 Ağustos *(o zamanki adıyla "v3")*` olur, gerisi olduğu gibi
v2'nin sonuna iner.

**4 · v3 dosyası silinir** — `git rm`.

**5 · Yirmi iki atıf çevrilir.** İki harfi harfine değişim, 22 dosyada:

| Eski | Yeni |
|---|---|
| `../roadmaps/2026-08-18-queen-agent-v3-roadmap.md` | `../roadmaps/2026-08-15-queen-agent-v2-roadmap.md` |
| `[v3 yol haritası Madde ` | `[v2 yol haritası Koşu 2 · Madde ` |

Metin de değişiyor çünkü *"v3 yol haritası"* diye bir belge kalmıyor; yalnız yolu çevirmek bağlantıyı
çözer ama cümleyi yalan yapar.

**6 · v8'in dal satırı yazılır** — `**Dal:** `feat/queenagent-v8``, merge commit'i `356d605` ile.

**7 · v7'nin ikinci dalı yazılır** — başlık satırının **sonuna** `feat/queenagent-v7.5`, 180–182
notuyla. Sonuna, çünkü çivi satırdaki ilk dalı belgenin dalı sayıyor.

**8 · v4'ün numara cümlesi** *"Numaralar v3'ten devam eder (52'de bitti)"* Koşu 2'yi gösterir.

**9 · Takım koşulur**, dördü de:

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

İki kırmızı yeşile döner. Bağlantı çivileri de bu adımda konuşur: v3'e kalan tek bir atıf varsa
`test_every_link_to_a_roadmap_resolves_from_where_it_is_written` söyler.

**10 · Yeşil commit'lenir.**

## Değişen dosyalar

`docs/superpowers/roadmaps/` altında dört belge *(v2 birleşir, v3 silinir, v7 ve v8 dalını yazar,
v4'ün bir cümlesi)* ve onlara bağlanan 22 spec/plan. Kod ve test değişmiyor; `dist` de değişmiyor,
çünkü ön yüze dokunan bir şey yok.
