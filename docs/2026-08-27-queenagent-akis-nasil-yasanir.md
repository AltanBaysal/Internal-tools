# Akış skill'i — nasıl yaşanır

**Tarih:** 27 Ağustos 2026 · **Durum:** tasarım taslağı, henüz kod yok.
**Kardeş belge:** [skill problemleri](2026-08-27-queenagent-skill-problemleri.md) — kararların
gerekçeleri orada.

Bu belge akışı **yaşanmış gibi** anlatıyor: kim ne diyor, ne zaman diske ne iniyor, tur nerede
bitiyor. Amaç, tasarımı tartışmadan önce gözle görmek.

Örnek senaryo: bir bar sahnesi, iki karakter.

---

## Tur 1 — kullanıcı akışı başlatır

Kullanıcı **Yeni sahne** skill'ini seçer, `edit` kipinde, ve yazar:

> Bir bar sahnesi yapmak istiyorum.

Model önce **bakar** — projede ne var:

```
⏺ list_files            No files
```

Boş. Yolu **plana döker** ve ilk soruyu sorar:

```
⏺ write_plan(bar-scene)              Saved
```

`bar-scene-plan.md`:

```markdown
# Bar sahnesi — plan

1. [ ] Karakterler — kimler var, promptları var mı
2. [ ] Mekânlar ve kıyafetler
3. [ ] Kaç kare, ve atlanmaması gereken anlar
4. [ ] Kareleri yaz — JSON'a ve okunacak md'ye
5. [ ] prompt+ ile promptları kur

## Kararlar
*(henüz yok)*
```

> Tamam, sıfırdan kuruyoruz. Yolu `bar-scene-plan.md`'ye yazdım, istersen bakabilirsin — nerede
> kaldığımızı oradan takip ediyorum.
>
> **Karakterler.** Sahnede kimler var? Elinde hazır prompt varsa yapıştır, yoksa anlat — ben
> kurarım.

**Turun sonu.** Diskte: `bar-scene-plan.md`.

Plan her turda güncelleniyor: biten adım işaretleniyor, verilen karar **Kararlar** başlığına
düşüyor. Tur 6'ya gelindiğinde orada *"8 kare — Deniz'in kapıdan girişi atlanmayacak"* yazıyor
olacak, ve bu bilgi sohbetin ortasında kaybolmuş olmayacak.

---

## Tur 2 — karakterler

> İki kişi. Aylin: 25 yaşında, uzun siyah saçlı, yeşil gözlü. Deniz'in promptu hazır:
> `1boy, short black hair, stubble, brown eyes`

Model iki karakteri de kurar — Aylin'i anlatılandan, Deniz'i verilenden — ve **yapı dosyasının
iskeletini** yazar:

```json
{
  "quality": "score_9, score_8_up, score_7_up, masterpiece, absurdres",
  "characters": {
    "aylin": "long black hair, green eyes, mature female",
    "deniz": "short black hair, stubble, brown eyes"
  },
  "outfits": {},
  "locations": {},
  "frames": []
}
```

```
⏺ create_file(bar-scene.json)        Saved
```

> İkisi de kaydedildi. Dikkat: kimlik tanımlarında `1girl` / `1boy` yok — kaç kişi olduğu karenin
> kendi alanı, çünkü aynı karakter bir karede tek başına, ötekinde biriyle beraber.
>
> **Aylin'i görmek ister misin?** Tek başına bir deneme promptu kurabilirim.

**Turun sonu.** Diskte: `bar-scene.json`.

---

## Tur 3 — karakter denemesi *(isteğe bağlı)*

> Evet, Aylin'i göreyim.

Model küçük bir deneme yapısı yazar ve kurar:

```
⏺ create_file(aylin-test.json)       Saved
⏺ build_prompts(aylin-test.json)     1 prompt
```

`aylin-test.py`:

```python
PROMPTS = [
    """score_9, score_8_up, score_7_up, masterpiece, absurdres, 1girl, long black hair, green eyes, mature female, plain background, standing, upper body""",
]
```

> Yapıştırıp bak. Beğenmezsen tanımı değiştiririm.

Asıl senaryonun yapı dosyasına dokunulmadı — deneme karesi gerçek prompt listesine karışmasın diye
kendi dosyasında. İşi bitince silinebilir.

**Turun sonu.** Diskte: `bar-scene.json`, `aylin-test.json`, `aylin-test.py`.

---

## Tur 4 — mekânlar

> İyi görünüyor. Devam.

> **Mekânlar.** Sahne nerede geçiyor? Tek bir bar mı, yoksa kareler farklı yerlerde mi?

*(Kullanıcı cevaplar, model `locations` haritasını `edit_file` ile doldurur. Kıyafetler de burada
sorulur — `outfits` haritası aynı şekilde dolar.)*

**Turun sonu.** `bar-scene.json` güncel: karakterler, mekânlar, kıyafetler dolu; `frames` hâlâ boş.

---

## Tur 5 — karelerde ne görmek istiyorsun

> Loş bir bar, gece. Aylin barda tek başına oturuyor, Deniz içeri giriyor ve yanına yaklaşıyor.

Model **kare kurmadan önce** anlaşmayı arar:

> Anladığım: üç ayak var — Aylin yalnız, Deniz'in girişi, ve ikisinin karşılaşması. Yaklaşık **6-8
> kare** çıkarır. Kaç kare istersin, ve atlamamı istemediğin bir an var mı?

**Turun sonu.** Hiçbir şey yazılmadı — bu tur bir soru turu.

---

## Tur 6 — kareler

