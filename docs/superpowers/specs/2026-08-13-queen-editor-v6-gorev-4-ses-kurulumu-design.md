# Görev 4 — Ses üreticisinin kurulumu

**Roadmap:** [v6](../plans/2026-08-13-queen-editor-v6-roadmap.md) · Blok 2

## Sorun

Ses grubunda tek satır var ve o satır artık var olmayan bir dünyaya ait:

```python
"audio": [
    # MMAudio's node downloads its own weights on first use; nothing here is ours to fetch.
    {"folder": "mmaudio", "name": "mmaudio_large_44k_v2.pth", "url": None},
],
```

"MMAudio'nun node'u" ComfyUI eklentisiydi; onu kullanmıyoruz. Dosya adı da yanlış: örnekleyici
NSFW fine-tune ağırlığını yüklüyor, `mmaudio_large_44k_v2.pth`'ı değil. Panel bugün var olmayan
bir dosyayı sorup "ses kurulu değil" diyor ve kurulunca da yanlış dosyayı arıyor.

## Kararlar

1. **Grup, örnekleyicinin gerçekten yüklediği dosyayı sayar:**
   `mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors`, HuggingFace'te `phazei/NSFW_MMaudio`
   deposunda. Adresi açık, token istemiyor — yani **uygulama kendisi indirebilir**, `url: None`
   olmasına gerek yok. Panelden "Kur"a basmak yetiyor.
2. **Temel ağırlıklar listeye girmez.** MMAudio'nun kendi VAE'si, Synchformer'ı ve vocoder'ı
   kütüphanenin `download_if_needed()`'i ile geliyor; nereye indiğini de o biliyor. Listeye
   koymak, indirmediğimiz bir dosyayı indirmişiz gibi göstermek olurdu.
3. **Kütüphanenin kendisi defterin işi.** `pip install -e .` bir model dosyası değil; üretici
   paneli dosya sayar, paket kurmaz. Görev 6'da defterin kurulum hücresine giriyor.
4. **Dosya ComfyUI'ın model ağacında durur** (`models/mmaudio/`). Tuhaf görünüyor — ComfyUI o
   klasörü okumuyor — ama kurucu, panel ve "kurulu mu" kontrolü hepsi tek köke bağlı, ve tek bir
   dosya için ikinci bir kök icat etmek aynı makineyi iki kez yazmak demek. Bedeli bir satırlık
   açıklama, kazancı tek kurulum yolu.
5. **Yol tek yerde yazılır.** `main.py` örnekleyiciye vereceği yolu grubun kendi satırından kurar;
   dosya adı ikinci bir kez elle yazılmaz. Ad değişirse hem panel hem örnekleyici birlikte değişir.
6. **`GROUPS["audio"]` tek satır kalır.** Örnekleyicinin yüklediği tek dosya o; ikinci bir satır
   eklemek panelin sayısını yalan yapardı.

## Ne değişiyor

| Yer | Bugün | Yarın |
|---|---|---|
| Ses grubu | `mmaudio_large_44k_v2.pth`, `url: None` | NSFW fine-tune `.safetensors`, HF adresiyle |
| Kurulum | panelden imkânsız, kullanıcı kendi indirir | panelden "Kur" indirir |
| Ağırlık yolu | hiçbir yerde | gruptan türetilir, `main.py` örnekleyiciye verir |

## Testler

- Ses grubu tek satır ve adı örnekleyicinin yüklediği dosya; adresi HuggingFace'in `phazei`
  deposunu gösteriyor ve `None` değil.
- Grup satırından kurulan yol `models/mmaudio/<ad>` ile bitiyor — `main.py`'nin yaptığı işin
  aynısı, ama test edilebilir bir yardımcıda.

## Öz eleştiri

- *Ağırlığı ComfyUI'ın klasörüne koymak ileride kafa karıştırır mı?* — Karıştırabilir, o yüzden
  satırın yanında neden orada olduğu yazıyor. Alternatif ikinci bir kök, ikinci bir "kurulu mu"
  yolu ve panelde ikinci bir kaynak demekti; tek dosya bunu hak etmiyor.
- *URL'nin doğruluğunu test edebiliyor muyuz?* — Hayır, test ağ istemiyor; iddia edebildiğimiz şey
  adresin var olduğu ve deponun adı. Adresin gerçekten indirdiğini Colab turu gösterir — tıpkı
  diğer HF satırları gibi.
