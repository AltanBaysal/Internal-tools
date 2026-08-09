# Mira — Faz 11: Silme (Madde 25-26)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) · [Faz 10](2026-08-09-mira-faz-10-okuma-design.md)

**Kapsam:** dosya satırındaki `×`, `trash/`'e taşıma ve **Undo** şeridi (Madde 25) · sohbet silme,
onaylı (Madde 26).
**Kapsam dışı:** yeniden adlandırma (Faz 12) · arama (Faz 13) · çöpü boşaltma (aşağıda karara
bağlandı: v1 boşaltmıyor).

---

## 1 · Silmek taşımaktır

`DELETE /api/projects/<pid>/files/<name>` → `{"trashed": "<çöpteki ad>"}`.

Dosya silinmez, `<pid>/trash/` altına **taşınır**. `store.move` bir `os.replace`'tir: mtime korunur,
o yüzden geri gelen dosya listede **eski yerine** oturur — tasarımın "en üste zıplamaz" sözü budur.

**Çöpte ad çakışması.** `plan.md` silinip yeniden üretilip yine silinirse `trash/plan.md` doludur.
İkincisi `plan-2.md` olur — Faz 8'in `unique_name` kuralının aynısı. Bu yüzden yanıt çöpteki adı
söyler: tarayıcı neyi geri isteyeceğini ancak böyle bilir.

**Diske hiçbir kayıt yazılmaz.** "Bu dosya aslında `plan.md` idi" bilgisini tutan bir dosya yok;
o bilgi **şeridin kendisidir** ve şerit ekrandan gidince teklif de biter. Kayıt dosyası açmak
`CODE-STANDARD`'ın "hiçbir artefakt bir başkasının cevabını tekrarlamaz" kuralını bozardı.

**`trash/` v1'de boşaltılmaz.** Ne uygulama ne de bir zamanlayıcı siler; kullanıcı isterse klasörü
kendisi temizler. Silmek bu yüzden gerçekten geri alınabilir bir iştir — teklif geçse bile dosya
diskte durur.

## 2 · Undo

`POST /api/projects/<pid>/trash/<trashed>/restore`, gövde `{"name": "<özgün ad>"}` → `{}`.

- Özgün ad **yeniden doluysa 409** ve gövdede sunucunun cümlesi. Sessizce yeni bir ad uydurmak
  kullanıcının bastığı düğmeden başka bir sonuç doğururdu; üstünü yazmak ise bir dosya kaybettirirdi.
- Çöpte o ad yoksa **404**.

**Şeridin ömrü** (yol haritasının açık maddesi): **zamanlayıcı yok.** Şerit
(a) Undo'ya basılınca, (b) başka bir dosya silinince — o zaman yeni silmeyi gösterir — ve
(c) projeden çıkılınca gider. Süreli bir şerit, sessizce kapanan bir pencere sözü verirdi; oysa
dosya `trash/`'te durduğu için kaybolan tek şey **teklif**, dosya değil.

Şerit metni: **"File deleted."** ve yanında **Undo**. Listenin üstünde durur — hem rayda hem proje
ekranındaki sütunda, çünkü ikisi de aynı listedir.

