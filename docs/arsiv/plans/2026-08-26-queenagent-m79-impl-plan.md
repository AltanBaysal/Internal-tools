# Madde 79 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-26-queenagent-m79-gonder-durdurmaya-doner-uygulama-design.md](../specs/2026-08-26-queenagent-m79-gonder-durdurmaya-doner-uygulama-design.md)
**Kırmızı testler:** `60856ef` — ön yüzde 4.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sıra

### 1. `Composer.jsx` — düğme iki durumlu olur

İki prop: `running`, `onStop`. Düğmenin yazısı, kapalılığı ve basma yolu ikisine bakar:

- Yazı: `running ? "Stop" : action`
- Kapalı: `!running && !ready` — akarken hiçbir zaman kapalı değil
- Basınca: `running ? onStop : submit`

Vurgu sınıfı `running || ready` olduğunda geliyor: akan bir cevabın karşısında tek eylem
durdurmaktır, yani o an birincil eylem odur.

`submit`'e dokunulmuyor. Ayrım düğmenin üstünde, içinde değil — `submit` taslak kurallarının
sahibi ve durdurmayı bilmesi gereken bir sebebi yok.

*Yeşile döner:* `Composer.test.jsx`'in üç kırmızısı.

### 2. `ChatScreen.jsx` — ayrı `Stop` gider, `onStop` `Composer`'a geçer

`foot`taki `thinking ? <button className="stop">` bloğu silinir. `Composer` `running={thinking}` ve
`onStop={onStop}` alır.

*Yeşile döner:* `ChatScreen.test.jsx`'in bir kırmızısı.
*Yeşil kalır:* 67'nin iki testi — düğmeyi adıyla arıyorlar, sahibini değil.

### 3. `workspace.css` — `.stop` ve `.stop:hover` silinir

Kullanan kalmadı. `workspace.css.test.js` bu sınıfları sormuyor *(bakıldı)*, yani düşen olmamalı.

### 4. `dist` derlenir

`npm run build --prefix queen-agent/frontend`, kaynakla **aynı commit'e**.

## Beklenen yeşil

Ön yüzde **502**. Arka uçta **2 failed, 442 passed** — ikisi defterin dalı.

**Bu maddenin asıl sınavı düşmeyen testler.** 67'nin *"akan cevap durdurulabiliyor"* ve
*"boştayken durdurulacak bir şey yok"* testleri dokunulmadan yeşil kalmalı. Biri düşerse görünen
değil çalışan bozulmuş demektir, ve o zaman kod düzelir — test değil.

## Bilerek yapılmayanlar

- **Enter dokunulmuyor.** Akarken de gönderiyor. Bu madde düğme hakkında; klavyenin akarken ne
  yapacağı ayrı bir davranış sorusu.
- **Proje ekranına `running` geçirilmiyor.** Orada akan bir cevap yok — sohbet henüz doğmamış.
- **Kırmızı gelmiyor.** 67'nin kararı duruyor: kendi cevabını kesmek yıkıcı bir iş değil.
