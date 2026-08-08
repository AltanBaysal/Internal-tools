# prompt-chat — Sohbet listesi ve Queen Editor görünümü

**Tarih:** 2026-08-08 · **Branch:** `feat/queen-editor-v2`
**Üstüne geldiği doküman:** [2026-08-08-prompt-chat-design.md](2026-08-08-prompt-chat-design.md)
— o spec'in **"Sohbetin kalıcılığı yok"** ve **"Queen Editor'ın tasarım dili taşınmaz"** kararlarını
bu doküman değiştirir. Geri kalan her kararı (backend yok, system prompt yok, streaming yok, ham
hata metni, Kopyala) aynen geçerlidir.

Tek sohbetlik araç, sohbetleri saklayan ve aralarında gezilen bir araca dönüşür. Yerleşim Claude
arayüzünün düzeni: solda liste, sağda sohbet.

## Ne çalışır

1. Sol kolonda sohbet listesi durur; üstünde **Yeni sohbet**, altında **Ayarlar**.
2. Bir sohbete tıkla → sağda o sohbet açılır. **Yeni sohbet** → boş bir sohbet açılır ve aktif olur.
3. Sohbet satırının üstüne gelince `×` çıkar; basınca onay sorulur, onaylanırsa sohbet gider.
4. Sekmeyi kapat, tarayıcıyı kapat, ertesi gün aç → **sohbetlerin ve açık olduğun sohbet durur.**
5. **Ayarlar** açılır kapanır: içinde API anahtarı ve model alanı. Anahtar kayıtlıysa kapalı gelir;
   **anahtar yoksa kendiliğinden açık gelir**, yoksa ilk açılışta ne yapılacağı belli olmaz.
6. Görünüş Queen Editor'ın paletine ve tipografisine yaklaşır.

Asıl kazanım: bir konuyu bir kez kurduğun sohbet duruyor. Uzun bir talimatı ya da bağlamı her
seferinde yeniden yazmıyorsun, o sohbete dönüp devam ediyorsun.

## Kapsam dışı

- **`vendor/kit` kopyalamak** — yalnız token'lar (renk, tipografi, yarıçap) alınır; bileşen kütüphanesi
  taşınmaz. Bu, önceki spec'in kararının hâlâ geçerli olan yarısı.
- **Sohbeti yeniden adlandırma** — ad ilk mesajdan türer, elle değiştirilmez.
- **Sohbet arama / sıralama / klasörleme** — liste, eklenme sırasında durur.
- **Sol kolonu daraltma** — sabit genişlikte.
- **Sunucuda saklama, senkronizasyon, dışa aktarma** — kalıcılık tek tarayıcının `localStorage`'ıdır.
- **Silmeyi geri alma** — onay var, geri alma yok.

## 1. Yerleşim

```
┌──────────────┬────────────────────────────────┐
│  + Yeni      │  Sen                           │
│    sohbet    │  ...                           │
│──────────────│                                │
│ ▸ Kanlı dövüş│  Grok                          │
│   sahnesi… ×│  ...              [Kopyala]    │
│ ▸ Anime test │                                │
│              ├────────────────────────────────┤
│──────────────│ [ Mesaj yaz…        ] [Gönder] │
│ ⚙ Ayarlar    │                                │
└──────────────┴────────────────────────────────┘
```

Sol kolon sabit genişlikte; liste uzarsa kendi içinde kayar. Sağ taraf bugünkü sohbet ekranıdır —
mesajlar, yazma kutusu, **Kopyala** hepsi olduğu gibi kalır.

## 2. Saklama

`localStorage`'da dört anahtar:

| Anahtar | İçerik |
|---|---|
| `chats` | JSON dizi: `[{ id: number, messages: [{role, content}], draft: string }]` |
| `active_chat` | açık sohbetin `id`'si |
| `xai_key` | değişmedi |
| `xai_model` | değişmedi |

**Sohbetin adı saklanmaz, türetilir** — `titleOf(messages)`. İki yerde tutulan tek bir gerçek olmaz;
ilk mesaj değişirse ad kendiliğinden doğrudur.

**`id` üretimi deterministiktir:** mevcut en büyük `id` + 1. Rastgelelik yok, `crypto` yok — bu
sayede sohbet mantığı saf kalır ve testi tarayıcısız koşar. Her kopya tek bir tarayıcıya ait olduğu
için çakışma diye bir sorun yok.

**Uygulamada her zaman açık bir sohbet vardır.** Üç durumda yenisi kurulur: hiç sohbet yokken,
aktif sohbet silindiğinde ve hepsi silindiğinde. Aktif olan silinirse listede kalanların **ilki**
aktif olur; hiç kalmadıysa boş bir sohbet açılır.

**Bozuk kayıt uygulamayı kilitlemez.** `chats` okunamayan bir JSON'sa (elle kurcalandı, yarım
yazıldı), uygulama boş bir sohbetle açılır — beyaz ekran vermez.

### Yazılan metin: her sohbetin kendi taslağı

