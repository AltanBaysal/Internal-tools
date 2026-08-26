# Madde 80 — Gönder ve durdur düğmesi ikon taşır · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 4, Madde 80 ·
**Bir önceki:** [Madde 79](2026-08-26-queenagent-m79-gonder-durdurmaya-doner-uygulama-design.md) —
iki düğmeyi tek düğmede topladı.
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz, ve tur kırmızı
commit'lenir.

---

## Ne değişiyor

Yazma kutusunun tek düğmesi bugün kelime taşıyor: sohbette `Send`, proje ekranında `Start`, cevap
akarken `Stop`. Kelime ikona bırakıyor.

| | Bugün | Bu maddeden sonra |
|---|---|---|
| Sohbet, boş ya da hazır | `Send` | `↑` |
| Proje ekranı, boş ya da hazır | `Start` | `↑` |
| Cevap akarken | `Stop` | `⏹` |

Düğmenin **ne yaptığı** değişmiyor. 79'un iki durumu, 67'nin durdurması, boş taslakta kapalı
olması — üçü de aynen duruyor. Bu madde yalnız düğmenin üstündeki şeye dokunuyor.

## Neden bu iki işaret

Depo ikonu resim olarak değil, harf olarak yazıyor: `+`, `×`, `⌄`, `✓`, `›`, `←`, ve 78'den beri
`⏺` ile `⎿`. Yeni bir çizim yolu açmıyoruz, var olanı kullanıyoruz.

- **`↑` (U+2191)** — gönderme oku. Yazdığın şey yukarı, sohbete gidiyor. Deponun ok ailesinden.
- **`⏹` (U+23F9)** — durdurma karesi. Unicode'daki adı zaten *"black square for stop"*, ve 78'in
  kullandığı `⏺` (U+23FA) ile aynı bloktan geliyor: aynı ağırlık, aynı yazı tipi yolu. O işaret
  ekranda çalıştığı bilindiği için bu da çalışır.

**Aynı ok iki isim taşıyor.** Proje ekranındaki düğme sohbet açar, sohbetteki cevap ister; ikisi de
"yazdığımı gönder" demek, o yüzden işaret aynı. Ayrılan şey ad: biri `Start`, öteki `Send`.

## Adı gitmiyor — görünmez oluyor

Bu maddenin tek gerçek riski. Kelime silinirse düğmenin **erişilebilir adı** da silinir, ve o ad
gidince düğme ekran okuyucu için isimsiz bir kutu olur. Yazı görünmez oluyor, yok olmuyor:

- `aria-label` adı taşır — `Send`, `Start` ya da `Stop`.
- `title` fareyle bekleyene aynı kelimeyi söyler.

İkisi de deponun kendi kalıbı: `.sidebar__add` (`+`) `aria-label` taşıyor, `.row-x` (`×`) ikisini
birden. Yeni bir şey icat edilmiyor.

Bunun kanıtı yeni bir test değil, **düşmemesi gereken testler**: `Composer.test.jsx` düğmeyi her
seferinde `getByRole("button", { name: "Send" })` ile buluyor, ve `App.test.jsx` uçtan uca `Start`
ile `Stop`'a basıyor. Ad giderse bu testlerin onu üçü birden patlar.

## Şekli deponun kendi kuralı söylüyor

Düğme daire olmuyor. `workspace.css.test.js` şunu tutuyor: *her denetim aynı değişkenle yuvarlanır* —
`--radius-control`. Bu dilde daire yalnız **nokta** demek: `.dots__dot` 6px, `.offline__dot` 7px, ve
başka daire yok.

Yani ikon düğmesi köşeli kalıyor; değişen tek şey kelime kadar geniş olmayı bırakması. Sabit bir
kare oluyor — yanındaki seçicilerle aynı boyda, 32×32.

Bunu tutan test yeni. Yuvarlaklığı tutan test ise **eski ve dokunulmuyor**: yeşil kalması, düğmenin
hâlâ bir denetim olduğunun kanıtı.

