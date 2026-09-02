# Madde 146 · Tur 1 (test) — Tasarım

**Kaynak:** [v6 yol haritası](../plans/2026-09-01-v6-roadmap.md), Madde 146
**Dal:** `feat/v6`
**Bu tur yalnız test yazar.** Uygulama, defter ve `dist` bu turda ellenmez.

## Ne çalışacak

QueenAgent üç modelden biriyle cevaplar. Seçim **yazma kutusunun ayağında**, `Skills`'in yanında;
her mesajla birlikte gider ve cevabın kaydına yazılır.

| id | Ad | Detay *(menüde)* | Taban adres | Anahtar |
|---|---|---|---|---|
| `grok-build-0.1` | Grok Build | `$1 / $2 per 1M` | `https://api.x.ai/v1` | `XAI_API_KEY` |
| `deepseek-v4-flash` | DeepSeek Flash | `$0.22 / $0.66 per 1M` | `https://api.deepseek.com` | `DEEPSEEK_API_KEY` |
| `deepseek-v4-pro` | DeepSeek Pro | `$0.66 / $1.98 per 1M` | `https://api.deepseek.com` | `DEEPSEEK_API_KEY` |

Fiyatlar off-peak; kaynakları yol haritasının 146. maddesinde.

## Yol haritasının düzeltilen iki yeri

Madde 146 belgeye *"defter seçtirir"* ve *"ekran değişmiyor"* diye girmişti. İkisi de yanlış, ve
düzeltmeyi kullanıcı verdi *(2 Eylül: "defter değil, modeli eskisi gibi seçelim")*.

**Seçim uygulamada.** Madde 82 bu makineyi sökmüştü, ama gerekçesi *"tek model varken hepsi boşa
çalışıyor"*dı — üç model olunca o gerekçe düşüyor. 82 yanlış değildi; **önşartı bitti.**

**Ekran değişiyor.** Madde 146 belgenin *"arayüz değişmiyor"* listesinden çıkıyor.

## Şekli — skill'in ayrımı, birebir

Kullanıcı kararı *(2 Eylül: "seçilen model skill gibi tutulsun, backend'de tutulmasın")*. Skill'in
bugünkü ayrımı üç parça, ve model üçünü de aynen alıyor:

| | Skill | Model |
|---|---|---|
| Gördüğü liste | `frontend/…/skills.js` | **yeni** `frontend/…/models.js` |
| id'nin motor için anlamı | `domain/skills.py` — yönerge metni | `config.py` — adres + anahtar |
| Seçimin kendisi | hiçbir yerde; her mesajla gider | aynı |
| Kaydı | `Message.skill` | **yeni** `Message.model` |

**Sunucu "şu an hangi model seçili" diye bir şey bilmiyor.** Seçim frontend'in oturum durumu;
istekle gelir, kullanılır, mesaja yazılır, biter.

**Mesaja yazılmasının gerekçesi ödünç değil, kodun kendi cümlesi** — `chat.py`'de `skill` alanının
üstünde yazılı: *"changing the selection later must not make an older turn look as though the new
skill produced it."* Model için aynısı, ve daha ağırı: bu maddenin bütün amacı karşılaştırma.

## Kırmızıya dönecek iddialar

### Arka uç

1. **Üç model id'si adresini ve anahtarını çözüyor.** `config.py` bir tablo taşıyor; `grok-build-0.1`
   xAI'nin adresini ve `XAI_API_KEY`'i, iki DeepSeek satırı `https://api.deepseek.com`'u ve
   `DEEPSEEK_API_KEY`'i veriyor.
2. **Tanınmayan ve boş id varsayılana düşüyor.** Madde 82 öncesinden kalma kayıtlarda `grok-4.3`
   yazıyor, ve bu maddeden önceki her mesajda hiçbir şey yazmıyor. İkisi de çalışmaya devam etmeli
   — `skills.py`'nin `instruction_for` ile yaptığının aynısı.
3. **`Message` bir `model` alanı taşıyor**, varsayılanı `""`. Diskte alanı olmayan bir sohbet
   okunuyor ve düşmüyor; yazılan bir mesajda alan geri geliyor.
