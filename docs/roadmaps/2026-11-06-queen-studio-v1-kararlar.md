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
