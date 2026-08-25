# v14 · Görev 8 — Detayda Üretim modu bilgi satırı · **test turu**

**Kaynak:** [yol haritası v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) 8. madde —
[İstek 3](../plans/2026-08-20-queen-editor-istekler.md) ve
[fark listesi](../research/2026-08-20-queen-editor-tasarim-v4-farklari.md) 93.

## Sorun

Fark 93: *"videolu bir karenin video sekmesinde sağ sütunda 'Üretim modu' satırı durur ve bu
videonun modunu salt bilgi olarak yazar — tıklanmaz, değişmez. Bağlı modda hedefi kare numarasıyla
değil dosya adıyla söyler ('Sonrakine bağla → P11_4.png'), çünkü sıra değişince numara yalan olur.
Satır ses sekmesinde hiç doğmaz."*

Modun kendisi 7. maddede kayda geçti ve kareye `modes` olarak ulaşıyor. Eksik olan **hedefin adı**:
bağlı bir videonun hangi kareye vardığı hiçbir yerde yazılı değil. İş `linkedTo` taşıyordu, motor onu
okuyup fotoğrafı indirdi, ve iş bittiğinde o bilgi de bitti.

## Kararlar

### 1 · Kayıt hedefin kimliğini değil, vardığı dosyayı yazıyor

Satıra `endsOn` giriyor: videonun vardığı fotoğrafın **dosya adı**, render'a verilen dosyanın ta
kendisi.

Kimliği (`linkedTo`) yazıp adı sonradan çözmek de olurdu. Olmadı, çünkü çözüm bir gün boşa
düşebilir: hedef kare silinebiliyor ve onu bağlayan video yerinde duruyor. O anda satır hedefi
söyleyemezdi — oysa video gerçekten bir yere vardı ve o yerin adı bellidir.

Tasarımın gerekçesi de bunu istiyor: numara yerine ad, çünkü ad yalan olmuyor. Render anında yazılan
ad hiç olmuyor.

### 2 · Vardığı yer varsa yazılıyor — moda bakılmadan

Loop kendi fotoğrafına varıyor, bağlı sonrakinin fotoğrafına, standart hiçbir yere. Kural tek:
**vardığı bir resim varsa satıra adı yazılır.** Loop'unki bugün hiçbir yerde okunmuyor ama doğru, ve
"şu modda yaz, bu modda yazma" kuralı motora modların adlarını ikinci kez öğretirdi.

Motor zaten o değeri elinde tutuyor: `_end_for`'un döndürdüğü çift, üreticiye giden `end`.

### 3 · Kareye `endsOn: {layer: file}` olarak çıkıyor

`modes`, `errors`, `prompts` ile aynı şekil: katmana göre haritalanmış, ve yalnız satırında olan
katmanlar içinde.

### 4 · Kopya götürüyor

`carry_layers` ses kopyasına kaynağın video satırını veriyor. `mode` gittiği gibi `endsOn` da
gidiyor — yoksa ikizin detay satırı hedefi söyleyemezdi.

### 5 · Satır yalnız videonun sekmesinde ve yalnız modu bilinen videoda

`open === "video"` **ve** karenin video modu var. Patlamış, silinmiş ya da modu hiç yazılmamış bir
video satırı doğurmuyor: kaydın son satırı kazanıyor ve o satırların hiçbirinde mod yok.

Ses sekmesinde hiç doğmuyor — orada videonun dosya adı görünüyor ama modu değil, çünkü sekme sesin.

### 6 · Bağlı mod hedefi okla söylüyor, ötekiler yalnız adlarını

- Standart → `Standart`
- Loop → `Loop`
- Sonrakine bağla → `Sonrakine bağla → P11_4.png`

Modun adı `production_modes.js`'ten geliyor — panelin seçicisiyle aynı kaynak, çünkü ikisi aynı şeyi
adlandırıyor. Listenin tanımadığı bir değer kendi kendini yazıyor: bozuk veriyi boş bir satır olarak
göstermek, ne olduğunu söylemekten az şey söyler.

### 7 · Satır bir kontrol değil

`Field` ile çiziliyor — Sıra ve dosya adının komşusu, aynı sarmalayan sırada. Tıklanacak hiçbir şey
yok: modu değiştirmek videoyu yeniden üretmek demek, ve o form aşağıda (9. madde).

## Yazılacak testler

**Motor — `test_photo_usecases.py`**

1. Bağlı videonun satırı vardığı fotoğrafı adıyla söylüyor.
2. Loop videosunun satırı kendi fotoğrafını söylüyor.
3. Standart videonun satırında alan yok.

**Kayıt — `test_photo_record.py`**

4. Satırdaki `endsOn` hücreye katlanıyor.

**Galeri cevabı — `test_photo_usecases.py`**

5. Kare `endsOn: {"video": …}` veriyor.

**Kopya — `test_photo_usecases.py`**

6. Ses kopyası kaynağın vardığı yeri de götürüyor.

**Detay — `PhotoDetail.test.jsx`**

7. Video sekmesinde satır modun adını yazıyor.
8. Bağlı modda hedefi dosya adıyla söylüyor.
9. Satır tıklanabilir bir şey değil.
10. Ses sekmesinde satır hiç yok.
11. Foto sekmesinde satır hiç yok.
12. Modu yazılmamış bir videoda satır hiç yok.

## Bitti sayılır

Dört komutun dördü de koşuyor, kırmızılar commit ediliyor. Kaynak dosyalara bu turda dokunulmuyor.
