# Madde 36 — Ayarlar ekranı ve xAI anahtarı · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 36](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** kullanıcı isteği (18 Ağustos) — tasarım belgelerinde karşılığı yok
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 1 · İstek ve dört karar

Kullanıcının cümlesi: *"grok xai keyini env olarak vermek istemiyorum, uygulama içinde ayarlar olsun,
oraya koyayım ve saved olsun."* Konuşmada dördü karara bağlandı:

| Soru | Karar |
|---|---|
| Ortam değişkeni | **Tamamen kalkar.** `XAI_API_KEY` diye bir şey yok; anahtarın tek yolu bu ekran |
| Ekran nerede | Kenar çubuğunun **altında "Settings" satırı**, kendi ekranı |
| Anahtar nasıl görünür | **Düz metin**, olduğu gibi |
| Anahtar yokken | Uygulama normal açılır; cevap istenince hata kartı çıkar, **altında Settings satırı** |

Tasarım projesinde ayar ekranı yok. Bu madde onu uyduruyor ve bunu açıkça söylüyor: ekranın dili ve
ölçüleri uygulamanın kendi dilinden (`.screen`, `.composer`, mono etiket) alınıyor, yeni bir görsel
fikir icat edilmiyor.

## 2 · Anahtar her istekte okunur

Bugün anahtar açılışta `XaiClient`'a **gömülüyor** (`main.py`). Ayarlar ekranı buna dokunmasa,
kaydettikten sonra sunucuyu yeniden başlatmak gerekirdi ve maddenin bütün amacı kaçardı.

Düzeltme: istemciye bir dize değil **anahtarı okuyan bir işlev** verilir. Her istekte çağrılır,
diskteki güncel değeri alır. Servis yine hiçbir şey bilmiyor — kendisine verilen işlevi çağırıyor,
o kadar.

**Anahtar boşken istek hiç gitmez.** İstemci bunu yerel olarak bilir ve kendi cümlesiyle söyler:
*"No API key is set."* Bu, "sebep uydurma" kuralının ihlali değil — uydurma, uzaktaki bir 401'e
"anahtar yanlış" demek olurdu; burada gönderilecek anahtar olmadığı **bizim bildiğimiz** bir
gerçek.

## 3 · Ayarlar ikinci bir feature

`CODE-STANDARD.md` bugün "tek feature var: workspace" diyor ve gerekçesini de yazıyor: proje, sohbet
ve dosya tek bir küme, çünkü *bir mesaja cevaben dosya yazmak üçüne birden dokunuyor*. Anahtar o
kümenin parçası **değil**: hiçbir sohbet, hiçbir dosya ona dokunmuyor.

Aynı belgenin kuralı da bunu söylüyor: "ikinci feature, gerçekten ayrı bir bağlam çıktığında
açılır." Bu o durum. Yasak (`feature ↛ feature`) çiğnenmiyor, çünkü **workspace settings'i import
etmiyor**: anahtarı motora bağlayan yer bileşim kökü (`main.py`), ki iki tarafı da tanımak onun işi.

