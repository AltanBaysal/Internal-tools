# Madde 65 — Açılış taslak sohbete düşer · **test turu**

**Tarih:** 2026-08-25 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Madde 65 ·
**Tur:** ikiden birincisi — bu belge yalnız **testleri** tarif eder. Kod ikinci turda yazılır ve
o turun kendi spec'i olur.

---

## Ne kanıtlanacak

Yol haritasının "nasıl görülür" satırı iki cümle, ve testler tam olarak o ikisini kanıtlamak
zorunda:

1. Uygulama açılıyor ve **hiçbir şey yazmadan skill seçilebiliyor**.
2. Proje ekranına **sidebar'dan girilmeye devam ediliyor**.

Birincisi maddenin kendisi, ikincisi maddenin bedeli: açılışı taşımak proje ekranını kaybettirmemeli.

## Bugünkü davranış

`/` bir ekran değil, bir çatal: liste geldikten sonra okunur, bir ekran seçilir ve adres
**replace** ile değiştirilir (push değil — push edilse geri tuşu çatala düşer ve kullanıcı yeniden
ileri fırlatılır).

Bugün çatal ilk projenin **proje ekranına** gönderiyor: `/p/<ilk proje>`. O ekranın yazma kutusunda
skill ve model seçici yok; seçiciler yalnız sohbet ekranında yaşıyor. Yani kullanıcı bir mesaj
göndermeden seçicilere ulaşamıyor.

Boş bir taslak sohbet ekranı zaten var ve adresi `/p/<proje>/c/new`; oraya bugün yalnız sidebar'daki
**"+ New chat"** düğmesi götürüyor.

## Değişen davranış

Çatalın hedefi `/p/<ilk proje>` yerine **`/p/<ilk proje>/c/new`** olur. Başka hiçbir şey değişmez:

- **replace kalır.** Çatalın geçmişe yazılmaması bu maddenin konusu değil ve bozulmamalı.
- **Proje yoksa hiçbir şey olmaz.** Liste boşken çatal `/`'da kalır ve boş ekranı çizer; bu madde
  o dalı hiç tutmuyor.
- **Sidebar'daki proje satırı proje ekranını açmaya devam eder** (`/p/<proje>`). Proje ekranı ayrı
  bir kapı — kullanıcının kendi kararı.
- **Yeni ekran yok.** Taslak ekranı zaten var; değişen tek şey oraya kimin, ne zaman gittiği.

## Yazılacak testler

Hepsi `queen-agent/frontend/src/App.test.jsx` içinde — açılış App'in davranışı, başka hiçbir
bileşenin değil. Arka uçta karşılığı yok: bu madde sunucuya hiç dokunmuyor, `pytest` yeşil kalır.

### 1. Uygulama ilk projenin taslak sohbetine açılır

Tek projeli bir liste verilir, uygulama render edilir. Adresin `/p/p1/c/new` olduğu ve **sohbet
ekranının** çizildiği görülür — proje ekranının başlığı (`.screen__title`) ortada yoktur.

*Neyi tutuyor:* maddenin kendisi. Bugün kırmızı, çünkü çatal hâlâ `/p/p1` diyor.

### 2. Açılışta, hiçbir şey yazmadan skill seçilebilir

Uygulama açılır. Hiçbir metin yazılmadan **Skills** düğmesine basılır, menüden bir skill seçilir ve
düğmenin artık o skill'in adını yazdığı görülür.

*Neyi tutuyor:* kullanıcının şikâyetinin tam karşılığı — *"illa bir şey yazacağım, sonra skill
seçebiliyorum"*. Test 1 adresi kanıtlıyor, bu test o adresin **işe yaradığını** kanıtlıyor; adres
doğru olup seçici çalışmasa madde yine bitmemiş olurdu.

*Neden taslakta seçim yapılabiliyor:* taslağın sunucuda kaydı yok, o yüzden seçim oturumun kendi
hâlinde tutuluyor ve bir sonraki sohbet onunla doğuyor. Test bunu bilmek zorunda değil, yalnız
düğmenin yeni adı yazdığını görür.

### 3. Proje ekranı sidebar'dan açılmaya devam eder

Uygulama açılır (yani taslak sohbete düşer), sonra sidebar'daki proje satırına tıklanır. Adresin
`/p/p1` olduğu ve proje ekranının başlığının çizildiği görülür.

*Neyi tutuyor:* maddenin bedeli. Bu test olmadan "açılışı taşıdık" ile "proje ekranını kaybettik"
aynı yeşili verir.

### 4. Bilinmeyen bir adres de taslak sohbete iner

Var olan test güncellenir: `/settings` gibi tanınmayan bir adres çatala düşüyor, ve çatalın hedefi
değiştiği için bu testin beklediği adres de değişiyor — `/p/p1` yerine `/p/p1/c/new`.

*Neden ayrı duruyor:* bu testin kendi tarihi var. Bir zamanlar gerçek bir ekran olan `/settings`
kaldırıldığında, çatalın koruması hâlâ düz `/` sorduğu için adres hiçbir yere gitmiyor ve boş sayfa
çiziyordu. Test o deliği kapatıyor; hedefi değişse de sorusu aynı kalmalı.

### 5. Çatal hâlâ geçmişe yazılmıyor

Var olan test güncellenir: beklenen adres `/p/p1/c/new` olur, `replaceState` çağrıldığı ve
`pushState` çağrılmadığı iddiası aynen durur.

*Neyi tutuyor:* geri tuşu. Yeni hedef push ile gidilirse geri tuşu çatala düşer ve kullanıcı
yeniden ileri fırlatılır — maddenin sessizce kırabileceği tek şey bu.

## Dokunulmayan testler

**"Proje yokken çatal boş ekranı çizer ve `/`'da kalır"** olduğu gibi kalır ve **yeşil kalmalıdır.**
Bu madde proje olan dalı taşıyor; olmayan dalı taşımak başka bir iştir ve kimse istemedi.

**"Çatal, render'ın değil tarayıcının adresini sorar"** da olduğu gibi kalır: hedef adresi hiç
iddia etmiyor, kullanıcının gittiği yerde kalmasını iddia ediyor.

## Kapsam dışı

Proje ekranının yazma kutusuna seçici eklemek *(kullanıcı seçmedi — açılışın taşınması seçildi)* ·
sidebar'daki "+ New chat" düğmesinin davranışı *(zaten aynı yere gidiyor, değişmiyor)* · proje
yokken açılış · taslak ekranının görünümü.

## Nasıl kırmızı görülür

```
npm test --prefix queen-agent/frontend
```

Beş testin **üçü** kırmızı düşer — 1, 2 ve 4, hepsi aynı sebeple: çatal hâlâ proje ekranına
gidiyor. Test 5 de kırmızı düşer, ama beklediği adres yüzünden; iddiasının kendisi bozulmuş değil.
Test 3 bugün **yeşil** geçebilir, çünkü sidebar zaten proje ekranını açıyor — o bir gerileme
kalkanı, kırmızı olması beklenmez ve olmaması bir sorun değildir.

`python -m pytest queen-agent -q` yeşil kalır; bu madde arka uca dokunmuyor.

Kırmızı görüldükten sonra **kırmızı hâliyle commit'lenir.** `skip` ve `xfail` yok — bir suite öyle
yeşile döndürülmez.
