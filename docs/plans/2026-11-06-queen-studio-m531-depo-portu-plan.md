# Madde 531 · Depo portu ve bellek içi adaptör — plan

[Tasarım](../specs/2026-11-06-queen-studio-m531-depo-portu-design.md). Her adım önce düşen bir testle.

1. **Bağımlılık yok.** Yalnız standart kütüphane: `json`, `hashlib`, `threading`, `tempfile`.
2. **Saat.** `tests/clock/test_clock.py` → `core/clock/clock.py` (`Clock`, `ManualClock`).
3. **Port.** `tests/storage/test_port.py` (`check_project`, `check_time`, `check_count`; port'un
   işlemleri `Op`'la aynı küme, kalıcı silme yok; `core/storage/` dışındaki modüller yalnız
   `core.storage.port`'u alır) → `core/storage/port.py` (`Row`, `Listed`, `Record`, `Entry`,
   `Commit`, `Project`, `Stored`, `Space`, `InProject`, `InExport`, `Place`, hatalar, `Port`,
   `Op`, `WRITES`, `MOST_RESERVED`, `MOST_ENTRIES`, bakışlar).
4. **Sözleşme.** `tests/storage/contract.py` (`Rig`, `PortContract`); `tests/storage/test_memory.py`'de
   `TestMemoryContract` → `core/storage/memory.py` (`MemoryStore`, `MemoryPort`; projeler, sonra
   dosyalar).
5. **Bellek içi adaptörün kendisi.** `tests/storage/test_memory.py`: hatalar (`Refuse`, `Drop`,
   `Slow`, `Run`, `between`), `times`, core başına hatalar, geçersiz enjeksiyon, `calls`, JSON,
   bekçiler, kota ve `space`, çöpün hemen olması, `NewerFormat` → `core/storage/faults.py`
   (`Refuse`, `Drop`, `Slow`, `Run`, `Faults`, `Due`; `memory.py` 548 satıra varınca ayrıldı: bir
   core'un hataları ve sayılan çağrıları ayrı bir iştir), `memory.py`'nin bekçileri ve kotası.
6. **Kontrol.** ruff, pyright; `write_openapi.py` (belge değişmemeli); iki suite, sırayla.
7. **Review'un bulguları.** Önce testler: `contract.py` (export'un `photos/` klasörü; `exists`'in
   `Stored`'u; bu portun vermediği sürüm; `format` ile yeni ve eski biçim; `seq` sözleşmeye taşındı;
   `put`/`copy`'nin biçimsiz `InProject`'i; dosya ya da klasör adresine `create` `Taken`; sığmayan
   satır), `test_memory.py` (`skip`, `project`, sürdürenler önce; çağrıların dosya projesi; kotanın
   değişmesi; içteki klasörün çöpü; çöpe giden projenin sürümü) → `port.py` (`Commit.format`,
   `Project.format`, `load`'ın `format`'ı, `exists -> Stored | None`, `export_folder`'ın `inside`'ı,
   `MOST_NAME`, `check_row`, `check_entries`), `faults.py` (`skip`, `project`, sıra), `memory.py`
   (verilen sürümler, biçim, alt klasör, `Taken`, `_project_at`, `quota` ayarı, `spoil(p, said)`).
   CODE-STANDARD'ın kapı cümlesi; spec'in sapmaları ve Sonraki maddeler'i.
