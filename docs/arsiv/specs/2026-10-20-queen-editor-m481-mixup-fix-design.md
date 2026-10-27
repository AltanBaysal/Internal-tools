# Madde 481 · Ajan karışan kareleri düzeltir — tasarım

**Tarih:** 20 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
481 · v10-7c · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey. Madde 20 Ekim'de hizalandı. Kod okununca çıkan soru ana ajana soruldu: brief'teki "aynı
kareye yazan bir fotoğraf işi" yolu ekranda eski fotoğrafı gösterirdi (aşağıda, "Neden yeni bir
kimlik"). Ana ajan 20 Ekim'de B'yi seçti — eski karenin yerinde yeni bir kimlik — ve aşağıdaki küçük
seçimlerin hepsini onayladı.

## Ne, neden

Kullanıcının sözü: *"prompt'u güncelle ve direkt çalıştır runı abicim tekt ek queeye koy ... direkt
güncelle eski fotoyu sil runı başlat sonraki fotoya geçe gibi"*; *"ama eski fotopğralar aynı yerde olur
sırası yeni bir yer egeçmez bak"*; *"promptu güncellesin gerekirse negatif promptunu geliştirisn
gerekirse tag silsin normalde kendiki karar versin model karıştırsada seed değiştirmek kurtamıyor
yani"*.

Kullanıcı "düzelt" deyince ajan 479'un listesindeki karışan kareleri birer birer düzeltir:

- Sebebe kendisi bakar ve düzeltmeye kendisi karar verir: karışmaya yol açan etiketi siler, negatif
  prompt'u geliştirir, ya da ikisini birden yapar.
- Yeni seed bir düzeltme değildir: düzelten sözlerdir, yeniden seed değil. Yalnız prompt ve negatif
  değişir; seed karenin kartındakidir (aşağıda, karar 2).
- Her kare için tek bir `fix_frame` çağrısı yapar, 480'in kapısının arkasında. Kullanıcı ekranda
  İzin ver ya da Reddet der.
- İzin ver'de karenin prompt'u ve negatifi güncellenir, eski fotoğraf silinir, yenisi **aynı yerde,
  aynı sırada** kuyruğa girer. Ajan fotoğrafı beklemeden sıradaki kareye geçer.
- Reddet'te kareye dokunulmaz.
- Videosu olan kareye dokunulmaz; videosu sırada olana da (aşağıda, karar 3).

## Bugün — koddan okunanlar

- **Yeniden üret** (`regenerate.py`, madde 77): sonucu yeni bir kare olarak eskinin üstüne, yanına
  koyar. Yeni kimlik madde 99'un kuralıyla verilir: aynı sözler ailenin sıradaki varyantı, yeni sözler
  sıradaki numara. `order.json` bütün sırayla yeniden yazılır.
- **Fotoğrafın adı karenin kimliğidir:** fotoğraf `photo_file(id)` olarak, yani `P3_0.png` olarak
  kaydedilir (`run_loop.py`). Sunucu fotoğrafları
  `Cache-Control: public, max-age=31536000, immutable` ile verir (`routes.py`). Bunun dayanağı "bir
  fotoğraf adresinin baytları hiç değişmez" kuralı; `next_number` ve `next_id` hiçbir adı bu yüzden
  yeniden kullanmaz.
- **Bir dosyayı iki kare tutabilir:** kopya kare kaynağının fotoğrafını paylaşır (madde 102).
  `files_to_unlink`, bir dosyayı ancak onu tutan son kare bırakınca siler.
- **Plan yalnız eklenir.** Bir kare için iki satır olursa kuyruk en sonuncusundan üretir
  (`queue._latest_per_frame`). Galerinin kartı ise karenin ilk satırından okunur
  (`list_frames`, `opening`).
- **Karenin negatifi** kartın `negative`'idir: planlı kartta plan satırının, kayıttan okunan kartta
  fotoğraf satırının. 479'un ajan kartında yoktu.
- **Karenin model, LoRA ve yönü** plan satırındadır. Kayıttan okunan bir kartta — kopya kare, plandan
  önceki kare — bunlar yoktur.
