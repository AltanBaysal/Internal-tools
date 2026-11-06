# Queen Studio v1 — Koşuda verilen kararlar

[Roadmap](2026-11-06-queen-studio-v1-roadmap.md) koşarken ana agent'ın kullanıcıya sormadan verdiği
kararlar. Koşu bitince kullanıcıyla bu belgenin üstünden geçilir.

Her karar: hangi maddede, ne karar verildi, neden, başka seçenekler neydi, hangi belge değişti.

## Sapmalar

Kod yazılırken tasarımdan ya da kurallardan farklı yapılanlar: hangi maddede, hangi adımın neyinden
neye, neden, hangi belge düzeltildi.

1. **Colab Secrets CLI'ın oturumunda okunamıyor** ([v1-1](2026-11-06-queen-studio-v1-roadmap.md#v1-1)).
   Google'ın cevabı: "Secrets can only be fetched when running from the Colab UI". CLI'la koşan testler
   aynı üç değeri (`HF_TOKEN`, `CIVITAI_COOKIE`, `GITHUB_TOKEN`) `.secrets/colab-secrets.env`'den alır:
   dosya `colab upload` ile VM'e gider, orada okunur, iş bitince silinir. Değerleri kullanıcı yazar,
   ana agent ve subagent'lar okumaz. Notebook'ta Secrets olduğu gibi kalır. Değişen: henüz belge yok;
   v1-25 ve v1-27 bunu kullanır.
2. **Colab CLI Windows'ta çalışıyor, kendi ev klasörü `.secrets/colab-home`** ([v1-1](2026-11-06-queen-studio-v1-roadmap.md#v1-1)).
   Belgeleri yalnız Linux ve macOS diyor; 0.7.5 bu makinede T4 açtı, kod koştu, kapattı. Token'ını,
   log'unu ve ayarlarını kullanıcı klasörüne yazdığı için her çağrıda `USERPROFILE` ve `HOME`
   `D:\Github\Internal-tools\.secrets\colab-home` gösterilir; `--config` yalnız oturum listesini
   taşıyor. CLI `queen-studio/.venv`'de: `queen-studio\.venv\Scripts\colab.exe`.
