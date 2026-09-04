# Madde 4 — Proje açıklaması gider · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 4](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynaklar:** fark 20 (`öksüz` · davranış · **kesin**, Y1·Y2·Y3) · `HANDOFF.md` §11 "Deliberately removed"
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 0 · Açık soru yok

Fark 20 üç yolun üçünde de aynı çıkmış ve tasarım açıklamayı "geri getirmeyin" listesine adıyla
yazmış: *"Project descriptions (data field and UI)"*. Ne veri alanı ne arayüz kalıyor; iki farklı
okuma yok, dolayısıyla bu maddede kullanıcıya sorulacak bir şey yok.

**Veri göçü sorulmuyor, çünkü karar zaten verilmiş.** Madde 1'de kullanıcı eski verinin önemsiz test
verisi olduğunu söyledi ve göç yapılmadı; aynı karar burada da geçerli. Eski `project.json`
dosyalarındaki `desc` alanı **silinmez, okunmaz** — okuyan taraf onu artık hiç sormaz, ilk yazımda
kendiliğinden düşer.

---

## 1 · Ne gidiyor

### 1.1 · Arka uç

| Yer | Ne olur |
|---|---|
| `domain/project.py` | `Project.desc` alanı gider |
| `domain/usecases/create_project.py` | `NEW_PROJECT_DESC` sabiti ve `desc=` ataması gider |
| `domain/usecases/edit_project.py` | `desc` parametresi ve dalı gider |
| `data/file_project_store.py` | `raw["desc"]` okuması ve `"desc"` yazması gider |
| `presentation/routes.py` | `PATCH`'in `desc=payload.get("desc")` satırı ve `_project_json`'daki `"desc"` gider |

**`edit_project` adı kalıyor.** Geriye tek düzenlenebilir alan (`name`) kalsa da işlev hâlâ "projeyi
düzenle"dir ve uç nokta hâlâ kısmi güncelleme yapan bir `PATCH`'tir. Adı `rename_project` yapmak
Madde 5'in söktüğü sohbet/dosya yeniden adlandırmalarıyla karışırdı; yol haritası da böyle bir ad
değişikliği istemiyor.

**`raw["desc"]`in gitmesi eski dosyaları kırmaz:** `list_all` sözlüğü okuyup yalnız sorduğu anahtarları
alıyor, fazlası sessizce yok sayılıyor. Ters yön de doğru — alanı olmayan yeni bir `project.json`
eski koda verilseydi `KeyError` olurdu, ama geriye doğru okuyan kimse yok.

### 1.2 · Ön yüz

| Yer | Ne olur |
|---|---|
| `ProjectScreen.jsx` | `screen__desc` paragrafı ve `onDescribe` prop'u gider |
| `App.jsx` | `onDescribe={() => ask(...)}` gider; `ask` yalnız ada kalır |
| `workspace.css` | `.screen__desc` kuralı gider |

Kart ikinci satırı **Madde 3'te** ızgarayla birlikte zaten gitti; bu maddede yapılacak bir şeyi
kalmadı.

### 1.3 · Belgeler

`CODE-STANDARD.md`'de iki satır bugünü anlatmıyor:

- *"The counts on a project card are a directory count."* — kart Madde 3'te silindi; sayaç artık
  kenar çubuğu satırında duruyor.
- `project.json` tablosunun *"what is this project called and how does it look"* satırı doğru
  kalıyor: ad ve renk hâlâ orada.

---

## 2 · Ne kalıyor

- **Proje adı ve yeniden adlandırma** — tasarım ikisini de koruyor.
- **`hue`** — projeye bağlı renk. Kaldırılıp kaldırılmayacağı fark 5'in konusu ve **Madde 8**'e ait;
  burada dokunulmuyor.
- **`PATCH /api/projects/<id>`** — uç nokta duruyor, yalnız gövdesinde `desc` kabul etmiyor. Gövdede
  `desc` gelirse sessizce yok sayılır: bilinmeyen alan bir hata değil, `PATCH`'in tanımı gereği
  gönderilmemiş sayılır.

---

## 3 · Katman denetimi

Yeni dosya yok, yeni bağ yok. Değişen her dosya kendi katmanında kalıyor: `domain/` bir alan ve bir
dal kaybediyor, `data/` şemadan bir anahtar çıkarıyor, `presentation/` iki satır kaybediyor.
`presentation → domain ← data → services` yönü değişmiyor; `feature ↛ feature`, `service ↛ feature`,
`service ↛ service` yasakları bu maddede hiç zorlanmıyor.

**CODE-STANDARD'ın "no file repeats another's answer" kuralı bu maddeyle güçleniyor:** `project.json`
artık yalnız iki soruya cevap veriyor — proje ne ad taşıyor ve nasıl görünüyor.

---

## 4 · Kabul ölçütü

1. Yeni proje `desc` alanı olmadan doğar; `project.json` yalnız `name`, `hue`, `createdAt` taşır.
2. `GET /api/projects` ve `PATCH /api/projects/<id>` cevaplarında `desc` anahtarı yoktur.
3. `PATCH` gövdesine `desc` konursa 400 değil 200 döner ve hiçbir şey değişmez.
4. Proje ekranında başlık satırından sonra doğrudan composer gelir; tıklanabilir paragraf yoktur.
5. İçinde `desc` olan eski bir `project.json` okunduğunda hata olmaz, alan yok sayılır.

## 5 · Risk

Küçük. Tek dikkat noktası `Project` dataclass'ının alan sırası: `desc` çıkınca konumsal olarak
kurulan her `Project(...)` çağrısı kayar. Testlerdeki kurulumlar anahtar sözcükle yazılmış, yine de
her çağrı yerinde denetlenir.