- **Bir partide yapılan varyantlar** başın seed'iyle üretilir (madde 411). Varyantın kendi plan
  satırındaki seed hiç kullanılmamıştır, ama kartın `seed`'i o satırdandır.
- **Bağlı video** (madde 402) kuyrukta beklerken bitiş karesinin fotoğrafını, sırası gelince okur
  (`linkedTo`).

## Neden yeni bir kimlik

Brief'in yolu, aynı kimliği yeniden üretmekti: planda aynı kimliğe yeni bir satır, slotu `queued`,
dosyayı sil. Bunun üç sorunu var:

1. **Eski fotoğraf ekranda kalır.** Yeni fotoğraf aynı adla (`P3_0.png`) iner. Eskisini bir kez
   göstermiş her tarayıcı, değişmez önbellekten eskisini bir yıl boyunca göstermeye devam eder.
   "Yenisi aynı yerde üretiliyor" ekranda görünmez.
2. **Paylaşılan dosya değişir.** Örneğin P3_0'ın videosu yok, ama video kopyası P3_1'in fotoğraf slotu
   `P3_0.png`'yi gösteriyor ve P3_1'in videosu o fotoğraftan yapılmış. P3_0'ı yerinde yeniden üretmek
   `P3_0.png`'nin üstüne yazar, P3_1'in fotoğrafı videosunun altında değişir. Bu, "videosu olan kareye
   dokunulmaz"ı bozar, ve aynı kimlikle bunun bir çaresi yok.
3. **Detay sayfası eski negatifi gösterir.** Kart ilk satırdan okunduğu için `list_frames`'in
   değişmesi gerekirdi.

**Seçilen (B):** yeni fotoğraf yeni bir kimliktir, ve eski karenin `order.json`'daki yerine konur.
Eski karenin fotoğrafı silinir, kart galeriden çıkar.

- Galerinin numarası aynıdır, galerideki yeri aynıdır, kuyruktaki yeri aynıdır.
- Önbellek kuralı ve paylaşılan dosyalar olduğu gibi kalır.
- Mevcut koddan hiçbir şey yeniden yapılandırılmaz: yeni bir iş türü yok, döngü değişmez. Yalnız var
  olan kurallar kullanılır: `family`, `next_id`, `known_ids`, `next_number`, `files_to_unlink`,
  `list_frames`, `run_queue`.

**Görünen bedel:** karenin kimliği, yani detay sayfasının adresi değişir, ör. `/photos/P3_0` →
`/photos/P12_0`. Eski karenin detay sayfası açıksa o kare artık yoktur.

## Ne değişir

### 1. `fix_photo` — fotoğraf özelliğinde yeni kullanım durumu

`features/photo_generation/domain/usecases/fix_photo.py`:

`fix_photo(runner, store, record, plan_store, order_store, producers, now, project, seen, prompt,
negative, …)` → `"fixed"`, `"waiting"`, `"changed"` ya da `"linked"`.

1. **Galeri bir kez okunur** (`list_frames`). Proje yoksa `"changed"` döner.
2. **Bayatlık kontrolü.** Kare kimliğiyle (`seen["id"]`) bulunur, galerideki numarasıyla asla. Kartın
   şu alanları ajanın gördüğüyle karşılaştırılır: `status`, `layers`, `owed`, `failed`, `prompts`,
   `negative`. Biri değişmişse ya da kare yoksa hiçbir şey yazılmaz ve `"changed"` döner. Prompt ya da
   negatif değişmiş, fotoğraf gitmiş, bir video gelmiş ya da sıraya girmişse: hepsi bu alanlarda
   görünür. Video kuralının kodda ikinci bir kopyası yok.
3. **Bağlı videonun bitişi.** Kuyruğun açık işlerinden biri (`queue.open_jobs`) bu kareye bağlı bir
   videoysa (`linkedTo`), hiçbir şey yazılmaz ve `"linked"` döner: fotoğraf silinirse o video sırası
   gelince bulamadığı bir karede düşerdi. Yapılmış bir bağlı video kendisine verilen resme zaten
   varmıştır; o kare düzeltilir.
