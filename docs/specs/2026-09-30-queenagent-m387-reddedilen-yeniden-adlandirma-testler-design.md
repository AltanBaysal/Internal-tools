# Madde 387 — Reddedilen yeniden adlandırma yazılan adı kaybetmez · testler

**Kullanıcıdan istenen:** yok. Madde `ALIGNED`; tasarım bu durumu çizmiyor, karar aşağıda.

## Bugün

`ProjectRow`'un `RenameField`'ı Enter'da (ya da başka yere basılınca) adı yukarı verir ve **hemen
kapanır**; satır eski adı gösterir. Sunucu `PATCH /api/projects/<id>`'yi reddedince `useProjects`'in
`editProject`'i `writeError`'ı kurar ve `null` döner: listenin üstünde `.list-error` satırı çıkar,
ama yazılan ad gitmiştir. Ad sorma ekranı (`NameProjectScreen`) ise reddedilen adı kutuda tutar ve
sunucunun sözünü söyler (Madde 364).

## Tasarım ne diyor

Hiçbir şey: `APP-BUGS.md` 26 — "no write fails in the pages". `projects/index.html`'in
`settleRename`'i adı gönderir ve alanı kapatır; reddi çizmez. Bu yüzden ad sorma ekranının
davranışı örnek alınır: **alan, sunucu cevap verene kadar açık kalır; reddedilince yazılan adla açık
kalır**, ve hata bugünkü yerinde, listenin üstündeki `.list-error` satırında görünür. Satırın içine
ikinci bir hata satırı eklenmez: aynı söz iki yerde yazılmış olurdu.

## Davranış (testlerin söylediği)

1. **Enter adı bir kez gönderir, alan cevabı bekler.** Cevap gelmeden alan açık, yazılan ad içinde;
   ikinci bir Enter ikinci bir istek değildir. Ad kabul edilince alan kapanır ve satır yeni adı
   gösterir.
2. **Reddedilen ad alanda kalır.** Sunucu reddedince alan açık, yazılan ad içinde, odak alanda; hata
   `.list-error` olarak sunucunun kendi sözüyle görünür.
3. **Kalan ad yeniden gönderilebilir.** Enter aynı adı tekrar gönderir; kabul edilirse alan kapanır,
   satır yeni adı gösterir, hata satırı gider.
4. **Esc vazgeçer.** Reddden sonra Esc alanı kapatır, satır eski adı gösterir, hiçbir şey
   gönderilmez. Hata satırı bir sonraki yazma işine kadar durur — bugünkü kural (Madde 364).
5. **Başka yere basmak da cevabı bekler.** Blur adı gönderir; alan kabul gelince kapanır.
6. **Boş ad** bugünkü gibi hiçbir şey sormaz ve alanı hemen kapatır.

## Satır ile ekran arasındaki söz

`onRename(id, name)` bir söz (promise) döner: ad kabul edildiyse doğru (truthy) bir değerle, reddedildiyse
yanlış (falsy) bir değerle çözülür. `App`'in `editProject`'i bugün zaten böyle döner: kabulde
düzenlenmiş proje, redde `null`.

## Testler

**`ProjectRow.test.jsx`** (satırın kendi davranışı, `onRename` sahte):

- Var olan "Enter saves what was typed, once, and closes the field" — `onRename` kabulle çözülür;
  alan cevaptan sonra kapanır, cevap beklenirken ikinci Enter ikinci çağrı yapmaz.
- Var olan "pressing anywhere else saves" — `onRename` kabulle çözülür; alan cevaptan sonra kapanır.
- Yeni: "a refused name stays in the field, ready to send again" — ilk cevap `null`: alan açık,
  değer `Harbour`, odak alanda; Enter tekrar gönderir, kabulde alan kapanır.
- Yeni: "the field stays while the name is on its way" — cevap gelmemişken alan açık ve adı tutuyor.
- Yeni: "Escape after a refusal gives the name up" — `null`dan sonra Esc: alan kapanır, eski ad,
  tek çağrı.

**`App.test.jsx`** (gerçek `useProjects` ve sahte sunucu, `refusingFirstWrite`):

- Var olan "a rename the server refuses leaves All projects standing, with the server's words" —
  artık: `Thesis` satırında alan açık, değeri `Dissertation`; `.list-error` sunucunun sözü; `Notes`
  yerinde; `Couldn't load projects.` yok.
- Yeni: "Enter again sends the kept name, and once it lands the row and the line follow" — ikinci
  PATCH, satır `Dissertation`, hata satırı yok.
- Var olan "the next write that lands takes the refusal's line away" — reddden sonra önce Esc ile
  vazgeçilir (alan artık kendiliğinden kapanmıyor), sonra `Notes` sabitlenir; anlamı aynı kalır.
