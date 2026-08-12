# Queen Editor v5 · Görev 16 — Video prompt'unu dil modeli yazar · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 5, Görev 16 ·
**Kaynak madde:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
27 · **Tür:** arka uç.

## Neden

Video işi kuyruğa prompt'suz giriyor (Görev 14, 15): panelde prompt kutusu yok, çünkü tasarım onu
kullanıcıya sormuyor. Sırası gelen işin yine de bir prompt'a ihtiyacı var — WAN I2V'ye ne yapacağını
söyleyen metin. Madde 27: **iş sırası gelince bir dil modeli fotonun kendi prompt'undan yazar**,
yazdığı metin kaydedilir ve detayda okunup düzenlenebilir.

## Ne olacak

Motor bir video işine geldiğinde, işin prompt'u boşsa dil modeline "bu foto prompt'undan hareket
prompt'u yaz" der; dönen metinle videoyu üretir ve **o metni videonun kaydına yazar**. Prompt'u
dolu bir iş modele hiç uğramaz — dolu olması, metnin kullanıcıdan geldiği anlamına gelir
(Görev 25'in "yeniden üret"i).

## Kararlar

### 1. Dil modeli xAI Grok

`collab-toolbox/queen-tools/prompt_converter.ipynb` tam bu işi yapıyor: Queen Editor'ün export
ettiği foto prompt'unu WAN I2V hareket prompt'una çeviriyor. Model **grok-4.3**, uç nokta
`https://api.x.ai/v1/chat/completions`, talimat o defterin `INSTRUCTION`'ı.

Devralınan şey **bilgi**, kod değil: Queen Editor kendi istemcisini yazar, o dosyayı çalışma anında
okumaz — aracın kendi sınırı (CODE-STANDARD).

Ayarlar config'de, hepsi ortam değişkeniyle değişebilir: `QE_XAI_API_KEY` (varsayılan boş),
`QE_XAI_MODEL` (`grok-4.3`), `QE_XAI_URL` (yukarıdaki uç nokta). İstek zaman aşımı 120 saniye —
defterin kendi değeri.

### 2. Anahtar Colab Secrets'tan gelir, yokluğu koşuyu durdurur

Notebook `XAI_API_KEY` gizli anahtarını okuyup sunucuya `QE_XAI_API_KEY` olarak geçirir — `GITHUB_TOKEN`
ve `CIVITAI_COOKIE` ile aynı yol. Anahtar yoksa notebook durmaz: yalnız fotoğraf üreten bir koşunun
dil modeline ihtiyacı yok.

Anahtarsız bir video işinin sırası gelirse istemci kendi cümlesiyle patlar ("XAI_API_KEY yok…") ve
bu **karenin değil koşunun** hatasıdır: bir sonraki iş de aynı yere düşecek. Motorun bugünkü kuralı
zaten bu ayrımı yapıyor (`policy.is_frame_fault`), yeni bir yol açılmıyor.

### 3. Prompt, işin kendi sırası gelince yazılır — bir kez

Yazma anı üretimden hemen öncesi: kuyruğa girerken yazılsaydı, saatler sonra sırası gelen iş
eskimiş bir metinle üretilirdi ve kuyruğa 40 iş atmak 40 istek demek olurdu.

Aynı işin üç denemesi bir istek harcar: yazılan metin işin denemeleri boyunca elde tutulur, iş
değişince bırakılır. Motorun deneme sayacı zaten böyle çalışıyor.

### 4. Yazılan metin videonun kendi kayıt satırına yazılır

Yeni dosya yok, ikinci yazar yok: motor katman inince zaten bir satır yazıyor (`prompt`, `negative`,
`seed`), video satırı da yazılan metni öyle taşır. Detay sayfası (Görev 23) onu oradan okur.

Video üretilemezse metin de kalmaz — hata satırı prompt taşımıyor. Doğrusu bu: kayıt "ne oldu"nun
kütüğü, olmamış bir katmanın prompt'u da olmamış demektir. Tekrar denendiğinde yeni bir metin
yazılır.

### 5. Modele ne sorulur: karenin foto prompt'u

Karenin foto satırı kayıtta duruyor ve prompt'u orada — kopya kare de dahil (Görev 15 onu böyle
doğurdu). Plan yerine kayıt okunur, çünkü kopya karenin planda foto işi yok.

Foto prompt'u boşsa **model çağrılmaz**: çevrilecek bir şey yokken modele sormak, uydurulmuş bir
prompt'a para ödemektir. İş boş prompt'la üretilir — I2V zaten fotoğrafın kendisini görüyor.

### 6. Motor "yazıcı"yı da bir tür haritasından bulur

Üreticiler gibi: `{iş türü: prompt yazıcı}`. Motor hiçbirini adıyla tanımaz, işin türüne bakar.
Fotoğrafın yazıcısı yok (prompt'u kullanıcıdan gelir), videonunki bu görevde doğar, sesinki
Görev 21'de aynı haritaya girer.

Yazıcı `write(prompts)` ile çağrılır — `prompts`, karenin **o an sahip olduğu katman prompt'ları**
(`{"photo": "…"}`). Ses yazıcısı foto ve video prompt'unu birlikte isteyecek (Görev 21); sözlük,
imzayı o gün değiştirmeden bunu karşılar.

## Nasıl görülür

1. Sırası gelen video işi üretilmeden önce xAI'ye bir istek gidiyor, foto prompt'u gövdede.
2. Videonun kayıt satırında dönen hareket prompt'u duruyor.
3. Prompt'u dolu bir video işi modele uğramıyor.
4. Anahtar yokken koşu duruyor ve panel istemcinin kendi cümlesini gösteriyor.

## Testler

**İstemci:** gövdede model, sistem talimatı ve foto prompt'u var · cevabın metni dönüyor · HTTP
hatası sunucunun kendi gövdesiyle patlıyor · boş cevap patlıyor · anahtar yokken kendi cümlesiyle
patlıyor.

**Yazıcı:** talimat sistem mesajı olarak gidiyor · foto prompt'u kullanıcı mesajı oluyor.

**Motor:** boş prompt'lu video işi yazıcıyı çağırıyor · dönen metinle üretiliyor · kayıt satırı o
metni taşıyor · prompt'u dolu iş yazıcıya uğramıyor · aynı işin üç denemesinde yazıcı bir kez
çağrılıyor · foto prompt'u yoksa yazıcı çağrılmıyor · yazıcının hatası koşuyu durduruyor.

## Kapsam dışı

- **Videonun gerçekten üretilmesi** — Görev 17. Bu görevde video üreticisi hâlâ yok; testler sahte
  üreticiyle koşar.
- **Katmanın dosya adı.** Motor bugün her katmanı `photo_file` ile adlandırıyor; video ve ses
  adlarının katman şemasına geçmesi Görev 17'nin işi. Bu görev prompt'a dokunur, ada dokunmaz.
- **Prompt'un detayda okunması/düzenlenmesi** — Görev 23, 25.
- **Ses prompt'u** — Görev 21.

## Riskler

- **İstek üretimden önce, üretim uzun.** Prompt yazıldıktan sonra render dakikalar sürüyor; kullanıcı
  o sırada duraklatırsa yazılan metin boşa gider (satır yazılmaz). Kabul: bir istek, bir cümlelik
  metin.
- **grok-4.3 adı.** Model adı config'de ve `QE_XAI_MODEL` ile değiştirilebilir — ad değişirse tek
  satır.
