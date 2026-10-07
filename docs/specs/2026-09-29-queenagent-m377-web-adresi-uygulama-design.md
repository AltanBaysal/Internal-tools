# Madde 377 — bağlantı testi internet adresini dosya saymaz · uygulama turu

**Kaynak:** [yol haritasının 377'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-29-queenagent-m377-web-adresi-testler-design.md); kırmızı
`11029a5d`.

**Kurallar:** queen-editor'ün [FOUNDATION.md](../../queen-editor/FOUNDATION.md)'si ve
[CODE-STANDARD.md](../../queen-editor/CODE-STANDARD.md)'si. Değişen yalnız bir test dosyası;
uygulama kodu, ön uç ve `dist` değişmez.

## Ne yazılır

**`queen-editor/backend/tests/test_version_record.py`'ye bir yardımcı: `_local_links(text)`.**
Bir metindeki `.md` ile biten bağlantıları, çapaları (`#…`) düşmüş olarak, bir küme hâlinde verir;
`://` taşıyan bağlantıyı vermez.

- **Düzenli ifade bugünkünün aynısı:** `test_a_roadmap_can_still_reach_everything_it_links_to`'nun
  kendi içinde yazdığı ifade yardımcıya taşınır. Çapanın düşmesi ve yerel bağlantıların okunuşu
  değişmez, yalnız internet adresi ayıklanır.
- **Ayıklama `"://"` ile:** `https://`, `http://` ya da başka bir şema, hepsi diskte aranacak bir
  dosya değil. Yerel bir yol `://` taşımaz. İfadeye bir ileri bakış eklemek aynı işi okunması daha
  zor bir biçimde yapardı.
- **Yeri öteki yardımcıların yanı:** `_markdown()`'un hemen altı, dosyanın `_`'li yardımcılarıyla bir
  arada.

**`test_a_roadmap_can_still_reach_everything_it_links_to` yardımcıya bağlanır:** kendi `re.findall`'ı
yerine `_local_links(_read(path))`. Geri kalanı — bağlantıyı roadmap'lerin klasöründen çözmek,
kırığı dosya adıyla toplamak, Türkçe hata cümlesi — olduğu gibi kalır. Kırık bir yerel bağlantı yine
kırmızı verir.

## Yazılmayanlar

- **`test_every_link_to_a_roadmap_resolves_from_where_it_is_written`'e dokunulmaz:** yalnız
  `-roadmap.md` ile biten bağlantılara bakıyor, ve bugün yeşil.
- **Bağlantının var olup olmadığı internette denetlenmez:** testin sorusu klasör taşımanın yerel
  yolları bozup bozmadığı; ağa çıkan bir test de kurala aykırı olurdu.
- **Başka bir düzenli ifade yardımcıya taşınmaz:** öteki testler başka sorular soruyor, ve madde
  yalnız bunu istiyor.

## Nasıl görülür

CLAUDE.md'deki dört satır. `python -m pytest queen-editor -q` yeşile döner: 1160 test, kırmızı yok.
Öteki üç süit yeşil kalır.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m377-web-adresi-uygulama-plan.md).
