# QueenAgent — Blok 2'nin sistem haritası

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 2 (69, 70, 71,
73, 75, 74).

**Bu belge ne değil:** kodun aynası. CLAUDE.md'nin kuralı — *bir doküman kodun söyleyemediğini
söyler, dosyanın adını verir, çünkü bayatlayan şey kopyadır*. Burada fonksiyon imzası, skill metni
ya da JSON şeması yok. Olan şey: **akışın tamamı**, altı şikâyetin o akışta nereye düştüğü, ve
hangi kararların verilmesi gerektiği.

**Bu belge ne:** Blok 2'nin altı spec'inin türeyeceği kaynak. Bir spec kaynağından türer, tersi
olmaz — o yüzden kapsam ya da karar değişirse önce burası düzelir.

---

## Akış: bir cümle nasıl cevaba dönüyor

```
kullanıcı bir cümle yazar
        │
        ▼
  presentation/routes.py ──────────── HTTP ve SSE. Kural taşımaz.
        │
        ▼
  usecases/stream_answer.py ───────── DÖNGÜ. En fazla 16 raunt.
        │
        ├── _conversation() ◄──────── domain/skills.py
        │     sohbetin tamamı + seçili skill'in metni
        │
        ├── engine.stream() ◄──────── domain/prompt.py  (taban yönerge)
        │     │
        │     ▼
        │   data/xai_engine.py ─────► services/xai/client.py ─────► xAI
        │     (rol çevirisi)            (HTTP, SSE, model adı)
        │
        └── run_tool() ◄───────────── domain/tools.py  (5 araç)
              │
              ├── domain/naming.py ─────────── üstüne yazmama kuralı
              ├── domain/build_prompts.py ──── yapı → prompt listesi
              └── data/file_file_store.py ──── diske yazma, çöp kutusu
```

**Bir raunt** = bir akan istek + o isteğin istediği bütün araç çağrıları, sırayla. Raunt hiçbir araç
istemezse döngü biter. On altıya ulaşmak bir son, hata değil.

**Her raunt sohbetin tamamını yeniden gönderiyor**, üstüne o raundun araç sonuçlarını ekleyerek. 71
tam olarak burayı soruyor.

## Altı madde nereye düşüyor

| # | Şikâyet | Kararın yaşadığı yer |
|---|---|---|
| **69** | Dosya güncellenmiyor, yanına numaralı kopya düşüyor | `naming.py` + `tools.py`'nin `create_file`'ı |
| **70** | İki karakterli karede kişi sayısı iki kez yazılıyor | `build_prompts.py` — karakterlerin sırayla eklendiği yer |
| **71** | Bağlam 300-500k'ya çıkıyor, uzun iş bölünmüyor | `stream_answer.py` — döngü ve `_conversation` |
| **73** | Agentic davranış taban yönergede yok | `prompt.py` (dört paragraf) ile `skills.py` (altı metin) arasındaki boşluk |
| **75** | Promptlar etiket olarak çıkıyor, cümle olmalı | `skills.py`'nin metinleri **ve** `build_prompts.py`'nin birleştiricisi |
| **74** | Altı skill tek akışa insin | `skills.py`'nin sözlüğü |

---

## Üç kuvvet

Altı madde altı ayrı problem değil. Üç kuvvet var, ve maddeler onların yüzeye çıktığı yerler.

### Kuvvet 1 — Modelden *rica* edilen şeyler (69, 70, 74)

[FOUNDATION](../../../queen-agent/FOUNDATION.md)'ın **5. ilkesi** şunu diyor: *modelin her seferinde
tekrarlaması gereken şeyi kod yapar.* Üç madde de bu ilkenin ihlali:

- **69** — "düzeltirken `edit_file` kullan" cümlesi iki skill metninde **ayrı ayrı yazılı**. Rica
  tutmayınca model `create_file` çağırıyor, kod hiçbir şey sormadan yeni bir dosya açıyor.
- **70** — kişi sayısının doğru yazılması modele bırakılmış. Oysa kaç karakter olduğu **kodun
  elinde**: kareyi kuran veri yapısında duruyor ve sayılabiliyor.
- **74** — aynı davranışlar altı metinde tekrar ediyor. Somut iki örnek: *"düzeltince dosyayı da
  düzelt"* iki skill'de, *"hepsini tek cevapta yazma, parça parça ver"* üç skill'de.

Bu üçü aynı ilaçla iyileşiyor: **rica koda dönüşür.**

### Kuvvet 2 — Kullanıcının emeği (69'un açık sorusu)

FOUNDATION'ın **1. ilkesi** en üstte: *kullanıcının emeği kutsal.* `naming.py` bu ilkenin kodudur —
hiçbir şey üstüne yazılmıyor, `plan.md` ikinci kez yazılınca `plan-2.md` oluyor. Kuralı tamamen
kaldırmak 1. ilkeyi kaldırmak demek.

**Ama kural zaten bir kez esnedi, ve esnemesinin gerekçesi kodda yazılı.** `build_prompts` çıktısını
**üstüne yazıyor**, ve sebebi şu: o dosya **türetilmiş**. Kaynağı diskte duruyor, yeniden
üretilebiliyor, ve numaralamak hangisinin güncel olduğunu okunamaz hâle getiriyor.