4. **Model mesajla birlikte giriyor ve mesajla birlikte çıkıyor.** İstek gövdesindeki `model`
   okunuyor *(`skill`'in yanında)*, ve sohbet JSON'unda geri veriliyor.
5. **İstemci mesaj başına kuruluyor, açılışta değil.** Bugün `main.py` tek bir `XaiClient`'ı sabit
   model ve sabit adresle kuruyor. Bu maddenin yapısal değişikliği bu: model artık çağrı başına
   bir girdi.
6. **`_spent()` iki usage şeklini de tanıyor.** xAI `prompt_tokens_details.cached_tokens`,
   DeepSeek `prompt_cache_hit_tokens` gönderiyor; ikisi de `cached`'e düşüyor. `sent` ve
   `answered` ayrışmıyor, ikisinde de aynı.
7. **`x-grok-conv-id` yalnız xAI'ye gidiyor.** DeepSeek'in önbelleği otomatik prefix eşleşmesi;
   başlık ona anlamsız. Bir DeepSeek isteğinde başlık **yok**.

### Ön yüz

8. **`models.js` üç satır taşıyor**, her biri id + ad + detay; detay fiyat.
9. **`modelName(id)` çözüyor.** Bilinen id adını, bilinmeyen id kendini, **boş id varsayılanın
   adını** veriyor. Son madde skill'den ayrıldığı yer: skill'de boş *"Skills"* demek, yani
   seçilmemiş olmak olağan bir hâl — modelde boş diye bir hâl yok, her cevabı bir model veriyor.
10. **`ModelPicker` tıklanıyor ve üç satır açıyor.** `SkillPicker`'ın şekli: `{model, open,
    onToggle, onChange}`. Seçili satır işaretli, bir satıra basmak `onChange`'i çağırıyor.
11. **Ayaktaki sıra ve şekil.** Bugün `Edit⌄Skills⌄Grok Build↑` — model tıklanamaz olduğu için
    şapkası yok. Artık var: `Edit⌄Skills⌄Grok Build⌄↑`.
12. **Seçim mesajla gidiyor.** `useChat`'in gönderdiği gövde `skill` ve `mode`'un yanında `model`
    taşıyor.
13. **Üçüncü menü açık-durum sırasına giriyor.** Madde 82 açık menü durumunu ikiliye indirmişti ve
    Escape sırasını kısaltmıştı; üçüncü picker ikisini de geri büyütüyor. Bir menü açıkken
    ötekinin açılması berikini kapatıyor.

## Ölecek testler

- **`ModelLabel.test.jsx`** — bileşen `ModelPicker` oluyor, dosya adıyla birlikte gidiyor.
- **`ChatScreen.test.jsx:635` ve `ProjectScreen.test.jsx:229`** — ikisi de
  `queryByRole("button", { name: /Grok Build/ })` sonucunun **null** olmasını çiviliyor, yani
  *"model tıklanamaz"*ı. İddia tersine dönüyor: artık bir düğüm, ve basılıyor.

Bunlar silinmiyor, **tersine çevriliyor** — bir kilit kaldırılırken yerine karşıtı konmazsa
davranış sessizce serbest kalır.

## Yeşil kalması gerekenler

- **Bütün skill testleri.** Model onun yanına geliyor, yerine değil.
- **`test_a_chat_that_still_carries_a_model_on_disk_is_read_without_it`** — ve bu şaşırtıcı
  değil, dikkat isteyen yer. O test Madde 82'nin kaldırdığı **sohbet düzeyindeki** `model`
  anahtarını konu ediyor; bu madde alanı **mesaja** koyuyor, sohbete değil. Sohbetin kökündeki
  `model` hâlâ okunmuyor ve hâlâ düşüyor. İki alan aynı adı taşıyor ama aynı yerde değil, ve test
  bu yüzden yeşil kalmalı. Kırmızıya dönerse alan yanlış yere konmuş demektir.
- **`test_the_xai_key_travels_to_the_app_in_the_environment`** — ikinci anahtar birincinin yerine
  değil yanına geliyor.
- Damga, jeton sayısı, `dist` bekçisi, sağlık ucu, depo testleri.

## Defterin iki anahtarı

`DEEPSEEK_API_KEY` de Secrets'tan okunuyor, `XAI_API_KEY` ile aynı yoldan, ve env'de uygulamaya
geçiyor. İkisi de basılmıyor — bugünkü `test_the_xai_key_is_never_printed` kilidi ikinciyi de
kapsayacak şekilde genişliyor.

**Durduran assert "en az biri" oluyor.** Bugün `assert XAI_API_KEY` sert duruyor. İkisini birden
şart koşmak yalnız Grok'la çalışmak isteyeni durdururdu; hiçbirini koşmamak uygulamayı işe
yaramaz hâlde başlatırdı. İkisi de yoksa defter duruyor, biri varsa devam ediyor — anahtarı olmayan
bir model seçilirse istek `XaiNotConfigured`'ın kendi cümlesiyle düşüyor.

## Kapsam dışı

- **`services/xai/` ve `XAI_*` adlarının değişmesi.** Yol haritasında yazılı: ölçülecek şey iki
  modelin farkı, ve aynı commit'te depo geneline yayılan bir rename o ölçüyü gürültüye boğar.
- **Menünün anahtarı olmayan sağlayıcıyı gizlemesi.** Liste frontend'de, frontend hangi anahtarın
  var olduğunu bilmiyor — ve `skills.js` de böyle bir şey yapmıyor.
- **Modelin ekranda mesaj başına gösterilmesi.** Alan kayda giriyor; çizilmesi ayrı bir iş ve
  istenmedi.
- **200k eşiğinin ölçülmesi.** Yol haritasında duruyor; bu madde ondan bağımsız koşuyor.
- **Sohbet düzeyinde model.** Madde 86 onu yazan ucu bilerek öldürdü; geri gelmiyor.

## Colab'da görülecek

Takım yeşil, seçimin **taşındığını** söyler — işe yaradığını değil. Onu söyleyen tek şey koşunun
kendisi: aynı iş üç modelle ayrı ayrı yaptırılıyor, cevaplara ve damgadaki jeton sayısına bakılıyor.
Kullanıcının kendi hükmü, ve o bu işin tek yetkili gözü.
