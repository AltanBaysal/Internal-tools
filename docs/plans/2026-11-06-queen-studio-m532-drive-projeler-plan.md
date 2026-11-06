# Madde 532 · Drive adaptörü: projeler ve kayıtlar — plan

[Tasarım](../specs/2026-11-06-queen-studio-m532-drive-projeler-design.md). Her adım önce düşen bir testle.

1. **Paketler.** `queen-studio/requirements.txt`: Drive'ın resmi kütüphanesi ve bağımlılıkları,
   `.venv`'deki sürümleriyle (ölçümler bunlarla koştu); yeni kurulum yok.
2. **Saat.** `tests/clock/test_clock.py` → `core/clock/clock.py`'ye `SystemClock`.
3. **Disk önbelleği.** `tests/disk/test_cache.py` → `core/disk/cache.py` (`DiskCache`).
4. **Bekleme.** `tests/storage/drive/test_retry.py` → `core/storage/drive/retry.py` (`Backoff`,
   `retryable`, `refusal`; adaptör 777 satıra varınca üç bekleyiş `read`, `again`, `written` de
   buraya taşındı).
5. **Drive API'nin kapısı.** `core/storage/drive/api.py` (`DriveApi`, `DriveError`, `DriveLost`,
   `Page`); `tests/storage/drive/fake.py` (`FakeDrive`).
6. **Biçim.** `core/storage/drive/limits.py` (`Limits`); `tests/storage/drive/test_head.py` →
   `core/storage/drive/head.py` (`Head`, `Block`, `Stream`, etiketler, `pack_head`, `read_head`,
   `read_lines`, `inflate`).
7. **Mühür.** `tests/storage/drive/test_seal.py` → `core/storage/drive/seal.py` (`due`, `reopens`,
   `seal`; sonra `plan` ve `Planned` adaptörden buraya).
8. **Adaptör.** `tests/storage/drive/rigs.py`, `test_contract.py` (sözleşme, dosya testleri
   "files: v1-9") ve `test_adapter.py` (çağrı sayıları, mühür, yarışlar, bekleme, sınırlar) →
   `core/storage/drive/adapter.py` (`DrivePort`), `core/storage/drive/kept.py` (`Kept`).
9. **Gerçek kütüphane.** `tests/storage/drive/test_google.py` (`q` kaçışı, hata çevirisi, zaman aşımı
   yerel sokete) → `core/storage/drive/google.py` (`GoogleDrive`).
10. **Gerçek Drive.** `tests/storage/drive/test_real.py`, `QUEEN_STUDIO_DRIVE_TOKEN` ile bir kez bu
    makineden; klasörünü çöpe atar.
11. **Kontrol.** ruff, pyright; `write_openapi.py` (belge değişmemeli); iki suite, sırayla.
12. **Review'un bulguları.** Önce testler (`test_seal.py`, `test_head.py`, `test_adapter.py`,
    `test_cache.py`, taklit API'nin `createdTime`'ı, bilinmeyen üst klasörde `404`'ü, `expire()`'ı) →
    her mühür taze kimlikte yeni blok, `retired` ve bir saat sonra çöp, mühürde süpürme (`seal.py`,
    `blocks.py`); `next` ve satır öneki kaldırıldı (`head.py`); proje başına kilit, `404`'ün her yerde
    adlandırılması, artık alınmayan kimlik, açılışta yeniden listeleme, klasörü çöpe gidemeyen proje
    silmenin başarısı, `project_most`, `bases_bytes`, tek havuzlu indirme (`adapter.py`, `kept.py`,
    `limits.py`); kimlik havuzu `pool.py`'ye, bloklar `blocks.py`'ye; `DiskCache.put`'un boşaltmadan
    önceki bakışı; spec.
13. **İkinci review.** Önce testler (`test_adapter.py`: son tarih, beklemenin son tarihte bitmesi,
    çöpteki adlı bloğun geri alınması, başarısız değişikliğin yeni klasörü, tek `generateIds`;
    `test_seal.py`: iki yarılı plan) → `retry.written`'a son tarih, `Backoff`'a `until`; çöp ve
    süpürme baştan sonra, süpürmede geri alma (`blocks.py`); blokların `createdTime`'ı ve iki yarılı
    plan (`seal.py`: `sealed`, `finish`); değişikliğin yazmaları `commit.py`'ye, küçük yazmalar
    `writes.py`'ye; `PARSED` ve sınırlar (`limits.py`); `Pool.take`'te `404`; portun `close()`'u;
    spec.
