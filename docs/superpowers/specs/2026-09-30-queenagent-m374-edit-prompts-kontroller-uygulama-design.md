# Madde 374 (v9-8f) — Edit prompts kontrollerle biter — uygulama

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 374 · v9-8f.
**Testler:** [testler spec'i](2026-09-30-queenagent-m374-edit-prompts-kontroller-testler-design.md) —
kırmızı commit `a2c13521`.

**Kullanıcıdan gereken:** yok.

## Değişen tek dosya: `queen-agent/backend/features/workspace/domain/prompt.py`

Kod değişmez; yalnız modele giden metin ve onun yanındaki docstring. `skills.py` Edit prompts'u zaten
`prompt.EDIT_PROMPTS`'tan okuyor.

### 1. `THE_CHECKS`'in ilk satırı

Önce:

```
- Run the checks below in order, each over every frame of the scenario.
```

Sonra:

```
- Run the checks in order, each over every frame of the scenario unless this step limits them.
```

Start a scenario'nun 6. adımı ve Improve'un 2. adımı daraltmaz; okunuşları aynı kalır. *below* düştü,
ve Check 2'de *"such as a face seen from behind"* → *"such as a face from behind"*: akış tavanını
aşmasın diye iki kelime (aşağıda *Kelimeler*). Anlam değişmez.

### 2. `EDIT_PROMPTS`'un 3. adımı ve yeni 4. adımı

Önce:

```
Step 3 -- the answer
- Call build_prompts again: the prompt file is rebuilt rather than patched.
- Say what you changed and which frames it reached. The built file is the answer: its prompts are never printed back.
```

Sonra:

```
Step 3 -- the prompts
- Call build_prompts again: the prompt file is rebuilt rather than patched.
- Say what you changed and which frames it reached.
- This step waits for no approval. Go on to Step 4 in the same turn.

Step 4 -- the checks
- This step limits the checks to the frames your change reached.
- Check 4 runs only if your change touched the scenario's cast: a character added, changed or taken out. Otherwise skip it.
```

ardından `THE_CHECKS` — önsöz, dört kontrol, kapanış —, metnin sonu olarak.

- *"The built file is the answer: its prompts are never printed back."* kalkar: kapanış
  (*"Do not print the prompts back"*) aynı kuralı söylüyor, ve 3. adım artık son söz değil.
- *"This step waits for no approval. Go on to Step N in the same turn."* akışın 5. adımıyla Improve'un
  1. adımının kalıbı.

### 3. `THE_CHECKS`'in docstring'i

İlk paragraf Edit prompts'u da sayar; yeni bir paragraf kapsamın ve Check 4 koşulunun neden Edit
prompts'un kendi adımında durduğunu söyler.

## Kelimeler

`THE_CHECKS` net üç kelime büyür (+5 kapsam, −2 kısaltma). Akışın ilk hâli tavan testinde 1027 çıktı —
elle sayım altı kelime eksikti —; iki kelimelik kısaltmayla **1025**, tavanın tam üstünde. Tavan
yükselmez: plan *"metin kısaltılır, tavan değil"* diyor. Improve ~680 (≤ 700). Edit prompts ~825–830
(≤ 830, test geçiyor); kendi kısmı ~300.

## Kararlar

Testler spec'indeki kararlar geçerli. Ek olarak: Edit prompts'a plan satırı eklenmez — önsözün plan
cümlesi senaryonun Start a scenario'dan kalan planına, yoksa temel metnin plan kuralına yaslanır.
