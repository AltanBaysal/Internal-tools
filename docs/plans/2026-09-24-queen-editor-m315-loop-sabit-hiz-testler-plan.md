# Madde 315 — Loop kuralı sabit hız da istiyor, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Loop kuralının hareketi sona kadar aynı hızda istediğini söyleyen tek test — kırmızı.

**Yaklaşım:** 307'nin kural testinin yanına bir test; kuralın metni okunuyor. Kuralın iki yazıcıya
gittiğini ve standart videonun etkilenmediğini 307'nin testleri zaten tutuyor.

**Spec:** [m315 test turu](../specs/2026-09-24-queen-editor-m315-loop-sabit-hiz-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod değişmiyor.

---

## Görev 1: Test

**Dosya:** Değiştir: `queen-editor/backend/tests/test_video_prompt_writer.py` —
`test_the_loop_rule_says_what_it_wants_and_what_it_refuses`'un hemen altına.

- [ ] **Adım 1: Test.**

```python
def test_the_loop_rule_asks_for_one_speed_to_the_end():
    # Madde 315: most generators ease into the last frame, and the next repeat starts from rest. The
    # rule asks for the same speed all the way to the last frame -- the user's words, "hareket sonuna
    # kadar aynı hızda sürsün, sona doğru yavaşlamasın".
    rule = _loop_rule()

    assert "same speed" in rule and "slow down" in rule
```

## Görev 2: Koşu ve kırmızı commit

- [ ] **Adım 1: Dört satırı koş** — `queen-editor` pytest'te yalnız bu test kırmızı; öteki üç satır
  yeşil.
- [ ] **Adım 2: Kırmızı commit** — test dosyası, spec ve bu plan: `test(m315): …(red)`.
