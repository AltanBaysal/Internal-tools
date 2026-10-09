# Madde 431 · Belgeler test edilmez — tasarım

**Tarih:** 8 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
431 · **Dal:** `feat/queen-editor-v9` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md) ·
queen-agent [FOUNDATION](../../queen-agent/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) — madde iki aracın da testlerine dokunuyor.

## Kullanıcıdan gereken

Hiçbir şey. Madde 8 Ekim'de hizalandı *(kullanıcı — "abi dokümanları test etmeyelim bunu kaldır
roadmape ekle"; Claude'un geri söylediğine — "çıkar başla")*.

## Ne, neden

Bazı testler belgeleri okuyor; bir belge kısalınca ya da yeniden yazılınca o testler kırmızıya
düşüyor, ve belge kodun değil insanın okuduğu bir şey. **Belgeyi okuyan testler kalkar, testler yalnız
kodu test eder;** belgeler bir testi kırmadan değiştirilebilir.

Madde test kaldırıyor, davranış eklemiyor: kaldırılan bir testi gösterecek bir kırmızı test yok, ve
yazılmıyor. Kanıt, aşağıdaki listenin diff'le karşılaştırılması ve dört satırın, kaldırılan test
sayısı kadar eksikle yeşil olması.

## Çizgi: belge ve kod

Maddenin sözü: **belge**, `.md` dosyası — CLAUDE.md, FOUNDATION, CODE-STANDARD, NOTEBOOK-STANDARD,
README'ler, BACKLOG, ve `docs/` altındaki yol haritaları, spec'ler ve planlar. Geri kalan her şey
**kod**: kaynak, CSS, grafiklerin JSON'u, notebook'lar — markdown hücreleriyle birlikte — ve ayar
dosyaları (`.mcp.json`, `.claude/settings.json`, `.gitignore`, `package.json`, `requirements.txt`).

Çizgiyi uygularken iki not:

- **QueenAgent'ın kendi `.md` dosyaları belge değil.** QueenAgent kullanıcıya `.md` dosyaları
  yazıyor; testleri onları `tmp_path`'e yazıp geri okuyor (`test_store.py`, `test_files_api.py`,
  `test_read_file.py`, `test_context_box.py` ve ötekiler). Bunlar uygulamanın verisi, deponun belgesi
  değil: kodu test ediyorlar, ve kalıyorlar.
- **Anmak okumak değil.** Bir docstring'in ya da yorumun bir belgeyi anması — *"(CODE-STANDARD,
  Tests)"*, *"BEHAVIOUR.md, Agent panel"*, *"FOUNDATION 1"* — hiçbir dosya açmıyor; kalıyor.

## Ne gider

Belge okuyan altı yer var; `.claude/worktrees/` altındaki eski kopyalar sayılmadı.

### A — Belgeyi adıyla okuyanlar

**1. `queen-editor/backend/tests/test_version_record.py` — bütün dosya.** Hepsi belge okuyor:
`docs/roadmaps/`'in dosyalarını (adlarını ve içlerini), `docs/**/*.md`'yi, deponun her klasörünün
yanındaki `.md`'leri ve CLAUDE.md'yi. Hiçbir dosya ondan bir şey içe aktarmıyor.

| Test | Okuduğu |
|---|---|
| `test_one_version_has_one_roadmap` | yol haritalarının adları |
| `test_every_roadmap_says_which_branch_it_ran_on` | yol haritalarının başlıkları |
| `test_no_branch_is_claimed_by_two_roadmaps` | yol haritalarının başlıkları |
| `test_a_numbered_branch_agrees_with_the_name` | yol haritalarının adları ve başlıkları |
| `test_every_link_to_a_roadmap_resolves_from_where_it_is_written` | bütün `.md`'ler ve CLAUDE.md |
| `test_a_links_text_names_the_version_it_goes_to` | bütün `.md`'ler ve CLAUDE.md |
| `test_a_roadmap_can_still_reach_everything_it_links_to` | yol haritalarının bağlantıları |
| `test_a_web_address_is_not_a_file_a_roadmap_has_to_reach` | dosya açmıyor; dosyanın kendi `_local_links`'ini sınıyor, o da yalnız belge bağlantıları için var |
| `test_every_roadmap_name_says_a_date_a_tool_and_a_version` | yol haritalarının adları |
| `test_roadmaps_live_in_their_own_folder` | `docs/plans/`'taki adlar |
| `test_claude_md_no_longer_calls_the_newest_document_the_current_version` | CLAUDE.md |

