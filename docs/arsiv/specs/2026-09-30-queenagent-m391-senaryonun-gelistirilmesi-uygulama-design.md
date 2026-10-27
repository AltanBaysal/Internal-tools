# Madde 391 — Senaryonun geliştirilmesi: Start a scenario sonunda kontrolleri yapar · uygulama turu

> **30 Eylül güncellemesi — kullanıcıyla satır satır yazıldı.** Aşağıdaki metin ilk taslak; son hâli
> [prompt.py](../../../queen-agent/backend/features/workspace/domain/prompt.py)'de, `START_A_SCENARIO`'nun
> 6 – 9. adımları. Kullanıcı metni satır satır okudu, her satırı kendisi düzeltti. Taslaktan farkı:
>
> - **Dört kontrol, üç değil.** Yeni 6. adım: her sahne tam dört saniyelik bir video olur. Sığmayan
>   sahne, bütün olayları korunarak sığacak şekilde yeniden yazılır; sığmıyorsa ikiye bölünür. Neyin
>   önemli olduğuna model karar vermez *(kullanıcı — "yapay zeka neyin önemli olduğuna karar
>   vermesin")*. Eski 6, 7, 8 birer kaydı.
> - **Her kontrol üç kısım:** *Context* neden yapıldığını söyler; *Part 1 -- review* kullanıcıya tek kısa
>   satırla ne geliştirdiğini söyler, build edilmiş prompt dosyasını okur, sorunlu kareleri ve
>   nedenlerini kendi `-review-N.md` dosyasına yazar — sorun yoksa dosya yazılmaz; *Part 2 -- fix*
>   yalnız o kareleri düzeltir.
> - **Kontroller build edilmiş dosyaya bakar**, karelerin tek tek alanlarına değil: sorun çoğu zaman
>   parçaların birleşiminde çıkar *(kullanıcı — "sadece action değil prompt kombinasyonu problem")*.
>   Düzeltme parçanın senaryo dosyasında geldiği yerde yapılır; başka kareler de aynı kaydı
>   kullanıyorsa kare için yeni kayıt açılır.
> - **Araç adı ve alan listesi yok** *(kullanıcı — "hangi tool olacağını belirtme llm zaten yeterince
>   güçlü çözer"; "tek tek isim verirsek yeni bir field eklediğimizde kırılır")*.
> - **Görsel kontrollerin (7 – 9) başında:** "The image model is weak and draws every tag in the
>   prompt." 8. adım yalnız karakteri değil her gizli tag'i arar — oda, kıyafet — ve örneği saç.
> - **Değişiklik raporu ve kapanış bölümü yok:** son adım prompt'ları yeniden kurar ve kullanıcıya
>   tamamlandığını söyler, o kadar.
> - **Basit İngilizce, zamir yok, başlıklar adımın işini söyler.** Tavan 1220: metin kullanıcıyla
>   yazıldıktan sonra 1212 kelime geldi, prompt'a dokunmadan tavan yazılı gerekçesiyle yükseldi.
> - Dört saniyelik video ve ilk kare bilgisi açılışa, sonraki bir maddede gider —
>   [prompt istekleri](../research/2026-09-30-queen-agent-prompt-istekleri.md), bölüm 3.

**Kaynak:** [test turunun spec'i](2026-09-30-queenagent-m391-senaryonun-gelistirilmesi-testler-design.md) —
kullanıcının kararları, kapsam ve testlerin tuttukları orada. Bu tur `test_skills.py`'de çalışma
ağacındaki 18 kırmızıyı yeşile getirir, ve başka hiçbir şey yapmaz.

**Kullanıcıdan gereken:** hiçbir şey. **Commit yok:** kullanıcı Changes'ten okur.

## Ne değişir

Yalnız [prompt.py](../../../queen-agent/backend/features/workspace/domain/prompt.py):

1. `START_A_SCENARIO`'nun metni (aşağıda).
2. Skill metinlerinin üstündeki yorumun son cümlesi. Bugün *"From here a sentence enters only by
   deleting one."* diyor; 391 tavanı yazılı bir kararla yükselttiği için artık doğru değil. Yeni hâli:
   *"From here a sentence enters only by deleting one, or by a written decision that raises the cap --
   the test keeps each one beside it."*

Başka sabit, araç açıklaması, skill, `WRITE_FRAME_SYSTEM_PROMPT`, `skills.js` ya da `dist` değişmez.

## Yaklaşımlar

- **Seçilen — her adım kendi kurallarını taşır.** 6, 7 ve 8 kendi başlıklarıyla, kendi madde
  işaretleriyle; her biri listeyi yeniden kurar, neyi değiştirdiğini söyler ve onay beklemediğini
  kendisi söyler. Kullanıcının istediği bu (*"promtplarda ayrı fiedlar açma"*, *"Direkt güncellesin
  yazsın sadece neyi değiştidğini"*), ve metnin geri kalanının biçimi de bu: 1. adım onay beklemediğini
  kendi satırında söylüyor.
- **Reddedilen — ortak kuyruğu bir kez, *How a step runs*'da söylemek.** Kelime tasarrufu ~50, ama o
  bölüm her adımın nasıl yürüdüğünü söylüyor ve orada *"wait for their yes"* yazıyor; üç adımın istisnası
  oraya yazılınca aynı bölümde iki kural çatışır. Zayıf model bir adımı okurken o adımın bütününü önünde
  görmeli.
- **Yasak — ayrı sabit** (`THE_CHECKS` gibi): geri alınan deneme buydu, ve T13 onu kırmızı yapar.

## Metin — modelin aldığı hâliyle

1 – 4. adımlar ve *How a step runs* değişmez. Açılışta yalnız sayı değişir:

```
... walking the user through eight steps in order, by asking.
```

5. adımdan sonrası:

```
Step 5 -- the prompts
- Fill the waiting frames with write_missing_actions, then write the list with build_prompts.
- This step waits for no approval. Go on to Step 6 in the same turn.

Step 6 -- one moment
- Where a frame's scene or action tells more than one moment, bring it down to one moment, or split it into one frame per moment.
- To bring it down, give update_frame the new scene and an empty action. To split it, bring it down to its first moment, then write the other moments with add_scene, before the next frame.
- Then fill those frames with write_missing_actions.
- Call build_prompts again if you changed anything, then say which frames you changed and what. If nothing needed changing, say so in a line.
- This step waits for no approval. Go on to Step 7 in the same turn.

Step 7 -- visible parts
- Read the camera angle in each frame's action. A part of somebody the angle hides must not be in that frame's prompt, or the model draws it anyway or puts it on somebody else.
- For such a frame, write a second entry of only what shows, with add_character or add_outfit, named for it, as in "man body no face" or "dress from behind". If one is already there, use it.
- Give update_frame the frame's cast with that entry in place of the whole one. Somebody the angle does not show at all leaves that frame's cast. The whole entries stay as they are.
- Call build_prompts again if you changed anything, then say which frames you changed and what. If nothing needed changing, say so in a line.
- This step waits for no approval. Go on to Step 8 in the same turn.

Step 8 -- can it be drawn
- Read the prompts build_prompts wrote. The image model is very weak: can it produce each one as it is written?
- Where a part cannot be produced as written, simplify it where it comes from, and keep the moment: the action with update_frame, or an entry with update_character, update_outfit or update_location.
- Call build_prompts again if you changed anything, then say which frames you changed and what. If nothing needed changing, say so in a line.
- This step waits for no approval. Close by naming the file and saying it is ready. Do not print the prompts back, offer nothing, and ask nothing: this is the last word.
```

## Kararlar

1. **Araçlar gerçekte çalıştıkları gibi.** Bir kareyi tek ana indirmek `update_frame`'e yeni sahne ve
   boş aksiyon vermek — `UPDATE_FRAME_ACTION`: boş aksiyon kareyi *"nobody has written yet"* hâline
   döndürür. Bölmek: ilk anı aynı yoldan, kalan anlar `add_scene` ile *before* sonraki kare
   (`ADD_SCENE`: *"unless before names a frame to go in front of"*); yeni kareler aksiyonsuz doğar.
   İkisini de `write_missing_actions` doldurur (*"what is waiting is what is empty"*). 7. adımda kadro
   `update_frame` ile bütün olarak verilir (`UPDATE_FRAME_CHARACTERS`: *"Replaces the whole cast"*).
2. **8. adım kullanıcının sorusunu sorar**, bir iddia yazmaz: *"The image model is very weak: can it
   produce each one as it is written?"* — *"çok zayıf"* kullanıcının kendi öncülü. *"image model"*
   açılışın modele verdiği ad. Modelin neyi çizemeyeceği yazılmaz.
3. **Örnek adlar çift tırnakta.** *"as in man body no face or dress from behind"* tırnaksız
   *"no (face or dress)"* diye okunabilir; tırnaklar ikisini ayırır, ve metnin kuralı kullanıcının
   sözlerini çift tırnağa koymak — iki örnek de kullanıcının (roadmap'teki 371).
4. **Kapanış sözü değişmeden** 8. adımın son madde işaretinde, 1. adımın *"This step waits for no
   approval. …"* satırının biçimiyle: önce onay cümlesi, sonra adımın ardından gelen.
5. **6. adımda gerekçe cümlesi yok**; 7. adımınki kullanıcının kendi sözü (*"yoksa model … öteki
   karakterler ekliyor"*). Kullanıcı fazla yazmayı istemiyor.

## Kelime sayısı

`split()` ile: bugünkü metin 427; yeni metin 799 (427 − 27 taşınan kapanış madde işareti + 16 yeni
5. adım satırı + 6. adım 114 + 7. adım 152 + 8. adım 117). Tavan test turunda 800 oldu.

## Mevcut testlerin gözetildiği yerler

Metinde yok: `shot`, `framing`, `one at a time`, `scene list`, `who is in it`, `edit_file`, `schema`,
`complex`, `what is simple`, `cannot draw`. Alt çizgili her kelime bir araç adı (`update_frame`,
`add_scene`, `write_missing_actions`, `build_prompts`, `add_character`, `add_outfit`,
`update_character`, `update_outfit`, `update_location`) ya da `pov_`; hiçbiri iyelik eki almıyor.
`create_file` hâlâ 2. adımdan önce, `start_scenario` 2 ile 3 arasında; son `build_prompts` 5. adımdan
sonra; *"a step ends when they approve it"* ve *"offer nothing, and ask nothing"* duruyor.

## Nasıl görülür

Dört satır, paralel: `python -m pytest queen-agent -q` tamamen yeşil (986), öteki üç süit yeşil.
Adım adım dökümü [uygulama planında](../plans/2026-09-30-queenagent-m391-senaryonun-gelistirilmesi-uygulama-plan.md).
