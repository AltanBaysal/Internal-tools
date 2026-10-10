# Madde 459 · `create_file`'ın tarifi plan dosyasını da sayar — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
459 · **Dal:** `feat/queenagent-v10`, ana klasörde, worktree yok · **Okuma:** metin modele gider; Claude
okuyup doğrular ve commit'ler *(kullanıcı, 10 Ekim — "kendin verify et")* · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Plan:** [m459 planı](../plans/2026-10-10-queen-agent-m459-create-file-plan.md)

## Ne, neden

**Bugün** `CREATE_FILE` *"Call this only when the user asked for something worth keeping"* diyor.
Oysa `SYSTEM_PROMPT`'un Planning 2'si ve Writing 1'i (*"Call create_file for a plan file, or when the
user asked for something worth keeping as a document"*) ile `START_A_SCENARIO`'nun 1. adımı (*"write a
plan file"*), kullanıcı istemeden bir plan dosyası yazdırıyor. Model iki ters söz duyuyor: system
prompt "plan dosyasını yaz", tool'un kendi tarifi "yalnız kullanıcı isterse".

**Olacak:** tool'un tarifi de system prompt gibi plan dosyasını sayar. En az kelimeyle, Writing 1'in
sırasıyla:

| | `CREATE_FILE`'ın ikinci satırı |
|---|---|
| Önce | `- Call this only when the user asked for something worth keeping: a draft, a report, a summary they will come back to.` |
| Sonra | `- Call this for a plan file, or when the user asked for something worth keeping: a draft, a report, a summary they will come back to.` |

Tarifin geri kalanı (ilk satır, `edit_file` ve `start_scenario` satırları) ve iki alanın metni
değişmez.

## Sınırlar

- Yalnız `prompt.py`'deki `CREATE_FILE` değişir. `SYSTEM_PROMPT`, skill'ler, `tools.py`, frontend ve
  queen-editor'e dokunulmaz.
- Test sözü değil anlaşmayı tutar: tarif plan dosyasını anar, ve *"only when the user asked"* artık
  demez. Kullanıcı cümleyi yeniden yazarsa test kırılmaz, plan dosyasını düşürürse kırılır.

## Maliyet

Disk ve ağ yok: metin modülde sabit. `TOOL_SPECS` her istekte modele gider; tarife beş kelime
(*"for a plan file, or"*) girer, *"only"* düşer: net dört kelime uzar.

## Ne zaman biter

- `create_file`'ın tarifi plan dosyasına izin veriyor ve system prompt'la aynı şeyi söylüyor.
- Yeni test önce kırmızı, sonra yeşil; dört suite yeşil.
