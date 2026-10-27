# Python bağımlılıkları dosyada durur · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-01-python-requirements-uygulama-design.md](../specs/2026-09-01-python-requirements-uygulama-design.md)
**Kırmızı commit:** `a52fca1`
**Bu tur test dosyalarına dokunmaz.**
**Test komutları (değişmez, dördü de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. `queen-editor/backend/requirements.txt` — bir satır eklenir.

```
flask>=3.0
pytest>=8.0
requests>=2.32
```

## B. `queen-agent/backend/requirements.txt` — yeni dosya.

```
flask>=3.0
pytest>=8.0
```

## C. Koşuldu: **dördü de yeşil**, ve sayılar öngörüldüğü gibi.

| Komut | Sonuç |
|---|---|
| `python -m pytest queen-agent -q` | **658 yeşil** *(656 + 2 bekçi)* |
| `python -m pytest queen-editor -q` | **720 yeşil** *(719 + 1 bekçi)* |
| `npm test --prefix queen-agent/frontend` | **568 yeşil** |
| `npm test --prefix queen-editor/frontend` | **584 yeşil** |

## D. Kurulum denendi, ve `pip` iki dosyayı da okudu.

```
python -m pip install -r queen-agent/backend/requirements.txt
python -m pip install -r queen-editor/backend/requirements.txt
```

Üç satırın üçü de **`Requirement already satisfied`**: `flask` 3.1.3, `pytest` 9.1.1, ve
queen-editor'de `requests` 2.34.2 — yani `>=2.32` tabanı karşılanıyor.

Maddenin gerçek iddiası buydu, ve testlerin ölçemediği yer burası: testler dosyanın *içeriğini*
ölçüyor, bu adım `pip`'in onu *okuyabildiğini*. 31 Ağustos'ta bu komut queen-agent için hiç yoktu ve
queen-editor için eksik bir ortam bırakıyordu.

## E. Yeşil commit.

## Bilerek yapılmayanlar

`torch` ve arkadaşları hiçbir dosyaya girmez. Testler ellenmez. Sürüm tavanı yazılmaz.
FOUNDATION.md'nin cümlesine dokunulmaz. Ön yüz, `dist`, `package.json` ellenmez.
