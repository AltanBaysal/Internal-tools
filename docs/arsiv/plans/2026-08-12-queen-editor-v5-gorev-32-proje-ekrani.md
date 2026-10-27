# Görev 32 — Proje ekranı ve silme davranışı · Uygulama planı

> **Ajanlar için:** GEREKLİ ALT BECERİ: bu planı superpowers:executing-plans ile görev görev uygula.

**Amaç:** Proje silmeyi söylediği şeyi yapan bir eyleme çevirmek, kart butonunu ve çıkış davranışını
tasarıma getirmek.

**Mimari:** Yeni bir foto üretimi kullanım durumu (`halt_project`) koşuyu durdurur; `delete_project`
onu bir **port** olarak alır, iki özellik yalnız `main.py`'de buluşur.

**Tasarım:** [spec](../specs/2026-08-12-queen-editor-v5-gorev-32-proje-ekrani-design.md)

## Genel kısıtlar

- Arayüz metni **Türkçe**, kod/yorum/test **İngilizce**.
- `feature ↛ feature`: projeler özelliği koşucuyu import etmez.
- Bekleme sınırı **5 sn**, adım **0.1 sn**; `sleep` dışarıdan verilir.
- Testler: `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend -- --run`.
- Ön yüz değiştiği için commit'te `dist/` yeniden üretilir.

---

### Task 1: Koşuyu durduran kullanım durumu

**Dosyalar:**
- Oluştur: `queen-editor/backend/features/photo_generation/domain/usecases/halt_project.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

**Arayüz:**
- Üretir: `halt_project(runner, interrupt, sleep, project) -> bool` — koşu bu projeye aitse
  durdurup `True`, değilse dokunmadan `False` döner.

- [ ] **Adım 1: Düşen testleri yaz** — dört durum: bu projenin koşusu durur (stop istendi,
      interrupt çağrıldı, reset edildi); başka projenin koşusuna dokunulmaz; patlayan interrupt
      yutulur; çıkmayan işçide süre dolar ve yine döner.
- [ ] **Adım 2: Koş, düştüklerini gör**
- [ ] **Adım 3: Kullanım durumunu yaz**

```python
LIMIT = 50      # 5 seconds in tenths: an interrupted render lands well inside this
STEP = 0.1


def halt_project(runner, interrupt, sleep, project):
    if runner.status().get("project") != project:
        return False
    if runner.status().get("status") == "running":
        runner.request_stop()
        try:
            interrupt()
        except Exception:
            pass
        for _ in range(LIMIT):
            if runner.status().get("status") != "running":
                break
            sleep(STEP)
    runner.reset()
    return True
```

- [ ] **Adım 4: Koş, geçtiklerini gör**

---

### Task 2: Silme önce durdurur

**Dosyalar:**
- Değiştir: `queen-editor/backend/features/projects/domain/usecases/delete_project.py`,
  `queen-editor/backend/main.py`
- Test: `queen-editor/backend/tests/test_project_usecases.py`, `test_project_routes.py`

**Arayüz:**
- Tüketir: `halt(project)` portu. Üretir: `delete_project(store, halt, name)`.

- [ ] **Adım 1: Düşen testleri yaz** — durdurma silmeden önce çağrılır (sıra kaydeden bir sahte
      ile); olmayan projede yine `ProjectMissing`; rota testinde `DELETE` durdurmayı tetikler.
- [ ] **Adım 2: Koş, düştüklerini gör**
- [ ] **Adım 3: Kullanım durumunu ve bağlamayı yaz** — `main.py`'de
      `partial(halt_project, _photo_runner, _comfy_client.interrupt, time.sleep)`
- [ ] **Adım 4: Koş, geçtiklerini gör**

---

### Task 3: Onay metni ve çerçevesiz çöp butonu

**Dosyalar:**
- Değiştir: `features/projects/ProjectsScreen.jsx`, `features/projects/ProjectCard.jsx`
- Test: `ProjectsScreen.test.jsx`, yeni `ProjectCard.test.jsx`

- [ ] **Adım 1: Düşen testleri yaz** — onay metni birebir; butonda `border: none`,
      `background: none`, renk `--danger`.
- [ ] **Adım 2: Koş, düştüklerini gör**
- [ ] **Adım 3: Metni ve stili yaz**
- [ ] **Adım 4: Koş, geçtiklerini gör**

---

### Task 4: Çıkış onayı yerine bilgi balonu

**Dosyalar:**
- Değiştir: `features/photo_generation/ProjectScreen.jsx`
- Test: `ProjectScreen.test.jsx`

- [ ] **Adım 1: Düşen testleri yaz** — "Projeden çık" onaysız `navigate("/")`; üretim akarken
      hover balonu açar, ayrılınca kapatır; boş ve duraklamış kuyrukta balon yok.
- [ ] **Adım 2: Koş, düştüklerini gör**
- [ ] **Adım 3: Onayı kaldır, balonu yaz** — 300px, `qe-dot qe-dot--alive` + iki satır; buton ve
      balon birlikte konumlanabilsin diye buton `position: relative` bir kabuğa girer.
- [ ] **Adım 4: Koş, geçtiklerini gör**

---

### Task 5: Tam takım ve commit

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] Commit (spec, plan, kaynak ve `dist/` aynı commit'te)
