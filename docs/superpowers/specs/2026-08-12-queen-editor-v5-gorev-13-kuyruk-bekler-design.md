# Queen Editor v5 · Görev 13 — Üretici eksikken kuyruk bekler · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 4, Görev 13 ·
**Kaynak madde:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
53 · **Tür:** arka uç + ön yüz.

## Neden

Bugün sırası gelen işin üreticisi yoksa motor **koşuyu hataya düşürüyor**: "Bu iş türü için üretici
yok". Bu, kullanıcının kuyruğa attığı işi kaybetmesi demek değil ama ekranda kırmızı bir son
demek — oysa olan şey bir hata değil, bir **eksik**: model grubu henüz inmemiş.

Tasarım bunu bekleme olarak anlatıyor: kuyruk durur, ne beklediğini söyler, kurulumu önerir ve
kurulum bitince **kendiliğinden** sürer.

## Ne olacak

| Durum | Bugün | Yarın |
|---|---|---|
| Sırası gelen işin üreticisi yok | koşu "hata" ile durur, kırmızı kart | koşu **bekliyor** hâline geçer |
| Kuyruk kartı | — | "Bekliyor — üretici kurulu değil" · altında "5 video" · "Kurulum bitince kuyruk kendiliğinden sürer." · tek buton **"Video üreticisini kur"** |
| Kurulum bitince | — | kuyruk kendiliğinden sürer |
| Kurulum iptal edilince | — | kuyruktaki işler **atılmaz**, bekleme sürer |
| Kısmi eksiklik | — | yalnız o türün kartı uyarır; motor eksik türü **atlamaz**, orada bekler |

## Kararlar

### 1. Bekleme, hatanın değil duraklamanın akrabasıdır

Motor eksik üreticiye gelince koşuyu `waiting` hâlinde bitirir ve hangi türü beklediğini söyler.
Hata değil çünkü hiçbir şey başarısız olmadı; duraklatma da değil çünkü kullanıcı istemedi. Kendi
adı olur, ve o ad kuyruk kartının kendi hâllerinden biri hâline gelir.

Beklerken **hiçbir satır yazılmaz**: iş kuyrukta borçlu kalır, tıpkı duraklatılan yarım iş gibi.
Kurulum iptal edilse de işler orada durur — madde 53'ün açık şartı.

### 2. Motor eksik türü atlamaz

Tür sırası (foto → video → ses) kuralın kendisi: video işleri yapılmadan sese geçilmez, ve video
üreticisi yoksa **sıra orada durur**. Atlamak, kullanıcının beklediği sıradan başka bir sırada iş
üretmek olurdu ve galerinin sırası da o sıraya bağlı (Görev 8).

### 3. Kuyruk kendiliğinden sürer — ekran sürdürür

"Kurulum bitince kuyruk kendiliğinden sürer" cümlesinin sahibi ekrandır: proje ekranı zaten yarım
kuyruğu açılışta sürdürüyor. Aynı kural genişler — **beklenen üretici kurulu hâle geldiğinde**
ekran koşuyu yeniden başlatır.

Arka uçta yapmak, kurulum feature'ının üretim feature'ını çağırması olurdu (`feature ↛ feature`).
Ekran ikisini de zaten görüyor; birleştirme yeri orası.

### 4. Buton üreticinin kendi adını söyler

Kartın tek butonu "Video üreticisini kur" — hangi üreticiyi kuracağını söyler ve doğrudan kurulumu
başlatır (üretim panelindeki Kur gibi, onay sormadan): kullanıcı zaten o işleri kuyruğa atmış, ne
istediği belli.

## Nasıl görülür

1. Üreticisi olmayan türde iş kuyruğa girince koşu kırmızıya düşmez; kuyruk kartı "Bekliyor —
   üretici kurulu değil" der.
2. Kartın altında kaç iş beklediği ("5 video") ve "Kurulum bitince kuyruk kendiliğinden sürer."
   yazar.
3. "Video üreticisini kur" butonuna basınca kurulum başlar; bitince kuyruk kendiliğinden akar.
4. Kurulum iptal edilirse kuyruktaki işler durur, bekleme sürer.

## Testler

**Arka uç:** üreticisi olmayan türe gelince koşu `waiting` döner ve türü söyler · bekleyen iş
kuyrukta borçlu kalır · eksik türden sonraki tür üretilmez · üreticisi olan türler eksik türe
gelene kadar normal biter.

**Ön yüz:** kuyruk kartı bekleme hâlini kendi metinleriyle çizer · buton üreticinin adını söyler ve
kurulumu başlatır · beklenen üretici kurulu hâle gelince ekran koşuyu sürdürür.

## Kapsam dışı

- **Video ve ses işlerinin gerçekten kuyruğa girmesi** — Blok 5-6. Bu görevde bekleme, testte
  üreticisi olmayan bir türle doğrulanır.
- **Kurulumun kendisi** — Görev 12'de yapıldı.

## Riskler

- **Ekranın sürdürmesi** (karar 3) tarayıcı kapalıyken çalışmaz: kurulum biter, kuyruk bekler,
  kullanıcı projeyi açınca sürer. Tasarımın cümlesi ("kuyruk kendiliğinden sürer") bu kadarını
  karşılıyor ve uygulamanın kuyruğu zaten açılışta sürüyor.
