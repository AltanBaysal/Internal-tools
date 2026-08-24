# v14 Görev 27 — Tünelin taşıma protokolü: İMPLEMENTASYON döngüsü tasarımı

**Tarih:** 2026-08-24 · **Kaynak:** [test spec'i](2026-08-24-queen-editor-v14-gorev-27-testler-design.md)
**Ölçüm:** [araştırma belgesi](../research/2026-08-23-queen-editor-galeri-yavasligi.md) §0
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 27

## Kırmızı testlerin istediği

Önceki commit iki testi kırmızı bıraktı; ikisi de `app.ipynb`'nin Flask hücresinin metnine bakıyor.

| # | Test | Ne arıyor |
|---|---|---|
| A1 | `test_the_tunnel_is_opened_over_tcp_rather_than_quic` | Hücrede `"--protocol", "http2"` |
| A2 | `test_the_protocol_flag_says_what_it_is_standing_in_for` | Aynı hücrede `QUIC` kelimesi |

## Değişiklik

Flask hücresi, tünel başlatması:

```python
tunlog = "/content/cloudflared.log"
# --protocol http2: Colab throttles the default QUIC. Same photo, 17.74 s -> 0.18 s.
subprocess.Popen(["/content/cloudflared", "tunnel", "--protocol", "http2",
                  "--url", f"http://127.0.0.1:{APP_PORT}"],
                 stdout=open(tunlog, "w"), stderr=subprocess.STDOUT)
```

`"--protocol"` ve `"http2"` **iki ayrı dize**. Tek dize yazılırsa `subprocess` onu tek argüman
sanır, cloudflared reddeder — ve A1 de düşer, ki bu doğru davranış.

### Verilen kararlar

**Bayrak sabit, seçenek değil.** Bir gün http2 ile tünel açılmazsa defter durur ve cloudflared'in
kendi log'unu basar. Varsayılana geri çekilmek, doksan kat yavaş bir uygulamayı "çalışıyor" diye
sunmak olurdu; QUIC'in bu ağda çalışmadığı ölçüldü.

*Bu yüzden bayrak bir sabite de alınmıyor:* bir kez kullanılan değere isim vermek dolaylılık ekler,
ve bir sabit "bu ayarlanabilir" diye okunur — verilen karar bunun tersi.

**Hücre çıktısı değişmiyor.** Bayrağın koşana görünmesi tartışıldı ve gerek görülmedi; çıktı
bugünkü sadeliğinde kalıyor — `✓ Flask ayakta`, link, yönerge.

**Yorum kısa.** Neden http2 kullanıldığı yeter; QUIC'in UDP üstünde çalıştığı, Colab'ın UDP'yi
kısıp TCP'yi kısmadığı gibi ayrıntılar okuyanın zaten çıkarabileceği şeyler. Ölçümün nerede
durduğunu `git blame` ve commit mesajı söylüyor, o yüzden belge yolu da yoruma girmiyor.

## Dal adı

Aynı hücre değil ama aynı iş: defteri bu koşunun gerçeğine uydurmak.

```python
# The notebook and the code it clones are one thing: the clone cell asserts on files this run
# added, so a branch without them stops before anything installs. Back to main once this lands.
BRANCH       = "feat/queen-editor-v4"       # released work lands in main; a dev run points here
```

Defter bugün `main`'i klonluyor, `main` ise bu koşunun dosyalarını taşımıyor —
`workflow_video_first_last_api.json` orada yok ve klon hücresi ona `assert` ediyor. Yani defter şu
hâliyle Colab'da hiç açılmıyor, madde 30'un turu da yapılamıyor.

**Riski yazılı:** iş main'e inerken bu satır `main`'e dönmezse herkes bir geliştirme dalını
klonlamaya başlar, ve bu sessizce olur. Yorumun son cümlesi bunun için orada.

**Testi yok, bilerek.** Dal adını sabitleyen bir test main'e inerken kaçınılmaz olarak kırılırdı:
yanlış şeyi korur, doğru işi engellerdi.

**Bayrakla aynı commit'e giriyor** — ayırmak bir satırlık iki commit üretirdi.

## Doğrulama

`python -m pytest queen-editor -q` → **711 passed.** İki kırmızı yeşile döner, 709 yerinde kalır.
Test dosyasına dokunulmaz: testi koda uydurmak turun anlamını yok eder.

Hızın kendisi burada doğrulanamaz — bir Colab hücresi pytest'te koşmuyor. **"Bitti" yargısı Colab
turunundur** (madde 30): çok kareli bir projede galeri açılırken uygulamanın kilitlenmemesi ve
karoların gözle görülür hızda dolması.

## Kapsam dışı

- **Uygulama koduna dokunulmuyor.** Değişen tek dosya `app.ipynb`.
- **Ön yüz derlenmiyor.** `frontend/` tarafına girilmiyor, `dist` yeniden üretilmiyor.
- **Hız yeniden ölçülmüyor** — kullanıcı kararı (24 Ağustos): *"hızlanması kesinse miktarını
  ölçmek önemli değil şimdilik, yine sorun yaşarsak ölçeriz"*.
