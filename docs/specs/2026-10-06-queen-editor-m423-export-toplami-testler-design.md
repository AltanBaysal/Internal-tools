# Madde 423 — Export'un toplamı her videonun kendi uzunluğundan, test turu

**Koşu:** Queen Editor v9 — `roadmaps/2026-10-05-queen-editor-v9-roadmap.md` · **Dal:**
`feat/queen-editor-v9` · **Parça:** 423 · v9-1c · **Tur:** 1/2 — yalnız testler.
**Üstüne kurulduğu:** [m422 test turu](2026-10-06-queen-editor-m422-h3-uzunlugu-testler-design.md),
[m422 uygulama turu](2026-10-06-queen-editor-m422-h3-uzunlugu-uygulama-design.md) — 422'den beri
üretilen H3 videosunun kayıt satırı uzunluğunu söylüyor (`"seconds"`).

**Kullanıcıdan gereken — yok.** Madde hizalandı; kararları yol haritasının *Maddelerin kararları →
v9-1* bölümünde. Aşağıdaki teknik kararlar Claude'un.

## Kullanıcının sözü ve tasarım

Madde v9-1 bölünürken bulundu: *"Export'un toplam süresi her videonun kendi uzunluğundan"*
*(kullanıcı, 5 Ekim — "uygula")*. **Bitti sayılır:** farklı uzunlukta H3 videoları olan bir
projede export ekranındaki toplam, videoların kendi uzunluklarının toplamı; tek uzunlukta videoları
olan projede toplam bugünküyle aynı.

Tasarımcının 206'sı (`queen-design`, `queen-editor-v2`, `2026-10-05-queen-editor-uzunluk-design.md`,
*Export özetinde*): *"toplam bundan **hesaplanır**: sabit sayı kalkar … **Özet cümlesinin biçimi
değişmez; ek bir döküm satırı yok.**"* Yeni durum *karışık uzunluklar*: 24 video, 6 × 4 + 4 × 5 +
6 × 8 + 8 × 12 = 188 sn → *"24 video export edilecek · 3:08 dk"*. Ekranda yalnız sayı değişir.

## Bugün ne oluyor

[export_summary.py](../../queen-editor/backend/features/photo_generation/domain/usecases/export_summary.py)
video sayısını oturumun video grafiğinin uzunluğuyla çarpıyor (`len(videos) * seconds()`), çünkü
422'ye kadar uzunluk seçilemiyordu. 422'den beri bir H3 videosu 4, 8 ya da 12 saniye; 12'lik üç
video bugün 3 × 4 = 12 saniye sayılıyor.

Uzunluk satırda duruyor ama hiçbir yere taşınmıyor: kaydın katlanışı (`slots`) `seconds`'ı almıyor,
galeri kartı onu göstermiyor, ve bir videoyu paylaşan kopya kare (`copy_frame.CARRIED`) onu
taşımıyor.

## Kararlar

1. **Bir videonun uzunluğu satırından; satır söylemiyorsa grafiğinkinden.** 422'den beri üretilen
   H3 videosunun satırı işin taşıdığı uzunluğu söylüyor. Satırı uzunluk söylemeyen video — 422'den
   önceki her video, ve WAN'ın her videosu — grafiğin kendi uzunluğunda çıktı; özet onu bugün
   sorduğu yerden, oturumun video üreticisinin `seconds()`'ından sorar.
   - **Elenen — her dosyayı ffprobe'la ölçmek:** her özet her video için bir süreç ve bir Drive
     okuması; ekran özeti galeri her değiştiğinde yeniden istiyor, kuyruk akarken iki saniyede bir.
     Yerelde ffprobe yok. Ve ölçülen süre kare sayısından gelir: grafiğin tam sayısını birebir
     tuttuğu bilinmiyor, tutmazsa tek uzunluklu projenin toplamı bugünkünden kayar — maddenin
     *bitti sayılır*ı aynı kalmasını istiyor.
   - **Elenen — projenin şimdiki uzunluk ayarı:** video eklendiği uzunlukta çıkıyor (422); ayar
     sonradan değişince toplam yalan söyler.
2. **Uzunluk satırdan özete dört durakta gelir:** kaydın katlanışı satırın `seconds`'ını — yalnız
   sayıysa — hücreye taşır; galeri kartı onu katman başına bir haritada verir, `lengths`
   (`{"video": 12}`), `modes`, `endsOn`, `renderSeconds` gibi; kopya kare onu kaynağından taşır
   (`CARRIED`); özet her videonun uzunluğunu toplar. Kartta adı `seconds` değil: kartın
   `renderSeconds`'ı modelin çalıştığı süre, ve iki ayrı süre neredeyse aynı adı taşımasın.
3. **Ekran değişmez:** tasarım cümlenin biçimini değiştirmiyor; özetin `seconds`'ı bugünkü yerinde,
   sayısı doğru. Frontend'in kodu ve `dist` değişmez; bir frontend testi tasarımın *karışık
   uzunluklar* cümlesini tutar.
