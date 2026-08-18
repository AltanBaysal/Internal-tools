# Madde 32 — Kalan sapmalar kapanır · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 32](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** sapma 79, 83, 84, 85 · [tasarım v2 farkları](../research/2026-08-14-mira-tasarim-farklari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 1 · Dört sapmadan ikisi iş, biri düşüyor, biri kapanmış

| Sapma | Ne oldu |
|---|---|
| 83 · çekilemeyen liste boş liste gibi konuşuyor | **bu maddede düzeltilir** |
| 84 · okunan dosya projeden dönünce yeniden açılıyor | **bu maddede düzeltilir** |
| 85 · model `.md` dışında uzantı isterse o uzantıyla yazılıyor | **düşüyor** — §4 |
| 79 · öğretici satır liste doluyken de duruyor | **kapanmış** — §5 |

---

## 2 · Sapma 83 — cevabını alamadığı soruya "hiç yok" demek

Bugün `useList` başarısızlığı yutuyor: `catch` listeyi boşaltıyor, `loading` biterken ekran
"No files yet — start a chat and QueenAgent will create one." diyor. Ekran, **cevabını alamadığı bir
soruya cevap vermiş** oluyor; üstelik teşvik ediyor. Sohbet sütunu daha sessiz yanlış yapıyor: hiç
liste, hiç cümle, hiç sebep.

Kural: **boş hâl cümlesi yalnız yükleme başarıyla bittiğinde çıkar.** Başarısızlıkta yerine
sunucunun kendi cümlesini taşıyan bir hata satırı durur — `CLAUDE.md`'nin "sebep uydurma" kuralı ve
sapma 82'nin kapanışı zaten bu cümleyi tarayıcıya kadar getirmiş durumda.

**Elde olan liste silinmez.** Bugün `catch` diziyi boşaltıyor; bir yenileme başarısız olduğunda
bu, dosyaları duran bir projeyi boş gösterir — ikinci bir yalan. Eldeki liste kalır, üstünde hata
satırı durur: dakika önce doğruydu, şimdi bilinmiyor, ve ekran ikisini birbirine karıştırmaz.

Desen yeni değil: `useProjects` başlangıçtan beri `error` tutuyor ve kenar çubuğu onu gösteriyor.
Bu madde aynı deseni öteki iki listeye taşıyor — üçüncü bir yol açmıyor.

### Hata satırı tek sınıf

Bugün `.file-list__error` var ve tek bir şeye hizmet ediyor: reddedilen bir silme. Şimdi aynı görünüş
üç yerde daha gerekiyor. Sınıf **`.list-error`** olarak adlandırılır ve dördü de onu kullanır: bir
listede bir şeyin ters gittiğini söyleyen satır hepsinde aynı şey. Görünüşü değişmiyor (mono, 11px,
yıkıcı ton) — değişen yalnız adın kapsamı, ve `.file-list__error` bir sohbet sütununda yanlış
okunurdu.

## 3 · Sapma 84 — kapatmak bir andır, saklamak değil

Bugün `useFile` açık dosyayı **projesiyle birlikte** tutuyor ve adı yalnız o proje ekrandayken
okuyor. Sonucu: başka projeye gidince panel kapanmış *görünür*, geri dönünce aynı dosya kendiliğinden
açılır. Tasarımın cümlesi "proje değişince **kapanır**" — kapatma anıydı, gizleme değil.

Düzeltme: proje değiştiğinde, açık dosya o projeye ait değilse **bırakılır**.

Bugünkü eşleştirme kalıyor, silinmiyor. İki sebep: (1) proje değişen render ile temizleyen etkinin
arasında bir kare var, eşleştirme o karede yanlış projenin dosyasının parlamasını engelliyor; (2)
bir dosya, onun projesine götüren gezinmeyle **aynı nefeste** açılabiliyor — temizleme yalnız
`projectId` değiştiğinde koştuğu için o açılışa dokunmaz. Bugünkü yorumun uyardığı tuzak buydu ve
kurtuluş yolu, etkinin `opened`'a değil yalnız projeye bakması.

## 4 · Sapma 85 düşüyor — ve sebebi Faz 7

Sapmanın dayanağı v1'in cümlesi: "**v1'de üretilen dosya markdown'dır**". Faz 7 bunu geçersiz kıldı:
`Generate prompts+` bir **`.json`** yapı dosyası yazıyor, `build_prompts` bir **`.py`** dosyası
üretiyor, ve okuyucu Madde 30'da ikisini göstermek için mono gövde kazandı. Uzantıyı `.md`'ye
çevirmek bugün üretim hattını **kırar**: `intro-shots.json` diye istenen dosya
`intro-shots.json.md` ya da `intro-shots.md` olurdu ve `build_prompts` okuyacak bir yapı bulamazdı.

Bugünkü davranış **bilerek kalıyor:** uzantı verilmişse korunur, verilmemişse `.md` eklenir. Ad
temizliği (`safe_name`) olduğu gibi duruyor — klasör yok, tuhaf karakter yok, boş ad `note.md`.

Bu bir sapmanın "yapılmadı"sı değil, **eskimesi**: 14 Ağustos'ta doğruydu, 18 Ağustos'ta değil.
Farklar belgesine tarihli bir not düşülür; kayıt silinmez.

## 5 · Sapma 79 zaten kapandı

"Chats create the files; you just open and read them." ikinci satırı üründe artık yok: hem ray hem
proje sütunu tek cümle gösteriyor ve o cümle yalnız liste boşken çıkıyor. Madde 20-22 ray ve sütunu
yeniden yazarken kapandı. Bu maddede yapılacak iş yok; testler zaten yerinde duruyor ve sapma
kayda geçmiş sayılır.

---

## 6 · Katman denetimi

**Ön uç:** `shared/useList.js` (hatayı tut), `features/workspace/useFiles.js` ve `useChatLists.js`
(dışa ver), `FileRail.jsx` · `ProjectScreen.jsx` (satırı çiz), `App.jsx` (iletir),
`useFile.js` (kapatma anı), `workspace.css` (`.list-error`).

**Arka uç:** dokunulmuyor. Sapma 85 düştüğü için `tools.py`'de değişiklik yok.

---

## 7 · Kabul ölçütü

1. Dosya listesi çekilemezse **hata satırı** çıkar ve "No files yet" **çıkmaz**.
2. Sohbet listesi çekilemezse aynı satır çıkar — sütun sessizce boşalmaz.
3. Satır sunucunun kendi cümlesini taşır; uydurulmuş sebep yok.
4. Yükleme sürerken ne hata ne boş cümle çıkar (iskelet).
5. Başarısız bir **yenileme** eldeki listeyi silmez.
6. Başarılı yüklemede hata satırı yok, liste boşsa cümle var.
7. Dosya açıkken başka projeye geçip dönmek paneli **kapalı** bulur.
8. Bir dosyayı başka projenin ekranındayken açıp o projeye gitmek paneli **açık** bulur *(aynı
   nefeste açılış korunur)*.
9. Model `report.txt` isterse projeye `report.txt` iner; uzantısız ad `.md` alır.

## 8 · Risk

Yok denecek kadar az; hepsi jsdom'da sınanabiliyor. `.list-error` adının değişmesi tek bir testi
dokunuyor, o test kendi kırmızısıyla taşınır.
