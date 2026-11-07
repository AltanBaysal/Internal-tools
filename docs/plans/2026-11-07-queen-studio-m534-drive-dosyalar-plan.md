# Madde 534 · Drive adaptörü: dosyalar — plan

[Tasarım](../specs/2026-11-07-queen-studio-m534-drive-dosyalar-design.md). Her adım önce düşen bir testle.

1. **Sınırlar.** `core/storage/drive/limits.py`'ye `simple_most` (5 MiB), `chunk` (16 MiB),
   `keep_free` (1 GiB).
2. **Drive API'nin kapısı.** `core/storage/drive/api.py`'ye altı çağrı: `stream`, `copy`, `about`,
   `upload_start`, `upload_chunk`, `upload_status`. `tests/storage/drive/fake.py` onları taklit eder:
   oturumlar, parça sırası, oturumun son baytta dosya oluşturması, kopyanın kimlik kuralları, kota.
3. **Parçanın beklemesi.** `tests/storage/drive/test_retry.py` → `core/storage/drive/retry.py`'ye
   `resumed`.
4. **Bayt.** `tests/storage/drive/test_transfer.py` → `core/storage/drive/transfer.py`: `upload` (tek
   istek ya da parça parça, kopunca durum sorusu, onaylanan baytlardan md5), `download` (geçici
   dosya, akarak, md5 ve boy, `os.replace`), `hashed`.
5. **Yerler.** `core/storage/drive/places.py` (`Places`): `media/` ve `exports/` adıyla, yoksa havuzdan
   kimlikle ve yeniden listeleyerek; `<p>/`'nin ilk dosyada açılışı; Drive'ın almadığı kimlikte yeni
   klasör ve yalnız `folder` etiketi.
6. **İşlemler.** `tests/storage/drive/rigs.py`'deki `FILES_V1_9` listesi ve atlayan fixture silinir;
   `tests/storage/drive/test_files.py` (çağrı sayıları tam eşitlikle, tekrarlar, yerler, sınırlar) →
   `core/storage/drive/files.py` (`Files`); `adapter.py`'de `DrivePort` kökü tutar, `Files`'ı kurar ve
   dosya işlemlerini ona devreder, `NotImplementedError`'lar ve `_FILES` gider.
7. **Gerçek kütüphane.** `tests/storage/drive/test_google.py` (parçanın ve indirmenin zaman aşımı yerel
   sokete, `upload_id`'nin ayıklanması, `Range` cevabı, Range'e uymayan yerel sunucu) →
   `core/storage/drive/google.py`: `copy`, `about` Drive'ın kütüphanesiyle; `stream` ve yükleme
   oturumu google-auth'un `AuthorizedSession`'ıyla, iş parçacığı başına bir oturum, `transfer` zaman
   aşımıyla; Drive'ın hata gövdesinin çevirisi iki yolun ortağı.
8. **Gerçek Drive.** `tests/storage/drive/test_real.py`: klasör adı `queen-studio-534-<rastgele>`;
   sözleşmenin dosya testleri ve 256 KiB parçalı yükleme denemesi; `QUEEN_STUDIO_DRIVE_TOKEN` ile bir
   kez bu makineden, klasör sonunda çöpe. Sonuçlar spec'in Gerçek Drive bölümüne.
9. **Kontrol.** ruff, pyright; `write_openapi.py` (belge değişmemeli); queen-studio'nun iki suite'i,
   sırayla, bir kez.
10. **Review'un ve ilk gerçek koşunun bulguları.** Önce testler (`test_retry.py`: son parçada `409`
    `Conflict`; `test_files.py`: üst üste binen yükleme, koşan `commit`'i bekleyen yeniden adlandırma,
    projeler arası kilit; `test_transfer.py`: büyüyen kaynak, ilerlemeyen turda tek bekleme;
    `test_google.py`: hata gövdesinde oturum, cevabın bayt sınırı, yönlendirilen indirme;
    `test_adapter.py`: adı başına bütün klasörler; `contract.py`: çöpteki dosyanın `ref`'ine `put`)
    → `resumed`'da `Conflict`; `<p>/`'nin yeniden adlandırılması `Writer.rename_folder`'a, projenin
    kilidinde; `writes.py`'ye `folder_named`, `folder_listed`, `listed`; proje başına `Places` kilidi;
    `check_ref` `head.py`'ye; `PIECE` tek sabit; bellek içi adaptörde çöpteki `ref` `Taken`.
    `test_real.py`: sarmalayıcının anahtar kelimeleri, çocukları önce çöpe atan son temizlik,
    yoklamalar; `tmp/m534-diag/diag.py` reddedilen klasörün teşhisi. Gerçek Drive'ı ana agent koşar.
11. **İkinci gerçek koşunun bulguları.** Taklit API gerçek Drive gibi: hiç açılmamış klasör boş
    listelenir, resumable oturumda kullanılmış kimlik son parçada reddedilir (`fake.py`); testler
    (`test_files.py`, `test_transfer.py`) → `Places` boş listede `<p>/`'yi açar, büyük `put` önce
    `ref`'e bakar (`files.py`). `test_real.py`: her test kendi klasöründe, çöpün sonucu
    `tmp/m534-real/trash.json`'a; dizi yoklamaları; yoklamaların bulduğu doğrulanır. Spec'in tablosu,
    Ne bozulabilir'i ve Gerçek Drive bölümü.