4. **Drive'daki eski satırlar okunmaya devam eder:** `seconds`'ı olmayan satırın hücresinde ve
   kartında uzunluk yok — tahmin edilmiş bir sayı değil —, ve özet onu grafiğin uzunluğuyla sayar.

**Değişmeyen:** özetin kapısı ve cevabının biçimi (`videos`, `seconds`, `silent`, `withoutVideo`,
`folder`); `main.py`'nin bağlantısı (özet bugünkü gibi `_video_generator.seconds`'ı alır); ekran.
Döngü, 422'nin satırı ve üreticiler ilk turda değişmedi; inceleme turu onları değiştirdi — aşağıda.

## Bilinen sonuçlar

*(İnceleme turundan sonraki hâli — aşağıda.)*

- **Bu değişiklikten önce yazılmış, uzunluk söylemeyen satır oturumun grafiğiyle sayılır**, bugünkü
  gibi: H3 oturumunda eski bir WAN videosu 4, WAN oturumunda 422'den önceki bir H3 videosu 5 saniye
  sayılır. O satır videoyu hangi modelin yaptığını söylemiyor; doğrusu yalnız dosyanın kendisinden
  okunur, ve o yukarıda elendi. Bundan sonra üretilen her video — WAN'ınki de — uzunluğunu satırında
  söyler, ve her oturumda doğru sayılır.
- **422 ile bu değişiklik arasında yazılmış H3 satırı** işin istediği uzunluğu söyler; video bir WAN
  oturumuna taşınmadıysa o, videonun gerçek uzunluğu.

## İnceleme turu — satır üretilen videonun uzunluğunu söyler *(koordinatör, 6 Ekim)*

**Bulgu:** 422'den beri döngü (`run_loop._made_with`) satıra işin `seconds`'ını yazıyor, üretici ne
yaparsa yapsın. H3 oturumunda 12 saniyeyle kuyruğa girip sonraki bir WAN oturumunda üretilen video
WAN'ın 5 saniyesiyle çıkar, ama satırı 12 der: kayıt doğru olmayan bir şey söylüyor, ve 423'ten beri
export ona güveniyor. Önce doğruluk (FOUNDATION 3): satır, yapılan videonun ne kadar sürdüğünü
söyler.

**Kararlar:**

1. **Video üreticisi, bir uzunlukla istenen videonun kaç saniye çıktığını söyler:**
   `seconds(asked=None)`. H3 istenen uzunluğu yapar — `asked` verildiyse o, verilmediyse grafiğinin
   kendi 4'ü. WAN her zaman grafiğinin kendi 5'ini yapar, ne istenirse istensin. Bugünkü `seconds()`
   aynı yöntem: argümansız hâli grafiğin uzunluğu, özetin sorduğu da o.
2. **Döngü her üretilen video satırına bu cevabı yazar** — `producer.seconds(job.get("seconds"))`,
   işin sayısını değil. Fotoğraf ve ses satırı uzunluk taşımaz.
3. **Özetin grafik yedeği yalnız uzunluk söylemeyen satır için kalır** — bu değişiklikten önce
   yapılan videolar.
4. **Porta yeni bir protokol:** `VideoGenerator(PhotoGenerator)` — `seconds(asked)`. Toplu üretim
   (`BatchPhotoGenerator`) gibi: yalnız video üreticisinin cevap verdiği bir soru.

**Sahteler:** döngü artık her video üreticisine bu soruyu sorduğu için, testlerde video yapan
sahteler cevap verir — `FakeGenerator` (ve alt sınıfları), `FakeVideoGenerator`, `FailsTwice`,
`Records` (`test_photo_usecases.py`), `test_reference_routes.py`'nin `FakeGenerator`'ı. Cevapları H3
gibi: istenen, istenmediyse 4. İki alt sınıf bir grubun ne kadar çalıştığını `self.seconds`'ta
tutuyordu ve yöntemi örtüyordu: `Takes` (`test_photo_usecases.py`) ve `BatchGenerator`
(`test_variant_batch.py`) onu `self.works`'te tutar; kurucularının argümanı aynı.

**Kanıt:** gerçek üreticiler gerçek döngüde, `test_producer_contract.py`'de — sözleşmeyi koşan tek
yer; grafikler gönderilen grafikler.

### `backend/tests/test_producer_contract.py`

11. **H3 için kuyruğa girip WAN'ın yaptığı video WAN'ın uzunluğunu söyler** — iş 12; WAN: satır 5.
12. **WAN oturumunun videosu grafiğinin uzunluğunu söyler** — iş uzunluk taşımıyor; WAN: satır 5.
13. **H3'ün videosu istendiği uzunluğu söyler** — parametreli 4, 8, 12; H3: satır o sayı.
    *(Bugün de yeşil: döngü işin sayısını yazıyor, ve H3'te ikisi aynı. Değişiklikten sonra da aynı
    kaldığını tutar.)*
