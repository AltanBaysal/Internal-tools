# Madde 459 — `create_file`'ın tarifi, plan

> **Koşum:** ana klasörde, `feat/queenagent-v10` dalında, **commit'lenmeden** ve hiçbir şey stage
> edilmeden — modele giden metni ana agent okur ve commit'ler. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** `CREATE_FILE` plan dosyasını da sayar, system prompt'un Writing 1'i gibi.

**Yaklaşım:** önce test, kırmızı görülür, sonra metin. Dosyalar Edit ile değişir.

**Spec:** [m459](../specs/2026-10-10-queen-agent-m459-create-file-design.md)

## Görev 1: Test — `queen-agent/backend/tests/test_tools.py`

- [ ] `test_create_file_no_longer_offers_to_write_a_structure`'ın yanına
  `test_create_file_counts_the_plan_file`: `create_file`'ın tarifi `plan file` der, ve
  `only when the user asked` demez.
- [ ] `python -m pytest queen-agent/backend/tests/test_tools.py -q -k plan_file` — kırmızı.

## Görev 2: Metin — `queen-agent/backend/features/workspace/domain/prompt.py`

- [ ] `CREATE_FILE`'ın ikinci satırı: `- Call this for a plan file, or when the user asked for
  something worth keeping: a draft, a report, a summary they will come back to.` Başka satır değişmez.
- [ ] Aynı test — yeşil.

## Görev 3: Dört suite, sırayla

- [ ] `python -m pytest queen-agent -q`
- [ ] `npm test --prefix queen-agent/frontend`
- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend`
