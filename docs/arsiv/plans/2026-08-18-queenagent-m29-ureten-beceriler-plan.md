# Madde 29 — Üreten üç beceri · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m29-ureten-beceriler-design.md](../specs/2026-08-18-queenagent-m29-ureten-beceriler-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

Yalnız arka uç: **bir tur**, önce testler (kırmızı), sonra uygulama.

---

## Adım 1 — Testler (kırmızı commit)

### yeni `test_skills.py` — metinlerin kendisi

- Üç kimlik tanınır ve metinleri boş değil; tanınmayan kimlik **boş dize** döner.
- Senaryo yönergesi `scenario.md`'yi, **10-15** cümleyi ve kullanıcının dilini söyler.
- Karakter ve kare yönergeleri **dosya yazmamayı** açıkça söyler.
- Karakter yönergesi kalite/skor etiketini dışarıda bırakır ve **birden çok aday** ister.
- Kare yönergesi hem kare sayısını **kullanıcıyla** kararlaştırmayı hem **küçük partileri** söyler.
- Kimlikler ön uçtaki kimliklerle aynı yazılır *(`skills.js`'in üç kimliği elle sabitlenir —
  arka uç JS'i okuyamaz, bu yüzden eşleşme testte yazılı durur)*.

### `test_stream_answer.py` — talimat nereye konuyor

- Beceriyle gönderilen mesajın **hemen önünde** `system` rolüyle metni durur.
- Aynı beceriyle ikinci mesaj metni **tekrarlamaz**.
- Beceri değişince yenisi bir kez girer.
- Bırakılıp geri dönülen beceri **yeniden** girer.
- Becerisiz sohbette hiçbir `system` mesajı yok.
- Tanınmayan kimlik hiçbir şey eklemez ve akış çalışır.
- Model cevapları araya girse de talimat tekrarlanmaz *(cevaplar beceri taşımaz)*.
- Talimat **sohbet kaydına yazılmaz**.

---

## Adım 2 — Uygulama

yeni `domain/skills.py` (üç metin + `instruction_for`) · `domain/usecases/stream_answer.py`
(konuşmayı kurarken araya koyma).

---

## Kapanış denetimi

- `prompt.py` değişmedi.
- `data/`, `presentation/` ve ön uçta değişiklik yok.
- Üç metin de "şunu yap" değil "bu işi şöyle yaparsın" kipinde.

## Risk

Metinlerin modele gerçekten uyup uymadığı testlerle değil Madde 35'in elle turunda görülür.
