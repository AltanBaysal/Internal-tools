# Madde 127 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 127
**Testler kırmızı commit'te (2ee5017).**

## Dokunulan dosyalar

**`stream_answer.py`** — `_named(names)` doğar: dosya varken
`"The project's files right now: a.json, b.md"`, yokken `"This project holds no files yet."`
`_asked(conversation, names, instruction)` konuşmanın arkasına önce bu satırı, sonra varsa skill
metnini koyar. Liste her raundda `file_store.list_names(project_id)` ile tazelenir — turun içinde
doğan dosya bir sonraki raundda görünür.

**`tools.py`** — `list_files` spec'i ve `run_tool`'daki dalı silinir. `MAX_ROUNDS`'un yorumundaki
*"list, read, ..."* zinciri güncellenir *(yorum kodla çelişemez)*. `counted` durur:
`read_file` ve kurucular kullanıyor.

**`modes.py`** — `READS`'ten `list_files` çıkar.

**`prompt.py`** — *"Use list_files to see what exists, and when the answer depends on a file..."*
→ *"Their names are listed for you in every request, so nothing has to be called to find out what
exists; when the answer depends on one, read it first with read_file -- and nothing the answer
does not need. ..."*

**`skills.py`** — akış adım 1: *"A chat's first turn opens with write_plan; later turns carry on
from what the chat already knows."* prompt+: *"find them with list_files, read both"* →
*"their names are in the request, read both"*.

## Sıra ve önbellek

İstek: taban → konuşma → **dosya adları** → skill metni. Adlar konuşmanın arkasında, çünkü tur
ortasında doğan dosyanın görünmesi gerekir; skill metninin önünde, çünkü Madde 93 son sözü ona
verdi. Prefix *(taban + konuşma)* değişmediği için 124'ün cache anahtarı korunur.

## Ayakta kalması gerekenler

93'ün sırası, 107'nin `A chat's first turn` pini, `read_file` ve içerik JIT'i, izin/kip davranışı,
kayıt ve ön yüzün eski `list_files` adını çizebilmesi.

## Bilerek yapılmayanlar

Dosya *içerikleri* isteğe girmez; `usecases/list_files.py` ve `FileStore.list_names` durur; ön yüz
ve `dist` ellenmez.
