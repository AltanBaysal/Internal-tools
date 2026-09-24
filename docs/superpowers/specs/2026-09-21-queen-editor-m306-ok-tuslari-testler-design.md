# Madde 306 — Ok tuşları prompt yazarken kareyi değiştirmeyecek, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok. Hata kullanırken bulundu *(21 Eylül)*: *"prompt düzenlerken prompt
textinde sağa sola gitmek için ok tuşunu kullanırsam aynı zamanda bu fotoğraflar arasında geçiş
yaptırtıyor."*

## Bugün ne oluyor

`PhotoDetail` pencereye bir tuş dinleyicisi bağlıyor: sol ok önceki kareye, sağ ok sonrakine,
Escape galeriye. Dinleyici **odağa hiç bakmıyor**; tek istisnası açık bir modal.

Yani prompt kutusunda yazarken sağ ok hem imleci kaydırıyor hem kareyi değiştiriyor — kullanıcı
düzenlediği kareden düşüyor, ve yazdığı kayboluyor. **Escape aynı hatanın ikinci yüzü:** yazarken
basınca sayfa kapanıyor.

## Kural

**Tuş bir metin kutusundan geliyorsa dinleyici onu kendine almıyor.** Metin kutusu: `input`,
`textarea`, ve `contenteditable` olan her şey — tarayıcının kendi metin gezinmesi oralarda çalışır,
ve sayfanın kısayolu onun üstüne binmez.

Kutunun dışındayken üçü de bugünkü gibi çalışıyor: galeriden bir kareye girip oklarla gezmek bu
sayfanın kendi hareketi.

**Escape bir istisna değil.** Yazarken kaçmak isteyen kullanıcı önce kutudan çıkar *(Tab, ya da
metnin dışına tıklamak)*. Tek kural, üç tuş.

## Yazılacak testler — `PhotoDetail.test.jsx`

1. **prompt kutusunda sağ ok kareyi değiştirmiyor.**
2. **prompt kutusunda sol ok kareyi değiştirmiyor.**
3. **prompt kutusunda Escape sayfayı kapatmıyor.**
4. **kutunun dışında üçü de bugünkü gibi** *(bekçi — bugün de yeşil)*.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor/frontend` kırmızı.