**Yazma kutusu sohbete aittir, ekrana değil.** Yarım bıraktığın metin o sohbetin `draft` alanında
saklanır; başka sohbete geçip döndüğünde kaldığın yerde durur, ve sekmeyi kapatsan bile durur —
`chats` ile birlikte `localStorage`'a yazılır. Mesaj gönderilince o sohbetin taslağı boşalır.

Sebebi: uzun bir metin yazarken yanlışlıkla başka bir sohbete tıklamak yazdığını götürmemeli.
Taslağı ortak tek bir kutuda tutmak da olurdu ama o zaman metin yanlış sohbete taşınırdı.

### Uçmakta olan cevap

Cevap beklenirken başka sohbete geçilebilir; cevap geldiğinde **onu isteyen sohbetin** mesajlarına
yazılır, o an ekranda duran sohbete değil. İstek gönderilirken sohbetin `id`'si yakalanır, cevap o
`id`'ye yazılır. Hata satırı da aynı şekilde kendi sohbetine düşer.

**Sayfa kapanırsa cevap kaybolur ve peşine düşülmez.** Yeniden açıldığında o sohbette senin mesajın
görünür, altında cevap yoktur; istersen tekrar gönderirsin. Mesajın silinmez — onu sen yazdın, o
senin emeğin; kaybolan yalnız gelmemiş cevaptır. Yarım kalan isteği sürdürmeye çalışan bir mekanizma
**yok**: `localStorage` bir kuyruk değil.

**Aynı anda tek istek uçar.** Bir cevap beklenirken hangi sohbette olursan ol gönderme kapalıdır.
Sohbet başına ayrı bekleme durumu tutmak mümkün ama bu ölçekte kazandırdığından fazla karmaşıklık
getirir.

## 3. Sohbetin adı

`titleOf(messages)`: ilk `user` mesajının **ilk 40 karakteri**, satır sonları boşluğa çevrilerek.
Mesaj 40'tan uzunsa bu 40 karakterin **sonuna** `…` eklenir (yani en fazla 41 karakter döner).
Hiç kullanıcı mesajı yoksa **"Yeni sohbet"**.

İlk mesajın seçilmesinin sebebi: sohbeti başlatan soru ya da talimat odur — sonrası hep onun
devamı. Sohbeti gerçekten ayırt eden şey ilk mesaj.

## 4. Silme

Satırın üstüne gelince sağında `×` belirir. Basınca **onay sorulur** — `window.confirm` ile,
"Bu sohbet silinecek. Emin misin?".

Onay isteğe bağlı değil: bir sohbette saatlerce uğraşılmış bir metin olabilir ve silmenin geri
alması yok. Yanlış bir tıkla o emeğin gitmesi kabul edilebilir değil.

## 5. Ayarlar

Sol kolonun en altında **Ayarlar** düğmesi; basınca üstünde anahtar ve model alanları açılır.

Açılış hâli anahtarın varlığına bakar: **kayıtlı anahtar varsa kapalı**, yoksa **açık**. Böylece
günlük kullanımda anahtar gözden kaybolur, ilk açılışta ise ilk yapılacak şey ekranda durur.

Anahtar alanı `type="password"` olarak kalır.

## 6. Görünüş

Queen Editor'ın token'ları alınır ([vendor/styles.css](../../../queen-editor/frontend/src/vendor/styles.css)):

| Token | Değer |
|---|---|
| `--bg` / `--bg-2` / `--bg-3` | `#0f0f10` / `#17171a` / `#202024` |
| `--border` / `--border-strong` | `#2b2b2f` / `#45454c` |
| `--ink` / `--ink-2` / `--ink-3` | `#ececee` / `#9a9aa0` / `#6a6a70` |
| `--accent` | `#a78bfa` (mor, az kullanılır) |
| `--danger` | `#c97064` |
| yarıçap | 4 / 8 / 12 |

