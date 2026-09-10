# Madde 203 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-10-queenagent-m203-adim-araci-uygulama-design.md](../specs/2026-09-10-queenagent-m203-adim-araci-uygulama-design.md)
**Test turu:** `0e631bf` — altı kırmızı.

**Amaç:** altı kırmızı kapansın, ve araç sayısı 19'dan 18'e insin.

**Komutlar** *(sabit satırlar, kuyruk eklenmez)*:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Yürüten:** bu oturum, tek başına.

---

## Bağlayıcı kurallar

- **Yorum bugünü söyler.** Kalkan bir şeyin izi yorumda bırakılmaz; kalan bir yorum yanlışsa
  düzeltilir *(CLAUDE.md)*.
- **Belge kodun aynası.** 190 belgeyle kodu eşitledi; bu madde ikisini birden değiştirir, yoksa
  fark bir gün sonra yeniden açılır.
- **Log tarih, gövdesi yeniden yazılmaz** — yalnız 203'ün ne yaptığını söyleyen birer satır eklenir.
- Commit mesajında çift tırnak yok; amend yok.

## Değişen dosyalar

| Dosya | Ne oluyor |
|---|---|
| `queen-agent/backend/features/workspace/domain/prompt.py` | üç metin ve akışın dördüncü döngü maddesi kalkar |
| `queen-agent/backend/features/workspace/domain/tools.py` | şema girdisi, dal, `_ticked`, `plan_name`, iki docstring |
| `queen-agent/backend/features/workspace/domain/modes.py` | `EDIT`'in listesinden bir ad ve yorumu |
| `docs/2026-09-09-queenagent-modele-giden-metinler.md` | §3'ün metni, §6'nın bölümü, araç sayısı |
| `docs/2026-09-09-queenagent-metin-duzeltmeleri.md` | 7 ve 10 numaraya birer satır |
| `docs/superpowers/plans/2026-09-06-queenagent-v8-roadmap.md` | 203 kapanır, sapma yazılır |

---

## Görev 1 · `prompt.py`

- [ ] **1.1 — akışın dördüncü döngü maddesi**

`START_A_SCENARIO`'nun `How a step runs:` listesinden son madde çıkar; üçüncü madde listenin sonu
olur ve satır sonu `\n` kalır, çünkü ardından boş satır ve `Step 1 -- the plan` geliyor.

```python
    '- "You decide" covers that step only. Choose, show it, and still wait for the yes. Ask the '
    "next step's question as usual -- one \"you decide\" is not permission for the rest.\n"
    "\n"
    "Step 1 -- the plan\n"
```

- [ ] **1.2 — üç metin**

Dosyanın sonundaki blok tümüyle gider:

```python
MARK_STEP_DONE = (
    "Tick one step off a plan: its box is filled and nothing else in the file is touched. Call it "
    "when the user has approved that step, so a later chat opening the plan reads where the work "
    "stopped. A step already ticked is left as it is."
)
MARK_STEP_DONE_NAME = "Which plan, by the name it was written under."
MARK_STEP_DONE_STEP = "Which step, by its number in the plan."
```

`BUILD_PROMPTS` dosyanın son sabiti olur.

**Kapanan test:** `test_the_step_ticking_texts_are_gone`, ve `test_no_step_is_ticked_off_the_plan_at_all`.

---

## Görev 2 · `tools.py`

- [ ] **2.1 — `TOOL_SPECS` girdisi**

`build_prompts`'tan sonraki blok gider, ve liste `]` ile kapanır:

```python
    {
        "type": "function",
        "function": {
            "name": "mark_step_done",
            "description": prompt.MARK_STEP_DONE,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": prompt.MARK_STEP_DONE_NAME},
                    "step": {"type": "integer", "description": prompt.MARK_STEP_DONE_STEP},
                },
                "required": ["name", "step"],
            },
        },
    },
```

- [ ] **2.2 — `_ticked`**

Fonksiyon ve docstring'i tümüyle gider; `counted` bir üsttekinin yerini alır.

- [ ] **2.3 — `plan_name`, ve `scenario_name`'in cümlesi**

`plan_name` gider. `scenario_name`'in docstring'i onu anıyor:

```python
def scenario_name(name):
    """A scenario is always .json, whatever it was asked for (Madde 167).

    Runs after safe_name, which is where a name from the model is cleaned: naming is this one's
    job. The reason is not tidiness: Madde 171 shuts .json to create_file and edit_file, so the
    tool that opens one has to land on the extension the door guards. Two that disagreed would
    leave the door in front of a file nothing writes, and the model holding a structure it could
    still edit as text.
    """
    return f"{name.rsplit('.', 1)[0]}.json"
```

