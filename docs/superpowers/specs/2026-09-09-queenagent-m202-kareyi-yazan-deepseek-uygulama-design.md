# Madde 202 · uygulama turu — kareyi yazan da DeepSeek, ve son eki taşır

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 202, ve
[test turu](2026-09-09-queenagent-m202-kareyi-yazan-deepseek-testler-design.md) — 5 kırmızı.

---

## Ne yazılacak

### `config.py`

`PROMPT_MODEL = "deepseek-v4-flash"`, ve yanındaki yorum **neden** taşındığını söyler: 175 bu
satırı, ana modelin o cümleyi yazmaması üzerine kurmuştu. Yazıyor. `grok-4.3` satırı duruyor, ve
yorumda **bilerek tutulduğu** yazılı — yoksa bir sonraki okuyucu onu 183'ün kuralına göre ölü
sayar.

### `prompt.py`

```
def write_frame_system_prompt():
    if not SYSTEM_PROMPT_SUFFIX:
        return WRITE_FRAME_SYSTEM_PROMPT
    return f"{WRITE_FRAME_SYSTEM_PROMPT}\n\n{SYSTEM_PROMPT_SUFFIX}"
```

`system_prompt()`'un aynı kalıbı, ve aynı iki sebeple: **işlev** olduğu için bugün yazılan bir son
ek bir sonraki isteğe yetişiyor, ve **boşken** metin bayt bayt eskisi kalıyor.

Sabit yerinde duruyor: uygulamanın kendi sayfası o, ve nöbetçi testler *(`MUST_BE_FULL`, kuralların
içeride olması)* onu adıyla tutuyor.

### `tools.py`

`_write_frame_prompt` ve `_write_missing_actions`, sabit yerine işlevi çağırır. Toplu araçta çağrı
**döngünün dışında** bir kez yapılır — her isteğe aynı string gider, ve iş parçacıklarına yine iki
bitmiş string verilir.

## Ne değişmiyor

`WRITE_FRAME_SYSTEM_PROMPT`'un kendi metni. Bu madde **kimin okuduğunu** ve **arkasına ne
eklendiğini** değiştiriyor, ne dediğini değil.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir: **948 · 648 · 739 · 591**. Ön yüz derlenmiyor.
