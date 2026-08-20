# Madde 56 · Tur 1 (test) — Tasarım

**Madde:** [v4 yol haritası Madde 56](../plans/2026-08-20-queenagent-v4-colab-roadmap.md)
**Bu belgenin konusu:** klon hücresini **ne tutacak**.

---

## Hücrenin işi

Depoyu Colab'ın yerel diskine indirmek, uygulamanın tek bağımlılığını kurmak, ve derlenmiş arayüzün
gerçekten geldiğini doğrulamak.

## Tutulacak kurallar

**1. Sil ve yeniden klonla.** `git pull` değil. Yerel ağaç harcanabilir; her koşu aynı yerden aynı
şeyi getirsin. `pull` bir birleştirme çakışmasıyla durabilir ve o hâlde ne olduğunu kullanıcı
anlayamaz. Sorulacak: `shutil.rmtree` var, ve `git pull` **yok**.

**2. Token kabuğa hiç girmez.** `subprocess.run` bir **argüman listesiyle** çağrılır, `shell=True`
ile değil. Kabuğa giren bir URL kabuk geçmişine ve log satırlarına düşer. Sorulacak: `shell=True`
defterde yok.

**3. Token hiçbir çıktıda görünmez.** Klon URL'i token taşıyor ve **hiç basılmıyor**; hata
durumunda git'in kendi stderr'i basılıyor ama token maskelenerek. Sorulacak: bir maskeleme
fonksiyonu var ve hata yolunda kullanılıyor.

**4. Sebep uydurulmaz.** Klon düşerse git'in kendi sözleri basılır — "token süresi dolmuş" gibi bir
tahmin değil. Deponun kuralı, ve burada özellikle kolay ihlal edilir: 403'ün onlarca sebebi var.

**5. Bağımlılık kurulur ve söylenir.** Uygulamanın tek üçüncü parti paketi Flask. Colab'da zaten
kurulu, ama defterin "Colab'da vardır" varsayımına sessizce yaslanması yanlış — bir satır, ve
kurulu olduğu için anında dönüyor.

**6. Derlenmiş arayüz aranır.** Defter derlemiyor. `dist/index.html` klondan sonra yoksa hücre
**durur** — unutulmuş bir derleme burada görünsün, kullanıcının karşısına boş sayfa olarak değil.
Bu, Madde 54'ün testlerinin depo tarafındaki karşılığı: orası commit'lenmiş mi diye sorar, burası
gelmiş mi diye.

**7. CONFIG koşmadan bu hücre koşmaz.** Bu hücrenin yollara ihtiyacı var ve onlar CONFIG'de
tanımlanıyor. Kapı olmazsa, düşmüş bir CONFIG ancak çok sonra ve anlaşılmaz bir hatayla ortaya
çıkar. queen-editor'ün deseni: `assert "..." in globals()`.

## Sorulmayan

Klonun **gerçekten çalıştığı**. Ağ yok, token yok, git yok — bu testin cevapladığı şey defterin
doğru şeyi söylediği, doğru çalıştığı değil.
