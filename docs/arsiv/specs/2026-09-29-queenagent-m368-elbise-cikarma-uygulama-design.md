# Madde 368 (v9-9) — Elbise çıkarma sahnesi senaryoya, aksi söylenmedikçe eklenmez: uygulama

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 368 · v9-9.
**Testler:** [2026-09-29-queenagent-m368-elbise-cikarma-testler-design.md](2026-09-29-queenagent-m368-elbise-cikarma-testler-design.md)
— kırmızı olan `test_the_scenes_step_writes_no_frame_of_clothes_coming_off_unless_asked`.

**Kullanıcıdan gereken:** yok.

## Ne değişiyor

`queen-agent/backend/features/workspace/domain/prompt.py`, `START_A_SCENARIO`'nun *Step 4 -- the
scenes* adımına bir madde eklenir. Başka hiçbir metin değişmez.

Adım bugün:

```
Step 4 -- the scenes
- Ask how many scenes and which moments matter.
- Write them with add_scene: one sentence each, in the language the user is writing in.
- Write no actions here.
```

Adım bundan sonra:

```
Step 4 -- the scenes
- Ask how many scenes and which moments matter.
- Write them with add_scene: one sentence each, in the language the user is writing in.
- What someone wears can change from one scene to the next. The moment clothes are taken off or
  changed is not written as a scene unless the user asks for it: the model cannot draw it.
- Write no actions here.
```

## Kararlar (subagent'ın, kullanıcısız)

1. **Yeri: sahneleri `add_scene` ile yazan maddenin hemen altı.** Kural hangi sahnelerin yazılacağı
   hakkında; model onu sahneleri yazan cümleyi okuduktan hemen sonra okur.
2. **İki cümle, sırasıyla izin sonra yasak.** Önce kıyafetin sahneden sahneye değişebildiği söylenir —
   yoksa model yasağı "kıyafet hiç değişmez" diye okuyabilir. Sonra yazılmayan an, istisnasıyla.
3. **"Elbise" değil "clothes".** Kullanıcı elbise dedi, ama kural her giysi için aynı: zayıf model bir
   ceketin çıkarıldığı anı da çizemez. Bu kelime seçimi, kuralın anlamını genişletmez — kullanıcının
   anlattığı neden *(ara kareyi çizemiyor)* her giysi için geçerli.
4. **Neden de söylenir** *(`the model cannot draw it`)*: bir kuralı nedeniyle okuyan model onu
   benzer durumlara taşır. "Weak" tekrar edilmez; `THE_IMAGE_MODEL` bunu metnin başında zaten söylüyor.
5. **Kelime sayısı:** 442 → 479, tavan 1000 *(Madde 367)*. Tavan değişmez.
