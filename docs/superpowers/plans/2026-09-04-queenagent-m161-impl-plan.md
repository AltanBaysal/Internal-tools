# Madde 161 — uygulama turu planı

**Spec:** [m161 yeniden adlandırma uygulama design](../specs/2026-09-04-queenagent-m161-yeniden-adlandirma-uygulama-design.md)

## 1. `_renamed` yazılır

`_frames_naming`'in yanına. Haritayı **yeniden kurar**, `pop` kullanmaz. Üç kare şeklini birden
okur, ve kaç karenin takip ettiğini döndürür.

## 2. `_set_entry` yeniden yazılır

`_opened`'a geçer. Sıra: boş ad → yok mu *(new_name ret / eksik alan ret / ekle)* → var mı
*(hiç alan yok ret → new_name kontrolleri → alanları indir → yaz)*.

`kind`/`tags` **`in args`** ile okunur, `args.get()` ile değil.

## 3. Üç araç tanımı

`required` → `["file", "name"]`. `new_name` parametresi ve iki cümle açıklamaya.

## 4. Koşulur ve yeşil görülür

CLAUDE.md'nin dört satırı; iki vitest yan yana koşmaz.

## 5. Commit

`feat(m161): …` — mesajda çift tırnak yok.
