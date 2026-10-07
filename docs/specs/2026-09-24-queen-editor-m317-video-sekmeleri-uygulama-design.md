# Madde 317 — Video panelinin iki sekmesi, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m317 test turu](2026-09-24-queen-editor-m317-video-sekmeleri-testler-design.md),
`8db0c72c`. Adlar ve kurallar orada; bu belge nasıl yapıldığını söylüyor.

## Sunucu

**`projects/data/reference_settings_store.py`** — `DriveReferenceSettingsStore`, `settings_store`'un
ikizi: aynı üç yöntem, dosya `reference_settings.json`, iki alan. `_text` / `_count` kopyalanıyor,
import edilmiyor — öteki modülün özel adları, ve ikisi birer satır.

**`projects/domain/usecases/save_reference_settings.py`** — `save_settings`'in ikizi: proje yoksa
`ProjectMissing`, varsa `{"prompts", "variants"}` yazılır. Doğrulama yok, aynı sebeple: dosya
kutuları doldurmak için var, ve sunucunun reddettiği metin de kullanıcının yazdığıdır. **Okuma için
yeni kullanım durumu yok:** `get_settings(store, project)` zaten "proje var mı, varsa deponun
cevabı" — depo değişince aynı cümle.

**`projects/presentation/reference_settings_routes.py`** — `make_reference_settings_blueprint`:
`GET` ve `PUT /api/projects/<proje>/reference-settings`, projects kapısının settings satırlarının
aynısı *(404, 500, 204; tipler kapıda boşa çevriliyor)*. **Ayrı bir blueprint**, projects'inkine iki
satır değil: photo_generation'ın havuzu da kendi blueprint'inde, ve projects'in bağlamasını bilen her
test dokunulmadan kalıyor.

**`main.py`** — depo, iki bağlı kullanım durumu, blueprint `create_app`'in listesinde.

## Ekran

**`api.js`** — `getReferenceSettings`, `saveReferenceSettings`; `getSettings` / `saveSettings`'in
kalıbı.

**`production_modes.js`** — `SOURCES`'ın etiketi `Kareden`. Yorum da: sekmeler, satır değil.

**`SidePanel.jsx`** — `LayerPanel`'e `project`.

**`LayerPanel.jsx`:**

- **Sekmeler** panelin tepesinde, kurulum kartının üstünde: `.wf-segment`, panel genişliğinde
  *(`display: flex`, düğmeler `flex: 1` — tasarımın `.tabs`'ı)*; yalnız video panelinde. `Üretim`
  satırı gidiyor.
- **Referanstan'ın dizilişi:** Model, `Referanslar` *(yalnız başlık; düğmesi 318'in)*,
  `Prompt listesi`, Varyant. Kareden'inki değişmiyor.
- **İki varyant:** `variants` Kareden'in, her kuruluşta `"1"`; `poolVariants` Referanstan'ın.
  Kutu hangi sekme açıksa onu gösterip yazıyor; sayım, ret, gönderim açık sekmenin sayısını okuyor.
- **Taslak:** modül düzeyinde `DRAFTS = new Map()`, proje başına `{ prompts, variants }` — fotoğraf
  panelinin `REMEMBERED`'ı gibi, bellekte. Yalnız video paneli okuyup yazıyor.
- **"Oturmuş" bayrağı** *(ref)*: kutular bu ziyaretin sözünü taşıyor mu — bir taslakla kurulduysa,
  kayıt geldiyse ya da bir tuşa basıldıysa evet. **Taslak ancak oturmuşken yazılıyor**; yoksa
  Referanstan hiç açılmadan kurulan bir panel boş bir taslak bırakır ve kayıt bir daha hiç sorulmazdı.
- **Kayıt**, Referanstan açıkken, kutular oturmamışken ve bu kuruluşta sorulmamışsa bir kez
  soruluyor. Cevap geldiğinde kutular hâlâ oturmamışsa ikisini birden dolduruyor; kayıtta varyant
  yoksa `"1"`. **Kaydın okunamaması sessiz:** kutular boş kalıyor — kaybedilen yalnız bir ön doldurma,
  ve ölü bir sunucuyu basış zaten söylüyor *(yazma burada düşer)*.
- **Basış**, Referanstan'dan: önce `saveReferenceSettings(project, { prompts, variants })`, ardından
  `onQueue`. Yazma düşerse `onQueue` çağrılmıyor ve cümlesi kırmızı kartta *(`refused`)*. `onQueue`'nun
  kendi hataları bugünkü gibi kancada *(`useGeneration.queueLayer` yakalıyor ve `null` dönüyor)*.

## Yeni SidePanel testinin kırmızısı

Test turunda yeni SidePanel testi beklenen *"Kareden yok"* yerine `handleAdd`'de bir `TypeError`'la
düştü. Bu turun sonunda yeşile dönmesi o kırmızının sekmelerin yokluğundan geldiğini gösterir;
dönmezse sebebi ayrıca aranır.

## Test turunda atlanan bir değişen test

`LayerPanel.test.jsx` — `keeps only the blocks the design leaves standing` Kareden'in bloklarını
`Üretim` satırıyla sayıyordu; bu maddenin kaldırdığı satır o. Test turu onu *Değişen*'e yazmamıştı,
ve kod yazılınca düştü. Soru aynı kalıyor, cevap yeni diziliş: Model, Kapsam, Üretim modu, Varyant.
Susturma değil — test hâlâ blokları sayıyor, ve bu commit'te değişiyor çünkü kırmızısı kodun değil
eski dizilişin kırmızısıydı.

**Yeni SidePanel testi yeşile döndü**, yani test turundaki `TypeError` kırmızısı sekmelerin
yokluğundan geliyordu.

## Dist

`npm run build --prefix queen-editor/frontend`; `dist/` kodla aynı commit'te.

## Bitti sayılır

Dört test satırı yeşil; kod, dist, bu spec ve planı tek commit.