Ayrım burada duruyor ve 69'un cevabı bu olabilir:

| | Üstüne yazılır mı |
|---|---|
| Kullanıcının emeğini taşıyan dosya *(senaryo, kareler, karakter)* | Hayır — kaybolan geri gelmiyor |
| Koddan türeyen dosya *(prompt listesi)* | Evet — kaynağından yeniden üretilebiliyor |

**Verilecek karar:** 69 bu ayrımı mı kullanacak, yoksa başka bir çizgi mi çekecek. Çünkü bir senaryo
dosyası da "düzeltilmek istenen" bir dosya, ve türetilmiş değil.

### Kuvvet 3 — Bağlam (71)

Tek başına duruyor ve şartı artık sağlanmış: **76 ölçüyü kurdu**, sayı ekranda. 71'in seçeceği yol
o sayıya bakarak seçilecek — FOUNDATION'ın 3. ilkesi ölçülmemiş bir sorunu optimize etmeyi
yasaklıyor.

Bugün bilinen: her raunt sohbetin tamamını yeniden gönderiyor, ve bir cevap on altı raunda kadar
dönebiliyor. Bilinmeyen: bunun ne kadarının önbellekten geldiği, yani gerçekte ne kadarının
ödendiği. Sayı bunu söylüyor.

---

## Prompt dili nerede yazılı (75)

75 diğerlerinden farklı: **iki yerde birden yaşıyor**, ve ikisi ayrı kararlar.

1. **Skill metinlerinde** — promptun neye benzeyeceğini tarif eden cümleler orada. *"Asla cümle
   değil"* diyen metin bu.
2. **`build_prompts.py`'nin birleştiricisinde** — kodun kendisi parçaları **virgülle** birleştiriyor
   ve boş parçaları atıyor. Yani etiket biçimi yalnız yönergede değil, **kodda**.

Metni değiştirip kodu bırakmak işe yaramaz: yapıdan kurulan promptlar yine virgülle birleşir.

**Bu, 75'i 74'ten önceye koyan bağın sebebi** *(yol haritasında yazılı)*: dil belli olmadan altı
skill tek metne indirilirse aynı metin iki kez yazılır.

## Taban yönerge ile skiller arasındaki boşluk (73)

`prompt.py` dört kısa paragraf: kim olduğu, projeyi görebildiği, ne zaman dosya yazacağı, cevabı
sohbete de yazacağı.

`skills.py` altı uzun metin, ve **ortak davranış onların içine dağılmış**. Skill seçilmeyen bir
konuşmada o davranışın hiçbiri yok — model plan yapmıyor, yazmadan önce okumuyor, sonunda ne
yaptığını söylemiyor.

**73'ün işi:** hangi skill seçili olursa olsun geçerli olan davranışı tabana taşımak. **74'ün işi:**
taban söylemeye başlayınca skillerdeki fazlalığı bırakmak. Sıra bu yüzden zorunlu.

---

## Sırayı zorlayan bağlar

Yol haritası bunları zaten taşıyor ve burada tekrarlanmıyor — orada okunur. Özeti: **68 → 76 → 71**
*(ölçü, optimizasyondan önce)*, **73 → 74** *(taban, sadeleşmeden önce)*, **75 → 74** *(dil, tek
metinden önce)*.

Kalan altının sırası: **69 · 70 · 71 · 73 · 75 · 74**.

## Verilecek kararlar

Altısının da spec'i açılmadan önce bir soru kapanıyor. Hepsi çıktının doğruluğu ya da modelin
davranışı hakkında — ekran hakkında değil, o yüzden Blok 2 beraber koşuluyor.

| # | Kapanacak soru |
|---|---|
| **69** | Üstüne yazma nerede serbest, nerede yasak. Türetilmiş/emek ayrımı yeterli mi |
| **70** | Diskte bugün duran yapı dosyalarındaki sayı etiketleri temizlenecek mi, yoksa kod onların üstüne mi yazacak |
| **71** | Bağlamın hangi yolla yönetileceği — 76'nın sayısına bakarak. **Bölünmesi bekleniyor** |
| **73** | Tabana hangi davranışlar iniyor |
| **75** | Kalite etiketleri cümlede ne olacak · diskteki etiket biçimli dosyalar dönüştürülecek mi · 70'in kişi sayısı cümlede nasıl söylenecek |
| **74** | Hangi skiller düşecek. Bir aday belli: promptları elle yazan yol, yapıdan kuranla aynı işi yapıyor ve karakteri elle kopyaladığı için 5. ilkeyle çarpışıyor |

## Bu haritanın söylemediği

- **Kodun kendisi.** Fonksiyon adları, imzalar, veri şekilleri — hepsi yukarıda adı geçen
  dosyalarda, ve orada okunur. Buraya kopyalanan her satır bir sonraki değişiklikte yalan olurdu.
- **Çözümler.** Her maddenin nasıl çözüleceği kendi spec'inde, kendi turunda yazılır.
- **Blok 4.** Ekran işleri; bu haritanın dışında.
