# Madde 309 — Composition root'un kendi testi

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `backend/main.py` import edilebilir olsun, ve import edilemediği gün bunu Colab değil
test takımı söylesin.

**Yaklaşım:** Test, notebook'un yaptığı şeyi yapıyor — `backend.main`'i import et, `app`'ine
`/api/health` sor, 200 bekle. İki video modeli dalında ayrı ayrı, çünkü `main.py` modelin üstünde
dallanıyor ve Colab **h3** koşuyor. Düzeltme, `_reference_files`'ın tanımını ilk kullanıldığı
satırın üstüne taşımak.

**Kaynak:** [Yol haritası v7, madde 309](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md)

## Her yere geçerli kurallar

- Testler **dört satırla** koşulur, [CLAUDE.md](../../../CLAUDE.md)'de yazıldığı gibi — parçalanmaz,
  süzülmez, tek dosyaya daraltılmaz.
- Takım **kodla** yeşile döner; `skip` ya da `xfail` ile değil.
- Test adları, yorumlar ve docstring'ler **İngilizce** *(CODE-STANDARD)*.
- `main.py` composition root'tur: somut sınıflar yalnız orada kurulur *(CODE-STANDARD)*. Bu madde
  o kuralı değiştirmiyor, yalnız dosyanın içindeki **sırayı** düzeltiyor.

---

## Görev 1: Test turu

**Dosyalar:**
- Oluştur: `queen-editor/backend/tests/test_composition_root.py`

**Neden yeni dosya:** var olan hiçbir test `backend.main`'i okumuyor. En yakını
`test_audio_engine_wiring.py`, ama o dosyaları metin olarak tarıyor — import etmiyor.

- [ ] **Adım 1: Testi yaz.** `backend.config`'i env değişkeniyle birlikte yeniden yükleyip
  `backend.main`'i taze import eden bir fixture; `QE_VIDEO_MODEL` boş ve `h3` için iki parametre;
  assert `/api/health` → 200. Fixture teardown'da env geri konur ve `config` yeniden yüklenir, yani
  sonraki testler gerçek ortamı okur.

- [ ] **Adım 2: Dört satırı koş.** Yeni testin **ikisi de** `NameError: name '_reference_files' is
  not defined` ile düşmeli. Başka bir test kıpırdamamalı.

- [ ] **Adım 3: Kırmızı commit.** Test dosyası + yol haritası satırı.

## Görev 2: İmplementasyon turu

**Dosyalar:**
- Değiştir: `queen-editor/backend/main.py`

- [ ] **Adım 1: Bloğu taşı.** `_clips`, `_reference_store`, `_reference_orders`, `_reference_files`
  ve onları anlatan yorum, `_photo_bp`'nin **üstüne** gider. Bağımlılıkları `_storage` ve
  `_photo_store` zaten yukarıda. `_references_bp` yerinde kalır.

- [ ] **Adım 2: Dört satırı koş.** Takım yeşil.

- [ ] **Adım 3: Yeşil commit**, ve yol haritasında 309 ✅ + *Durum: 18/18*.

## Bilinmeyen

`main.py`'ın 183'ten sonrası bugüne kadar hiç koşulmadı. Taşımadan sonra orada ikinci bir import
hatası çıkabilir. Tahmin edilmiyor: test koşulur, çıkarsa aynı maddede düzeltilir ve yazılır.
