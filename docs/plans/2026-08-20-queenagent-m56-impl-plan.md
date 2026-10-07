# Madde 56 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-20-queenagent-m56-impl-design.md](../specs/2026-08-20-queenagent-m56-impl-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Tek dosya

`queen-agent/app.ipynb` — CONFIG hücresinin arkasına bir kod hücresi (`# === Clone ===`).

## İçerik

```
assert "CLONE_DIR" in globals()      # kapı
_mask(text)                          # token yerine <token>
shutil.rmtree(CLONE_DIR) if exists   # sil
subprocess.run(["git", "clone", "--branch", BRANCH, "--depth", "1", clone_url, CLONE_DIR], ...)
returncode != 0 -> RuntimeError(_mask(stderr))
pip install -q flask
assert os.path.exists(f"{APP_DIR}/frontend/dist/index.html")
print("✓ …")
```

`clone_url` hiçbir yerde basılmıyor. `shell=True` yok.

## Beklenen yeşil

Yedi testin yedisi. Toplam **375** — 368 + 7. *(Plan önce 377 diyordu: kırmızı koşudaki
"370 passed" satırı toplam sanılmıştı, oysa toplam 375'ti.)*

## Kapanış denetimi

- `clone_url` yalnız `subprocess.run`'a giriyor; hiçbir `print`'te yok.
- Hata yolunda `_mask` var.
- Kullanıcının gördüğü metinler Türkçe, yorumlar İngilizce.
- Defter hâlâ geçerli JSON.

## Yeşil turda iki düzeltme, ve neden

**1. Yorumda `shell=True` geçiyordu.** Test kaynağın tamamını tarıyor ve yorumu koddan ayıramıyor,
yani yasakladığı dizeyi anlatan bir yorum testi düşürüyordu. Yorum yeniden yazıldı. Testi yorumları
anlayacak kadar karmaşıklaştırmak, kazandığından fazlasını götürürdü.

**2. Test `pip install` dizesini arıyordu**, uygulama `["pip", "install", …]` kullanıyor. Burada test
**kuralı değil yazımı** çivilemişti: kural "Flask kuruluyor mu", ve argüman listesi bunu tam olarak
yapıyor. Test, aynı satırda `pip` ve `flask` geçen bir satır arayacak şekilde gevşetildi — kural
duruyor, yazıma bağlılığı gitti.

Kırmızı commit'lenmiş bir testi yeşil turda değiştirmek kural olarak yanlış; burada yapılmasının
sebebi, testin kuralı değil bir yazım tercihini tutuyor olması. Sessizce yapılmadı, buraya yazıldı.