*(`plan_name`'in kardeşlik cümlesi, kardeş kalmadığı için kendi cümlesine döndü.)*

- [ ] **2.4 — `run_tool`'un dalı**

`start_scenario` dalından sonraki `if name == "mark_step_done":` bloğu, `file_store.write` ve
`Ticked` cevabına kadar gider.

- [ ] **2.5 — `run_tool`'un docstring'i**

```python
def run_tool(file_store, project_id, name, arguments, engine=None):
    """Run one call and answer the model in words. A miss is an answer, not a crash.

    The engine is here for the one tool that answers out of a model rather than out of the file
    store (Madde 175). Optional, because the other seventeen neither take it nor notice it.
    """
```

**Kapanan testler:** `test_the_step_ticking_tool_is_gone`,
`test_every_tool_is_declared_to_the_model`, `test_no_name_is_bent_into_a_plans_shape_any_more`.

---

## Görev 3 · `modes.py`

- [ ] **3.1 — `EDIT`'in son adı**

```python
        # Madde 185, and since 208 the only tool here that spends the user's money at a second
        # provider: one request for every frame still waiting, in one call. The widest single spend
        # any of these makes, and the quieter modes keep their gate in front of it.
        "write_missing_actions",
    ),
}
```

*(Yani `"mark_step_done",` satırı ile üstündeki dört satırlık 198 yorumu gider.)*

**Kapanan test:** `test_no_mode_lets_the_step_ticking_tool_through`.

**Dokunulmayan:** `ends_the_turn` — o çift PLAN ile `create_file`, ve bu madde onu ilgilendirmiyor.

---

## Görev 4 · Süit

- [ ] **4.1 — arka uç:** `python -m pytest queen-agent -q` → tamamı yeşil.
- [ ] **4.2 — ön uç:** `npm test --prefix queen-agent/frontend` → 648 yeşil.

Beklenmeyen bir kırmızı çıkarsa commit atılmaz.

---

## Görev 5 · Belgeler

- [ ] **5.1 — okuma kopyası**

§3'ün akış bloğundan dördüncü madde çıkar:

```text
- Close an approved step with mark_step_done. It fills that step's box and touches nothing else.
```

§6'nın `mark_step_done` bölümü — başlık, notu, tarifi ve iki parametresi — çıkar. §6'nın giriş
notundaki *"yalnız `mark_step_done` elden geçmedi, çünkü 203 onu kaldırıyor"* cümlesi, kaldırmanın
gerçekleştiğini söyler hâle gelir, ve **18 tarif** sayısı araç sayısıyla birlikte yazılır.

- [ ] **5.2 — düzeltme log'u**

7 ve 10 numaraya birer satır. Gövdelerine dokunulmaz:

```text
**203 maddeyi çevirmedi, geri çekti** *(kullanıcı kararı, 10 Eylül)*: kutuyu dolduran tur kalktı,
ve döngü üç maddeye indi. 11 numaranın bulgusu — kutular yalnız bir not — bu maddede sonuna kadar
götürüldü.
```

- [ ] **5.3 — yol haritası**

203 satırı `kapandı` olur ve hash'ini alır. Maddenin gövdesine, sapmayı söyleyen bir satır: kendi
*"Ne çalışır"*ı kapanış maddesinin `edit_file`'ı anmasını istiyordu; kullanıcı 10 Eylül'de maddenin
tümüyle düşmesini seçti.

- [ ] **5.4 — commit**

İki commit: kod yeşili *(Görev 1–4)*, sonra belgeler *(Görev 5)* — bu koşunun her maddede
yürüttüğü sıra.

```
feat(m203): the plan keeps its boxes and nobody ticks them
docs(v8): 203 closes, and the reading copy loses a tool
```

---

## Kendi kontrolü

- **Spec'in her maddesi bir göreve düşüyor mu?** Kalkanlar → 1–3; iki yorum → 2.3 ve 2.5; kip
  kapısı → 3.1'in notu; belgeler → 5.
- **Yer tutucu var mı?** Yok.
- **Ad tutarlılığı:** `MARK_STEP_DONE`, `MARK_STEP_DONE_NAME`, `MARK_STEP_DONE_STEP`, `_ticked`,
  `plan_name`, `scenario_name`, `run_tool`, `_WITHOUT_ASKING` — hepsi bugün var, ve üçü hariç
  hepsi kalıyor.
- **Kalan çağıran var mı?** `plan_name`'in tek çağıranı 2.4'te silinen daldı; `_ticked`'inki de.
  Silme sırası önemli değil, ikisi de aynı commit'te.
