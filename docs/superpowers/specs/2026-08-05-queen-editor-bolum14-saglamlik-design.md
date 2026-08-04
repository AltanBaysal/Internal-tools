# Queen Editor — Bölüm 14: Sağlamlık

**Tarih:** 2026-08-05 · **Yol haritası:** [2026-08-03-queen-editor-v2-roadmap.md](../plans/2026-08-03-queen-editor-v2-roadmap.md) Bölüm 14
**Tasarım kaynağı:** claude.ai/design `Queen Editor Basit v1.html` — `ArtboardS_GenError`,
`ArtboardS_GenStopped`.

## Ne çalışır

Hiçbir senaryoda iş kaybı yok:

1. **Tekil kare patlarsa** galeride kırmızı bir kare kalır ve üstünde **Tekrar dene** durur; üretim
   sıradaki kareyle devam eder, ilerleme kartında "N fotoğraf üretilemedi — diğerleri devam ediyor"
   satırı görünür (bu satır Bölüm 7'den beri var).
2. **Ölümcül durma** (üst üste hatalar, servis ölümü) → panelde kırmızı "Üretim durdu — X/Y
   tamamlandı" kartı, altında sunucunun kendi teknik satırı ve üstünde büyük **Kaldığı yerden
   devam et**; basınca yalnız eksikler üretilir.
3. **Oturum ölse bile** — sekme kapansa, bilgisayar kapansa, Colab çökse — proje yeniden açılınca
   yarım kalan üretim aynı kartla karşılar ve tek tıkla sürer.

## Kapsam dışı

- Otomatik yeniden deneme / geri çekilme (backoff) — kullanıcı basar, araç kendiliğinden denemez.
- ComfyUI'ın kendisini yeniden başlatmak — notebook'un işi.
- Hatalı karenin sebebini yorumlamak: sunucunun/servisin metni ne diyorsa o basılır.

## 1. Yarım kalan üretim nereden bilinir

Oturum ölünce sunucunun belleği gider; Drive kalır. Yarım kalan üretim zaten oradan okunabiliyor:
**plan eksi kayıt** (Bölüm 13'ün kuralı). Yeni uç bunu söyler:

`GET /api/projects/<p>/queue` → `{"pending": [dosya adları], "total": N}`

- `pending` — planın, kayıtta karşılığı olmayan kareleri, plan sırasıyla.
- `total` — planın tamamı; kart "X/Y tamamlandı" derken Y budur, X = `total - len(pending)`.
- Plan yoksa `{"pending": [], "total": 0}` — yarım iş yok demektir.

Bu uç **koşu sürerken de doğrudur** ama ekran o sırada `/api/status`'un canlı `pending`'ini
kullanır (Bölüm 13): saniyede bir dosya okumak yerine, zaten gelen cevabın içindekini. Kuyruk ucu
**proje açılışında ve koşu bittiğinde** sorulur.

**Teknik sebep uydurulmaz.** Oturum ölümünden sonra neden durduğu bilinmiyor: kart yalnız
"Üretim yarım kaldı — X/Y tamamlandı" der, kırmızı teknik satır **yoktur**. Aynı oturumda ölümcül
durma olduysa sebebi sunucu biliyor ve kart onu basar.

## 2. Hatalı kareler ve Tekrar dene

Koşu sırasında patlayan kareler `/api/status`'ta adlarıyla taşınır: `failed` sayısının yanına
`failures: ["12_c.png", …]`. Galeri bunları tasarımdaki gibi çizer: `wf-img` çerçevesi
`var(--danger)`, zemin `var(--danger-bg)`, içinde `Icon.Warn` ve altında
`Btn sm` **Tekrar dene** (`color/borderColor: var(--danger)`, saydam zemin); dosya adı satırı
`var(--danger)`.

**Tekrar dene** yalnız o kareyi üretir: `POST /api/projects/<p>/retry` · gövde `{"file": "12_c.png"}`
→ 202. Kare plandan bulunur (numara + harf + prompt + seed aynen), üretilirse kayda girer ve
galeriye normal fotoğraf olarak düşer. Plan o kareyi tanımıyorsa 404, üretim sürüyorsa 409.

Hatalı kare listesi **oturumluktur**: yeniden açılınca o kareler "yarım kalan üretim"in bir
parçasıdır ve Kaldığı yerden devam et onları da üretir. Ayrı bir "hata defteri" dosyası
tutulmaz — hangi karenin eksik olduğu zaten plan eksi kayıttır, ikinci bir gerçek kaynağı olmaz.

## 3. Ekranda ne değişir

Panelin durumları (Bölüm 13'ün tablosuna eklenerek):

| Durum | Panelde |
|---|---|
| `error` (bu oturumda ölümcül durma) | büyük **Kaldığı yerden devam et** + kırmızı kart "Üretim durdu — X/Y tamamlandı" + `Mono size={10}` teknik satır |
| `idle` **ama kuyrukta kare var** | büyük **Kaldığı yerden devam et** + kırmızı kart "Üretim yarım kaldı — X/Y tamamlandı" (teknik satır yok) |

Kart tasarımın `wf-stroke` + `borderColor: var(--danger)` + `background: var(--danger-bg)`
kalıbıdır; içinde `Icon.Warn` + `Note size={12}` `var(--danger)` başlık, altında `Mono size={10}`
`var(--ink-3)` teknik satır (varsa). Düğme `Btn hl` + `Icon.Regen`, panelin en üstünde — tasarımın
notu: "bitti kartıyla aynı kalıp: büyük buton + altında durum kartı".

Galeri, yarım kalan üretimde de bekleyen kareleri gösterir (kuyruk ucundan): kullanıcı neyin eksik
olduğunu kartı okumadan da görür.

## 4. Doğrulama

1. ComfyUI'ı öldür → üst üste hata → kırmızı "Üretim durdu" kartı + teknik satır; ComfyUI'ı
   kaldır → Kaldığı yerden devam et → yalnız eksikler üretilir, tamamlananlar tekrar üretilmez.
2. Üretim sürerken tek bir kare patlasın → galeride kırmızı kare + Tekrar dene; üretim durmadan
   sürer; Tekrar dene → yalnız o kare üretilir, yerine normal fotoğraf gelir.
3. Üretim sürerken sekmeyi kapat, projeyi yeniden aç → "Üretim yarım kaldı — X/Y" kartı ve bekleyen
   kareler; devam et → kaldığı yerden sürer.
4. Runtime'ı tamamen kapat, yeni oturum aç, projeyi aç → aynı kart (teknik satır yok, çünkü sebep
   bilinmiyor).
5. Hiç yarım işi olmayan projede kart **yok**, panel normal Üret'i gösterir.

## Kararlar

- **Yarım iş plandan okunur** (`plan − kayıt`), ayrı durum dosyası yazılmaz.
- **Oturum ölümünden sonra teknik sebep gösterilmez** — bilinmeyen uydurulmaz.
- **Tekrar dene tek kareyi plandan üretir**; hatalı kare listesi oturumluktur.
- **Kuyruk ucu açılışta ve koşu bitince sorulur**, poll sırasında değil — canlı kuyruk zaten
  `/api/status`'ta.