**2. `queen-agent/backend/tests/test_pin_archive.py` — bir test.**
`test_the_standard_names_both_new_files` queen-agent'ın CODE-STANDARD.md'sindeki tabloyu okuyor.
Onunla birlikte `CODE_STANDARD` sabiti ve `# ---- The standard ----` başlığı gider.

**3. `queen-agent/frontend/src/shared/app.css.test.js` — iki test.** `the standard names every
keyframe the frontend defines` ve `the standard forbids no animation, and calls no motion the only
one` `../CODE-STANDARD.md`'yi okuyor. Onlarla birlikte `STANDARD` sabiti ve üstündeki Madde 379
yorumu gider.

### B — Taramanın bir parçası belge

Bu üç tarama bir klasörü dolaşıp bulduğu dosyaları açıyor, ve belgeleri de buluyor. Gidecek olan
yalnız `.md` dosyaları; testler kalır, ve kod ile notebook taramada kalır.

**4. `queen-agent/backend/tests/test_retired_provider.py`.** `_written()` README.md, BACKLOG.md,
FOUNDATION.md ve CODE-STANDARD.md'yi de veriyor; `test_no_path_names_the_retired_provider` adlarına,
`test_no_file_mentions_the_retired_provider` içlerine bakıyor. **Gider:** `.md` dosyaları
`_written()`'dan — belgelerin ne adına ne içine bakılır.

**5. `queen-editor/backend/tests/test_retired_provider.py`.** Aynı tarama; BACKLOG.md'yi bugün adıyla
atlıyor, README.md, FOUNDATION.md ve CODE-STANDARD.md'yi açıyor. **Gider:** `.md` dosyaları
`_written()`'dan; `_SKIPPED_FILES`'taki `BACKLOG.md` ve yorumun onu anlatan yarısı bunun içinde kalır
ve gider.

**6. `queen-editor/backend/tests/test_audio_engine_wiring.py`.** `_mentions()` `.md` dosyalarını da
açıyor — queen-editor'ün dört `.md`'si. **Gider:** `.md` uzantı listesinden. Docstring'in taramanın
sebebini bir belgeyle anlatan cümlesi *("it is a document telling somebody to export a graph that
nothing reads")* artık doğru olmaz; taramanın baktığı kodla yeniden yazılır.

## Ne kalır

- **Notebook'ların testleri:** queen-agent `test_notebook.py` (`queenagent.ipynb`); queen-editor
  `test_notebook_clones_its_branch.py`, `test_notebook_installs_the_producer_groups.py`,
  `test_notebook_stays_readable.py`, `test_notebook_times_its_cells.py` (`queeneditor.ipynb`).
- **Ayar dosyalarının testleri:** `test_playwright_mcp.py` (`.mcp.json`, `.claude/settings.json`,
  `.gitignore`); iki aracın `test_frontend_toolchain.py`'si (`package.json`) ve
  `test_requirements.py`'si (`requirements.txt` ve `.py` dosyaları); `test_dist_is_committed.py` (git
  ve `dist/index.html`).
- **Kaynağı okuyan öteki testler:** `test_workflow_asset.py`, `test_producer_contract.py`,
  `test_composition.py`, `test_composition_root.py`, `test_prompt.py`, `test_agent_answer.py`,
  `test_video_prompt_writer.py`, `ChatScreen.test.jsx`, `workspace.css.test.js`, `Gallery.test.jsx`,
  ve `app.css.test.js`'in, `test_pin_archive.py`'nin geri kalanı.
- collab-toolbox'ın testi yok; NOTEBOOK-STANDARD.md'yi hiçbir test açmıyor.

## Sınırlar

- Yalnız bu altı test dosyası değişir. Belgelere, kural dosyalarına, BACKLOG'a ve yol haritasına
  dokunulmaz.
- Belgeyi anan docstring'ler ve yorumlar kalır; yalnız 6'nın artık doğru olmayan cümlesi düzelir.
- Frontend'in kaynağı değişmez; `dist`'e dokunulmaz.

## Bitti sayılır

- Hiçbir test bir `.md` dosyasını okumuyor; notebook'ların ve ayar dosyalarının testleri yerinde.
- Dört satır yeşil, ve sayılar tam kaldırılan testler kadar düşük — bugün 989, 838, 1518, 869:
  - `python -m pytest queen-agent -q` → **988** (bir test, 2);
  - `npm test --prefix queen-agent/frontend` → **836**, 44 dosya (iki test, 3);
  - `python -m pytest queen-editor -q` → **1507** (on bir test, 1);
  - `npm test --prefix queen-editor/frontend` → **869**, değişmez.
- Taramalarda test kalkmıyor (4 – 6): sayıları değişmez, yeşil kalırlar.
