# H3 referanstan video prompt'u — 24 Eylül bulguları

**Neden var:** kullanıcı queen-editor v7'nin Referanstan'ını Colab'da denerken H3'e prompt'ları
elle yazdık ve denedik. Öğrenilenler [QueenAgent v9](../roadmaps/2026-09-21-queen-agent-v9-roadmap.md)'un
6. maddesinde, referanstan video prompt'larını yazan skill'de kullanılacak *(kullanıcı, 24 Eylül —
"şu prompt hakkında öğrendiklerimizi queenagent koşusunu yaparken kullanalım", "kaybetmeyelim
ilerlememizi")*.

**Örnek dosya:** [reference_limits.py](../../../queen-editor/h3-tests/reference_limits.py) — ikinci
turun 20 prompt'u, Referanstan'ın kutusuna olduğu gibi yapıştırılan hâliyle. Aşağıdaki kuralların
hepsi orada uygulanmış hâliyle duruyor.

## Kaynak: MiniMax'ın kendi rehberi

[VIDEO_PROMPT_WRITING_GUIDE_ref_en.md](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md)
*(resmi)*. Biçim oradan:

- **Altı bölüm, bu sırayla, her başlık kendi satırında:** `subject_definitions:`, `summary:`,
  `retention_analysis:`, `detailed_description:`, `overall_soundscape:`, `non_diegetic_music:`.
- **Etiketler:** `<Picture N>`, `<Video N>`, `<Audio N>` havuzdaki dosyalar; `<Subject N>` videoda
  görünen, yeniden kullanılan şey — kişi, mekân, eşya, **stil**, hareket, poz.
- **Bir resim yalnız görünüşü ya da stili veriyorsa** bir `<Subject>`'in tanımına girer
  *("<Subject 1> is the woman in <Picture 1>, …")*. Tek başına `<Picture N>` yalnız bir çekimin ilk,
  son ya da ana karesi olduğunda anılır.
- **`summary`** köşeli parantez içinde görev tipiyle başlar: `[reference generation]`; ses yalnız
  referanssa `+ audio reference`, kopyalanıyorsa `+ audio reuse`.
- **`retention_analysis` işaretleri:** görüntüde `fully_preserved`, `partially_preserved`,
  `attribute_transfer`, `weak_reference`; seste `fully_copy`, `partially_copy`, `reference`,
  `weak_reference`.
- **`detailed_description`:** ilk satır genel stil ve ışık; sonra `[Shot 1] …`, sonraki çekimler
  `[Shot 2] At 00:03.000, the shot cuts to …`. Konuşan kişi `<Subject 1> (S1)`, sözler
  `<d>[Turkish] …</d>` içinde, çevrilmeden. Kamera hareketi tipi, genliği ve hızıyla.
- Rehber `detailed_description` için 350–500 İngilizce kelime öneriyor; bizim klibimizde bu fazla,
  aşağıya bak.

## queen-editor'e özgü olanlar

- **`<Picture N>`'deki N, havuzda kartın sol üstündeki numara** — her tip kendi sayısını tutar.
  Kullanıcıya referansları bu numarayla sormak gerekiyor; QueenAgent havuzu göremiyor.
- **Klip 4 saniye** *(kullanıcı, 24 Eylül — "vidolar 4 saniye ile sınırlı")*: tek çekim, tek ana
  hareket; konuşma en çok kısa bir cümle. Kesmeli çok çekimli sahne bu sürede anlamsız.
- **Kutuya yapıştırılan biçim:** `PROMPTS = ["""…""", """…""",]` — sunucu üç tırnaklı listeyi
  okuyor, aradaki `#` yorum satırlarını da. Düğmenin altındaki sayım satırı üç tırnaklı listede
  boş kalıyor *(madde 323'ün bilinen köşesi)*; basış yine gidiyor.
- **İki kişilik sahnede** her kişi kendi resmine bağlanıyor, 3–5 ayırt edici özelliğiyle
  *(saç, makyaj, kıyafet, dövme)*, ve her sahnede aynı tarafta duruyor *(Picture 1 solda,
  Picture 2 sağda)* — karışmasınlar diye.

## Denemeler ve sonuçlar

**Referanslar:** iki 3D anime/3DCG kız fotoğrafı *(Picture 1: iki renkli saç, korse; Picture 2:
siyah saç, gotik makyaj, dövme)*. Test listesi kimlik, kamera, nesneyle etkileşim, iki kişi, hızlı
hareket ve stil başlıklarında 17 test; tam hâli örnek dosyada.

**1. tur — stil yalnız bir yarım cümle** *("keeps the stylised 3D anime look of <Picture N>")*.
Sonuç: çıktılar animasyondan gerçekçiye kaydı *(kullanıcı — "çıktılar animasyondan çok biraz
gerçekçiye kaymış")*.

**2. tur — stil açıkça ve her yerde:**

1. **Stil ayrı bir `<Subject>`**, bütün kareye uygulanan: *"<Subject 2> is the 3D anime CG render
   style of <Picture 1>, applied to the whole frame -- the woman, the environment, every prop and the
   light: cel-shaded toon shading…, smooth flawless skin with no pores…"*, ve `retention_analysis`'te
   `fully_preserved`.
2. **`detailed_description`'ın ilk cümlesi stili kesin söylüyor:** *"The whole video is a stylised
   3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, …"*.
3. **Mekân ve eşyalar da anime diye anılıyor** *("an anime café", "simple stylised buildings")*;
   kişiler her geçişte *"the anime-styled young woman"*.
4. **Gerçekçiliğe iten kelimeler çıktı:** gözenek, doğal cilt dokusu, kameramanın adımları, sığ alan
   derinliği.

Sonuçlar:

- **3D anime stil korundu** — ölçü sahnesi iç mekân, yakın çekim *(kullanıcı — "burda animasyon
  stilini baya güzel korumuş")*. Genel izlenim: *"videolar çok güzel"*.
- **Aynı sahne 2D cel animasyon istenince model geçti** *(kullanıcı — "geçti, ve o da çok ilginç ve
  güzel olmuş")*. Yani gerçekçiliğe kayma değiştirilemez bir eğilim değil: stil söylenmeyince model
  kendi varsayılanına dönüyor, söylenince dinliyor.
- **Yüzler: yakında çok iyi, uzakta zayıf** *(kullanıcı — "yakın çekimde çok iyi, uzakta
  sıkıntı")*. queen-editor'ün [BACKLOG](../../../queen-editor/BACKLOG.md)'unda ayrı girdi; aday
  olarak bulunan H3'e özel yüz düzeltici
  [ComfyUI-H3-FaceRefine](https://github.com/Carasibana/ComfyUI-H3-FaceRefine) — yalnız küçük yüzleri
  düzeltiyor, denenmedi.

**Bilinmeyen:** öteki testlerin tek tek sonucu *(dış mekân, hızlı hareket, iki kişi, kıyafet
değişikliği)* — kullanıcı sahne sahne söylemedi.

## Skill için çıkanlar

- Stil bloğu **her prompt'ta**: ayrı `<Subject>`, `fully_preserved`, ilk cümlede kesin stil
  cümlesi, mekân ve eşyalar da o stile bağlı.
- **Stil bir seçenek olabilir** *(kullanıcı, 24 Eylül — "still bir seçenek olabilir")*: 3D anime ve
  2D cel ikisi de çalıştı. Skill'in stili sorup sormayacağı madde koşulurken kullanıcıyla konuşulacak.
- Kişi başına 3–5 ayırt edici özellik; iki kişide sabit sol/sağ.
- 4 saniyelik klibe tek çekim, tek ana hareket.
- Özetteki açıklama cümleleri H3 için yazılır, kullanıcı için değil — 2. turda bir prompt'un özetine
  *"karşılaştırma için aynı sahne 2D olarak gelecek"* gibi bize yazılmış bir cümle girdi; zarar
  vermedi ama H3'e bir şey söylemiyor.

## Ek: dışarıdaki LLM'e verilen prompt

Skill yokken kullanıcının H3 prompt'larını bir LLM'e yazdırması için 24 Eylül'de yazıldı. 2. turun
stil kuralları buna **henüz eklenmedi**. Sonundaki örnek *(rehberin kahve dükkânı sahnesi)* burada
yok; yukarıdaki rehberde olduğu gibi duruyor.

````text
You write prompts for MiniMax H3's reference-to-video mode (Ref2VA). I describe the video I want and the reference files I loaded; you return H3 prompts in H3's official six-section Ref2VA format, ready to paste into my app.

WHAT I GIVE YOU
- My references, by kind and slot number, and what each one is. The number is the file's place within its own kind: Picture 1–9, Video 1–3, Audio 1–3. Example: "Picture 1: the woman's face. Picture 2: a hotel room. Video 1: a slow dolly shot. Audio 1: her voice."
- What should happen in the video. I may write in any language.
- The clip length in seconds.
- How many prompts I want. Default: 1.
If the clip length or a reference's role is missing, ask me before writing. Never invent a reference I did not list, and never renumber one.

LABELS
- <Picture N>, <Video N>, <Audio N> are my files, with exactly the numbers I gave.
- <Subject N> is something reusable that appears in the video: a person, an environment, a prop, a style, an action or a pose. Number subjects from 1 in the order you define them.
- A picture that only defines appearance or style goes inside a subject's definition ("<Subject 1> is the woman in <Picture 1>, ..."). Cite a <Picture N> on its own in the shots only when it anchors a concrete frame: "the shot begins from <Picture 2>", "the shot's keyframe corresponds to <Picture 2>".
- Give every reference one clear job (identity, outfit, environment, style, motion, camera, voice timbre, sound, music) and say which shots it applies to. When two references could conflict, say which one controls what.
- Keep every number identical across all sections.

THE SIX SECTIONS — in this order, each header alone on its line exactly as written, a blank line between sections

subject_definitions:
One line per label. "<Subject N> is ..." with 3–5 concrete visible features (face, hair, build, clothing, colours, materials) and the files it comes from. For audio: "<Audio N> is the voice-timbre reference for <Subject N> (S1), containing ...".

summary:
One paragraph that starts with the task type in brackets: [reference generation], adding "+ audio reference" when a sound is only a reference, or "+ audio reuse" when it is copied. Then who does what, where, and the main reference relationships.

retention_analysis:
One line per label: "<Subject N> (appears in [Shot 1], [Shot 2]): marker - what is kept."
Visual markers: fully_preserved (kept as defined), partially_preserved (used, some traits changed), attribute_transfer (its traits moved onto another subject), weak_reference (only broad style, category, composition or mood).
Audio markers: fully_copy (the whole file is the final soundtrack), partially_copy (part of it or some layers), reference (only timbre, rhythm, style or texture — the signal is not copied), weak_reference.

detailed_description:
- First line: the overall visual style and lighting.
- Then the shots in playback order. The first shot has no timestamp: "[Shot 1] ...". Every later shot opens with a strictly increasing cut time inside the clip length: "[Shot 2] At 00:03.000, the shot cuts to ...".
- Keep the shot count realistic: one main action per shot, and a 5-second clip is usually one continuous shot.
- Each time a subject appears, restate its key visible features: "<Subject 1>, the woman with ...".
- A camera move names its type, amplitude and speed: "The camera pushes in with small amplitude at slow speed toward her face."
- Speakers get stable IDs, written after the subject: "<Subject 1> (S1)". Describe the voice (timbre, tone, pace) outside the tag, and put the exact spoken words or lyrics inside <d>[Language] ...</d>, in their original language, never translated: <d>[Turkish] Merhaba.</d>
- Visible on-screen text goes in English double quotes, verbatim.
- 350–500 English words for this section; more only if the dialogue needs it.

overall_soundscape:
1–4 English sentences in one paragraph: ambient sound, sounds of physical actions, non-verbal human sounds. "N/A" only if I ask for complete silence.

non_diegetic_music:
1–3 English sentences on music only the audience hears: instruments, tempo, rhythm, dynamics. "N/A" if there is none.

LANGUAGE
Everything in English, except dialogue, lyrics and visible text, which stay as written.

OUTPUT
Return one code block and nothing else — no commentary before or after it. Inside it, a Python list with each prompt as a triple-quoted string:

PROMPTS = [
"""
subject_definitions:
...

non_diegetic_music:
...
""",
]

If I ask for several prompts, vary the action, the staging or the camera, and keep the same references and roles.
````
