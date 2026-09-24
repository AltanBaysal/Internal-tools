# Madde 317 — Video panelinin iki sekmesi, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Kararlar maddede: iki sekme, Kareden değişmiyor, Referanstan'ın prompt
listesi ve varyantı fotoğraf panelinin mantığıyla tutuluyor *(kullanıcı, 24 Eylül — "fotoğraf
promttaki mantığın aynısı olsun"; varyant için "1")*.

## Bugün ne oluyor

Video paneli tek form; ortasındaki `Üretim` satırı *(`Karelerden` · `Referanstan`)* formun geri
kalanını değiştiriyor ([LayerPanel.jsx](../../../queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx)).
Referanstan'ın kutusu `Promptlar` başlığını taşıyor. Panelin durumu bileşenin içinde: panel her
açılışta, ve bir kareye girip çıkınca, sıfırdan kuruluyor — yazılan prompt listesi gidiyor.
Tek bir varyant kutusu iki form arasında paylaşılıyor.

Fotoğraf panelinin mantığı *(GeneratePanel.jsx — `REMEMBERED`, `opening`)*: taslak bellekte, proje
başına; bir taslak yoksa kutular projenin kaydından doluyor; kayıt `Kuyruğa ekle`'ye basınca yazılıyor
*(ProjectScreen.handleGenerate)* ve yazılamazsa iş gönderilmiyor.

## Kurallar

1. **Video panelinin tepesinde iki sekme:** `Kareden` · `Referanstan` — `.wf-segment` içinde iki düğme,
   seçili olan `is-on`. `Üretim` satırı ve `Karelerden` sözcüğü yok. Ses panelinde sekme yok.
2. **Panel her kuruluşta Kareden'de açılıyor.**
3. **Kareden'in dizilişi bugünkü:** Model, Kapsam, Üretim modu, Varyant. **Referanstan'ın:** Model,
   Referanslar, Prompt listesi, Varyant. Başlıklar `data-label` taşıyor; sıraları bu. `Referanslar`
   bloğunun düğmesi 318'in, bu maddede başlık yalnız yerini tutuyor.
4. **Referanstan'ın kendi varyantı var.** Kareden'in varyantı bugünkü gibi her kuruluşta 1; Referanstan'ın
   varyantı tutuluyor. *(Karar: madde Kareden'i "değişmeden" diyor ve tutulmasını yalnız Referanstan
   için istiyor; tek kutu paylaşılsa Kareden'in varyantı da tutulurdu.)*
5. **Referanstan'ın taslağı proje başına bellekte:** sekme değişince ve panel yeniden kurulunca
   duruyor. Taslak varsa kayda sorulmuyor.
6. **Taslak yoksa, Referanstan ilk açılınca proje kaydı soruluyor** ve kutuları dolduruyor; kayıtta
   varyant yoksa 1. **Kayıt yoldayken kutular bekletilmiyor**, ve kayıt geldiğinde o ana kadar
   yazılmış bir şeyin üstüne yazmıyor.
7. **Basış gidince kayıt önce yazılıyor:** `saveReferenceSettings(project, { prompts, variants })`,
   `variants` sayı; ardından `onQueue`. **Yazılamazsa iş gönderilmiyor** ve sunucunun cümlesi
   cevap yuvasında. Kareden'in basışı bu kaydı yazmıyor.
8. **Kayıt sunucuda, kendi dosyasında:** `reference_settings.json` — `{"prompts": str, "variants":
   int | null}`. Fotoğraf panelinin `settings.json`'u başka bir anda yazılıyor, o yüzden ayrı dosya
   *(CODE-STANDARD, Separation of concerns)*. Okunamayan dosya ve yanlış tipli alan boş okunuyor, tıpkı
   `settings.json` gibi. Kapı: `GET` / `PUT /api/projects/<proje>/reference-settings`; bilinmeyen
   proje 404, `PUT` proje yaratmıyor, yanlış tipler boşa çevriliyor.

## Adlar *(uygulama turu bunlara uyar)*

- Sunucu: `backend/features/projects/data/reference_settings_store.py` — `DriveReferenceSettingsStore`
  *(`project_exists`, `read`, `write`)*; `backend/features/projects/domain/usecases/save_reference_settings.py`
  — `save_reference_settings(store, project, prompts, variants)`; okuma `get_settings(store, project)`
  ile, yeni kullanım durumu yok; `backend/features/projects/presentation/reference_settings_routes.py`
  — `make_reference_settings_blueprint(get_reference_settings, save_reference_settings)`.
- Ekran: `api.js` — `getReferenceSettings(project)`, `saveReferenceSettings(project, { prompts,
  variants })`; `LayerPanel`'e `project` geliyor.

## Yazılacak testler

### `backend/tests/test_reference_settings.py` — yeni dosya

Yeni modüller testlerin içinde import ediliyor: dosya bu turda yok, ve dosya düzeyinde bir import
toplama hatasıyla bütün koşuyu durdururdu.

1. **Hiç yazılmamış kayıt boş okunuyor** — `{"prompts": "", "variants": None}`.
2. **Yazılan geri okunuyor, metin yazıldığı gibi** — satır sonları ve sondaki virgül dahil.
3. **Okunamayan dosya ve yanlış tipler boş okunuyor.**
4. **Kayıt kendi dosyasında** — yazınca `reference_settings.json` var, `settings.json` yok; fotoğraf
   kaydı boş okunuyor.
5. **`save_reference_settings` verileni yazıyor.**
6. **`save_reference_settings` olmayan projeyi reddediyor** — `Proje yok: yok`, hiçbir şey yazılmıyor.
7. **Kapı: yeni proje boş cevap veriyor.**
8. **Kapı: `PUT` 204, ardından `GET` aynısını veriyor.**
9. **Kapı: bilinmeyen proje 404, `GET` de `PUT` da.**
10. **Kapı: `PUT` proje yaratmıyor.**
11. **Kapı: yanlış tipler boşa çevriliyor** — `variants` için `True` ve `"4"` dahil.

### `backend/tests/test_composition_root.py`

12. **`main.py` kapıyı bağlıyor** — iki video modelinde de ana uygulama
    `/api/projects/m317-yok/reference-settings`'e 404 ve `{"error": "Proje yok: m317-yok"}` diyor.

### `frontend/src/shared/api.test.js`

13. **Kayıt projenin kendi adresinde okunup yazılıyor** — `GET` ve `PUT`
    `/api/projects/<kodlanmış ad>/reference-settings`, gövde `{ prompts, variants }`.

### `frontend/src/features/photo_generation/LayerPanel.test.jsx`

`api.js`'in iki yeni fonksiyonu sahte *(`vi.mock`, geri kalanı gerçek)*; kayıt varsayılan olarak boş,
yazma başarılı. Taslak modülde, proje başına tutulduğu için **her render kendi proje adını alıyor** —
yoksa bir testin yazdığı ötekinin panelinde açılırdı.

*Sekmeler:*

14. **Video paneli Kareden'de açılıyor ve kare formunu gösteriyor** — Kareden `is-on`, Referanstan
    değil; başlıklar Model, Kapsam, Üretim modu, Varyant; `Üretim` ve `Karelerden` yok.
15. **Referanstan tasarımın sırasıyla diziliyor** — Model, Referanslar, Prompt listesi, Varyant;
    Referanstan `is-on`.
16. **Ses panelinde sekme yok.** *(Bekçi: bugün de yeşil — ses panelinin bir `Üretim` satırı hiç
    olmadı; bu test sekmeler geldikten sonra da öyle kalmasını tutuyor.)*

*Referanstan'ın tuttukları:*

17. **Prompt listesi ve varyantı sekmeler arasında duruyor; Kareden'in varyantı kendi 1'inde.**
18. **Panel yeniden kurulunca da duruyor, ve panel Kareden'de açılıyor** — kayda ikinci kez
    sorulmuyor.
19. **Taslak yokken kutular proje kaydından doluyor.**
20. **Kayıtta varyant yoksa Referanstan 1'den açılıyor** — kayda sorulmuş olarak.
21. **Yolda olan kayıt yazılanın üstüne yazmıyor** — kayda sorulmuş olarak.
22. **Basınca kayıt önce yazılıyor, ardından iş gidiyor** — `saveReferenceSettings(proje, { prompts,
    variants: 3 })`, `onQueue`'dan önce; Kareden'in basışı kaydı yazmıyor.
23. **Kayıt yazılamazsa iş gitmiyor** — sunucunun cümlesi ekranda.

### `frontend/src/features/photo_generation/SidePanel.test.jsx`

24. **Raydan yeniden açılan video paneli Kareden'de, Referanstan'a yazılan duruyor** — `fetch`
    sahte; panel raydan kapanıp açılıyor.

**Değişen:**

- `LayerPanel.test.jsx` — `asks the video panel where the video comes from, and never the sound
  panel`: `Karelerden` artık `Kareden`.
- `SidePanel.test.jsx` — `passes the reference prompt list through to the queue` *(325)*: basış artık
  kaydı önce yazıyor, o yüzden `fetch` sahte; kaydın yazılması başarılı.

**Bekçiler, bugün de yeşil:** LayerPanel'in kapsam, varyant, mod ve ses testleri — Kareden
değişmiyor; referans bloğunun öteki testleri — sayım ve gönderim; `test_projects_routes.py`'ın
`settings` testleri — fotoğraf kaydı değişmiyor.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest'te 1–12 kırmızı; `queen-editor/frontend` vitest'te
13–15, 17–24 ve `Karelerden`'i `Kareden`'e çeviren test kırmızı — 16 ve 325'in testi yeşil *(325'in
sahte `fetch`'i bu turda henüz kullanılmıyor)*; `queen-agent` satırları yeşil.