4. **Yeni kimlik**, yeniden üretin kuralıyla (madde 99): aynı prompt (boşluklar sayılmaz) ailenin
   sıradaki varyantını alır, ör. `P1_1`; yeni prompt sıradaki numarayı, ör. `P12_0`. Kopya bir karenin
   (`C1_P1_0`) adı kaynağının ailesini taşır: aynı sözlerle düzeltilen kopya `P1_1` olur.
5. **Plan satırı:**
   - yeni prompt ve negatif;
   - kartın seed'i: planlı kartta satırının, kopya kartta kaynağının kayıt satırının. Bir partide
     yapılmış varyantta bu, partinin hiç kullanmadığı kendi satır seed'idir (madde 411); yalnız
     üretilen resim partinin resmi olmaz — başka sözlerle zaten olamazdı. Düzelten sözlerdir, yeniden
     seed değil;
   - model, LoRA ve yön, karenin fotoğrafını yapan plan satırından (`copy_frame.made_by`, kareler
     arasında resim paylaşmanın kuralının durduğu yerde). O satır fotoğrafın dosya adından bulunur
     (`frame_id_of(card["file"])`), yani kopya kare kaynağınınkileri alır; plan hiç kırpılmadığı için
     kaynak silinmişse de satırı oradadır. Satırı olmayan, plandan önceki bir kare o zamanki gibi
     üretilir: grafiğin kendi modeli, LoRA yok, dikey (`orientation.of`);
   - sahne (`scene`), varsa; galeri sahneyi ailenin numarasından bulur.
