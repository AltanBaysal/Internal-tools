# Madde 57 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-20-queenagent-m57-impl-design.md](../specs/2026-08-20-queenagent-m57-impl-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Tek dosya

`queen-agent/app.ipynb` — klon hücresinin arkasına bir kod hücresi (`# === Serve ===`).

## İçerik

```
assert "APP_DIR" in globals()
pkill -f main.py ; pkill -f cloudflared
Popen(["python", "main.py"], cwd=APP_DIR, env={**os.environ, "QUEENAGENT_ROOT": DRIVE_ROOT})
90 sn boyunca /api/health  ->  düşerse log'un son 30 satırı + RuntimeError
cloudflared indir (yoksa) -> Popen(tunnel --url) -> log'dan trycloudflare linkini oku
print(link)  +  print(parolasız uyarısı)
tail -f
```

## Yorumların söyleyeceği

Neden `cwd=APP_DIR` (`backend` ancak oradan çözülüyor), neden `env={**os.environ, …}` (`PATH`
korunmalı), neden sebep uydurulmuyor, neden hücre bitmiyor, neden `pkill`.

## Beklenen yeşil

Sekiz testin sekizi. Toplam **383** — 375 + 8.

## Kapanış denetimi

- Uyarı, linkin basıldığı yerin hemen yanında.
- `QUEENAGENT_ROOT` gerçekten `DRIVE_ROOT`'a bağlı.
- Kullanıcının gördüğü metinler Türkçe, yorumlar İngilizce.
- Defter hâlâ geçerli JSON, ve dört hücre.

## Bundan sonra

Defter bu maddeyle **çalışır** hâle geliyor: Colab'a yüklenip denenebilir. Madde 58 kalan işi yapar
— arkadaşının adım adım yolu, Drive'da ne olduğu, ve `BRANCH`'in `main`'e çevrilmesi.
