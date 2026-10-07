# Madde 4 — Proje açıklaması gider · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m4-aciklama-design.md](../specs/2026-08-17-queenagent-m4-aciklama-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra implementasyon.

---

## Adım 1 — Testler (kırmızı commit)

### 1.1 · Arka uç

**`test_project_usecases.py`**

- `test_new_project_is_born_with_the_default_name_and_description` → **yeniden yazılır**:
  `test_new_project_is_born_with_the_default_name`, `NEW_PROJECT_DESC` importu gider.
- Kurulum yardımcısındaki `Project(..., desc="", ...)` çağrısından alan çıkar.
- *(yeni)* `test_a_project_carries_no_description`: `Project`'in alanları arasında `desc` yok
  (`dataclasses.fields`).

**`test_edit_project.py`**

- `test_sending_only_a_description_leaves_the_name_alone` → **silinir**.
- `test_sending_only_a_name_leaves_the_description_alone` → **yeniden yazılır**: ad değişince
  `hue` ve `createdAt` yerinde kalır.
- Boşluk kırpma testi yalnız ada bakar.
- *(yeni)* `test_a_description_is_not_something_a_project_can_be_given`: `edit_project(..., desc=...)`
  `TypeError` verir.

**`test_file_project_store.py`**

- Kurulumdan `desc="Notes."` çıkar.
- *(yeni)* `test_the_written_file_holds_no_description`: yazılan `project.json`'ın anahtarları
  tam olarak `name`, `hue`, `createdAt`.
- *(yeni)* `test_an_old_file_with_a_description_is_read_without_complaint`: elle `desc` içeren bir
  `project.json` yazılır, `list_all()` onu sorunsuz okur.

**`test_projects_api.py`**

- `desc` gönderen `PATCH` testi → **yeniden yazılır**: gövdede `desc` gelse bile 200 döner ve cevapta
  `desc` anahtarı yoktur.
- *(yeni)* `test_the_answer_carries_no_description`: `POST /api/projects` cevabının anahtarları
  arasında `desc` yok.

### 1.2 · Ön yüz

**`ProjectScreen.test.jsx`**

- `the title, the description and both column headings are drawn` → başlık ve iki sütun başlığına
  bakar, açıklamaya bakmaz.
- `clicking the description asks to change it` → **yeniden yazılır**:
  `the screen carries no description to click` — `PROJECT.desc` verilse bile ekranda çizilmez.
- Kurulumdaki `desc` alanı kalabilir (sunucudan gelmeyen bir alanın çizilmediğini göstermek için
  bilerek bırakılır) — testin adı bunu söyler.

**`App.test.jsx`** — `PROJECT` ve `stubProjects` kurulumlarındaki `desc` alanları gider; hiçbir test
açıklamaya bakmıyor, dolayısıyla kırmızı beklenmiyor.

**Ölçülen kırmızı: arka uçta 22, ön yüzde 1.**

Tahmin 5–7'ydi, çıkan 22. Fark yeni iddiadan değil, **kurulumdan** geliyor: dört test dosyasının
`Project(...)` yardımcılarından `desc` çıkarıldığı an, o yardımcıyı kullanan her test
`TypeError: missing 1 required positional argument: 'desc'` ile düşüyor. Yani asıl yeni iddia 6
tane; kalan 16'sı alanın hâlâ zorunlu olduğunun aynı kanıtı. Alan gidince hepsi birden yeşile
döner — dönmezse, gerçekten kırılan bir şey var demektir.

---

## Adım 2 — Implementasyon

### 2.1 · Arka uç

1. `domain/project.py`: `desc: str` alanı gider.
2. `domain/usecases/create_project.py`: `NEW_PROJECT_DESC` ve `desc=` gider.
3. `domain/usecases/edit_project.py`: `desc` parametresi ve dalı gider; docstring'i "kısmi
   güncelleme" olarak doğru kalır.
4. `data/file_project_store.py`: `desc=raw["desc"]` ve yazılan sözlükteki `"desc"` gider.
5. `presentation/routes.py`: `PATCH`'in `desc=` satırı ve `_project_json`'daki `"desc"` gider.

### 2.2 · Ön yüz

6. `ProjectScreen.jsx`: `screen__desc` paragrafı ve `onDescribe` prop'u gider.
7. `App.jsx`: `onDescribe` satırı gider. `ask` yalnız adı sorduğu için `field` parametresi
   gereksizleşir — sadeleştirilir.
8. `workspace.css`: `.screen__desc` kuralı gider.

### 2.3 · Belgeler

9. `CODE-STANDARD.md`: *"The counts on a project card are a directory count."* → kart Madde 3'te
   silindi; cümle kenar çubuğu satırını anacak şekilde düzeltilir.

### 2.4 · Kapanış denetimi

- Bağımlılık yönü: yeni bağ yok, katman değişmedi.
- Ölü kod: `NEW_PROJECT_DESC`, `.screen__desc`, `onDescribe`, `ask`'ın `field` parametresi — hepsi
  aynı maddede gider.
- `grep desc` ile kalan tek geçerli kullanım `tools.py`'deki xAI şema `description`'ları olmalı.

---

## Risk

`Project` dataclass'ından alan çıkması, konumsal kurulan her `Project(...)` çağrısını kaydırır.
Testler anahtar sözcük kullanıyor ama üretim kodundaki iki çağrı (`create_project`,
`file_project_store.list_all`) yerinde denetlenir.
