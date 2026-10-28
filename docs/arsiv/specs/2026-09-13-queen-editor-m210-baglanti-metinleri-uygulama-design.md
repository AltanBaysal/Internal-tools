# Madde 210 · Bağlantı metinleri — uygulama turunun tasarımı

**Tarih:** 13 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)
**Test turu:** [tasarım](2026-09-13-queen-editor-m210-baglanti-metinleri-testler-design.md) ·
[plan](../plans/2026-09-13-queen-editor-m210-baglanti-metinleri-test-plan.md) · kırmızı `8774414`

## Eşleme

Kırmızının listesi dört hedefe dağılıyor, ve her hedefte metindeki eski numaranın bugünkü karşılığı
tek: hangi belgeye gittiği bilindiğinde hangi koşu olduğu da biliniyor.

| Hedef belge | Metindeki eski numara | Yerine |
|---|---|---|
| `…-queen-editor-v1-roadmap.md` | v2 · v3 | `v1 Koşu 2` · `v1 Koşu 3` |
| `…-queen-editor-v2-roadmap.md` | v4 | `v2` *(tek koşu, bölüm yok)* |
| `…-queen-editor-v3-roadmap.md` | v5 · v6 · v7 · v8 · v9 · v11 · v12 · v13 | `v3 Koşu 1` … `v3 Koşu 8` |
| `…-queen-editor-v4-roadmap.md` | v14 | `v4` *(tek koşu, bölüm yok)* |

Koşu numaraları uydurulmuyor; hedef belgelerin kendi `# Koşu N — … *(o zamanki adıyla "…")*`
başlıklarından okunuyor.

## Değişim hedefe göre yapılır, metne göre değil

Bu turun tek gerçek tuzağı: **`v2` yazan her metin yanlış değil.** queen-editor v1 ve v3 yol
haritaları, metni *"v2 yol haritası"* olan ve `2026-08-08-queen-editor-v2-roadmap.md`'ye giden bir
bağlantı taşıyor — ve bu doğru, metindeki numara hedefin numarasıyla aynı. Kör bir metin değişimi
bunları bozar. *(Örnek burada bilerek düz metin: parantezli yazılsaydı bağlantı çivisi onu bu
klasörden çözmeye çalışırdı.)*

O yüzden her bağlantı **çifti** olarak ele alınıyor: önce hedefin dosya adından sürümü çözülüyor,
sonra yalnız o hedefe ait eşleme uygulanıyor, ve yalnız **bağlantı metninin içinde**. Metnin dışındaki
hiçbir `v5` cümlesine dokunulmuyor — bir spec'in gövdesinde *"v5 turunda şu karara varıldı"* demesi
o günün kaydıdır ve bu maddenin konusu değil.

## Elle kalanlar

Değişim, numarayı bölüm adıyla birlikte yerine koyuyor: eski *"v3 yol haritası"* metninde `v3`'ün
yerine `v1 Koşu 3` geçince ortaya sözcük sırası bozuk bir tamlama çıkıyor. İki kalıpta oldu ve ikisi
de elle düzeldi — biri *"v1 yol haritası · Koşu 3"*, öteki koşu ile görev arasına `·` alan
*"v3 Koşu 1 · Görev 2"*. Çivi bunları yakalamaz *(numara doğru)*, okuyan yakalar.

## Dokunulmayanlar

- **`adıyla` geçen metinler.** Yeniden adlandırmayı anlatan cümleler eski numarayı söylemek zorunda;
  çivi de onları muaf tutuyor.
- **Dosya adları.** `2026-08-13-queen-editor-v7-gorev-3-foto-modelleri-design.md` gibi spec adları
  olduğu gibi kalıyor: bir spec'in adı yazıldığı günün kaydı, ve onları değiştirmek yazılmış her
  atıfı kırardı. Standart yalnız **yol haritası** adlarını bağlıyor.
