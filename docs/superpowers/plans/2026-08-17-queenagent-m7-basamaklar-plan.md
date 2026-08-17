# Madde 7 — Kenar çubuğu daralma basamakları · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m7-basamaklar-design.md](../specs/2026-08-17-queenagent-m7-basamaklar-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız test** (kırmızı gider), sonra stil.

---

## Adım 1 — Test (kırmızı commit)

**Yeni dosya: `features/workspace/workspace.css.test.js`** — dört kilit testi:

1. `.sidebar` varsayılanı 280px.
2. Üç basamak: 1000→226, 780→198, 640→172.
3. İç boşluk yalnız en dar basamakta değişir.
4. 1100px bloğu `.sidebar`'a hiç dokunmaz.

**Ölçülen kırmızı: 3.** (Dördüncüsü — varsayılan genişlik — zaten doğruydu ve yeşil geldi; testi
onu koruyor.)

**İki teknik engel çıktı, ikisi de dosyayı okuma biçiminde:**

- `new URL("./workspace.css", import.meta.url)` → `TypeError: The URL must be of scheme file`.
  vitest modülleri kendi protokolüyle servis ediyor, `import.meta.url` bir dosya adresi değil.
- `import CSS from "./workspace.css?raw"` → sessizce boş dize. Bu daha kötüsüydü: **üç test
  yanlış sebeple geçiyordu**, çünkü boş dizede her `indexOf` −1 dönüyor ve `not.toContain` her zaman
  tutuyor. Kırmızı beklerken yeşil görmek uyarı oldu.

Çözüm: `readFileSync(resolve(process.cwd(), "src/features/workspace/workspace.css"))`. Çalışma
dizini `npm test --prefix` sayesinde her zaman ön yüz kökü.

---

## Adım 2 — Stil

1. `@media (max-width: 1000px)` → `.sidebar { width: 226px }`
2. `@media (max-width: 780px)` → `.sidebar { width: 198px }`
3. `@media (max-width: 640px)` → `.sidebar { width: 172px; padding: 16px 10px }`
4. 1100px bloğundan `.sidebar` kuralı çıkar; bloğun geri kalanı aynen kalır.
5. Yorumlar bugünü anlatacak şekilde ayrılır: basamakları anlatan yorum yeni bloklara, rayı anlatan
   yorum 1100px bloğuna.

---

## Risk

Sıra: üç blok artan darlıkta yazılıyor (1000, 780, 640), böylece dar pencerede en dar kural
kazanıyor. Aynı özgüllükte son kural kazandığı için sıralama bozulursa 640px'te 226px uygulanır.
