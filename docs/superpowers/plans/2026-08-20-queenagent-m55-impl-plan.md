# Madde 55 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-20-queenagent-m55-impl-design.md](../specs/2026-08-20-queenagent-m55-impl-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Tek dosya

`queen-agent/app.ipynb` *(yeni)* — nbformat 4, iki hücre.

**Hücre 1 (markdown)** — defterin ne yaptığı, kısaca. Adım adım kullanım Madde 58'in işi.

**Hücre 2 (kod, `# === CONFIG ===`)** — sırasıyla:

1. `from google.colab import drive, userdata` + `import os` *(tek iş yapmayan satırlar)*
2. `drive.mount("/content/drive")` — **ilk iş**
3. `DRIVE_FOLDER = "queenAgent"`, `REPO`, `BRANCH`, `CLONE_DIR`, `APP_DIR`, `APP_PORT`
4. `DRIVE_ROOT = f"/content/drive/MyDrive/{DRIVE_FOLDER}"`, `makedirs`, `assert os.path.isdir(...)`
5. `GITHUB_TOKEN` — `try: userdata.get("GITHUB_TOKEN") except: ""`
6. `assert GITHUB_TOKEN, "…Secrets…GITHUB_TOKEN…"`
7. `print` — kök ve dal

`BRANCH = "feat/queenagent-colab"`: `main`'de bu defter henüz yok, ve olmayan bir dal ilk koşuda
anlaşılmaz bir klon hatası verir. Madde 58 birleştirmeden sonra `main`'e çevirir.

## Beklenen yeşil

Yedi testin yedisi. Toplam **368** — 361 + 7. *(Plan önce 369 diyordu; düşen Madde 60'ın sekiz
testi sayımdan çıkmamıştı.)*

## Kapanış denetimi

- `queenAgent` dizesi defterde tam bir kere geçiyor. *(İlk yazımda markdown hücresi klasör yolunu
  ikinci kez yazıyordu ve test bunu yakaladı. Kural deponun kendi kuralı: bir belge, kodun zaten
  söylediğini tekrarlamaz — eskiyecek olan kopyadır. Markdown artık ayarı **adlandırıyor**, değerini
  yazmıyor.)*
- `XAI_API_KEY` defterde hiç geçmiyor.
- Deftere yapıştırılmış bir token yok.
- Kullanıcının gördüğü metinler Türkçe, yorumlar İngilizce.
- Dosya geçerli JSON — testin ilk maddesi bunu zaten soruyor.
