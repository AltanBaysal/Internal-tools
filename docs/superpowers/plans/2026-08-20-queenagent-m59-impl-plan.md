# Madde 59 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-20-queenagent-m59-impl-design.md](../specs/2026-08-20-queenagent-m59-impl-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Tek dosya

`queen-agent/backend/services/store/store.py` — yalnız `write_text`.

```
full = self._full(rel)
os.makedirs(os.path.dirname(full), exist_ok=True)
temp = full + ".writing"
try:
    open(temp, "w", encoding="utf-8") ile yaz
    os.replace(temp, full)
except BaseException:
    temp'i sil (silme kendi patlarsa bastır)
    raise
```

Yorumlar **neden**i söyler: geçici dosya neden hedefin yanında (dosya sistemi geçilemez, Colab'da
kök Drive), neden temizleniyor (klasör arayüzde listeleniyor), neden `BaseException`
(`KeyboardInterrupt` de yarım dosya bırakır).

## Beklenen yeşil

1. `test_a_failed_write_leaves_the_old_file_alone` — hedefe hiç dokunulmadı.
2. `test_a_failed_write_leaves_nothing_behind` — zaten yeşildi, yeşil kalır.
3. `test_the_temporary_file_is_written_beside_its_target` — `os.replace` çağrılıyor ve iki yol aynı
   dizinde.

Toplam **361**.

## Kapanış denetimi

- `write_text`'in imzası ve `_full` çağrısı değişmedi; hiçbir çağıran dokunulmadı.
- `move` ve `remove` değişmedi.
- Takımın geri kalanı yeşil — özellikle `test_file_chat_store`, `test_file_project_store`,
  `test_files_api`: hepsi bu fonksiyonun üstünde duruyor.
