# v14 · Görev 11 — Kart kopyalama · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-11-kart-kopyalama-testler-design.md) —
kararlar orada verildi ve commit edilmiş 29 test onları tarif ediyor.

## Değişen dosyalar

Dokuz dosya, dört katman. Yeni olan tek dosya kopyalama işinin kendisi; geri kalanı ona giden yol.

| Dosya | Ne kazanıyor |
|---|---|
| `domain/photo_name.py` | kopya önekinin yazılması ve okunması |
| `domain/copy_frame.py` | ikizin adı, ve bütün katmanları taşıyan taşıma |
| `domain/usecases/copy_frames.py` | **yeni** — işin kendisi |
| `presentation/routes.py` | `POST …/frames/copy` |
| `backend/main.py` | bağlama |
| `frontend/src/shared/api.js` | çağrı |
| `…/useGeneration.js` | kancanın geçişi |
| `…/ProjectScreen.jsx` | galeriye bağlanması |
| `…/Gallery.jsx` | düğme, kısayol, seçimin taşınması |

### 1 · Önek: yazan ve okuyan tek yer

`photo_name` bugün "iki şema okur, biri yazar" diyor. Önek üçüncü bir şema değil, ikisinin de
**önüne** takılan bir parça — dolayısıyla ayrı bir dal değil, **ayrılan bir baş** olarak yazılıyor:

- `copy_id(base, index)` → `C1_P11_1`
- `copy_parts(name)` → `(1, "P11_1")`, öneksiz adda `(None, ad)`

`_parts` — sayı ve varyantı okuyan tek yer — adı önce önekinden ayırıyor. Kopya, kaynağının resmini
tutuyor; o resmi yapan prompt hangisiyse kopya da onun ailesinden. Soyulmasaydı `copy_frame.family()`
kopya kare üstünde aileyi bulamaz, "yeniden üret" adı `PNone_1` olurdu.

### 2 · İkizin adı ve taşınması

`copy_frame` iki şey kazanıyor:

- `next_copy_id(ids, source)` — tabana göre bir üst indeks, boşluk kullanmadan. Taban, kaynağın
  önekinden ayrılmış hâli: kopyanın kopyası `C2_`, iç içe değil.
- `carry_all(record, project, copy, frame, now)` — kaynağın **bütün** katmanları.

Bugünkü `carry_layers` ile ikisi tek bir iç işlevin iki çağrısı: biri `queue.ORDER`'ın verilen
katmandan aşağısını, öbürü tamamını veriyor. Satırın nasıl yazıldığı tek yerde kalıyor.

**Patlamış katman korumasının evi de orası.** Kırmızı bir katman karenin `layers` haritasında hâlâ
bir dosya adlandırıyor ama o dosya diskte yok; yeni karede `done` satırı olarak yazmak onu var
saymak olurdu. Bugünkü `carry_layers`'ın kapsamı bu duruma zaten düşmüyor, yani kural onun için de
doğru ve bedelsiz.

### 3 · İşin kendisi

`copy_frames(record, store, plan_store, order_store, now, project, frames)`:

1. Gövde metin dizisi değilse `InvalidFrames`.
2. Galeri okunuyor (olmayan proje burada `ProjectMissing` veriyor).
3. Her kimlik için: galeride yoksa ya da üretilmemişse **atlanıyor**; varsa ikiz adlandırılıyor,
   katmanları taşınıyor, listeye giriyor. Ad havuzu her doğumda büyüyor, yani bir istekte aynı
   kaynaktan iki ikiz aynı adı almıyor.
4. Doğan varsa sıra dosyası `placed` ile bir kez yazılıyor — bütün dizi, kopyalar kaynaklarının
   üstünde.
5. `{"copies": [...]}` dönüyor.

Plan satırı **yazılmıyor** ve kuyruk **çalıştırılmıyor**: üretilecek bir şey yok. Kopya galeriye
kaydın kendisinden düşüyor — `list_frames`'in planın tanımadığı kareler döngüsü.

### 4 · Rota

`POST /api/projects/<proje>/frames/copy` — silme rotasının aynısı, gövdesi `{frames: [...]}`.
Cevap `{copies, frames}`: iş kuralının cevabının üstüne galeri ekleniyor, yani galeriyi bilen taraf
yine yalnız rota. 400 gövde için, 404 proje için.

### 5 · Ekran

`Gallery` üç şey kazanıyor:

- Seçimin **üretilmiş** yarısı erken hesaplanıyor. Bugün onay metninin altında duruyor; kısayol
  bileşenin tepesinden dinlendiği için yukarı çıkıyor ve boş galeride de tanımlı oluyor.
- Bardaki **Kopyala**, Sil'in solunda, çerçevesiz — ve yalnız o yarı doluyken çiziliyor.
- Escape'i dinleyen etki artık **Ctrl + D**'yi de dinliyor: onay penceresi açıkken ikisi de susuyor,
  ve kısayol `preventDefault` ile tarayıcının yer iminden alınıyor.

Basıştan sonra seçim ikizlere geçiyor. İstek reddedilirse hiçbir şey dönmüyor ve seçim yerinde
kalıyor.

`api.js` → `useGeneration` → `ProjectScreen` bağlantısı `removeFrames`/`removePhotos` ile birebir
aynı biçimde: kanca cevabın galerisini ekrana koyuyor, ikizlerin adlarını çağırana veriyor.

## Bitti sayılır

Dört komutun dördü de yeşil. `dist` bu commit'te derleniyor, yol haritası 11/31 oluyor.