Tipografi **IBM Plex Sans**, mesaj gövdeleri dahil; `index.html`'e Queen Editor'daki `<link>`'in
aynısı girer. Bu bir CDN çağrısıdır — araç yalnız `localhost`'ta ve internet bağlıyken çalıştığı
için (zaten xAI'a çıkıyor) sorun değil.

## 7. Dosya yapısı

```
prompt-chat/src/
  main.jsx          # değişmedi
  App.jsx           # sohbeti yürütür, Sidebar'ı bağlar          (değişir)
  Sidebar.jsx       # sol kolon: liste, yeni, sil, ayarlar       (yeni)
  Sidebar.test.jsx                                               (yeni)
  storage.js        # saf: sohbet listesi işlemleri, titleOf     (yeni)
  storage.test.js                                                (yeni)
  usePersisted.js   # localStorage kancaları (metin + JSON)      (yeni)
  Message.jsx       # değişmedi
  chat.js           # değişmedi
  api.js            # değişmedi
  app.css           # token'lar ve yeni yerleşim                 (değişir)
```

`usePersisted` bugün `App.jsx`'in içinde duruyor; ikinci bir tür (JSON) gerektiği ve `App.jsx`
zaten büyüdüğü için kendi dosyasına çıkar.

**`storage.js` saf kalır** — `localStorage`'a dokunmaz, React bilmez. Okuma/yazma `usePersisted.js`'in
işidir. Katman kuralı önceki spec'teki gibi: saf mantık ayrı, I/O ayrı.

`storage.js` arayüzü:

| Fonksiyon | Döndürdüğü |
|---|---|
| `nextId(chats)` | yeni `id` — en büyüğü + 1, boş listede 1 |
| `createChat(chats)` | `{ chats, id }` — sonuna boş sohbet ekler (`messages: []`, `draft: ""`) |
| `deleteChat(chats, id)` | o sohbetsiz yeni liste |
| `replaceMessages(chats, id, messages)` | o sohbetin mesajları değişmiş yeni liste |
| `setDraft(chats, id, draft)` | o sohbetin taslağı değişmiş yeni liste |
| `titleOf(messages)` | başlık metni |

Hepsi girdiyi değiştirmez, yeni liste döndürür.

## 8. Testler

Mevcut 28 test aynen kalır — `chat.js`, `api.js` ve `Message.jsx` değişmediği için 15'i hiç
etkilenmez; `App.test.jsx`'in sohbet testleri yeni yerleşime göre seçicilerini günceller.

| Dosya | Yeni olarak neyi kanıtlar |
|---|---|
| `storage.test.js` | `id` üretimi, ekleme/silme/taslak girdiyi bozmuyor, `titleOf` kırpma ve "Yeni sohbet" hâli |
| `Sidebar.test.jsx` | Liste çiziliyor, tıklayınca seçiliyor, **Yeni sohbet** ekliyor, `×` onay sorup siliyor, onay reddedilirse silmiyor, Ayarlar açılıp kapanıyor ve anahtarsız açık geliyor |
| `App.test.jsx` | Sohbet değiştirince mesajlar değişiyor; gönderilen mesaj **açık sohbete** yazılıyor; her sohbet **kendi taslağını** gösteriyor ve gönderince taslak boşalıyor; beklerken sohbet değiştirilirse cevap **isteyen sohbete** düşüyor; `localStorage` bozuksa uygulama yine açılıyor |

## 9. Doğrulama (elle, tarayıcıda)

1. `npm run dev` → sol kolon, boş bir sohbet ve **açık** Ayarlar (anahtar yok).
2. Anahtarı gir → Ayarlar'ı kapat → mesaj gönder, cevap gelsin.
3. **Yeni sohbet** → boş ekran; eski sohbet listede duruyor, adı ilk mesajın.
4. İki sohbet arasında gidip gel → her biri kendi mesajlarını gösteriyor.
5. Sekmeyi kapat, yeniden aç → sohbetler ve açık olan yerinde; Ayarlar bu sefer **kapalı**.
6. Bir sohbeti sil → onay çıkıyor; İptal → duruyor; Tamam → gidiyor.
7. Açık olan sohbeti sil → başka bir sohbet açılıyor, ekran boş kalmıyor.
8. Hepsini sil → boş bir sohbetle devam ediyor, beyaz ekran yok.
9. A sohbetinde yarım bir metin yaz, B'ye geç → B'nin kutusu boş; A'ya dön → metnin duruyor.
   Sekmeyi kapatıp aç → hâlâ duruyor. Gönder → A'nın kutusu boşalıyor.
10. Uzun sürecek bir mesaj gönder, cevap gelmeden başka sohbete geç → cevap geldiğinde gönderdiğin
    sohbette duruyor, o an baktığın sohbete bulaşmıyor.

## Kararlar

- **Sohbetler `localStorage`'da saklanır** — önceki spec'in "kalıcılık yok" kararı kalkar. Sebebi
  bir konuyu kurduğun sohbete geri dönebilmek, bağlamı her seferinde yeniden yazmamak.
- **Ad saklanmaz, ilk mesajdan türetilir** — iki yerde tutulan tek bir gerçek olmasın diye.
- **Taslak sohbete aittir ve saklanır** — yanlış tıklama ya da kapanan sekme yazdığını götürmesin.
- **Aynı anda tek istek uçar** — sohbet başına bekleme durumu, kazandırdığından fazla karmaşıklık.
- **Yarım kalan istek sürdürülmez** — sayfa kapanırsa mesajın kalır, cevap gelmez, tekrar gönderirsin.
- **`id` = en büyük + 1** — deterministik olduğu için sohbet mantığı saf kalır, testi tarayıcısız koşar.
- **Uygulamada hep açık bir sohbet vardır** — silme sonrası da, ilk açılışta da; boş ekran bir durum değil.
- **Bozuk `localStorage` uygulamayı kilitlemez** — boş sohbetle açılır.
- **Silme onay ister** — geri alması yok ve içinde emek olabilir.
- **Ayarlar anahtar yoksa açık, varsa kapalı gelir** — ilk açılışta yol gösterir, sonra yoldan çekilir.
- **Token'lar alınır, `vendor/kit` alınmaz** — hizalanmanın ucuz olan yarısı.
- **`storage.js` saf, I/O `usePersisted.js`'te** — önceki spec'in katman kuralının aynısı.