6. **Sıra:** `order.json` bir kez yazılır, eski kimliğin yerinde yeni kimlikle.
7. **Eski karenin kapanışı:** fotoğraf slotu ve karenin kırmızı slotları (başarısız bir video ya da
   ses). Başka bir karenin tuttuğu dosya kalır (`files_to_unlink`). Önce disk, sonra `deleted`
   satırları (`remove_frames`'in sırası). Yapılmış bir videoya burada hiçbir zaman dokunulmaz: ajan
   onu zaten sormaz, ama sorsa bile video kalır.
8. **`run_queue`.** Başka bir projenin üretimi işçiyi tutuyorsa (`Busy`) iş planda borçlu kalır ve
   `"waiting"` döner. Fotoğraf, bu projenin kuyruğu çalışınca üretilir. Hiçbir şey geri alınmaz.

**Çökme sırası.** Önce yeni satır, sonra yeni kimliğin eski yerde olduğu sıra, sonra eski dosya, en
son eskinin `deleted` satırları. Hiçbir anda bir şey kaybolmaz:

| Çökme | Sonuç |
|---|---|
| Plan yazılmadan | hiçbir şey değişmemiş |
| Plan ile sıra arasında | eski kare yerinde; yeni kare sırasız, galerinin en üstünde bekler |
| Sıra ile silme arasında | yeni kare yerinde; eski kare tam, sırasız olduğu için en üstte |
| Silme ile `deleted` satırı arasında | `remove_frames`'teki gibi: kayıt eski fotoğrafı "var" der, dosya yok; kart kırık resim gösterir, kullanıcı silebilir |

Silme başarısız olursa (bağlantı koptu) hata yükselir. Kayıt dokunulmamış kalır, eski kare tam
durur, yenisi yanında. Bunu bir test gösteriyor.

### 2. `fix_frame` — ajanın dördüncü aracı (`agent/domain/tools.py`)

`fix_frame(frame, prompt, negative)`: model karenin bütün yeni prompt'unu ve bütün yeni negatifini
yazar.

**Önce yalnız karttan.** Şu durumlarda izin sorulmaz, adım yazılmaz, modele nedeni döner:

| Kart | Modele dönen |
|---|---|
| Videosu var (`layers`'ta, `failed`'da değil) | "Frame N has a video, so it is not changed." |
| Videosu sırada (`owed`'da `video`) | "Frame N has a video in the queue, so it is not changed." |
| Fotoğraf yok ya da başarısız | "Frame N has no photo to fix." |
| Fotoğrafın prompt'u yok | "Frame N has no photo prompt to fix." |
| Prompt boş, metin değil, ya da negatif metin değil | "A fix needs the frame's whole new prompt, which cannot be empty, and its whole new negative prompt, which can." |
| Prompt da negatif de aynı (boşluklar sayılmaz) | "Frame N already has this prompt and negative, so nothing would change." |

Ajan bu cevapları "videosu var, atlandı" ve "videosu sırada, atlandı" diye listeler.

**Değişiklik, 480'in biçiminde:**

```json
{"title": "N numaralı kare düzeltilecek",
 "details": [{"label": "Prompt", "before": "<eski>", "after": "<yeni>"},
             {"label": "Negatif prompt", "before": "<eski>", "after": "<yeni>"},
             {"label": "Fotoğraf", "text": "Eski fotoğraf silinecek; yenisi aynı yerde üretilecek."}]}
```

Değişmeyen alanın detayı yazılmaz. Sözlerin çevresindeki boşluk bir değişiklik sayılmaz ve kareye de
gitmez.

**Adım** "N numaralı kareyi düzeltiyor…" / "N numaralı karenin düzeltmesini işledi". Bitmiş cümle
tarafsızdır: adım işten önce yazılır, ve iş kareyi değişmiş bulup hiçbir şeyi değiştirmeyebilir; ne
olduğunu ajanın cevabı söyler. **İş**, fotoğraf özelliğinin düzeltmesine kartı — değişikliğin tarif
edildiği kartın kendisini — verir, ve cevabını modele söyler:

| Cevap | Modele dönen |
|---|---|
| `fixed` | "Frame N was fixed: its prompt and negative were changed, its old photo was deleted, and its new photo is in the queue in the frame's own place." |
| `waiting` | "… but another project's generation is running now, so its new photo waits in the queue until this project's queue runs." |
| `changed` | "Frame N changed after you read it, so nothing was changed. It is read again at the user's next question; do not call fix_frame on it again now." |
| `linked` | "Frame N is where another frame's queued video ends, so it is not changed." |

`changed`'in ikinci cümlesi yeniden denemeyi durdurur: ajanın elindeki kart sorunun başındaki
hâlidir, aynı soruda yeniden çağırmak ancak yine `changed` olurdu.

### 3. Ajanın negatifi okuması

`read_frame`'in bütün kartına `negative` girer. Negatifi olmayan bir kartta, yani plandan önceki
karede, `""`'dir.

### 4. Talimat (`agent/domain/prompt.py`)

- **`INSTRUCTION`**:
  - Context'e `fix_frame` eklenir — yalnız prompt ve negatif değişir, kare öteki ayarlarını tutar;
    `read_frame` negatifi de verir.
  - Rules: ajan projeyi yalnız `fix_frame` ile değiştirir, ve yalnız kullanıcı karışmaları düzeltmesini
    isteyince.
  - *Checking for mix-ups*'taki "change nothing"e "unless the user also asks you to fix them" eklenir:
    kontrol ve düzeltme bir soruda istenebilir.
  - Yeni bölüm, *Fixing mix-ups*: karışan kareler en küçük numaradan yukarı birer birer düzeltilir.
    Önce `read_frame` ile prompt ve negatif okunur. Sebep kurallarla prompt'ta bulunur, düzeltmeye
    ajan karar verir: etiket silmek, negatifi geliştirmek, ya da ikisi. Yeni seed bir düzeltme
    değildir. Prompt'un geri kalanı olduğu gibi kalır. Her kare için bir `fix_frame` çağrılır, fotoğraf
    beklenmez. Videolu ve videosu sıradaki kareler kendi cümleleriyle atlanır. `fix_frame` yeni
    fotoğrafın beklediğini söylerse ajan kullanıcıya bu projenin kuyruğunu başlatmasını söyler.
    Sonunda düzeltilenler ve düzeltilmeyenler listelenir.
  - İzin diye bir şeyden hiçbir yerde söz edilmez (480).
- **`FIX_RULES`**: 479'un dışarıda bıraktığı üç cümle, QueenAgent'tan kopya, içe aktarma yok:
  - Rule 4'ün "remove the extra part"'ı, kelimesi kelimesine;
  - Rule 5'in "make the part simpler, and keep the same moment"'i, kelimesi kelimesine;
  - Step 8'in Part 2'si, senaryo dosyasının yerinde karenin prompt'uyla: "Find each tag the camera
    angle hides in the prompt of the frame, and remove the hidden tag there."
- **Ajanın sistem mesajı** artık `INSTRUCTION + MIXUP_RULES + FIX_RULES + SYSTEM_PROMPT_SUFFIX`.
  Düzeltmeye ana ajan karar verdiği için kurallar onun mesajına girer. Kontrolün talimatı
  (`MIXUP_RULES + MIXUP_CHECK + …`) değişmez: kontrol yalnız bulur, düzeltme cümlelerini almaz.

### 5. Kablolama (`main.py`)

Ajana fotoğraf özelliğinin `fix_photo`'su verilir, galeri okuyucusunun verildiği gibi. Özellik başka
bir özelliği içe aktarmaz. Kuyruk, öteki her yolun kullandığı aynı nesnelerle kurulur: koşucu,
store'lar, üreticiler, yazarlar, ilk kare çıkarıcısı, referans havuzu, zaman satırı.

`answer_question(box, frames, picture, fix, run, project, earlier, question)` ve
`run_tool(ask, frames, picture, fix, project, call)`: `fix` bir argüman olarak eklendi.

### 6. Ekran (`useAgentChat.js`, `AgentPanel.jsx`, `SidePanel.jsx`, `ProjectScreen.jsx`, `useGeneration.js`)

Açık galeri, izin verilen bir düzeltmeyi sayfa yenilenmeden izler, ve kart boş bir "Eski" değeri
"(boş)" diye yazar. Ne zaman ve nasıl: aşağıda, karar 7. Maliyeti: değişiklik başına bir `/frames` ve
bir `/api/status`, sonra üretim sürdükçe bugünkü iki saniyelik yoklama.

## Maliyet

Koddan sayıldı, ölçülmedi. 472'den beri her `Storage` işlemi önce kökü bir kez stat eder; aşağıdaki
sayılar işlemlerdir.

| Bir düzeltme (`fix_photo`) | Drive işlemi |
|---|---|
| Galeri okuması (`list_frames`): proje stat'ı, kayıt damgası (değiştiyse satırları), plan, sıra | 4 – 5 |
| Plan okuması (bağlı video kontrolü ve fotoğrafı yapan satır, ikisi bir okumadan) ve kayıt damgası | 2 |
| Yeni kimlik: aynı sözlerde `known_ids` (plan + kayıt damgası); yeni sözlerde `next_number` (klasör listesi, O(dosya) tek çağrıda; plan; kayıt damgası) | 2 – 3 |
| Plan ekleme (okuma + yazma) | 2 |
| Sıra yazma | 1 |
| Eski fotoğraf: silme (dosya paylaşılıyorsa yok); slotlar yukarıdaki okumadan | 0 – 1 |
| `deleted` satırı, kapanan slot başına | 1 (+ kırmızı slot başına 1) |
| `run_queue` | bellekte; boşta ise döngü başlar, onun okumaları kuyruğun olağan bedeli |

Toplam düzeltme başına yaklaşık 12 – 15 işlem. Hepsi O(1); proje, sohbet ya da kare sayısıyla
büyümez. Yalnız okunan baytlar planın ve kaydın boyuyla büyür. Plan bir istekte 3 – 4 kez okunur:
`list_frames` ve `plan_store.append` kendi okumalarını yapar, ve bunları birleştirmek var olan kodu
yeniden yapılandırmak olurdu.

| Ajan tarafı | Disk | Ağ |
|---|---|---|
| Karttan geri çevrilen bir çağrı | yok | yok |
| İzin | 480'deki gibi | yok |
| Düzeltmenin kendisi | yukarıdaki tablo | **yok:** DeepSeek'e istek gitmez |
| Ajanın turları | — | düzeltme başına araç cevabı bir satır; talimat her turda `MIXUP_RULES` + `FIX_RULES` kadar, yaklaşık 600 token büyür |

Tipik bir "düzelt" sorusu üç turdur: `read_frame`'ler, `fix_frame`'ler, cevap.

## Ne kaybolabilir, ne bozulabilir

- **İzinden önce hiçbir şey yazılmaz** (480). Reddet'te, durdurmada ve yeniden başlamada `fix_photo`
  çalışmaz.
- **Bayat kare:** kullanıcı dakikalar sonra cevap verebilir. `fix_photo` kartı o anki kareyle
  karşılaştırır; değişmişse hiçbir şey yazmaz. Aynı soruda aynı kare ikinci kez düzeltilmek istenirse
  eski kart hâlâ ajanın elindedir. İzin yine sorulur, ama eski kimlik artık olmadığı için cevap
  `changed` olur.
- **Çökme:** yukarıdaki sıra. Bir dosyanın altından kayıt satırı silinmez; yeni satır hep eskiden
  önce yazılır.
- **Disk hatası:** `OSError`, ajanın koşusunu sistemin cümlesiyle bitirir (koşucu, `run.fail`).
  Yarıda kalan bir düzeltme çökme tablosundaki satırlardan biridir.
- **Aynı anda iki istek — aynı kimlik.** İki düzeltme, ya da bir düzeltme ve bir Yeniden üret, yeni
  kimliği planı eklemeden önce okunan numaralardan hesaplar. İkisi birbirinin yaklaşık 1 – 2 saniyesi
  içinde gelirse aynı kimliği hesaplarlar. Planda aynı kimliğe iki satır olur, galeri bu kimliği tek
  kart çizer, ve iki kareden biri galeriden düşer. Yeniden üret bu yarışı bugün de taşıyor
  (Yeniden üret ile Yeniden üret); kabul edildi *(ana ajan, 20 Ekim)*.
- **Aynı anda iki istek — sıra.** İkisi de `order.json`'ı kendi galeri okumasından yazar: biri
  ötekinin yeni karesini sıradan düşürebilir. O kare kaybolmaz, galerinin en üstüne çıkar. Bu yarış da
  Yeniden üret'te ve sürüklemede bugün var.
- **Paylaşılan dosya:** başka bir karenin tuttuğu fotoğraf silinmez, o karenin fotoğrafı değişmez.
- **Modelden gelen değerler:** kare numarası `frames`'te aranır. Prompt ve negatif metin olarak plana
  yazılır, hiçbir zaman yola ya da dosya adına girmez. Dosya adları kimlikten ve kayıttan gelir,
  silme `Storage`'dan geçer. Gizli bir değer yok.

## Bu maddenin kararları

1. **Eski karenin yerinde yeni bir kimlik** (B) *(ana ajan, 20 Ekim)*. Galerideki numarası, yeri ve
   kuyruktaki yeri aynı; görünen bedeli detay sayfasının adresinin değişmesi.
2. **Yalnız prompt ve negatif değişir.** Model, LoRA ve yön fotoğrafı yapan plan satırından, sahne
   karenin kendisinden. Seed kartın seed'idir: bir partide yapılmış varyantta bu, partinin hiç
   kullanmadığı kendi satır seed'idir (madde 411), yani yeni resim partinin resminin aynısı olmaz.
   Kullanıcının sözü "seed değiştirmek kurtarmıyor": düzelten sözlerdir, yeniden seed değil *(ana
   ajan, 20 Ekim — satırın seed'i kalır, ve bu dürüstçe yazılır)*. Bunu bir test gösteriyor.
3. **Videosu sıradaki kare de atlanır,** "videosu sırada, atlandı" *(ana ajan, 20 Ekim)*: silinen
   fotoğraftan video üretilirdi. **Başka bir karenin sıradaki bağlı videosunun bittiği kare de
   düzeltilmez** (`linked`) *(ana ajan, 20 Ekim)*: o video sırası gelince fotoğrafı bulamazdı.
4. **Bayatlık, kartın izlenen alanlarıyla** fotoğraf özelliğinde kontrol edilir; değişmişse hiçbir şey
   yazılmaz.
5. **Başka bir proje çalışıyorsa düzeltme yapılır ve fotoğraf sırada bekler** (`waiting`) *(ana ajan,
   20 Ekim)*.
6. **`FIX_RULES` ajanın sistem mesajında,** kopya; kontrolün talimatında değil.
7. **Galeri düzeltmeyi izler** *(ana ajan, 20 Ekim — QA'dan sonra; önceki karar "frontend
   değişmez"di)*. QA gördü ki İzin ver'den sonra açık galeri silinen fotoğrafı göstermeye devam ediyor
   ve yeni kareyi ancak sayfa yenilenince gösteriyordu: sayfa `/frames`'i ve `/api/status`'u yalnız
   açılışta ve kendi başlattığı ya da açılışta bulduğu bir üretim sürerken soruyor
   (`useGeneration.js`). Düzeltmenin sunucuda başlattığı üretimi hiç fark etmiyordu. Gerçek ComfyUI'da
   kullanıcı bütün üretim boyunca silinmiş bir fotoğrafa bakardı; madde ise eski fotoğrafın silindiğini
   ve yenisinin aynı yerde üretildiğini görmeyi söylüyor. Ekranda değişenler:
   - **Ne zaman:** izin verilen değişikliğin adımı bitince ya da soru bitince. Ajan değişikliğin adımını
     İzin ver'den hemen sonra yazar, ve sıradaki çağrıya ya da sorunun sonuna geçerken bitirir; adım
     bitmişse iş çalışmıştır. Cevap gelir gelmez sormak, işten önce sormak olabilirdi.
     `useAgentChat`, İzin ver'in anındaki adım sayısını değişikliğin adımının yeri olarak tutar; sohbet
     o adımı bitmiş ya da soruyu bitmiş gösterince `onChanged`'i bir kez çağırır. Reddet'te ve
     yerine ulaşmamış bir İzin ver'de (ör. `409`) çağrılmaz; İzin ver'den sonra gelen bir durdurmada
     bir kez çağrılır, çünkü iş çalışmış olabilir. Tutulan yer projesiyle birlikte tutulur: bir sohbetin
     numarası yalnız kendi projesinde onu adlandırır.
   - **Bir model turu gecikme:** bir sorunun son düzeltmesinden sonra galeri bir model turu geç
     izler, çünkü son adım ancak cevabın turu bitip cevap yazılınca biter.
   - **Kablolama:** `ProjectScreen` → `SidePanel` (`onAgentChanged`) → `AgentPanel` (`onChanged`) →
     `useAgentChat`. `SidePanel` ajanın panelini bugün de içe aktarıyor; yeni bir sınır geçilmiyor.
   - **Ne olur:** `useGeneration`'ın `follow`'u, yani açılışın kendi `poll`'u. Galeri yeniden
     okunur, işçi sorulur; bir üretim sürüyorsa iki saniyelik zincir sürer. Üretim varsayılmaz: işçiyi
     başka bir proje tutuyor olabilir, cevap sunucunun.
   - **Kartta boş alan:** 480'in kartında boş bir "Eski" ya da "Yeni" değer "(boş)" diye yazılır,
     çıplak bir etiket kalmaz — boş olan ya da boşaltılan bir negatif kendi başına bir cevaptır.
   - `dist` yeniden kuruldu.

   **Sınır:** ajan paneli değişiklik yapılmadan kapanırsa, başka bir sohbet açılırsa ya da sohbetler
   listesi açıksa, sinyal panelle birlikte gider, o sohbete dönülünce ya da liste kapanınca gelir. Galeri o zaman bir sonraki açılışta ya da
   yenilemede yeni kareyi gösterir.

## Sınırlar

- Talimat yalnız 479'un karışan listesini düzeltmeyi söyler. Ajan başka bir değişiklik yapamaz.
- Kayıt (`photos.jsonl`), plan ve sıra dosyalarının şeması değişmez.
- Notebook değişmez.
- Gerçek bir modelin düzeltmelerinin kalitesi testle ölçülmez; kullanıcının sondaki denemesinde
  görülür.
- **Bu maddenin dışında, ana ajana bildirildi:** bugün iki yol fotoğrafı eski bir adla yeniden
  üretiyor, ve değişmez önbellek eski baytları gösterebilir. `retry_frame`'in "kırmızı yok" yolu
  silinmiş bir fotoğrafı aynı adla yeniden üretir. `run_loop` da fotoğrafı silinmiş bir kartta
  videonun ilk karesini `photo_file(id)` adıyla kaydeder. Ana ajan backlog'a alıyor.

## Bitti sayılır

1. **Testler gösteriyor ki:**
   - `test_fix_photo.py`:
     - yeni fotoğraf eski karenin yerinde, yeni sözlerle ve sıradaki numarayla; seed, model, LoRA,
       yön ve sahne karenin kendisinin;
     - eski fotoğraf siliniyor ve kare galeriden çıkıyor; yeni fotoğraf kuyrukta eskinin yerinde;
     - yalnız negatif değişince ailenin sıradaki varyantı, kopya bir karede (`C1_P1_0`) de;
     - partide yapılmış bir varyant kendi satırının seed'iyle üretiliyor;
     - sıradaki bir bağlı videonun bittiği kare `linked` ve hiçbir şey yazılmıyor; yapılmış bir bağlı
       videonun bittiği kare düzeltiliyor;
     - başka bir karenin tuttuğu fotoğraf diskte kalıyor;
     - kopya kare, kaynağı silinmiş olsa da, fotoğrafını yapan satırın ayarlarıyla üretiliyor;
     - plandan önceki kare dikey ve grafiğin modeliyle;
     - başarısız video eski kareyle gidiyor; yapılmış bir video hiç silinmiyor;
     - prompt'u, negatifi değişmiş, videosu gelmiş ya da sıraya girmiş, ya da gitmiş bir kare, ve
       olmayan bir proje hiçbir şey yazmıyor;
     - başka bir proje çalışırken `waiting`;
     - silme düşünce plan ve sıra yazılmış, kayıt dokunulmamış, eski kare tam.
   - `test_agent_answer.py`:
     - dört araç, `fix_frame` `frame`, `prompt`, `negative` alıyor;
     - sistem mesajı kuralları ve `FIX_RULES`'u taşıyor, `FIX_RULES` üç cümleyi söylüyor;
     - `read_frame` negatifi veriyor;
     - değişiklik önce, adım sonra, kart fotoğraf özelliğine gidiyor; değişmeyen alan ve boşluk
       yazılmıyor;
     - Reddet'te düzeltme çağrılmıyor;
     - `waiting`, `changed` ve `linked` modele kendi cümleleriyle dönüyor; iki kare ayrı ayrı
       soruluyor;
     - videolu, videosu sıradaki, fotoğrafsız, fotoğrafı başarısız, prompt'suz ve değişmeyen kare,
       ve sözleri eksik çağrı izin sormuyor ve adım yazmıyor.
   - `test_composition_root.py`: `main.py`'nin kurduğu hâliyle `fix_frame`, gerçek dosyalarda plan
     satırını, sırayı, silinen fotoğrafı ve `deleted` satırını yazıyor ve kuyruğu başlatıyor.
   - `AgentPanel.test.jsx`:
     - izin verilen değişikliğin adımı bitince ve soru bitince ekran bir kez haberdar ediliyor; ajan
       sıradaki değişikliğe geçerken de; İzin ver'den sonra durdurulunca bir kez;
     - Reddet'te, yerine ulaşmamış bir İzin ver'de, başka bir sohbet açıkken ve başka bir projede
       edilmiyor;
     - boş "Eski" ve boş "Yeni" değer "(boş)" yazıyor.
   - `useGeneration.test.jsx`: `follow` galeriyi yeniden okuyor ve süren üretimi izliyor; zaten süren
     bir zincirde tek zincir kalıyor.
   - `ProjectScreen.test.jsx`: İzin ver'den sonra, değişikliğin adımı bitince galeri yeniden okunuyor,
     P1_0'ın kutusu gidiyor, P3_0'ınki çiziliyor ve üretim izleniyor — sayfa yenilenmeden.
2. **İki satır yeşil:** `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend`.
   `npm run build --prefix queen-editor/frontend` ile `dist` yeniden kurulmuş.
3. **Ekranda, 481'in QA'sında (480'in "Bitti sayılır" 4'ü de):** sahte bir modelle her kare için kart
   çıkıyor. İzin verilen karenin yerinde yeni fotoğraf üretiliyor ve açık galeri bunu sayfa
   yenilenmeden gösteriyor; reddedilene dokunulmuyor.
4. **Kullanıcının sondaki denemesi:** gerçek modelle "düzelt".
