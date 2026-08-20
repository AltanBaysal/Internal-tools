# Madde 62 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-20-queenagent-m62-impl-design.md](../specs/2026-08-20-queenagent-m62-impl-design.md)
· tur 1: [test tasarımı](../specs/2026-08-20-queenagent-m62-test-design.md) ·
[test planı](2026-08-20-queenagent-m62-test-plan.md)

**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adımlar

### 1. Backend — anahtarın yeni yolu

- `backend/config.py`: `XAI_API_KEY = os.environ.get("XAI_API_KEY", "")`. Bugün orada duran ve
  anahtarın Settings ekranında yazıldığını söyleyen yorum kalkar; yerine anahtarın neden burada
  olduğu geçer.
- `main.py`: `XaiClient(lambda: config.XAI_API_KEY, …)`. Settings import'ları, `settings_store` ve
  `make_settings_bp(...)` satırı gider.
- `backend/features/settings/` ağacının tamamı silinir.

### 2. Backend — anlattığı kod gitmiş testler

- `test_settings.py`, `test_settings_api.py` silinir.
- `test_projects_api.py::test_the_settings_file_is_not_a_project` **kalır, adı ve yorumu değişir.**
  Sorduğu şey hâlâ değerli — proje olmayan bir dosyanın listeye karışmaması — ama gerekçesi
  ("artık gerçek bir dosya") yanlışa dönüyor. Bir başıboş dosya üzerinden sorulur hâle gelir.
- `test_xai_client.py`'deki *"The old sentence named an environment variable that no longer exists"*
  yorumu düzeltilir: değişken geri geldi. Deponun kuralı — çakışmada yorum koda uydurulur.

### 3. Arayüz — Settings'in izleri

- `features/settings/` klasörü (ekran, hook ve iki test dosyası) silinir.
- `shared/useRoute.js`: `settings` dalı gider; `/settings` yakalanmayanların düştüğü yere düşer.
- `App.jsx`: `useSettings` ve `SettingsScreen` import'ları, `apiKey`/`saveApiKey`, `onOpenSettings`,
  `missingKey`, `onSettings`, `route.view === "settings"` bloğu ve iskelet koşulundaki
  `route.view !== "settings"` — hepsi gider.
- `App.jsx` çatal koruması **genişler**: `window.location.pathname === "/"` yerine, tarayıcının o
  anki adresinin bir çatala çözülüp çözülmediği sorulur. Madde 52'nin kazandığı şey korunuyor —
  soru hâlâ tarayıcıya soruluyor, render'a değil.
- `Sidebar.jsx`: `onOpenSettings` prop'u, `sidebar__foot` bloğu ve içindeki düğme gider.
- `ChatScreen.jsx`: `missingKey`, `onSettings` ve hata kartındaki düğme gider. Kart sunucunun
  cümlesiyle kalır.
- `workspace.css`: `.sidebar__foot`, `.sidebar__settings`, `.field*` ailesi ve `.failure__settings`
  gider. Hepsi yalnız silinen parçalar tarafından kullanılıyor — kontrol edildi.

### 4. Arayüz — eskiyen testler

- `Sidebar.test.jsx`: Settings satırının varlığını söyleyen iki test silinir. Katlanmış kenar
  çubuğu testindeki *"Settings düğmesi yok"* satırı da çıkar — **bu, yeşil bir testten bir iddia
  çıkarmak demek ve açıkça yazılıyor:** düğme artık hiçbir durumda yokken, "katlanınca yok"
  demek hiçbir şey söylemiyor.
- `ChatScreen.test.jsx`: eski üç Settings testi silinir. Üçü de tur 1'de eklenen tek testin içinde
  kalıyor.
