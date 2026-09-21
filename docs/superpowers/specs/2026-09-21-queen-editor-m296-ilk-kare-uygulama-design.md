# Madde 296 — Video inince ilk karesi fotoğraf yuvasına, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m296 test turu](2026-09-21-queen-editor-m296-ilk-kare-testler-design.md),
`e3607a90` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## Sıra önemli

Araç dosyası **önce** doğar, ve takım bir kez daha koşulur: kırmızı commit'te eksik modül toplamayı
durdurduğu için altı döngü testi kendi hatasını söyleyemedi. `FfmpegStills` var olunca — ve döngüye
hiç dokunmadan — o altısının `TypeError` ile düştüğü görülür. Ancak ondan sonra döngü değişir.

## 1. `data/ffmpeg_stills.py`

Tek iş: baytlardan ilk kareyi PNG olarak çıkarmak.

```
ffmpeg -y -i <video> -frames:v 1 <hedef.png>
```

`-ss` yok: istenen şey videonun **başlangıcı**, ve bir arama bunu bir başka kareye kaydırırdı.
`run` enjekte edilir *(FfmpegAudio'daki sebeple: test makinesinde ffmpeg yok; Colab'da var)*, ve
geçici oda `MMAudioGenerator`'ın yaptığı gibi `mkdtemp` ile açılıp `finally` içinde silinir — patlasa
da diskte video bırakmaz.

Hata ffmpeg'in **kendi son satırı**. `_last_line` yardımcısı `ffmpeg_audio.py`'da özel; üç satırı
burada yeniden yazmak, iki data modülünü birbirinden bağımsız tutmaya değer.

## 2. `domain/ports.py` — `Stills`

```
class Stills(Protocol):
    def first_frame(self, video: bytes) -> bytes: ...
```

## 3. `domain/run_loop.py`

Videonun satırı yazıldıktan **hemen sonra**, aynı `named.steady()` kapısının içinde: dosya ve satır
tek bir yeniden adlandırmaya karşı birlikte korunuyor, ve resim de o kartın klasörüne yazılıyor.

Yuvanın boş olup olmadığı `layers.can_produce(…, PHOTO)` ile sorulur — kural 293'te tek yere indi ve
burada tekrarlanmaz. `slots` turun kendi anlık görüntüsü; render sırasında o yuvaya kimse yazamaz,
çünkü tek yazan bu döngü.

Çıkarma bir `try` içinde: patlarsa video **tamamdır** ve kuyruk devam eder, hata `log`'a ffmpeg'in
cümlesiyle düşer. Yutulmuyor, yalnız videoyu öldürmüyor.

## 4. Yedi kapı

`stills=None`, `writers`'ın gittiği yoldan: `run_queue`, `start_batch`, `queue_layer`, `regenerate`,
`retry_frame`, `retry_failed`, `resume_batch`. Birini unutmak, o kapıdan üretilen videonun resimsiz
kalması demek — hepsi aynı commit'te.

## 5. `main.py`

`_stills = FfmpegStills()`, ve `writers=_writers` yazan altı `partial`'a `stills=_stills`.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil; turun on testi döner.
