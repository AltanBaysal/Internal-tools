# Madde 78 — Tool call satırı yeniden çizilir · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [test turu spec'i](2026-08-26-queenagent-m78-tool-satiri-testler-design.md) ·
**Testler:** `139e59f` — arka uçta 10, ön yüzde 5.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder. Test yazılmaz.

---

## Özetin yolu

Yeni bir yol açılmıyor: `target` 66'da hangi yoldan geldiyse `outcome` aynı yoldan geliyor.

`run_tool` → `ToolResult.outcome` → `stream_answer`'ın kurduğu `ToolCall` → diske ve tele → ekran.

## Her aracın kendi cümlesi

| Araç | Özet | Neden bu |
|---|---|---|
| `list_files` | `3 files` / `No files` | Sıfırı saymak "hiç yok"u söylemiyor; ikisi ayrı cümle |
| `read_file` | `45 lines` | Ne kadar okunduğu diskte durmuyor — o anın kaydı, ve bayatlamıyor |
| `create_file` | `Saved` | Ad üst satırda zaten var; ikinci kopya ilk değişiklikte bayatlar |
| `edit_file` | `Edited` | Aynı sebep |
| `build_prompts` | `12 prompts` | Sayı işin kendisi |
| *(reddedilen her dal)* | `No file by that name` gibi | Ret de turun yaptığı bir şey |

Cümleleri araç yazıyor çünkü ne olduğunu bilen o. Dışarıdan `text`i ayrıştırmak, aynı bilgiyi
ikinci kez ve kırılgan bir biçimde türetmek olurdu.

**Noktasız.** Modele giden `text` bir cümle ve noktası var; okuyucuya giden özet bir etiket. İkisi
farklı okuyucuya yazıldığı için farklı biçimde.

## Ekranda: iki katman

Bugünkü `.tool-call` bir satır. Artık iki:

```
⏺ read_file(aylin.json)
  ⎿ 45 lines
```

- **`.tool-call__head`** — işaret, araç adı, parantez içinde konusu. Konusu yoksa parantez de yok.
- **`.tool-call__outcome`** — işaret ve özet. Özet yoksa satır hiç doğmuyor.

66'nın `.tool-call__name` / `.tool-call__target` ikilisi ve CSS'teki `·` ayıracı gidiyor: ayıracın
işini artık parantez yapıyor, ve parantez metnin kendisinde olduğu için "boşken ayıracı gizle"
kuralına gerek kalmıyor. Kural CSS'ten metne taşınmış oluyor — bir yerde eksilme, bir yerde
sadeleşme.

**Tipografi değişmiyor:** mono, `var(--muted)`, 11.5px, vurgusuz. Alt satır bir girinti kazanıyor,
o kadar.

## Kapsam dışı

Araçların ne yaptığı *(yalnız bir cümle daha söylüyorlar)* · sonucun tamamının saklanması *(test
turunun kararı)* · katlanır satır · dosya kartları · arka ucun geri kalanı.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur** — aynı anda koşturulduklarında vitest bu makinede zaman aşımına düşüyor
(Madde 77'de bir kez kovalandı).

Arka uçta **2 failed, 442 passed** — ikisi defterin dalı. Ön yüzde **497**, hepsi yeşil.

`dist` **kaynağıyla aynı commit'te** derleniyor: `ChatScreen.jsx` ve `workspace.css` değişiyor.
