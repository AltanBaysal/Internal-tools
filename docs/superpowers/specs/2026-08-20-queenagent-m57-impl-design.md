# Madde 57 · Tur 2 (uygulama) — Tasarım

**Madde:** [v4 yol haritası Madde 57](../plans/2026-08-20-queenagent-v4-colab-roadmap.md)
**Turun kırmızısı:** [Tur 1 tasarımı](2026-08-20-queenagent-m57-test-design.md) —
`test_notebook.py`, sekiz test.
**Bu belgenin konusu:** sunucu hücresinin kendisi.

---

## Sıra

1. **Kapı** — `assert "APP_DIR" in globals()`.
2. **Temizlik** — `pkill` ile önceki `main.py` ve `cloudflared` süreçleri.
3. **Başlat** — `Popen(["python", "main.py"], cwd=APP_DIR, env=…)`, log bir dosyaya.
4. **Bekle** — `/api/health` 90 sn, cevap gelmezse log'un son satırları ve `RuntimeError`.
5. **Tünel** — `cloudflared` indirilir, açılır, log'undan link okunur.
6. **Bas** — link, ve yanında parolasız olduğu uyarısı.
7. **Açık kal** — `tail -f`.

## Kök neden ortamla geçiyor

Uygulama nereye yazacağını `QUEENAGENT_ROOT`'tan öğreniyor, ve varsayılanı ev dizini. Colab'da ev
dizini yerel disk — runtime kapanınca her şey gider, ve kullanıcı bunu ancak ertesi gün anlar.
Defter bu değişkeni Drive'a bakan yola bağlıyor; bağlamayı unutmak, sessizce veri kaybetmenin en
kısa yolu.

`env={**os.environ, …}`: Colab'ın kendi ortamı korunuyor, üstüne bir anahtar ekleniyor. Ortamı
sıfırdan kurmak `PATH`'i de götürürdü.

## Neden `cwd=APP_DIR`

`main.py` `from backend import config` diyor, ve `backend` ancak `queen-agent/` dizininden çözülüyor.
Başka bir dizinden başlatmak `ModuleNotFoundError` verir.

## Düşen sunucu

90 saniye `/api/health` yoklanıyor. Cevap gelmezse **sunucunun kendi log'unun** son satırları
basılıyor ve `RuntimeError` atılıyor. Sebep uydurulmuyor: bir Flask süreci onlarca sebeple ölür —
eksik paket, tutulu port, bozuk bir import — ve defter hiçbirini bilmiyor.

## Uyarı linkin yanında

Uygulamada giriş yok, ve bu kullanıcının kararı. Kararın bedeli: linki eline geçiren her şeye
erişiyor — anahtarı harcayabiliyor, bütün dosyaları okuyabiliyor. Uyarı **linkin bastığı satırın
hemen yanında** duruyor; README'de ya da markdown'da yazılı olması, o an linki kopyalayıp gönderen
kişiye ulaşmaz.

## Hücre neden bitmiyor

Biten bir hücre Colab'a "burada iş kalmadı" der; runtime boşta sayılır ve kapatılır, tünel de
onunla gider. `tail -f` hücreyi açık tutuyor **ve** aynı anda sunucunun log'unu canlı gösteriyor —
tek satırla iki iş.

## Yeniden çalıştırma

Hücre ikinci kez koşarsa önce `pkill`. Bu oturumda tam olarak bunun eksikliği yaşandı: eski bir
sunucu bütün istekleri karşılamaya devam etti ve yeni sunucu portu aldığını sandı. Colab'da aynı
şey runtime yeniden başlamadan hücre tekrar çalıştırıldığında olurdu.
