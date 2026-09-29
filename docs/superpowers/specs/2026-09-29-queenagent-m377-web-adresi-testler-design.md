# Madde 377 — bağlantı testi internet adresini dosya saymaz · test turu

**Kaynak:** [yol haritasının 377'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md). queen-editor'ün
koduna dokunur; madde QueenAgent v9'un koşusunda çıktı.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne kanıtlanacak

`queen-editor/backend/tests/test_version_record.py`'deki
`test_a_roadmap_can_still_reach_everything_it_links_to`, bir roadmap'in `.md` ile biten her
bağlantısını roadmap'in klasöründen çözüp diskte arıyor. v9 roadmap'i iki rehbere internet
adresiyle bağlanıyor, ve iki adres de `.md` ile bitiyor:

- `https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md`
- `https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md`

Diskte böyle bir dosya olamaz, ve queen-editor'ün arka uç süiti 28 Eylül'den beri kırmızı
*(`d9c2d6f5`)*. Testin sorusu *"klasörlerin taşınması bir roadmap'in kendi dosyalarına giden yolunu
bozdu mu"*; internet adresini hiçbir taşıma bozamaz.

## Testler ne tutar

**Yeni bir iddia:** bağlantıları toplayan tek bir yardımcı — `_local_links(text)` — bir metindeki
yerel `.md` bağlantılarını verir, internet adresini vermez. Hem `https://…/GUIDE.md` hem de
`../plans/x-plan.md#adim-2` taşıyan bir metinden yalnız `../plans/x-plan.md` döner: adres dışarıda
kalır, çapa (`#…`) düşer. Çapanın düşmesi bugünkü davranış, ve yardımcı onu korur.

**Mevcut test yerinde kalır:** kırık bir yerel bağlantıyı yine yakalar. Yardımcı, onun bugün kendi
içinde yazdığı düzenli ifadenin yerine geçer; uygulama turunda test ona bağlanır.

## Neden yardımcı üzerinden

Testin kendisi bütün roadmap'leri okuyor. Bir internet adresinin sayılmadığını ancak gerçek
roadmap'lere bakarak kanıtlamak, v9'un MiniMax bağlantılarına yaslanmak demek: onlar bir gün
silinirse iddia hiçbir şey kanıtlamadan yeşil kalır. Yardımcıya küçük bir metin vermek, iddiayı
roadmap'lerin bugünkü hâlinden bağımsız kılar.

## Bu turda yazılmayanlar

- **`_local_links` yazılmaz**, mevcut test de değişmez: ikisi uygulama turunda.
- **`test_every_link_to_a_roadmap_resolves_from_where_it_is_written`'e dokunulmaz:** yalnız
  `-roadmap.md` ile biten bağlantılara bakıyor, ve bugün kırmızı değil.

## Nasıl görülür

CLAUDE.md'deki dört satır. `python -m pytest queen-editor -q` iki kırmızı verir: yeni iddia
(`_local_links` henüz yok) ve eski kırmızı. Öteki üç süit yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m377-web-adresi-testler-plan.md).
