# Yeni editör — 11. Kod standardı

Kodun nasıl düzenlendiği ve hangi kurallarla yazıldığı.

## Düzen

- **Core, API gruplarıyla birebir:** `projects`, `frames` (medya dahil), `edits`, `jobs`, `queue`,
  `exports`, `history`, `models`; discovery ve health küçük bir `api` grubundadır. Bir endpoint'i
  arayan aynı adlı klasöre bakar.
- **Her grup klasöründe üç dosya:** kurallar (dışarıdan habersiz), kayıt (depoya nasıl yazıldığı),
  endpoint'ler.
- **Kapılar ayrıdır:** `storage` (depo portu; Drive ve bellek içi adaptörleri), `comfy`, `ffmpeg`,
  `downloads` (Hugging Face ve Civitai'den model indirmek; kuralları `models` grubundadır), saat,
  Colab diski ve ekran kartı.
  Bir kapı hiçbir gruba bakmaz; kapılar birbirine bakmaz.
- **Gruplar birbirini çağırabilir, döngü olmaz.** Ör. kare silinirken `frames`, `jobs`'a sorar;
  `jobs` da `frames`'e soruyorsa bu döngüdür ve yasaktır.
- Gerçek kapılar tek bir başlangıç dosyasında bağlanır.
- UI da aynı gruplarla düzenlenir.

## Dil

- Kod, yorumlar, API açıklamaları, hata mesajları ve UI İngilizcedir.
- `docs/` altındaki belgeler Türkçe kalır.

## Mesajlar

- Endpoint'lerin ve alanların açıklamaları agent'a yazar gibi yazılır.
- Hata mesajı neyin eksik ya da yanlış olduğunu ve nedenini söyler.
- Bir servisin (Drive, ComfyUI, ffmpeg) hatası, servisin kendi sözleriyle iletilir.
- Her hata dört alanla döner: `code` (sabit adı), `message` (ne olduğu; bir servisin hatasıysa onun
  sözüyle), `details` (ek bilgi), `hint` (agent'a bir sonraki adım; kullanıcıya sorulacaksa bunu da
  söyler). Fikir PostgREST'ten; birebir aynı olması gerekmez. Core'un ve adaptörün hataları,
  FastAPI'nin kendi doğrulama hataları da, aynı biçime çevrilir.
- `hint` yalnız core'un kesin bildiğini söyler. Core'un kendi kuralından gelen hatada ne yapılacağını
  söyler (ör. "işi kuyruktan çıkarman yeterli"). Bir servisin hatasında (Drive, ComfyUI, ffmpeg)
  `message` servisin kendi sözüdür; `hint` neden tahmin etmez ve emir vermez, yalnız durumu ve elde
  olan seçeneği söyler (ör. "kuyruk bu hata yüzünden durdu; neden düzelince `resume` ile
  sürdürülebilir"). Söyleyecek kesin bir şey yoksa boş kalır.

## Maliyet

- Her endpoint'in maliyeti spec'te yazılıdır: kaç depo isteği yaptığı, kaç dosya okuduğu.
- Hiçbir istek bütün projeleri ya da bütün kareleri gereksiz yere okumaz.
- Bir işlem liste büyüdükçe büyüyorsa nedeni yazılır.

## Temiz kod

- Çalışan çözümlerin en basiti seçilir.
- Her dosyanın tek işi vardır.
- Yorum nedeni ve bugün doğru olanı söyler; geçmiş git'tedir.

## Kontrol araçları

- Python: `ruff` (biçim ve yaygın hatalar), `pyright` (türler, sıkı).
- UI: TypeScript sıkı modu, `eslint`.
- Testlerle birlikte koşarlar; biri hata verirse değişiklik bitmiş sayılmaz.
