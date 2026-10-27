# Madde 210 · Bağlantı metinleri — test turunun tasarımı

**Tarih:** 13 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)
**Öncesi:** [sürüm kaydı](2026-09-11-queen-editor-m210-surum-kaydi-testler-design.md) ·
[QueenAgent'ın dalları](2026-09-13-queen-editor-m210-queenagent-dallari-testler-design.md)

## Bulunan

On üç belge beşe inerken adlar değişti ve **bağlantıların yolu düzeltildi, metni düzeltilmedi.** Bugün
120 spec ve plan şunun gibi bir satır taşıyor:

> **Yol haritası:** *"v5 yol haritası Görev 12"* → hedefi `2026-08-12-queen-editor-v3-roadmap.md`

Bağlantı çözülüyor — o yüzden `test_every_link_to_a_roadmap_resolves_from_where_it_is_written` yeşil
kaldı. Yalan söyleyen şey **metin**: v5 diye bir belge yok, ve okuyucu tıklamadan önce olduğunu
sanıyor. Maddenin kuralı *"ad kaydın kendisidir"* ise, o adı yazan her yer de kayıttır.

**Kullanıcı kararı, 13 Eylül:** hepsi düzelir, ve bir çiviyle tutulur. İkinci okuma — *"o spec 13
Ağustos'ta yazıldı, o gün belgenin adı gerçekten v7'ydi, tarihî kayıt sayılsın"* — tartışıldı ve
seçilmedi: eski ad zaten hedefteki `Koşu N` başlığında duruyor, yani onu bağlantı metninde tutmanın
bir bedeli var ve bir getirisi yok.

## Çivi

Bir bağlantının **metnindeki** sürüm numarası, **gittiği belgenin** sürüm numarasından farklı olamaz.

Okuma şöyle: markdown bağlantısının hedefi bir yol haritasıysa, hedefin adından *(tool, sürüm)*
çözülür; metinde `v<N>` geçiyorsa o `N` hedefin sürümüne eşit olmalı. Metinde hiç numara yoksa
söyleyecek bir şey yok, muaf.

**Bir muafiyet var: eski adı açıkça anan metin.** Yeniden adlandırmayı anlatan cümlenin eski adı
söylemesi gerekir, ve orada söylemek doğrudur — v5 yol haritası kendi tablosunda *"20 Ağustos'ta v14
adıyla kapanan koşu"* diye bağlanıyor. Muafiyetin işareti **`adıyla`** kelimesi: bir metin eski adı
*"… adıyla"* diye anıyorsa geçmişten söz ettiğini söylemiş olur. Kelimeyi taşımayan bir metin bugünü
anlatıyor sayılır.

Muafiyeti dar tutmanın sebebi: geniş bir muafiyet çivinin kendisini boşa çıkarır, ve bu çivi zaten
tek bir şeyi tutuyor — numaranın sessizce eskimesini.

## Neyi tutmuyor

Metindeki numara ile hedefin numarası aynı olduğu hâlde **bölüm** yanlış olabilir — *"v3 yol haritası
Koşu 5 · Görev 12"* derken Görev 12 aslında Koşu 1'de olabilir. Bunu tutmak her koşunun madde
aralığını bilmek demek, ve o aralıklar belgenin gövdesinde başlık başlık duruyor; okuması kırılgan,
değeri düşük. Koşu adı bu turda elle ve eşlemeden konuyor.

## Bu turda değişen

Yalnız [test_version_record.py](../../../queen-editor/backend/tests/test_version_record.py). 120
dosyanın metni **uygulama turunun** işi; bu tur kırmızıyı koyar ve kırmızı ihlallerin tam listesini
basar.