**Geri alma başarısız olursa şerit kalır** ve altında sunucunun kendi sözleri yazar; sebep
uydurulmaz (Faz 7'nin hata kuralı). Şerit kalır çünkü teklif hâlâ geçerlidir — dosya çöpte duruyor.

## 3 · Sohbet silme

`DELETE /api/projects/<pid>/chats/<cid>` → `{}`.

- **Onay tarayıcının kendi kutusudur** (`window.confirm`). Faz 3 yeniden adlandırmayı `window.prompt`
  ile sormuştu; ikinci bir diyalog dili icat etmiyoruz. Cümle **"Delete this chat? Its files stay in
  the project."** — ne gittiğini ve neyin kaldığını aynı satırda söyler.
- **Geri alınmaz ve `trash/`'e gitmez.** Tasarım Undo'yu yalnız dosyaya veriyor; sohbete onay veriyor.
  İkisini birden vermek, onayı gereksiz kılardı.
- **Sohbetin ürettiği dosyalar kalır.** Dosya projeye aittir, sohbete değil — v1 tasarımının ilk
  kararlarından biri.
- Silinen sohbet iki listeden de çıkar (kenar çubuğu ve proje ekranı) ve proje kartının sayısı düşer.
- **Açık sohbet silinemez:** `×` yalnız proje ekranındaki satırda var, sohbet ekranının başlığında
  yok. Bu yüzden "silinince nereye gidilir" diye bir durum doğmuyor ve o dal yazılmıyor.

**Dolu kırmızı buton yok.** Ne satırdaki `×` ne de onay kutusu kırmızı bir eylem düğmesi taşır;
yıkıcı dil uygulama genelinde aynıdır.

## 4 · Ekranlar

- **`×` dosya ve sohbet satırlarında.** Satırda durur, satır üstüne gelince görünür hâle gelir;
  DOM'da her zaman vardır. Kenar çubuğundaki sohbet satırlarında **yoktur** — orası gezinme yeridir.
- **Açık panelin dosyası silinirse panel kapanır.** Var olmayan bir şeyi okumaya devam edemez.
- Silme ve Undo listeyi ve proje kartının sayısını tazeler.

## 5 · Yanıtlar hep JSON

Silme ve geri alma **200 + gövde** döner, 204 değil. Tarayıcının tek istek yolu (`shared/api.js`)
her yanıtın gövdesini okur; 204 için oraya bir istisna koymak, tek anlamı olan "sunucu hayır dedi"
kuralını bozardı.

## 6 · Katmanlar

| Katman | Ekleme |
|---|---|
| services/store | `remove(rel)` — sohbet dosyasını gerçekten siler |
| domain/errors | `NameTaken` |
| domain/ports | `FileStore.delete/restore` · `ChatStore.delete` |
| domain/usecases | `delete_file` (çöpteki adı döner) · `restore_file` · `delete_chat` |
| data | `FileFileStore.delete/restore` — `unique_name` çöpte de geçerli · `FileChatStore.delete` |
| presentation | `DELETE …/files/<name>` · `POST …/trash/<trashed>/restore` · `DELETE …/chats/<cid>` |
| frontend | `useFiles` siler ve geri alır · `DeletedStrip.jsx` · `FileRow`/`ProjectScreen` satırlarında `×` · `shared/api.js` `deleteJson` |

`unique_name` Faz 8'de `domain/tools.py` içinde doğmuştu; çöp de aynı kuralı kullandığı için
`domain/naming.py`'ye taşınır ve `tools.py` oradan alır. İki yerde iki kopya olsaydı biri kayardı.

## 7 · Testler

1. Silinen dosya `files/`'tan çıkar, `trash/`'te belirir; yanıt çöpteki adı söyler.
2. Aynı ad ikinci kez silinince çöpte `-2` alır, ilki durur.
3. Geri alınan dosya `files/`'a döner ve **mtime'ı korunur** (listede eski sırasında).
4. Özgün ad doluyken geri alma 409, dosya çöpte kalır.
5. Çöpte olmayan bir adı geri alma 404.
6. Silinen sohbet `get` ile bulunamaz; ürettiği dosyalar yerinde durur.
7. Olmayan sohbeti silme 404.
8. Ön yüz: `×` satırı listeden çıkarır ve şerit belirir.
9. Ön yüz: Undo dosyayı geri getirir ve şerit gider.
10. Ön yüz: sohbet silme onay ister; iptal edilince hiçbir istek gitmez.
11. Ön yüz: açık panelin dosyası silinince panel kapanır.

## 8 · Kabul kriteri

`pytest` ve `npm test` yeşil. Ekranda: ortadaki bir dosyayı sil → satır gider, şerit çıkar → Undo →
dosya **aynı sırada** geri gelir. Dosya üretmiş bir sohbeti sil → onay sorar; sohbet gider, dosyaları
listede durur.
