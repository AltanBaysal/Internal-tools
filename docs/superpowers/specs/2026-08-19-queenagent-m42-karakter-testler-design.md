# Madde 42 — Karakter dosyaya, sayı kullanıcıya · Test Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 42](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Kaynak:** [test bulguları, bulgu 5](../research/2026-08-18-queenagent-test-bulgulari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

Bu belge **yalnız testlerin** turuna aittir.

---

## 1 · Üç şey değişiyor

**Sayıyı model karar vermiyor.** Bugünkü kural "iki üç aday sun" diyor; kullanıcı beş isterse de üç
geliyor. Yeni kural: kullanıcı söylediyse o kadar, söylemediyse **sor**. Kaç aday isteneceği
kullanıcının işi, ve bir tahmin her seferinde ya fazla ya eksik.

**Çıktı sohbete değil dosyaya.** Adaylar sohbete yazıldığında beğenilen prompt elle kopyalanıyor —
tam da yapı dosyasının önlemek için var olduğu iş. Çıktı, yapı dosyasındaki haritalarla **aynı
şekilde** bir JSON olur; doğrudan yapıştırılabilir.

**Dosyanın adı karakterden gelir.** `aylin.json`. Genel bir ad, denemeler biriktikçe hangi dosyanın
kim olduğunu kaybettiriyor.

## 2 · Yapıştırılan prompt

Kullanıcı beğendiği bir görselin promptunu yapıştırabiliyor. O prompt bir **biçim örneği**:
etiketlerin yoğunluğu, sırası, dili oradan alınır. Ama içinden kareye ait olanlar — poz, mekân,
kamera, kalite etiketleri — ayıklanır, çünkü onlar karakterin değil.

## 3 · Kıyafet yazılır, kimliğe girmez

Madde 40 kıyafeti `outfits`'e taşıdı ve karakter yönergesinden "what they are wearing" cümlesini
düşürdü. Bu madde işin diğer yarısını yapıyor: beceri kıyafeti **üretmeye devam eder**, ama aynı
dosyada ayrı bir `outfits` girdisi olarak ve giysiye göre adlandırılmış hâlde. Kullanıcının sözü:
*"karakter becerisi elbiseyi yazsın ama karaktere yazmasın."*

## 4 · Testler ne çiviliyor

**`test_skills.py`:**

| # | Durum | Beklenen |
|---|---|---|
| 1 | Karakter yönergesi | "two or three" geçmez; sayı kullanıcıdan gelir, söylenmediyse sorulur |
| 2 | Karakter yönergesi | `create_file` geçer; "stays in the chat" ve "Do not create a file" geçmez |
| 3 | Karakter yönergesi | Dosya adı karakterden türer, örneğiyle (`aylin.json`) |
| 4 | Karakter yönergesi | Çıktının şekli: `characters` ve `outfits` girdileri, yapı dosyasıyla aynı |
| 5 | Karakter yönergesi | Yapıştırılan prompt biçim örneğidir; kareye ait olanlar ayıklanır |
| 6 | Sohbette kalan beceriler | Artık yalnız `split-into-frames` |

6 numaralı test bugünkü parametreli testin daraltılmış hâli: karakter becerisi artık dosya yazıyor,
o listede kalması yalan olurdu.

## 5 · Testlerin bakmadığı yer

Modelin gerçekten sorup sormadığı, gerçekten temiz JSON yazıp yazmadığı yönergeyle sınanamaz —
kullanıcının elle turunda görülür. Test yönergenin ne söylediğini çiviliyor.

## 6 · Kabul ölçütü — kırmızının doğru olması

1-6 **düşer**: bugünkü metin iki üç aday diyor, sohbette kalıyor, dosyadan hiç söz etmiyor.
`skip` yok, `xfail` yok.