> 8 kare olsun. Deniz'in kapıdan girdiği anı mutlaka istiyorum.

Model kareleri **beşerli partiler** hâlinde yazar, her parti bir sonraki yazılmadan diske inerek:

```
⏺ edit_file(bar-scene.json)          Edited
⏺ edit_file(bar-scene.json)          Edited
⏺ create_file(bar-scene-kareler.md)  Saved
```

JSON'daki `frames` dizisi dolar:

```json
{
  "people": "1girl",
  "characters": { "aylin": ["gecelik"] },
  "location": "bar-gece",
  "action": "sitting alone at the bar, holding a glass",
  "camera": "medium shot, from the side"
}
```

İki kişilik karede:

```json
{
  "people": "1boy, 1girl",
  "characters": { "aylin": ["gecelik"], "deniz": ["ceket"] },
  "location": "bar-gece",
  "action": "leaning in to speak, she turns towards him",
  "camera": "medium shot, over the shoulder"
}
```

Ve `bar-scene-kareler.md`, **kullanıcının kendi dilinde**, okumak için:

```markdown
1. Aylin barda tek başına, elinde bardak. Yandan orta plan.
2. Kapı açılıyor, Deniz eşikte. Geniş plan, arkadan.
...
8. İkisi yan yana, konuşuyorlar. Omuz üstü.
```

> Sekiz kare hazır. JSON asıl kaynak; md senin okuman için. Bir kareyi değiştirmek istersen söyle,
> ikisini birden düzeltirim.

**Turun sonu.** Diskte: `bar-scene.json` *(dolu)*, `bar-scene-kareler.md`, ve denemeler.

---

## Tur 7 — devir

Kullanıcı skill'i **prompt+** olarak değiştirir ve yazar:

> Promptları kur.

```
⏺ read_file(bar-scene.json)          42 lines
⏺ build_prompts(bar-scene.json)      8 prompts
```

`bar-scene.py`:

```python
PROMPTS = [
    """score_9, score_8_up, score_7_up, masterpiece, absurdres, 1girl, long black hair, green eyes, mature female, white nightgown, dim bar, night, neon signs, sitting alone at the bar, holding a glass, medium shot, from the side""",
    ...
]
```

İki kişilik karede sıra şöyle çıkar — ana karakter başta, ikinci kişi en sonda:

```
quality, 1boy 1girl, AYLIN, gecelik, bar-gece, action, camera, DENIZ, ceket
```

---

## Bu tek turda olmuyor — ve olmamalı

Yukarıda **yedi tur** var, ve altısı kullanıcının bir cümlesiyle başlıyor. Sebebi tasarım değil,
işin doğası: akış soru soruyor ve cevabı bekliyor. Bir tur içinde soru sorup kendi kendine cevap
vermek, sormamakla aynı şey olurdu.

Skill seçili kaldığı için bu kendiliğinden çalışıyor: kullanıcı cevap yazar, aynı skill bir sonraki
turu karşılar.

### Ama bir sorun var: model nerede kaldığını nereden biliyor

Her tur, sohbetin tamamını yeniden okuyarak başlıyor. Kısa bir akışta sorun yok. Uzayınca iki şey
oluyor:

- **Dikkat ortada düşüyor.** Beşinci turda üçüncü turda verilen karar konuşmanın ortasında kalıyor.
- **Bağlam tavanı var** — 50.000 jeton. Uzun bir intake sohbeti ona yaklaşabilir.

### Karar: akış bir plan yazar ve kendisi takip eder

*(kullanıcı kararı, 27 Ağustos)*

İlk turda skill `write_plan` ile adımları dosyaya döküyor — `bar-scene-plan.md` — sonra onu **kendi
kendine** takip ediyor ve ilerledikçe güncelliyor. Kullanıcının onaylaması gereken bir kapı değil;
kullanıcı için orada duruyor, **görülebilsin diye**.

Neden: nerede kalındığı ve verilen kararlar diskte duruyor. Bağlam ne kadar uzarsa uzasın model
plana bakarak devam edebiliyor, ve kullanıcı planı açıp okuyabiliyor — istersen elle de
düzeltebilirsin.

Alternatif düşünüldü ve seçilmedi: plansız yürümek, durumu yapı dosyasından okumak
*(`characters` doluysa o adım geçilmiş)*. Fazladan dosya istemiyordu ama *"kullanıcı 8 kare
istedi"* gibi kararları hiçbir yerde tutmuyordu.

### Bunun açığa çıkardığı engel

`write_plan` bugün **`edit` kipine verilmiyor.** Araç listesi şöyle
*([modes.py](../../queen-agent/backend/features/workspace/domain/modes.py))*:

| Kip | Araçlar |
|---|---|
| `ask` | `list_files`, `read_file` |
| `plan` | `list_files`, `read_file`, `write_plan` |
| `edit` | `list_files`, `read_file`, `create_file`, `edit_file`, `build_prompts` |

Akış skill'i `edit` kipinde çalışıyor — dosya yazması gerekiyor — ve o kipte `write_plan` elinde
yok. **Yapılacak iş: `write_plan` `edit` kipine de eklenecek.**

Turu bitirme kuralı sorun çıkarmıyor: `ends_the_turn` yalnız `plan` kipinde tetikleniyor, yani
`edit` kipinde plan yazmak turu bitirmiyor ve akış aynı turda devam edebiliyor.

`write_plan`'in üstüne yazması da tam istenen şey: plan ilerledikçe güncelleniyor, ve
`bar-scene-plan-2.md` diye ikinci bir dosya doğmuyor.