3. **Drive erişimi yalnız uygulamanın açtığı dosyalara** ([v1-1](2026-11-06-queen-studio-v1-roadmap.md#v1-1)):
   `drive.file` izni, deneme hesabında, token `.secrets/drive-token.json`. Neden: testler yalnız kendi
   açtıklarına dokunur; uygulama doğrulama istemeden yayında, token düşmüyor.
4. **`.secrets/` okunmaz** ([v1-1](2026-11-06-queen-studio-v1-roadmap.md#v1-1); kullanıcı, 6 Kasım —
   "okumayı engelleyen bir kural ekle"). `.claude/settings.json` Read ve Edit'i yasaklar,
   `.claude/hooks/guard_secrets.py` okuyan kabuk komutlarını durdurur. Betikler yolu alır, değer basmaz.
5. **Colab'da Drive gereken testlere deneme hesabının token'ı geçici olarak gider** ([528 · v1-4](2026-11-06-queen-studio-v1-roadmap.md#v1-4)).
   `colab upload` ile VM'e, iş bitince `colab rm` ile silinir, oturum kapatılır. Neden: Colab'ın
   kendi Drive girişi CLI'da tıklamasız açılmıyor. Güvenlik kontrolü bunu "veri dışarı çıkıyor" diye
   işaretledi; giden token yalnız deneme hesabının, yalnız uygulamanın açtığı dosyalara erişen
   token'ı, gittiği yer o hesabın kendi Colab VM'i. Bir kez de başarısız bir yükleme, o oturumun
   çalışma zamanı adresini (içinde geçici bir anahtarla) ekrana bastı; oturum kapandı.
6. **Drive ölçümlerinden çıkan düzeltmeler** ([528 · v1-4](2026-11-06-queen-studio-v1-roadmap.md#v1-4)).
   4. adıma yazıldı: çağrı süreleri ölçülenle değişti (okumalar ~0,1 sn, yazmalar ~0,8 sn); Drive
   yoğun yazmada reddetmiyor, yavaşlatıyor, geçici `503` de yeniden denenir; 500 fotoğraflı export'un
   kopyaları ~16 sn değil ~1,5–3 dk; export adları kodda tam karşılaştırılır, çünkü Drive'ın ad
   araması Türkçe I'yı eşlemiyor; eski sürümler kotaya sayılmıyor, Değerlendirme 9'un iki önlemi
   yapılmaz. Açık kalan: bu makineden bir klasörün çöpe atılması bir kez `appNotAuthorizedToChild`
   ile reddedildi, nedeni bulunamadı; gerçek Drive'a karşı testlerde (v1-8, v1-9) izlenir. Ayrılmış
   kimliklerin 1, 3, 7 günlük bakışı 7, 9, 13 Kasım'da.
7. **Hız sınırı deneyini kullanıcı atlattı, sonuç yine tutuldu** ([528 · v1-4](2026-11-06-queen-studio-v1-roadmap.md#v1-4);
   kullanıcı, 6 Kasım — "üst limiti de denemeyelim"). Atla kararı gelmeden koşmuştu; sonuç 6'daki
   düzeltmenin dayanağı.
8. **`GET /api`'nin satırları düz yazı** ([529 · v1-5](2026-11-06-queen-studio-v1-roadmap.md#v1-5)):
   6. adımın `{"method","path","summary"}` nesneleri yerine `"GET /health: …"`. Neden: endpoint başına
   ~33 bayt, oturum başına ~370 token daha az (kullanıcı, 5 Kasım — "token olarak efficient olsun").
   Değişen: 6. adım, Discovery.
9. **Bilinmeyen sorgu parametresi de hata** ([529 · v1-5](2026-11-06-queen-studio-v1-roadmap.md#v1-5)):
   6. adım yalnız gövdeyi söylüyordu; `?paht=` gibi bir yazım hatası sessizce bütün dizini dönüyordu.
   Listeler (v1-6) sorgularını kendileri çözer ve bilinmeyen alanı kendileri reddeder. Değişen: 6.
   adım, Gövde.
10. **Hata alan yollarına `path.` eklendi** ([529 · v1-5](2026-11-06-queen-studio-v1-roadmap.md#v1-5)):
    `body.`, `query.`, `header.` yanında adresin kendi alanı (`{id}` gibi) için. Değişen: 6. adım, Biçim.
11. **Listelerde regex yok; yerine `like` / `ilike`** ([530 · v1-6](2026-11-06-queen-studio-v1-roadmap.md#v1-6);
    kullanıcı, 6 Kasım — "1"). 6. adım `match`/`imatch` ile Python regex'i diyordu. İlk yapılan:
    `regex` paketi, sorgu başına 1 sn bütçeyle — `re` durdurulamıyor ve GIL'i tutuyor, `(a|aa)+$` gibi
    tek bir kalıp core'u dondururdu. Ama bütçe yalnız eşleşmeyi kesiyordu, derlemeyi değil: reviewer'ın
    büyük iç içe tekrarlı kalıpları yalnız derleyen denemesi bu makinenin 16 GB'ını doldurup onu
    çökertti; Colab'da da core'u, süren üretimle birlikte öldürürdü. Dışarıdan gelen bir kalıbı
    çalıştırmak, dışarıya program yazdırmaktır. Şimdi: PostgREST'in `like`/`ilike`'ı, joker `*`,
    regex motoru olmadan doğrusal eşleşmeyle; kalıp en çok 200 karakter; `ilike` I, ı, İ'yi `i`'ye
    katlar. `regex` paketi çıktı. Ders olarak dışarıdan gelen her girdinin zaman, bellek ve disk
    harcamasına sınır aranıyor (madde 12). Değişen: 6. adım, Liste sorgusu.
12. **Girdinin sürebildiği her harcamanın bir sınırı var** ([530 · v1-6](2026-11-06-queen-studio-v1-roadmap.md#v1-6);
    kullanıcı, 6 Kasım — "bundan ders çıkar hem geçmiş hem gelecek değişikliklere bak"). 11'deki
    çöküşten. `CODE-STANDARD.md`, Cost: dışarıdan gelen her metnin, listenin ve sayının bir üst sınırı,
    her dış çağrının bir zaman aşımı, her cevabın bir bayt bütçesi var; sınır geçilince iş yapılmadan
    reddedilir, sessizce kesilmez; hiçbir girdi onu program gibi çalıştıran bir motora (regex, eval,
    kabuk) gitmez. Reviewer ve QA bu makinede onu tüketebilecek deneme koşmaz; sınırı küçük bir
    denemeyle gösterir. 530'da: sorgu en çok 16 KiB, alan başına en çok 2 süzgeç, `in` en çok 1000
    değer, `order`/`select`'te bir alan bir kez, cevap en çok 1 MiB. Bitmiş kodun ve sonraki
    maddelerin denetimi yapıldı; ne olacağı kullanıcıda. Değişen: `CODE-STANDARD.md`,
    `.claude/agents/reviewer.md`, `qa.md`.
13. **Depo portu kare, iş, edit bilmez** ([531 · v1-7](2026-11-06-queen-studio-v1-roadmap.md#v1-7)).
    4. adımın tablosu değişikliği tek tek sayıyordu (kalkan kareler, yeni sıra, kuyruk…); port yalnız
    baştan yazılanı (satır ve hal) ve bir kez yazılanı (kayıtlar ve history) bilir. Bilgi aynı, 4.
    adımın çağrı sayıları değişmez; anlamı core verir. Reviewer'ın bulgusuyla eklenenler: `commit`
    yalnız bu portun son verdiği sürümü alır (yoksa başka Colab'ın değişikliği sessizce ezilebilirdi);
    port grupların biçimini (`format`) tutar, yeni biçimli projeyi eski core'a yazdırmaz; `exists`
    dosyanın boyunu ve md5'ini döner, çıktısı Drive'da olan iş indirmeden kapanır; export'un `photos/`
    alt klasörü; `trash_project`. Kapı kuralı: bir kapı başkasına yalnız kendisine verilen tür için
    bakar (depo `Clock` alır). On bir sapmanın hepsi:
    [m531 spec, 4. adımdan sapmalar](../specs/2026-11-06-queen-studio-m531-depo-portu-design.md#4-adımdan-sapmalar).
    Değişen: `CODE-STANDARD.md`, kapı kuralı.
14. **Sekiz büyük madde ikiye bölündü** (roadmap; kullanıcı, 6 Kasım — "roadmapte başka böyle büyük
    task varsa onları da parçalara bölelim"; "Yes, all 8"). 532'nin iki turu bir saati geçince. v1-10,
    v1-14, v1-16, v1-17, v1-21, v1-25, v1-27 ve v1-28'in ikinci yarısı v1-34…v1-41 oldu, tabloda
    bölündüğü maddenin hemen altında. Eski numaralar yerinde, çünkü spec'ler ve bu belge onlara
    bakıyor. Bölünen maddelerin kabul koşullarına, madde 12'nin denetiminden o maddeye düşen sınırlar
    eklendi: history'nin taradığı blok sayısı, indirmede ve export'ta disk, export belleğinin klip
    sayısıyla büyümemesi, log'un boyu, `/wait`'in iş parçacığı tutmaması. Yolda bulunan iş artık
    v1-42'den.
15. **Denetimin kalanı da roadmap'e girdi** (kullanıcı, 6 Kasım — "sen karar ver"). Yapılmış kod için
    [v1-42](2026-11-06-queen-studio-v1-roadmap.md#v1-42) (`health`'in beklememesi, 1 MiB gövde, hatanın
    yalnız gösterilen sorunları biçimlemesi, bağlantı sınırı), v1-8'den sonra. Sonraki maddelerin kabul
    koşullarına denetimin önerdiği sayılar: kare 20.000, sahne 500, prompt 4000, negatif 2000 karakter,
    1000 bekleyen iş, edit'te 5000 yer, projede 200 edit, toplu silme 1000, aynı anda 2 ffmpeg ve tek
    indirme, listede 25 çağrı ve 8 resim; ComfyUI'ye ve indirmelere süre sınırı, Civitai anahtarının
    log'da görünmemesi, büyük projenin yüklenmemesi. Sayılar önerinin kendisi; kullanıcı sonda bu
    belgenin üstünden geçerken değiştirebilir. Yolda bulunan iş v1-43'ten.
16. **Drive'da her mühür yeni bir blok yazar, eskisi bir saat sonra çöpe gider** ([532 · v1-8](2026-11-06-queen-studio-v1-roadmap.md#v1-8)).
    4. adım açık bloğu yerinde yeniden yazıyordu; iki Colab aynı anda mühürlese proje kalıcı okunamaz
    olurdu (reviewer). Şimdi: taze kimlikte yeni blok; yerini veren blok bir saat sonra çöpe, hiçbir
    şey kalıcı silinmez (ilke 1). Her değişikliğin 10 dakikalık bir son süresi var, geçerse reddedilir;
    böylece bir saat içinde eski bloğu anan bir baş dosyası yazılamaz. Zamanlar Drive'ın saatinden.
    Bedeli: mühür başına +1 listeleme ve çöp; kapanan blok başına çöpte 30 gün ~3–7 MB (kayıtlar),
    ~55 MB (history), sürekli çalışan bir Colab için en çok ~2,6 GB; videoların yanında küçük, history
    bloğunu 1 MB'ta kapatmak (Değerlendirme 9) yapılmadı. Öbür sapmalar: `load` baş dosyası için 2
    çağrı (değişmemiş projede 1), yazmanın kimliği `w`, kaybolan yazmadan önce md5'e bakılması, klasör
    kimliği etikette, `create` mühürlemez, bilinmeyen `v` okunamaz, disk önbelleğinin anahtarı md5.
    Hepsi: [m532 spec, 4. adımdan sapmalar](../specs/2026-11-06-queen-studio-m532-drive-projeler-design.md#4-adımdan-sapmalar).
17. **Bağlantı değil, bellekteki gövdeler sayılır** ([533 · v1-42](2026-11-06-queen-studio-v1-roadmap.md#v1-42)).
    Denetim aynı anda açık bağlantıya sınır diyordu; uvicorn'un sınırı boştaki bağlantıları ve küçük
    resim isteklerini de sayıyor, düz yazıyla reddediyordu, tünelden gelen bir resim yağmuru ekranı
    kırardı. Bedeli bellekte: 1 MiB'lık gövde açılınca ~24 MB olabiliyor. Şimdi: aynı anda okunan
    gövdeler en çok 8 MiB, aşılınca `busy` (503, dört alan); gövdesiz istek hiç reddedilmez. Gövde
    sınırı 1 MiB, en büyük gerçek gövdenin (edit'in 5000 yeri) ~3,5 katı. Yalnız bellek okuyan
    endpoint `async` (FOUNDATION 2'ye yazıldı). Değişen: roadmap'in kabul satırı, 6. adım, FOUNDATION,
    CODE-STANDARD (sunucunun kendi koruması düz yazıyla cevap verir, 530'un h11 sınırı).

## Koşudan önce, belgelerin gözden geçirilmesinde

1. **Kaynak karesi silinmiş `i2v` işi saklanan fotoğrafla yapılır** ([v1-18](2026-11-06-queen-studio-v1-roadmap.md#v1-18)).
   Neden: 4. adım fotoğrafı iş için zaten saklıyor; iş durmadan yapılabilir. Seçenek: kuyruğu
   `source_frame_missing` ile durdurmak; kaldırıldı. Değişen: 2., 4., 6. adım.
2. **Kuyruk maddesi ikiye bölündü** ([v1-17](2026-11-06-queen-studio-v1-roadmap.md#v1-17),
   [v1-18](2026-11-06-queen-studio-v1-roadmap.md#v1-18)): kuyruğun kendisi; kendiliğinden durması ve
   core'un yeniden başlaması. Neden: tek madde bir coder'a fazla büyüktü. Seçenek: tek madde. Değişen:
   roadmap, numaralar v1-32'ye kaydı.
3. **Dört Colab'ın hız sınırı bu makineden, deneme hesabıyla dört süreçle ölçülür**
   ([v1-4](2026-11-06-queen-studio-v1-roadmap.md#v1-4)). Neden: testte ücretli katman kullanılmaz ve ölçümler yalnız deneme hesabıyla yapılır.
   Seçenek: dört gerçek Colab. Değişen: 4. adım.
4. **Sürüm kuralı için yer tutucu sayfa** ([v1-3](2026-11-06-queen-studio-v1-roadmap.md#v1-3)): ekran
   yalnız "Queen Studio V1" yazar; tasarlanan ekranlar sonda yerine geçer. Neden: UI en sonda yapılır,
   ilk madde de kurulumdur; sürüm yine ilk ekranda görünür. Değişen: 13. adım, roadmap.
5. **VS Code'un Colab eklentisine düşülmez** ([v1-1](2026-11-06-queen-studio-v1-roadmap.md#v1-1)):
   yalnız Google'ın Colab CLI'ı. Neden: eklentide runtime'ı seçmek ve her hücreyi çalıştırmak
   kullanıcının tıklamasını istiyor; koşu kullanıcıyı beklemeden yürümeli. Seçenek: CLI olmazsa
   eklenti. Değişen: 10. adım, roadmap.
