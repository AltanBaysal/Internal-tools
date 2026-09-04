# Madde 8 — Renkler · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 8](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynaklar:** fark 74, 75 · **karar 2, 9** · `HANDOFF.md` §6, §10
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 0 · Açık soru yok; iki küçük nokta gerekçesiyle karara bağlanıyor

Fark 74'ün çelişkisini **karar 2** çözdü (`#B23A2E` kazandı), fark 75 zaten tek okumalı, **karar 9**
projenin rengini kaldırdı. Sorulacak bir şey kalmıyor. İki nokta tasarımda yazılı değil, ikisi de
mevcut kuraldan türetiliyor:

**1. Noktanın tek tonu ne olacak?** Kullanıcı "mürekkep ya da soluk gri" dedi, ikisini de kabul
etti. **Seçilen: `--muted`.** Gerekçe görsel dilin kendi kuralı — nokta bir işaret, bir eylem değil;
mürekkep tonu onu satırın adıyla eşit ağırlığa çıkarır ve gözü adın önüne çeker.

**2. Yıkıcı renk bugün nereye uygulanacak?** Tasarımın saydığı üç yıkıcı yüzey (proje başlığındaki
Delete, ⋯ menüsündeki satır, onay kutusunun dolu düğmesi) **henüz yok** — Madde 17, 18 ve 19'da
geliyorlar. Bugün var olan tek yıkıcı denetim satırlardaki `×`. **Onun hover rengi yıkıcı aileye
geçer**; aile geri kalanıyla birlikte değişkenlerde bekler.

**Hata metinleri yıkıcı aileye geçmez.** `.failure__*` ve `.empty__error` bugün `#8a5237` kullanıyor;
bir hata bir yıkıcı eylem değildir, sunucunun söylediğini aktaran bir cümledir. Hata dilinin kendi
maddesi var (**Madde 16**) ve renkleri orada karara bağlanır.

---

## 1 · Palet

`shared/app.css`'in `:root` bloğu, ve yalnız orası:

| Değişken | Değer | Ne işaretler |
|---|---|---|
| `--accent` | `#b5623c` | birincil eylem, ve yalnız o |
| `--accent-hover` | `#9e5232` | **dolu** vurgu yüzeylerinin üstüne gelme hâli |
| `--accent-link-hover` | `#8f4a2c` | vurgu renginde **yazı**nın üstüne gelme hâli |
| `--destructive` | `#b23a2e` | yıkıcı eylem |
| `--destructive-hover` | `#973026` | yıkıcı yüzeyin üstüne gelme hâli |
| `--destructive-line` | `#ebcfc9` | yıkıcı çerçeve |
| `--destructive-soft` | `#fdf4f2` | yumuşak yıkıcı zemin |

**`--accent-strong` ikiye ayrılıyor ve adı kalmıyor.** Bugün tek bir değişken hem dolu düğmelerin
hem bağlantıların hover'ını veriyor; fark 75 ikisini ayırıyor. Ayrılan iki şeyin eski adı ikisinden
birine kalırsa hangisi olduğu okunmaz — o yüzden ikisi de yeni adla yazılıyor.

Dolu vurgu yüzeyleri (`--accent-hover` alanlar): `.sidebar__new-chat`, `.empty__action`,
`.composer__send--ready`.
Vurgu renginde yazı (`--accent-link-hover` alanlar): `a`, `.strip__undo`.

---

## 2 · Projenin rengi gider

`hue` bir veri alanıydı; `desc` gibi kökten sökülüyor.

| Yer | Ne olur |
|---|---|
| `domain/project.py` | `hue: int` gider |
| `domain/usecases/create_project.py` | `HUE_STEP` ve renk üretimi gider |
| `data/file_project_store.py` | `raw["hue"]` ve yazılan `"hue"` gider |
| `presentation/routes.py` | `_project_json`'daki `"hue"` gider |
| `ProjectDot.jsx` | **silinir** |
| `Sidebar.jsx` | yerine `<span className="dot" />` |
| `workspace.css` | `.dot` ölçüsünü ve tek tonunu kendi kuralında taşır |

**`ProjectDot` neden kalmıyor:** bileşenin tamamı renk formülüydü. Formül gidince geriye tek bir
`<span>` kalıyor ve onu bir dosya arkasında saklamak, okuyanı boş yere bir dosya daha açmaya
zorluyor. Ölçü ve renk artık satır içi stil değil, `.dot` kuralı — bileşenin kendi rengini yazmaması
CODE-STANDARD'ın kuralı.

**Göç yok.** İçinde `hue` olan eski `project.json` okunur, alan sorulmadığı için sessizce düşer —
Madde 4'teki `desc` ile aynı.

**Belge düzeltmesi:** `CODE-STANDARD.md`'nin artifact tablosu `project.json` için *"what is this
project called and how does it look"* diyor. Renk gidince "nasıl göründüğü" diye bir cevap kalmıyor;
satır düzeltilir.

---

## 3 · Katman denetimi

Bir alan domain'den, bir anahtar şemadan, bir anahtar cevaptan, bir bileşen ön yüzden çıkıyor. Yeni
bağ yok, yön değişmiyor, üç yasak zorlanmıyor. Renklerin tek evi `shared/app.css` olmaya devam
ediyor: bu maddede hiçbir bileşen kendi rengini yazmıyor, tersine yazdığı tek renk (noktanınki)
oradan geliyor.

---

## 4 · Kabul ölçütü

1. `shared/app.css` yıkıcı ailenin dördünü de tanımlar.
2. Dolu vurgu hover'ı ile bağlantı hover'ı **farklı** değişkenlerdir ve `--accent-strong` diye bir
   değişken kalmaz.
3. Satırlardaki `×` hover'da yıkıcı renge döner.
4. `Project` alanları arasında `hue` yoktur; `project.json` yalnız `name` ve `createdAt` taşır;
   API cevaplarında `hue` anahtarı yoktur.
5. İçinde `hue` olan eski bir `project.json` hatasız okunur.
6. Kenar çubuğundaki noktaların hiçbiri satır içi renk taşımaz; hepsi aynı tondadır.

## 5 · Risk

Palet testinin de Madde 7'deki gibi bir **kilit testi** olması: jsdom stil dosyasını yüklemiyor, bu
yüzden değişkenlerin varlığı ve değerleri dosyadan okunarak doğrulanıyor. Ne kanıtladığı testin
başında yazıyor; gerçek doğrulama Madde 35.
