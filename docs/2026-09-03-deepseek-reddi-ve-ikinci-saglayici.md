# DeepSeek'in reddi nereden geliyor, ve ikinci sağlayıcı neden bırakıldı

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **İlgili madde:** 149 *(kullanıldı ve geri
alındı)*, 160 *(bu kayıt)*

Bu belgenin tek işi bir soruya cevap vermek: **"DeepSeek reddediyor, başka bir sağlayıcı deneyelim
mi?"**

Denendi. Cevap aşağıda.

## Kısa cevap

**Hayır — sağlayıcı değiştirmek reddi kaldırmıyor.** Ama **ret de mutlak değil:** aynı model,
`Start a scenario` akışının içinde işi yaptı. Sorun sağlayıcıda değil, isteğin **çıplak mı çerçeveli
mi** geldiğinde.

## Ne yapıldı

Madde 149 aynı DeepSeek ağırlığına **ikinci bir yol** açtı: kendi API'sinin yanında, OpenRouter
üzerinden **DeepInfra'ya sabitlenmiş** bir satır. Amaç modeli ikna etmek değildi — **reddin nereden
geldiğini ölçmekti.**

Yolun mantığı şuydu:

- DeepSeek V4'ün ağırlıkları **MIT lisanslı**. Ticari kullanım, değiştirme ve yeniden dağıtım
  serbest, ve DeepSeek onları bunun için yayımladı. Yani "DeepSeek kalitesi" DeepSeek'in sunucusuna
  bağlı değil.
- Sağlayıcıların **sözleşmeleri** ise ayrı. DeepSeek kendi şartlarında müstehcen içeriği yasaklıyor;
  Together AI §4.2 açıkça *"obscene, or constitutes pornography"* diyor; **DeepInfra'nın şartlarında
  böyle bir madde yok** — yalnız yasa dışı, aldatıcı, taklit ve hak ihlali yasak.
- Bu bir filtre atlatma değil: açık lisanslı bir ağırlığı, o kullanıma izin veren bir sağlayıcıda
  çalıştırmak.

Sabitleme *(`allow_fallbacks: false`)* bir hız ayarı değil **sözleşme seçimiydi**: aynı modeli
OpenRouter'da 17 sağlayıcı sunuyor ve içlerinde Together AI var. Sabitlenmemiş bir istek,
pornografiyi açıkça yasaklayan bir sağlayıcıya düşebilirdi.

## Ölçünün iki yarısı

**1. Çıplak sorulunca reddediyor.** Skill'siz bir sohbette doğrudan istenen sahne için
`DeepSeek Flash · Infra` Türkçe ve gerekçeli bir ret verdi — *"açık ve detaylı cinsel içerik
yazmıyorum"* — ve ardından üç alternatif önerdi.

Aynı ağırlık, başka şirket, aynı cevap. **Yani ret sağlayıcının filtresi değil, ağırlıkların
kendisi.** Ölçmek istenen şey buydu, ve ölçüldü.

**2. Akışın içinde çalıştı.** Aynı model, `Start a scenario` akışında, skill metninin çerçevesi
altında işi yaptı.

**Sonuç: ret bağlama bağlı.** Karar veren şey ağırlıklara yazılmış bir yasak değil, isteğin ne
olduğunun anlaşılıp anlaşılmaması. 3 Eylül'de bir ara yazılan *"DeepSeek ailesi kapandı"* hükmü tek
bir çıplak istek üstüne verilmişti ve **yanlıştı**; o gün kaldırıldı.

Bu ikinci yarı uygulamayı nasıl kullandığımızla ilgili, ve daha değerli olan yarısı: **çerçeve
çalışıyor.**

## İkinci sağlayıcı neden koddan çıktı

Madde 149'un altı commit'i **geri alındı** *(kullanıcı kararı, 3 Eylül)*. OpenRouter yolu,
DeepInfra sabitlemesi, isteğin gövdesine alan ekleyen `extra` tesisatı ve üçüncü anahtar onunla
gitti.

