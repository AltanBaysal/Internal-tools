# Madde 480 — Değiştiren araçlar için izin kapısı, plan

> **Koşum:** bu oturumda, ana klasörde, `feat/queen-editor-v10` dalında, adım adım, test önce (TDD).
> Adımlar `- [ ]` ile işaretlenir. Commit ana ajanın.

**Hedef:** değiştiren bir araç çağrısı ekranda İzin ver / Reddet ile, ne değişeceği yazılı bir kart
açar ve yalnız İzin ver'de çalışır; Reddet'te hiçbir şey değişmez ve ajana ret söylenir; okuyan araçlar
izinsiz çalışır; otomatik mod yok.

**Spec:** [m480](../specs/2026-10-20-queen-editor-m480-permission-gate-design.md)

**Araçlar:** pytest, vitest, vite build.

## Her yere geçerli kurallar

- Yorumlar, docstring'ler ve modele giden metinler **İngilizce**; ekrandaki yazılar Türkçe.
- Dosyalar Read / Edit / Write ile değişir. Kabuk yalnız pytest, npm ve git status / diff için.
- Sahte değiştiren araç (`fix_frame`) yalnız testlerde; `TOOLS`'a girmez.
- İki suite birer birer koşulur.

---

## Görev 1: backend testleri

- [ ] `test_agent_answer.py`: `FakeRun.permit` — sorulanı yazar, `permits` listesinden cevaplar,
  liste boşsa testi düşürür (okuyan araç sormamalı). `fix_frame` fikstürü döngünün `run_tool`'unun
  önüne konur. Yeni testler: izin, ret (modele ret cümlesi, turun sıradaki çağrısı çalışıyor),
  soru sırasında durdurma, bir turda iki değişiklik, okuyan üç araç izinsiz.
- [ ] `test_agent_runner.py`: işi kendi iş parçacığında koşan `asks` fikstürü ve en çok beş saniye
  bakan `until`. Testler: izin / ret, başka sayı ya da sohbet ya da proje, ikinci cevap, soru yokken
  cevap, bekleyişte durdurma, durdurulmuş koşu, sayıların ayrılığı ve projeye göre `asking`.
- [ ] `test_agent_routes.py`: `app_over`'a `threaded`; `/working` beklentilerine `"asking": []`;
  `answer_permission` kablosu; 404 ve 503 testlerine `/permission`; yeni testler: izin, ret,
  durdurma, `409`, bozuk gövdeye `400`.
- [ ] `test_composition_root.py`: kapının asıldığı `/permission`.
- [ ] Kırmızı.

## Görev 2: backend

- [ ] `tools.py`: `run_tool` `(adım, iş, değişiklik)`; üç araç `None`; değişikliğin biçimi docstring'de.
- [ ] `answer_question.py`: `REJECTED`; adım ya da değişiklik varsa önceki adım bitirilir;
  değişiklikte `run.permit`, ret ve durdurma.
- [ ] `ports.py`: `Run.permit`.
- [ ] `runner.py`: `_Run.asking / allowed / permit`; `AgentRunner.now`, `reply`, `_permit`; kilit
  üstünde bir `Condition`; sayaç saatten, mikrosaniyede; `stop` bekleyeni uyandırır.
- [ ] `chats.py`: `BadPermission`, `NotAsked`, `answer_permission`; `working_chats`
  `runner.now(project)`'u, `{"working", "asking"}`, döner.
- [ ] `answer_question.py`: adım yazıldıktan sonra, işten önce bir durdurma bakışı daha.
- [ ] `tests/conftest.py`: `until` ve `ended` fikstürleri, iki test dosyası için.
- [ ] `routes.py`: `POST …/permission`; `/working` use case'in cevabını olduğu gibi döner; 400 ve 409.
- [ ] `main.py`: `answer_permission` kablosu.
- [ ] Yeşil.

## Görev 3: frontend testleri (`AgentPanel.test.jsx`)

- [ ] Sahte sunucu: `asking`, `/working` `{working, asking}`, `/permission` kapısı (sayı uymazsa
  `409`), `holdAnswer`; durdurma bekleyen değişikliği siler.
- [ ] "AgentPanel — permission" testleri: yeniden yüklemede kart, bakışta beliriş, İzin ver / Reddet
  sayıyla, izin sonrası adım, yoldayken kapalı düğmeler, `409`, ■, yalnız kendi sohbeti.
- [ ] Kırmızı.

## Görev 4: frontend

- [ ] `api.js`: `workingChats` bütün gövdeyi döner; `answerPermission`.
- [ ] `useAgentChat.js`: `asking`, `answering`, `look`, `permission`, `permit`; durdurma `asking`'i
  süzer.
- [ ] `AgentPanel.jsx`: `Permission` kartı; `Question` çocuğunu "Çalışıyor…"nun yerinde çizer.
- [ ] `app.css`: `.qe-chat-permit…`.
- [ ] Yeşil.

## Görev 5: Bitiş

- [ ] `npm run build --prefix queen-editor/frontend`.
- [ ] `python -m pytest queen-editor -q`, sonra `npm test --prefix queen-editor/frontend`.
- [ ] `git status` / `git diff` ile değişen dosyaları gözden geçir.
