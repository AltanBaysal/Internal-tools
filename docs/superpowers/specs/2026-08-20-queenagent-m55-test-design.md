# Madde 55 · Tur 1 (test) — Tasarım

**Madde:** [v4 yol haritası Madde 55](../plans/2026-08-20-queenagent-v4-colab-roadmap.md)
**Bu belgenin konusu:** CONFIG hücresini **ne tutacak**.

---

## Defter nasıl test edilir

Çalıştırılarak değil **okunarak**. Bir Colab hücresi burada koşamaz: `google.colab` yok, Drive yok,
GPU yok. Ama metnin cevaplayabileceği sorular tam da önemli olanlar — hangi hücre neyi yapıyor,
hangi sır nereden okunuyor, eksik olan söyleniyor mu.

Desen queen-editor'ün defter testinden alınıyor: `.ipynb` bir JSON, `json.load` ile ayrıştırılıp
hücrelerin kaynağı okunuyor. Ham metin olarak okumak yanlış olurdu — kaçırılmış tırnaklar ve satır
sonları aranırdı, hücrenin çalıştırdığı kod değil.

İki yardımcı: bütün hücrelerin kaynağı tek metin olarak (`_source`), ve **belli bir hücrenin**
kaynağı (`_cell`). İkincisi gerekli çünkü bazı sorular "var mı" değil "**nerede**" — ve tek metin
hücreleri birbirinden ayıramaz.

## Tutulacak kurallar

**1. Drive ilk bağlanır.** İzin penceresi ilk saniyede çıkmalı (NOTEBOOK-STANDARD, madde 1).
Kırkıncı saniyede beliren bir izin kutusu, kullanıcının başından kalktığı bir koşuyu bekletir.
Sorulacak şey: `drive.mount` çağrısı CONFIG hücresinde, ve **kendisinden önce iş yapan bir satır
yok**.

**2. Kök, adı tek yerde duran klasör.** `MyDrive/queenAgent` — ama `queenAgent` dizesi bir kere
geçmeli (`DRIVE_FOLDER`), yolun içine ikinci kez gömülmemeli. İki kopya, biri değişince yalan olur.

**3. Bağlanmamış bir Drive sessizce geçmez.** Mount başarısızsa `/content/drive` altına yazmak
Colab'ın yerel diskine düşer, ve o klasör runtime ile birlikte ölür — kullanıcı çalıştığını sanır,
sonra her şey gider. Kök oluşturulduktan sonra gerçekten orada mı diye bakılmalı.

**4. GitHub token'ı Secrets'tan gelir, defterin içinden değil.** Defter git'te; kaynağına
yapıştırılmış bir token, erişim verdiği deponun içine konmuş olurdu.

**5. Token yoksa ne yapılacağı söylenir.** Boş bir `KeyError` değil, ne ekleneceğini ve nereye
ekleneceğini söyleyen bir `assert`. Ve sebep uydurulmaz.

**6. xAI anahtarı burada sorulmaz.** queen-editor onu Secrets'tan okuyor; QueenAgent'ın kendi
Settings ekranı var ve anahtar Drive'daki `settings.json`'a düşüyor — bir kere yazılıyor, sonsuza
kadar kalıyor. Bu **bilerek** ayrılan yer, ve testi olmazsa biri "queen-editor'de var, burada
unutulmuş" diye ekler.

## Sorulmayan

Hücrenin **çalıştığı**. Bu test defterin doğru şeyleri söylediğini tutuyor, doğru çalıştığını değil;
onu ancak Colab'da koşmak gösterir, ve o kullanıcının turu.
