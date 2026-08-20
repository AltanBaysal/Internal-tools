# Madde 62 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-20-queenagent-m62-test-design.md](../specs/2026-08-20-queenagent-m62-test-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adımlar

### 1. `backend/tests/test_config.py` — iki test eklenir

Anahtarın ortamdan geldiği ve yokken **boş** olduğu. İkisi de `importlib.reload` ile soruluyor:
önemli olan modülün kaynağında ne yazdığı değil, uygulamanın elinde kalan değer. Her test kendi
`finally`'sinde ortamı geri alıp modülü yeniden yükler — yoksa değiştirilmiş bir `config` bütün
takımın altında kalır.

### 2. `backend/tests/test_composition.py` — yeni dosya, üç test

`main.py`'nin **kaynağı okunarak** soruluyor. Gerekçesi: birleştirme kökü içeriği tamamen bağlantı
olan tek dosya, ve "neyi neye bağladı" sorusunun başka yolu yok — modülü import etmek gerçek bir
uygulama kurar ve kullanıcının asıl veri köküne dokunur. Bir dosyanın ne dediğini okumak bu depoda
zaten var: `test_notebook.py` baştan sona bunu yapıyor.

Üç soru: anahtar `config.XAI_API_KEY`'den mi alınıyor; `features.settings` hâlâ bağlanıyor mu;
`backend/features/settings` klasörü duruyor mu.

### 3. `backend/tests/test_notebook.py` — bir test yerine dört, artı bir kilit

`test_the_xai_key_is_not_asked_for_here` **silinir** — söylediği şeyin tam tersi karar verildi.
Yerine:

| Test | Ne soruyor |
|---|---|
| `test_the_xai_key_comes_from_secrets` | `userdata.get("XAI_API_KEY")` var mı |
| `test_a_missing_xai_key_says_what_to_do` | `assert XAI_API_KEY` hücresi Secrets'ı ve adı anıyor mu |
| `test_the_xai_key_travels_to_the_app_in_the_environment` | Serve hücresi `env` içine koyuyor mu |
| `test_the_notebook_no_longer_points_at_a_settings_screen` | Defterde "Settings" geçiyor mu |

### 4. `frontend/src/shared/useRoute.test.js` — bir test tersine döner

`/settings is a place of its own` → `/settings is no longer a place`. Beklenen: yakalanmayan her
adresin düştüğü yer, yani `view: "root"`.

### 5. `frontend/src/features/workspace/Sidebar.test.jsx` — bir test eklenir

Settings satırının olmadığı. Eski iki test (satır var; proje seçilmeden de var) **bu turda
kalır** — dosya kendi kendisiyle çelişir, ki kırmızı commit'in tanımı bu.

### 6. `frontend/src/features/workspace/ChatScreen.test.jsx` — bir test eklenir

Hata kartının, **eski bayraklar verilse bile** Settings düğmesi çizmediği. Ölü prop'ları bilerek
geçiriyor: testin konusu tam olarak "ne verilirse verilsin" olduğu için, eski davranışın gittiğini
ancak eski girdiyle kanıtlayabilir. İkinci turdan sonra da bir nöbetçi olarak kalır — dalı geri
ekleyen biri bunu düşürür.

### 7. `frontend/src/App.test.jsx` — iki test eklenir

`/settings` adresinin çatala düşüp projeye indiği (tasarımdaki tuzağın testi), ve uygulamanın
sunucuya hiç `/api/settings` sormadığı.

## Beklenen kırmızı

**On dört test.** Backend dokuz: config iki, composition üç, defter dört. Arayüz beş: useRoute bir,
Sidebar bir, ChatScreen bir, App iki.

**Bir tanesi kırmızıya dönmeyecek, ve bu bilerek:** `test_the_xai_key_is_never_printed`. Defterde
bugün `XAI_API_KEY` diye bir dizge hiç geçmiyor, dolayısıyla "hiçbir print satırı onu taşımıyor"
iddiası doğuştan yeşil. Bu bir test değil, **kilit** — Madde 55 ve 56'da olduğu gibi: saf bir yokluk
iddiası, dayandığı şey var olmadığı sürece düşemez. Değeri geleceğe dönük; klon URL'sini basmayı
yasaklayan testin kardeşi. Kilit olduğu burada yazılıyor ki sonradan "test yazıldı" diye okunmasın.

Takımın toplam sayıları koşudan **sonra** kaydedilir. Bu planın önceki sürümlerinde tahmin edilen
toplamlar beş kez tutmadı; tahmin edilebilir olan yeni testlerin sayısı, takımın tamamı değil.

## Bu turda yapılmayan

Hiçbir üretim kodu, hiçbir belge, defterin kendisi. Silinecek olan hiçbir eski test — `test_settings.py`,
`test_settings_api.py`, `SettingsScreen.test.jsx`, `useSettings.test.jsx` ve App/Sidebar/ChatScreen
içindeki eski Settings testleri yerinde durur ve yeşil kalır. Anlattıkları kod hâlâ orada; ikinci
turda onunla birlikte giderler.