Alternatif — anahtarı workspace'in içine koymak — workspace'e "motorun kimlik bilgisi" diye bir iş
daha yüklerdi; mağaza tablosunun kendi kuralı ("beşinci soruyu cevaplayan alan beşinci artefaktı
ister") tam da bunu yasaklıyor.

```
backend/features/settings/
  domain/settings.py          Settings (dataclass) + port
  domain/usecases/…           read_settings · save_settings
  data/file_settings_store.py settings.json şeması burada
  presentation/routes.py      GET · PATCH /api/settings
```

## 4 · Diskte nerede durur

Kökün altında **`settings.json`** — proje klasörlerinin kardeşi. `FileProjectStore.list_all()`
`project.json` taşımayan her şeyi zaten atlıyor ("anything else living under the root is not ours to
read"), yani ayar dosyası projeler listesine sızmaz. Bugünkü davranış, yeni bir korumaya gerek yok.

**Şifreleme yok.** Tek kullanıcılı, kendi makinesinde çalışan bir uygulamada anahtarı şifrelemek,
"şifreyi nereye koyacağız" sorusunu bir tur öteye taşımaktan başka bir şey yapmaz. Dosya kökün
altında, repo dışında; `git status` onu hiç görmüyor.

## 5 · Uç noktalar

| Uç | Ne |
|---|---|
| `GET /api/settings` | `{"apiKey": "…"}` — kaydedilmiş anahtar, düz metin |
| `PATCH /api/settings` | gövdede `apiKey`; kaydeder ve kaydedilmiş hâli döndürür |

`PATCH`, sohbetin desenini izliyor: bugün tek alan var, model varsayılanı ileride aynı uca girer.
Tanınmayan bir alan gelirse **400** — sohbetin PATCH'i de böyle davranıyor.

`GET /api/model`'e dokunulmuyor: o, varsayılan modelin adını söyleyen ayrı bir soru.

## 6 · Ekran

- Kenar çubuğunun **en altında** "Settings" satırı; adresi `/settings`.
- Ekran: başlık **Settings**, mono etiket `XAI API KEY`, tek satırlık bir girdi (düz metin), **Save**
  düğmesi. Kaydedince altında mono bir **"Saved."** satırı çıkar; girdiye dokununca kaybolur —
  "kaydedildi" bir an, kalıcı bir durum değil.
- Reddedilen kayıt sunucunun kendi cümlesini gösterir (`.list-error`, Madde 32'nin satırı).
- Boş anahtar kaydetmek **meşru**: anahtarı silmenin yolu bu.

## 7 · Anahtar yokken hata kartı

Cevap denendiğinde bugünkü kart çıkar ve motorun cümlesini taşır ("No API key is set."). Kartın
altına **Settings'e götüren bir satır** eklenir; yalnız anahtar gerçekten yokken. Nereden bilindiği
önemli: **hata metnine bakılarak değil**, uygulamanın `GET /api/settings`'ten öğrendiği yerel
gerçekle. Metne bakmak, sunucunun cümlesi bir gün değiştiğinde sessizce bozulurdu.

## 8 · Katman denetimi

**Arka uç:** yeni `features/settings/` (dört küçük dosya), `services/xai/client.py` (dizeyi değil
işlevi tutar), `config.py` (`XAI_API_KEY` silinir), `main.py` (bağlar).
`XAI_MODEL` ve `XAI_BASE_URL` **kalıyor** — bu madde yalnız anahtarı taşıyor.

**Ön uç:** yeni `features/settings/SettingsScreen.jsx` ve `useSettings.js`, `shared/useRoute.js`
(dördüncü adres), `Sidebar.jsx` (satır), `ChatScreen.jsx` (kartın altındaki satır), `App.jsx`,
`workspace.css`.

## 9 · Kabul ölçütü

1. `XAI_API_KEY` kodun hiçbir yerinde geçmiyor.
2. Kaydedilen anahtar `settings.json`'da yaşıyor ve yeniden başlatınca duruyor.
3. Motor anahtarı **her istekte** okuyor: kaydetmek, yeniden başlatmadan cevabı değiştiriyor.
4. Anahtar boşken istek gönderilmiyor ve söylenen şey "No API key is set."
5. `GET /api/settings` anahtarı düz metin döndürüyor; `PATCH` kaydediyor, tanımadığı alanda 400.
6. Boş anahtar kaydedilebiliyor (silme yolu).
7. Kenar çubuğunun altındaki Settings satırı `/settings`'e gidiyor; adres yeniden yüklemeye dayanıyor.
8. Kaydedince "Saved." çıkıyor, girdiye dokununca gidiyor.
9. Hata kartının altındaki Settings satırı **yalnız anahtar yokken** çıkıyor ve hata metnine
   bakılarak karar verilmiyor.
10. Ayar dosyası projeler listesinde görünmüyor.

## 10 · Risk

Anahtarın gerçekten çalıştığı ancak canlı istekte görülür — Madde 35'in 26. adımı. Ekranın görsel
dili tasarımdan gelmiyor; uygulamanın kendi öğeleri kullanıldı, göz oraya da bakacak.
