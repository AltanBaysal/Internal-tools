# Madde 56 · Tur 2 (uygulama) — Tasarım

**Madde:** [v4 yol haritası Madde 56](../plans/2026-08-20-queenagent-v4-colab-roadmap.md)
**Turun kırmızısı:** [Tur 1 tasarımı](2026-08-20-queenagent-m56-test-design.md) —
`test_notebook.py`, yedi test.
**Bu belgenin konusu:** klon hücresinin kendisi.

---

## Sıra

1. **Kapı** — `assert "CLONE_DIR" in globals()`. Bu hücrenin yolları CONFIG'de tanımlı; kapı olmazsa
   düşmüş bir CONFIG çok sonra ve izi sürülemez bir hatayla ortaya çıkar.
2. **Sil** — `shutil.rmtree(CLONE_DIR)`. Yerel ağaç harcanabilir.
3. **Klonla** — `subprocess.run` bir argüman listesiyle, `--depth 1`, `--branch BRANCH`.
4. **Düşerse söyle** — git'in kendi stderr'i, token maskelenmiş, `RuntimeError`.
5. **Flask** — `pip install -q flask`.
6. **Derlenmiş arayüz var mı** — `dist/index.html` aranır, yoksa durulur.
7. **Söyle** — tek satır, ne olduğunu.

## Token üç yerden birden korunuyor

Bir sırrı bir kere korumak yetmiyor; sızabileceği her yol ayrı ayrı kapanmalı.

- **Kabuk:** `subprocess.run` argüman listesiyle çağrılıyor, `shell=True` yok. Kabuğa giren bir URL
  kabuk geçmişine ve log satırlarına düşer.
- **Çıktı:** `clone_url` hiçbir `print`'in içinde geçmiyor. Token'ı taşıyan tek dize o.
- **Hata metni:** git'in stderr'i basılmadan önce `_mask`'ten geçiyor — token yerine `<token>`.
  Hata metinleri en kolay unutulan sızıntı yolu, çünkü mutlu yolda hiç görünmüyorlar.

## Sebep uydurulmuyor

Klon düşerse basılan şey git'in **kendi sözleri**. Bu deponun kuralı ve burada özellikle kolay
ihlal edilir: 403'ün onlarca sebebi var — süresi dolmuş token, yanlış kapsam, deftere erişim
verilmemiş secret, silinmiş dal. Defter hangisi olduğunu bilmiyor, o yüzden tahmin etmiyor.

## Neden `dist` burada da aranıyor

Madde 54 deponun tarafını tutuyor: bundle commit'lenmiş mi. Bu, çalışma anının tarafı: bundle
**gelmiş mi**. İkisi aynı hatayı iki farklı yerde yakalıyor, ve buradaki olmazsa unutulmuş bir
derleme kullanıcıya boş sayfa olarak varıyor — hiçbir şey söylemeyen bir hata.

## Flask neden kuruluyor

Uygulamanın tek üçüncü parti bağımlılığı. Colab'da zaten kurulu, yani satır anında dönüyor. Yine de
yazılıyor: defterin "Colab'da vardır" varsayımına sessizce yaslanması, o varsayım bir gün
değiştiğinde anlaşılmaz bir `ModuleNotFoundError` demek.