Sebebi basit: **soru cevaplanmıştı.** Yol açıldı, ölçü alındı, ve ölçü ikinci sağlayıcının reddi
kaldırmadığını söyledi. Geriye kalan tek kazanç *"ileride başka bir model bir tablo satırı
uzaklıkta"* idi, ve o kazanç taşıdığı tesisatı hak etmiyordu.

**DeepSeek'in reddettiği yerde kullanıcı Grok Build'e geçip devam ediyor.** Menüde iki DeepSeek
modeli ve Grok duruyor, ve bu yeter.

## Yanında kaybolmasın diye

**Fiyatlar** *(3 Eylül'de OpenRouter'ın kendi model sayfasından doğrulandı)*. OpenRouter jeton başına
komisyon **eklemiyor**: DeepInfra satırı orada da $0.08 / $0.18, DeepSeek'in kendi satırı $0.22 /
$0.66. Kredi yüklerken alınan ücret ayrı ve **ölçülmedi**.

**DeepSeek'in kendi fiyatı düz değil.** Menüdeki rakam off-peak; peak saatlerde *(01–04 ve 06–10
UTC, hafta içi)* ikiye katlanıyor. DeepInfra'da saat yok.

**Önbellek isabetinde DeepSeek daha ucuz** *($0.007'ye karşı $0.016)*, ama kaçırma fiyatı 2.75 kat
pahalı ve bağlam kutusu her round yeniden gidiyor — %90 isabette bile toplam DeepInfra'da kalıyordu.

**Daha ucuzu vardı ve alınmadı:** OpenInference $0.05 / $0.16. Sabitlemenin sebebi fiyat değil hangi
sözleşme altında koşulduğuydu, ve o sağlayıcının şartları okunmadı.

**Ortak havuz 429 veriyor.** İlk deneme `engine_overloaded` / `upstream_provider_shared_pool` ile
düştü. Bu hem sabitlemenin çalıştığının kanıtıydı *(hata `provider_name: DeepInfra` diyor)* hem de
bedeli: sağlayıcı doluysa istek düşüyor, ve uygulama 429'da kendisi tekrar denemiyor. **Bu bulgu
yaşamaya devam ediyor:** Madde 155'in `write_frame_prompt`'u istekleri beşerli dalgalar hâlinde
atıyor ve ilkini tek başına gönderiyor, tam olarak bu yüzden.

**DeepInfra'nın kataloğunda açıkça sansürsüz model yok** *(3 Eylül'de bakıldı)*. Oradaki ucuz ve
güçlü olanlar GLM ve Qwen aileleri — ikisi de DeepSeek'le aynı düzenleyici ortamdan, yani bu konuda
daha gevşek olmaları için bir sebep yok.

## Depo dışında kalan tek şey

Colab Secrets'taki **`OPENROUTER_API_KEY`**. Uygulama artık onu hiç okumuyor. Kullanıcı isterse
siler; kod tarafını ilgilendirmiyor.

## Aynı fikri yeniden önerecek olana

Bu belgenin var olma sebebi bu. Madde 149 tam olarak yukarıdakiler bilinmediği için doğdu, ve
revert docs'u da geri aldığı için ölçüsü hiçbir yerde yazmıyordu.

Yeni bir sağlayıcı önermeden önce sorulacak soru **"hangi sağlayıcı"** değil: *ret ağırlıklardan
geliyor, ve çerçeve onu zaten aşıyor.* Değişecek şey sağlayıcı değil, isteğin nasıl çerçevelendiği.

## Kaynaklar

- [DeepInfra şartları](https://deepinfra.com/terms)
- [DeepInfra fiyatları](https://deepinfra.com/models/text-generation)
- [Together AI §4.2](https://www.together.ai/terms-of-service)
- [OpenRouter sağlayıcı yönlendirme](https://openrouter.ai/docs/features/provider-routing)
- [DeepSeek V4 MIT lisansı](https://framia.converge.ai/page/en-US/news/deepseek-v4-open-source-mit-license)
