# Madde 78 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-26-queenagent-m78-tool-satiri-uygulama-design.md](../specs/2026-08-26-queenagent-m78-tool-satiri-uygulama-design.md)
**Kırmızı testler:** `139e59f` — arka uçta 10, ön yüzde 5.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sıra

Özetin yolu boyunca, kaynaktan ekrana.

### 1. `domain/tools.py` — her dal kendi özetini yazar

`run_tool`'un ve `_edit` ile `_build`'in her `ToolResult`'ı dördüncü alanı doldurur:

| Dal | Özet |
|---|---|
| `list_files` dolu | `{n} files` |
| `list_files` boş | `No files` |
| `read_file` bulundu | `{n} lines` |
| `read_file` yok | `No file by that name` |
| `create_file` | `Saved` |
| `edit_file` başarılı | `Edited` |
| `edit_file` dosya yok | `No file by that name` |
| `edit_file` eski metin boş | `Nothing to replace` |
| `edit_file` eşleşme yok | `Not found` |
| `edit_file` çok eşleşme | `{n} matches` |
| `build_prompts` başarılı | `{n} prompts` |
| `build_prompts` reddedildi | `Refused` |
| Bozuk JSON argüman | `Bad arguments` |
| Bilinmeyen araç | `Unknown tool` |

Noktasız: modele giden `text` bir cümle, okuyucuya giden özet bir etiket.

*Yeşile döner:* `test_tools.py`'nin yedi kırmızısı.

### 2. `domain/usecases/stream_answer.py` — özet `ToolCall`'a geçer

`ToolCall(tool, result.target)` → `ToolCall(tool, result.target, result.outcome)`. Tek satır.

*Yeşile döner:* `test_stream_answer.py`'nin bir kırmızısı.

### 3. `data/file_chat_store.py` — diske

`_call_json` boş olmayan `outcome`'ı yazar; okuma `call.get("outcome", "")` ile alır. `target` ile
aynı kural, aynı satırın yanında.

*Yeşile döner:* `test_file_chat_store.py`'nin bir kırmızısı.

### 4. `presentation/routes.py` — tele

`_chat_json`'daki çağrı sözlüğü üçüncü anahtarı taşır, boşken de.

*Yeşile döner:* `test_chats_api.py`'nin bir kırmızısı.

### 5. `ChatScreen.jsx` — satır iki katman olur

`ToolCalls` bileşeni her çağrıyı iki parçaya böler:

- `.tool-call__head` — `⏺ {tool}` ve konusu varsa `({target})`. Metin tek parça olarak kurulur,
  çünkü testler onu metniyle arıyor ve parçalı bir düğüm eşleşmez.
- `.tool-call__outcome` — `⎿ {outcome}`. `outcome` boşsa hiç doğmaz.

66'nın `.tool-call__name` ve `.tool-call__target` span'leri gider.

*Yeşile döner:* `ChatScreen.test.jsx`'in beş kırmızısı.

### 6. `workspace.css` — iki sınıf yerine üç

`.tool-call` bir sütun olur. `.tool-call__name`, `.tool-call__target` ve
`.tool-call__target::before` silinir — ayıracın işini artık parantez yapıyor, ve parantez metnin
içinde olduğu için "boşken gizle" kuralına gerek kalmıyor. `.tool-call__outcome` bir girinti alır.

**`workspace.css.test.js` var ve 59 test taşıyor.** Silinen sınıflardan birini soruyorsa kırmızıya
döner; o zaman test de bu maddenin parçası olarak güncellenir, çünkü sorduğu şey artık yok.

### 7. `dist` derlenir

`npm run build --prefix queen-agent/frontend`, kaynakla **aynı commit'e**.

## Beklenen yeşil

Arka uçta **2 failed, 442 passed** — ikisi defterin dalı. Ön yüzde **497**.

## Koşuda çıkanlar

**Altı tane 66 testi düştü, ve düşmeleri doğruydu.** Dördü arka uçta `ToolCall` eşitliği kuruyor,
ikisi ön yüzde araç adını ve dosyayı ayrı metin düğümü olarak arıyor. Üçüncü alan doldurulunca
birinciler eşleşmedi; parantez metne girince ikincilerin aradığı düğümler kalmadı. Hepsi bu
maddenin getirdiği şeyi söyleyecek biçimde güncellendi — iddiaları değişmedi, biçimleri değişti.

**Test turunun planı "mekanik kırmızı beklenmiyor" diyordu ve o tur için doğruydu**: alan vardı ama
boştu, yani eşitlikler tutuyordu. Doldurmak ikinci turun işi, ve kırılma orada çıktı. **Ders:**
varsayılanlı bir alan test turunu sessiz geçiriyor, ikinci turda konuşuyor.

**Bir de kopya hatası:** tek satırlık bir dosya `1 lines` diyordu. Deponun kendi kuralı var —
arayüzde *"one of a thing is one, not one of them"* diye bir test bile duruyor. `counted()`
eklendi; `matches` dalı ondan muaf, çünkü yalnız birden çokken çalışıyor ve kural `matchs`
üretirdi.

## Bilerek yapılmayanlar

- **Sonucun tamamı saklanmıyor.** Test turunun kararı: bir okumanın sonucu dosyanın kendisi ve o
  zaten diskte.
- **Özet çevrilmiyor.** QueenAgent'ın arayüzü İngilizce, ve CODE-STANDARD bunu ayrıca yazıyor.
- **Satır katlanmıyor.** Claude Code uzun sonucu katlıyor; bizim özetimiz zaten tek satır.
