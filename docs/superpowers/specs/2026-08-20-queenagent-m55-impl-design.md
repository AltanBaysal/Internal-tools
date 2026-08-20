# Madde 55 · Tur 2 (uygulama) — Tasarım

**Madde:** [v4 yol haritası Madde 55](../plans/2026-08-20-queenagent-v4-colab-roadmap.md)
**Turun kırmızısı:** [Tur 1 tasarımı](2026-08-20-queenagent-m55-test-design.md) —
`test_notebook.py`, yedi test.
**Bu belgenin konusu:** CONFIG hücresinin kendisi.

---

## Defterin şekli

`queen-agent/app.ipynb`, nbformat 4. Bu maddede iki hücre doğuyor: başlık (markdown) ve CONFIG
(kod). 56 ve 57 arkasına ekleyecek.

Markdown hücresi bu maddede **kısa** kalıyor — arkadaşının adım adım yolu Madde 58'in işi, ve
defterin ne yaptığını bilmeyen bir kullanıcıya henüz sunulmuyor. Burada yalnız defterin ne olduğu
yazılı.

## CONFIG'in sırası, ve neden bu sıra

**1. Drive bağlanır — ilk satır.** İzin penceresi ilk saniyede çıksın (NOTEBOOK-STANDARD, madde 1).
`import` dışında hiçbir şey ondan önce gelmez. Kırkıncı saniyede beliren bir kutu, kullanıcının
başından kalktığı bir koşuyu bekletir.

**2. Ayarlar.** `DRIVE_FOLDER`, `REPO`, `BRANCH`, `CLONE_DIR`, `APP_DIR`, `APP_PORT`. Hepsi tek
hücrede, çünkü değiştirilecek şeylerin tek yeri olmalı.

`queenAgent` adı **bir kere** geçiyor: `DRIVE_FOLDER`. Kök ondan türetiliyor. İki kopya, biri
değişince yalan olur.

`BRANCH` değişken: geliştirirken `feat/queenagent-colab`, hazır olunca `main`. Bugün `main`
yazılmaz — o dalda henüz bu defter yok, ve olmayan bir dala işaret eden bir ayar, ilk koşuda
anlaşılmaz bir klon hatası verir.

**3. Kök oluşturulur ve gerçekten orada mı diye bakılır.** `makedirs` sonrası `isdir` kontrolü:
mount düşerse `/content/drive` altına yazmak Colab'ın **yerel diskine** düşer, ve o klasör runtime
ile birlikte ölür. Kullanıcı çalıştığını sanar, sonra her şey gider — sessiz kalması en pahalı hata.

**4. Token Secrets'tan okunur.** `userdata.get("GITHUB_TOKEN")`, `try/except` içinde: secret yoksa
ya da deftere erişim verilmemişse `userdata` fırlatıyor, ve o çıplak hata kullanıcıya ne yapacağını
söylemiyor. Yakalanıp boşa çevriliyor, sonra aşağıdaki `assert` ne yapılacağını söylüyor.

**5. Ne olduğu basılır.** Kök ve dal. Kullanıcı hangi klasöre ve hangi dala baktığını görmeli.

## xAI anahtarı burada yok

queen-editor onu Secrets'tan okuyup uygulamaya ortamla geçiriyor. QueenAgent'ın kendi Settings
ekranı var, ve anahtar Drive'daki `settings.json`'a düşüyor — kök Drive'da olduğu için **bir kere**
yazılıyor ve her oturumda orada duruyor. Defterin bunu bilmesine gerek yok.

## Dil

Kullanıcının gördüğü her şey Türkçe: markdown, `print` çıktıları, `assert` mesajları. Yorumlar
İngilizce — onları geliştirici okuyor. Deponun dil kuralı.