## Kırmızıya dönecek testler

**Dört yeni** — `Composer.test.jsx`, Madde 80 başlığı altında:

1. **Düğme kelime değil ok taşır.** Metni `↑`, ve içinde `Send` geçmiyor.
2. **Fareyle üstünde bekleyen ne olduğunu okuyor.** `title` `Send` diyor.
3. **Cevap akarken ok kareye dönüyor.** Metin `⏹`, ad hâlâ `Stop`.
4. **Proje ekranının düğmesi aynı ok, başka ad.** `action="Start"` ile metin `↑`, ad `Start`.

**Bir yeni** — `workspace.css.test.js`: `.composer__send` sabit kare, `32px` × `32px`.

**Dört güncellenen** — üçü sıra testi, biri ayakta ne durduğu:

| Dosya | Bugün | Olacak |
|---|---|---|
| `Composer.test.jsx` | `["Grok 4.5", "Send"]` | `["Grok 4.5", "↑"]` |
| `ChatScreen.test.jsx` | `["Skills⌄", "Grok 4.6⌄", "Send"]` | `["Skills⌄", "Grok 4.6⌄", "↑"]` |
| `ChatScreen.test.jsx` | `["Skills⌄", "Grok 4.6⌄", "Stop"]` | `["Skills⌄", "Grok 4.6⌄", "⏹"]` |
| `ProjectScreen.test.jsx` | `["Skills⌄", "Grok 4.6⌄", "Start"]` | `["Skills⌄", "Grok 4.6⌄", "↑"]` |

Üçü **eksilerek zayıflıyor**: bugün son sıradaki düğmenin *Send* olduğunu metinden okuyorlar, yarın
metin yalnız bir ok. Kaybolan kanıt geri konuyor — aynı testte bir satır daha, son düğmenin adını
soran: `aria-label` `Send` / `Stop` / `Start`. Sıra da kimlik de yerinde kalıyor.

Toplam **dokuz kırmızı**.

## Dokunulmayan yeşiller — bu maddenin asıl sınavı

| Ne | Neyi kanıtlıyor |
|---|---|
| `Composer.test.jsx`'in `draw()`'a dayanan on testi | Ad `Send` olarak duruyor |
| `App.test.jsx` — `Start`'a ve `Stop`'a basan iki test | Ad uçtan uca duruyor |
| `ChatScreen.test.jsx` — 67'nin iki durdurma testi | Durdurma çalışmaya devam ediyor |
| `NoProjectsScreen.test.jsx` — yazma kutusu olmayan yerde `Send` yok | Düğme kaçmadı |
| `workspace.css.test.js` — `--radius-control` | Düğme hâlâ bir denetim |
| `app.css.test.js` — `--accent-hover` | Vurgu yolu bozulmadı |

Biri düşerse görünen değil çalışan bozulmuş demektir.

## Kapsam dışı

- **Başka hiçbir düğme.** `Try again`, `New chat`, onay kutusunun düğmeleri — hepsi kelime kalıyor.
  Kullanıcının istediği yazma kutusunun düğmesi.
- **Enter.** 79'da olduğu gibi dokunulmuyor.
- **Seçicilerin ikonu.** `Skills⌄` ve model adı kelime; onlar ne yaptığını değil, neyin seçili
  olduğunu söylüyor — bir ikonun söyleyebileceği şey değil.
- **Vurgu kuralı.** 79 nasıl bıraktıysa öyle: akarken de hazırken de vurgulu, boş taslakta değil.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur** — birlikte koşturulduğunda vitest bu makinede zaman aşımına düşüyor.

Ön yüzde **9 failed, 498 passed** beklenir — beş yeni testle toplam 507. Arka uçta **2 failed,
442 passed** — ikisi defterin
dalı, kullanıcının kendi isteğiyle `feat/queenagent-v5`'i gösteriyor ve deneme bitince `main`'e
dönecek.

`dist` bu turda derlenmiyor: kaynak değişmiyor, yalnız testler yazılıyor.