14. **Uzunluk istemeyen H3 videosu grafiğin kendi uzunluğunu söyler** — iş uzunluk taşımıyor; H3:
    satır 4.

### `backend/tests/test_video_length.py`

15. **422'nin `test_a_job_that_carries_no_length_is_made_at_the_graphs_own`'u:** satırda `seconds`
    yok demiyordu artık doğru değil; satır üreticinin cevabını söyler — sahte üretici için 4.
    Üreticiye `None` gittiği yerinde.

### Kırmızı beklenen — inceleme turu

- 11: 12 ≠ 5; 12 ve 14: `KeyError: 'seconds'`; 15: `KeyError: 'seconds'`.
- 13 (3 durum) yeşil. Sahtelerin cevabı ve iki adın değişmesi bugün de yeşil: döngü henüz sormuyor.
- Toplam 4 kırmızı; öteki her şey yeşil.

## Nasıl kanıtlanıyor

Yeni dosya `backend/tests/test_export_total.py`. Kayıt **gerçek `DrivePhotoRecord`**, geçici
klasörde: kanıtlanan, Drive'daki satırdan ekrandaki sayıya giden yolun bütünü, katlanış dahil.
Mağaza, plan ve sıra `test_photo_usecases.py`'nin sahteleri; grafiğin uzunluğu bir `lambda`. Ekran
testi `ExportScreen.test.jsx`'te, sahte özetle.

## Yazılacak testler

### `backend/tests/test_export_total.py` — yeni

Yardımcı: `project(tmp_path, *videos)` — her kare `n_a`'nın fotoğrafı ve üretilmiş videosu var;
`videos` her videonun satırının söylediği uzunluk, `None` söylemeyen satır.

**Kaydın katlanışı**

1. **Uzunluğunu söyleyen video satırı onu hücreye taşır** — satır `"seconds": 12`: `slots`'ta
   videonun hücresi `seconds` 12.
2. **Uzunluktan önce yazılmış satırın hücresinde uzunluk yok** — `seconds` anahtarı yok. *(Bugün de
   yeşil: Drive'daki eski satırları tutar.)*

**Galeri**

3. **Kart videosunun ne kadar sürdüğünü söyler** — `lengths == {"video": 12}`.
4. **Videosu uzunluk söylemeyen kartın uzunluğu yok** — `lengths == {}`: tahmin yok.

**Export özeti**

5. **Toplam her videonun kendi uzunluğunun toplamı** — 4, 8, 12; grafik 4: `videos` 3, `seconds`
   24.
6. **Satırı uzunluk söylemeyen video grafiğin uzunluğuyla sayılır** — 12 ve `None`; grafik 5:
   `seconds` 17.
7. **Tek uzunluktaki videolar bugünkü gibi toplanır** — `None`, `None`; grafik 4: `seconds` 8.
   *(Bugün de yeşil: maddenin "bugünküyle aynı"sını tutar.)*
8. **Bir videoyu paylaşan kopya kare o videonun uzunluğuyla sayılır** — 12 saniyelik videosu olan
   kare *Kopyala* ile kopyalanır (`copy_frames`); grafik 4: `videos` 2, `seconds` 24.
9. **Seçilen uzunlukta üretilen video o uzunlukla sayılır** — fotoğrafı olan kareye elle
   `"seconds": 12` taşıyan bir video işi yazılır, döngü koşar (`make_job`, sahte üretici); grafik
   4: `seconds` 12. *(422'nin satırı, katlanış ve özet birlikte.)*

### `frontend/src/features/photo_generation/ExportScreen.test.jsx`

10. **Karışık uzunlukların toplamı tasarımın yazdığı gibi** — özet `videos` 24, `seconds` 188:
    *"24 video export edilecek · 3:08 dk"*. *(Bugün de yeşil: ekran yalnız sunucunun sayısını
    yazar, ve değişmez.)*

## Kırmızı beklenen

- 1: `KeyError: 'seconds'` — katlanış uzunluğu taşımıyor.
- 3, 4: `KeyError: 'lengths'` — kartta harita yok.
- 5: 12 ≠ 24; 6: 10 ≠ 17; 8: 8 ≠ 24; 9: 4 ≠ 12 — özet sayıyı grafikle çarpıyor.
- Toplam 7 kırmızı; 2, 7, 10 yeşil. Öteki her test yeşil kalır.

## Bilinçli olarak yapılmayan

- Dosyanın süresini ölçmek (yukarıda, 1).
- Satırın hangi modelin yaptığını söylemesi: sorusu yok, ve eski satırlara yardımı yok.
- Ekranda uzunluk dökümü: tasarım istemiyor.
- Kapı testi: kapı özeti olduğu gibi JSON'a çeviriyor; mevcut testi
  (`test_the_export_summary_is_json_not_a_download`) yerinde.
