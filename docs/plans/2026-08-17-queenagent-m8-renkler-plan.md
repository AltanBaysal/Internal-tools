# Madde 8 — Renkler · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m8-renkler-design.md](../specs/2026-08-17-queenagent-m8-renkler-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra implementasyon.

---

## Adım 1 — Testler (kırmızı commit)

### 1.1 · Arka uç — renk alanı gider

- **`test_project_usecases.py`**: `test_hue_steps_with_the_number_of_existing_projects` ve
  `test_hue_wraps_around_the_colour_wheel` **silinir**; `test_a_project_carries_no_description`
  yanına `test_a_project_carries_no_colour` gelir. Yardımcıdan `hue=0` çıkar.
- **`test_projects_api.py`**: `test_two_projects_get_different_ids_and_hues` →
  `test_two_projects_get_different_ids`; cevap anahtar kümesinden `hue` çıkar.
- **`test_file_project_store.py`**: yardımcıdan `hue=94` çıkar; yazılan dosyanın anahtarları
  `{"name", "createdAt"}` olur; eski dosya testi `hue`'yu da yok sayılan alanlar arasına alır.
- **`test_edit_project.py`**: yardımcıdan `hue=94` çıkar;
  `test_the_hue_and_the_creation_time_are_never_touched` → yalnız oluşturma zamanına bakar.

### 1.2 · Ön yüz

**Yeni: `shared/app.css.test.js`** — Madde 7'deki gibi bir **kilit testi**:
1. yıkıcı ailenin dört değişkeni ve değerleri,
2. `--accent-hover` ve `--accent-link-hover` ayrı ve farklı değerde,
3. `--accent-strong` diye bir değişken kalmamış,
4. dolu vurgu yüzeylerinin üçü `--accent-hover`, iki yazı yüzeyi `--accent-link-hover` kullanıyor,
5. `.row-x:hover` yıkıcı renge dönüyor.

*(4 ve 5 `workspace.css`'e bakar; okuma yardımcısı Madde 7'nin testindekiyle aynı biçimde kurulur.)*

**`Sidebar.test.jsx`** — *(yeni)* `every project dot is the same tone`: hiçbir noktada satır içi
`background` yok. Fixture'lardan `hue` çıkar.

**`App.test.jsx`, `ProjectScreen.test.jsx`** — fixture'lardan `hue` çıkar (kırmızı beklenmiyor).

**Ölçülen kırmızı: arka uçta 19, ön yüzde 7.**

Arka uçtaki sayı yine kurulumdan şişiyor — Madde 4'teki `desc` ile birebir aynı desen: `Project`
yardımcılarından `hue` çıkınca o yardımcıyı kullanan her test `TypeError` veriyor. Gerçek yeni iddia
5 tane. Alan gidince hepsi birden yeşile dönmeli.

Ön yüzdeki 7'nin 6'sı palet kilidi, 1'i noktanın satır içi rengi.

---

## Adım 2 — Implementasyon

1. `shared/app.css`: `--accent-strong` gider; `--accent-hover`, `--accent-link-hover` ve yıkıcı
   ailenin dördü gelir. `a:hover` yeni adı kullanır.
2. `workspace.css`: üç dolu yüzey `--accent-hover`, `.strip__undo:hover` `--accent-link-hover`,
   `.row-x:hover` `--destructive`. `.dot` kuralı ölçüyü ve tek tonu alır.
3. `ProjectDot.jsx` **silinir**; `Sidebar.jsx` `<span className="dot" />` çizer.
4. `domain/project.py`, `create_project.py`, `file_project_store.py`, `routes.py`: `hue` gider.
5. `CODE-STANDARD.md`: `project.json` satırı düzeltilir.

### Kapanış denetimi

- `grep hue` → yalnız "artık yok" testleri kalmalı.
- `grep accent-strong` → hiç kalmamalı.
- `grep "#8a5237"` → yalnız hata metinleri kalmalı (Madde 16'nın konusu).

---

## Risk

Fazla silmek: `#8a5237` hata metinlerinde de duruyor ve yıkıcı renge benziyor. Spec onu adıyla
koruyor, kapanış denetimi yokluyor.
