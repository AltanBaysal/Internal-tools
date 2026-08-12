# Queen Editor v5 · Görev 21 — Ses prompt'unu dil modeli yazar · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 6, Görev 21 ·
**Kaynak madde:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
32 · **Tür:** arka uç.

## Neden

Ses işi kuyruğa prompt'suz giriyor (Görev 20) — panelde kutu yok, çünkü tasarım sormuyor. Sırası
gelen işin yine de MMAudio'ya ne üreteceğini söyleyen bir metne ihtiyacı var.

## Ne olacak

Motor bir ses işine geldiğinde, işin prompt'u boşsa dil modeline karenin **hem foto hem video**
prompt'undan ses prompt'u yazdırır; o metinle üretir ve metni sesin kayıt satırına yazar. Video
tarafında kurulan kalıbın (Görev 16) aynısı — bu görevde yalnız **ne sorulduğu** yeni.

## Kararlar

### 1. Yazıcı ikisini birden okur

Yazıcı portu zaten katmanın sahip olduğu bütün prompt'ları alıyor (`write(prompts)`), Görev 20'de
kayıt katman katman prompt'ları söyler oldu. Ses yazıcısı `photo` ve `video` anahtarlarını birlikte
okur: sahne fotoğrafın prompt'unda, hareket videonunkinde, ses ikisinin toplamı.

### 2. Talimat MMAudio'nun kendi dilinde

Sistem mesajı ses için yazılır: sahnede duyulacak sesleri kısa, virgülle ayrılmış bir metin olarak
istemek — MMAudio metin girdisini böyle kullanıyor. Müzik istenmez (sahnenin kendi sesi istenir),
konuşma istenmez (dudak senkronu tutmaz), sonuç tek satırdır.

Bu talimat bize ait: `collab-toolbox`'ta ses tarafında bir çeviri talimatı yok
(`mmaudio_generate.ipynb` prompt'u kullanıcıdan alıyor), yani devralınacak bir metin de yok.

### 3. Foto ya da video prompt'u yoksa model çağrılmaz

Görev 16'nın kuralı: çevrilecek bir şey yokken sormak, uydurulmuş bir prompt'a para ödemektir.
Motor bunu zaten yapıyor (`any(source.values())`), ses için ayrıca bir şey yazılmaz.

## Nasıl görülür

1. Sırası gelen ses işi üretilmeden önce xAI'ye tek istek gidiyor; gövdede foto ve video prompt'u
   birlikte.
2. Sesin kayıt satırında dönen metin duruyor.

## Testler

**Yazıcı:** foto ve video prompt'u tek kullanıcı mesajında, ikisi de etiketli · video prompt'u
yoksa yalnız foto gider · talimat müzik ve konuşma istemediğini söyler.

**Motor:** ses işi yazıcıya karenin iki prompt'uyla gidiyor (Görev 16'nın testleri katman
haritasından geçtiği için ses de aynı yoldan koşar).

## Kapsam dışı

- **Sesin üretilmesi ve videoya bindirilmesi** — Görev 22.
- **Prompt'un detayda okunması/düzenlenmesi** — Görev 23, 25.

## Riskler

- **Talimatın kalitesi ancak gerçek koşuda görülür.** Metin tek dosyada ve tek yerde; beğenilmezse
  değiştirilecek şey bir sabit.