- `App.test.jsx`: Settings satırının ekranı açtığı test ve anahtarı kaydeden test silinir. Madde
  52'nin testlerinden **biri yaşar, taşıtı değişir**: iki projeli liste, gidilen yer ikincisi, çünkü
  çatalın kendi indiği yer birincisi. Öteki — uygulamanın içinden gidileni — ölür; senaryosu artık
  ulaşılamıyor ve yaşayan test onu zaten içine alıyor. Gerekçesi tasarımın 1. bölümünde, testin
  kendi yorumunda da yazıyor. *(Bu plan önce ikisinin de yaşayacağını söylüyordu; uygulama okununca
  düzeltildi.)*

### 5. Defter

`queenagent.ipynb`, **NotebookEdit ile** (Edit değil: dosya JSON):

- CONFIG: `XAI_API_KEY` Secrets'tan okunur — `GITHUB_TOKEN` ile aynı `try/except` + `assert` şekli.
  Anahtarın Settings'e yazıldığını söyleyen yorum kalkar.
- Serve: `env` içine `"XAI_API_KEY": XAI_API_KEY`.
- Serve'ün son satırlarındaki *"İlk açılışta: Settings → xAI anahtarını yaz"* gider.
- Parolasızlık uyarısındaki *"senin xAI anahtarınla istek atabilir"* **kalır** — hâlâ doğru.

### 6. Belgeler

`FOUNDATION.md` Karar 1, `CODE-STANDARD.md` (veri tablosu + "iki özellik" bölümü), `README.md` —
tasarımın 3. bölümündeki üç yalan. Ve yürürlükteki yol haritasına Madde 62 eklenir.

### 7. `dist`

`npm run build --prefix queen-agent/frontend`, ve **aynı commit'te**. Deponun kuralı, ve
`test_dist_is_committed.py` alternatifi reddediyor.

## Beklenen yeşil

Tur 1'in on dört kırmızısı. Takımın toplam sayıları koşudan **sonra** kaydedilir — silinen test
sayısı toplamları düşürüyor ve bu planın atalarında tahmin edilen toplamlar beş kez tutmadı.
**Sonuç: backend 382, arayüz 474.**

## Koşarken çıkan iki şey

**Kilit kendi yazarını yakaladı, ve haklı olan koddu.** `test_the_xai_key_is_never_printed`, hiçbir
`print` satırında `XAI_API_KEY` dizgesinin geçmemesini istiyordu. Defter kullanıcıya hangi secret'ı
ekleyeceğini söyleyince kırmızıya döndü — oysa o cümle kullanıcının görmesi gereken şey. Test
**adı** yasaklıyordu, oysa kural **değer** hakkında. Madde 56'daki `pip install` testiyle aynı hata:
bir yazımı sabitlemek, kuralı sormak yerine.

Test kurala çevrildi: değer bir `print`e ancak `{XAI_API_KEY}` ile ya da doğrudan argüman olarak
girebilir; sorulan bunlar. Hâlâ bir kilit — bugün hiçbiri olmuyor. **Kırmızı commit'lenmiş bir
iddianın yeşil turda değiştirilmesi budur ve burada yazılı olması gerekiyordu.**

**`git rm` klasörü bırakıyor.** `backend/features/settings` silindikten sonra yerinde `__pycache__`
altında bytecode kaldı, yani klasör durmaya devam etti ve `test_the_settings_feature_is_gone` haklı
olarak düştü. Ayrıca silindi. Testin dosyaları değil **klasörü** sorması bu yüzden doğruydu.

## Kapanış denetimi

- `queen-agent/` altında `settings` diye bir dosya, klasör, rota veya sınıf kalmamış.
- `grep`: `missingKey`, `onOpenSettings`, `onSettings`, `useSettings`, `settings.json` — hiçbiri
  yok. `docs/superpowers/` altındaki eski madde belgeleri hariç: onlar yazıldıkları günün kaydı ve
  kasten eskiyorlar.
- Yerelde anahtarsız açılan uygulama hâlâ açılıyor; sohbet, sunucunun kendi cümlesini gösteriyor.
