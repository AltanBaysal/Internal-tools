# Queen Editor — Yol Haritası v11

**Durum:** Hazırlanıyor · 0/5 bitti

**Önceki sürüm:** [v10](2026-10-20-queen-editor-v10-roadmap.md) — bitti.

**Sıra: tek tek, dalga yok** *(kullanıcı, 27 Ekim — "ilk queen ediytor tasklarını yapıcaz bitincebana
haber vericeksin queen anget tasklarına geçiçez"; "sıryaal paralel yapmicaz")*. Koşu bu roadmap'le
başlar, QueenAgent v12 bundan sonra gelir. Bir madde birleşince sıradaki başlar; worktree açılmaz, iş
ana klasörde koşunun dalında yürür.

1. **v11-3** — Drive'a kayıt olmayınca hata. Fotoğraf kaybettirdiği için ilk.
2. **v11-2** — sıra boşken bildirim.
3. **v11-1** — Krea'da SNOFS + Slime, ve Qwen.
4. **v11-5** — arşiv; koşunun belgeleri yazıldıktan sonra, linkler bir seferde düzelsin diye.
5. **v11-4** — femboy LoRA'sı, kullanıcıyla, en sonda *("bir femboy taskını son al çünkü ban ihtiaçın
   olcak")*. Bitince kullanıcıya haber verilir, sonra QueenAgent v12'ye geçilir.

---

| Numara | İş | Durum |
|---|---|---|
| [v11-1](#v11-1) | Translucent Penetration: Krea'da, ve Qwen yeni model olarak | `ALIGNED` |
| [v11-2](#v11-2) | Sıra boşken bildirim | `ALIGNED` |
| [v11-3](#v11-3) | Drive'a kayıt olmayınca hata verip dursun | `ALIGNED` |
| [v11-4](#v11-4) | Femboy LoRA'sı | `ALIGNED` |
| [v11-5](#v11-5) | Eski belgeler ve roadmap'ler arşive | `ALIGNED` |

---

<a id="v11-1"></a>
### v11-1 — Translucent Penetration: Krea'da, ve Qwen yeni model olarak

**Kabul koşulu:**
- Krea seçiliyken LoRA kutusunda üç seçenek var: **SNOFS** (bugünkü gibi, varsayılan), **SNOFS + Slime**
  (ikisi birlikte yüklenir) ve **Boş** (LoRA yok).
- Fotoğraf üretirken **Qwen Image 2.1 Turbo** seçilebiliyor. LoRA kutusunda iki seçenek var:
  **Translucent Penetration** ve **Boş**.
- Bir Krea senaryosunun kareleri Qwen seçilerek de üretilebiliyor.

Bugün Translucent Penetration panelde "Slime" adıyla yalnız Nova ve DaSiWa'da var. Krea onu
kullanmıyor; kendi graph'ındaki SNOFS'la çiziyor. Qwen ise 484'ün denemesinden sonra Queen Editor'e
hiç girmedi.

**Kullanıcının kararları** *(27 Ekim)*:
- **Krea'da SNOFS'un yanına girer:** *"SNOFS'un yanına girsin. İkisi aynı anda yüklenir. Slime
  fotoğrafında SNOFS da etkisini sürdürür."*
- **Seçilince devreye girer, ve bir de Boş seçeneği olur:** *"Seçilince. Panelde Krea'nın LoRA kutusuna
  "SNOFS + Slime" gibi bir seçenek eklenir. Seçilmezse bugünkü gibi yalnız SNOFS çizer."*; *"bir de
  snofs olmadan bir sürümünü eklme boş"*.
- **Qwen doğrudan Queen Editor'e girer:** *"queen editore direkt girsin ve tek lora translucent
  penetration olsun"*. Deneme yapılmaz.
- **Hangi Qwen:** *"Qwen Image 2.1 Turbo: resmi şablon, 8 adım, cfg 1."*
- **Qwen'in LoRA kutusu:** *"boş ve etransulent penetration 2 versiyon"*.
- **Qwen'in prompt'ları** *(cevap: "3")*: şimdilik Krea senaryosu Qwen'le de çizilir, QueenAgent'ta bir
  şey değişmez. LoRA'nın tetik kelimesini, Nova'daki Slime'da olduğu gibi Queen Editor ekler. İlk
  fotoğraflar Qwen'in ayrı kural istediğini gösterirse QueenAgent'a ayrı bir madde açılır.

<a id="v11-2"></a>
### v11-2 — Sıra boşken bildirim

**Kabul koşulu:** Sıra 10 dk boş kalınca ekranda "orada mısın?" çıkıyor ve tarayıcı bildirimi
geliyor. Sıra boş kaldıkça ikisi her 10 dk'da bir yeniden geliyor. Bir export ya da ajanın cevabı
sürerken ikisi de gelmiyor.

**Neden:** Colab boşta açık kalınca A100 boşa para yiyor, ve sekme arka planda kalmış olabilir.

**Kullanıcının kararları** *(27 Ekim)*:
- **Süre:** *"10dk"*.
- **Bildirim:** *"bir de bildirim atabiliryosa iyi olur arkaplanda kalmış olabilri çünkü"*.
- **Colab'ı kapatmak bu maddeden çıktı:** *"bence bunu roadmapten backloga koyalım şuanlık kapatmak
  yerine bildirim yollasın sadece ve 1 sayılsın"*. "1": süren export ya da ajan cevabı iş sayılır.
  Kapatma [BACKLOG.md](../../queen-editor/BACKLOG.md)'de, *"Boşta Colab kapansın"*.
- **Tekrar** *(cevap: "2")*: bildirime cevap gelmezse sıra boş kaldıkça her 10 dk'da bir yeniden gelir.
- **Ekranda da sorulur** *(cevap: "yes")*: bildirimle birlikte ekranda "orada mısın?" çıkar.

<a id="v11-3"></a>
### v11-3 — Drive'a kayıt olmayınca hata verip dursun

**Kabul koşulu:**
- Drive'a kayıt hangi sebeple olmazsa olsun, fotoğrafta, videoda ve export'ta ekranda bir hata çıkıyor
  ve o sırada süren iş duruyor.
- Ekranda bitmiş görünen her iş, Colab kapatılıp açıldıktan sonra da Drive'da duruyor.

**Ne oldu** *(kullanıcı, 27 Ekim)*: fotoğraflar üretildi ve ekranda hepsi bitmiş göründü; *"ai bazen
düzgün fotoğraf üretmiyor bozukları siliyoruz"*. Sonra videolar üretildi, bozukları silindi, ve Colab
kapatıldı. Yeniden açılınca fotoğrafların yarısı yoktu. Hiç hata görülmedi; *"fotoğraf için yok bu
arada çalışmıyor video içindeo lmuyor"*.

**Kullanıcının kararları** *(27 Ekim)*:
- *"karmaşıklaştırma hata versin ve üretim yad aexport ne yapılıyorsa dursun"*. Önceden uyarı da işi
  bekletme de yok.
- *"drive dolduğuan özel değil drive kayıt olmadığında genel bir hata çıksın"*.
- Durduktan sonrası *"normal hata davranışı neyse o"*: bugün üretimi durduran bir hatada iş sıradan
  düşmüyor, yeniden başlatınca o kare yeniden çiziliyor.

**Spec'in ilk işi sebebi görmek.** Kodda Drive'a yazma hatası üretimi durduruyor, ama kullanıcı hiç
hata görmedi. İki tahmin var: Colab'ın Drive bağlantısı dosyayı önce kendi diskine yazıp Drive'a sonra
ve sessizce gönderiyor olabilir; ya da bozuk bir karenin silinmesi, dosyasını paylaşan başka bir karenin
fotoğrafını götürüyor olabilir.

<a id="v11-4"></a>
### v11-4 — Femboy LoRA'sı

**Kabul koşulu:** Adayların deneme sonucu yazılı. Kullanıcının seçtiği LoRA Queen Editor'de Nova ve
DaSiWa'nın LoRA kutusunda seçilebiliyor.

**Kullanıcının kararları** *(27 Ekim)*: *"Seninle birlikte, deneme notebook'unda. femboysXL ve
Civitai'den 1–2 aday daha ComfyUI'de denenir, hangisinin kalacağına sen karar verirsin."*; *"bunu
yapalım sonra karar veridğimizi queen editore koyarız"*. Deneme notebook'u
`collab-toolbox/photo_experiments/` altına girer.
- **QueenAgent'a ne gider:** *"şöyle özel bir prompt gerkeilyors mesela bir tetik çümlesi bu roadmpai
  koşarken queen agent yeni bir görev aç unaligned gerkiyorsa tabi"*. Seçilen LoRA bir tetik cümlesi
  gibi özel bir prompt istiyorsa, koşu sırasında QueenAgent v12 roadmap'ine `UNALIGNED` yeni bir
  madde açılır; istemiyorsa açılmaz.
- **Sıra:** *"bir femboy taskını son al çünkü ban ihtiaçın olcak"*. Deneme kullanıcıyla birlikte
  yapıldığı için bu madde koşunun en sonunda yürür.

<a id="v11-5"></a>
### v11-5 — Eski belgeler ve roadmap'ler arşive

*(Kullanıcı, 26 Ekim — "ee bu belgeyi arayacak claude code böyle yaparsan queen editor roadmapine
eklemeyi ve düzeltemeyi belgleri ve eski roadmpaleri arşive almayı".)*

**Kabul koşulu:**
- Eski bir belgede adı geçen her belge, linkine tıklanınca açılıyor.
- `docs/roadmaps/`, `docs/specs/`, `docs/plans/`, `docs/research/` ve `docs/design-needs/` içinde
  yalnız açık sürümlerin ve açık işlerin belgeleri duruyor; bitenler `docs/arsiv/`'de.

`4403108a`, `docs/` kökündeki on çalışma notunu sildi ve onlara giden linkleri düz yazıya çevirdi.
Örneğin v6 roadmap'inde şimdi yalnız *"skill problemleri belgesi"* yazıyor. Bunu okuyan, Claude Code
da olsa, o belgeyi arar ve bulamaz.

**Kullanıcının kararları** *(27 Ekim)*:
- **Tek arşiv** *(cevap: "Önerim: 1")*: `docs/arsiv/`, içinde `roadmaps/`, `specs/`, `plans/`,
  `research/`, `design-needs/` ve `notlar/`.
- **Arşive girenler:** *"1'dekiler, ayrıca bitmiş işlere ait research/ ve design-needs/ belgeleri."*
  Yani biten sürümlerin roadmap'leri, spec'leri ve planları; git'ten geri gelen on not
  (`notlar/`'a); ve bitmiş işlere ait `research/` ile `design-needs/` belgeleri.
- Taşınan her belgeye giden linkler yeni yere göre düzeltilir, düz yazıya çevrilmiş linkler de yeniden
  link olur. Spec'lerin çoğu kendi roadmap'ine link veriyor, bu yüzden bu iş yüzlerce linke dokunur.
