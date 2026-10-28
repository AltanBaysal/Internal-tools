# Madde 354 — Cevabın altında cached ve missed · uygulama turu

**Kaynak:** [test turunun spec'i](2026-09-29-queenagent-m354-cached-missed-testler-design.md) ve
kırmızı commit'lenmiş testleri. Tasarım: queen-design `queen-agent-v3`, 189 ve 192 — `shell.js`'in
`stamp`'i, `kit.css`'in `.msg__stamp-cached` ve `.msg__stamp-missed`'i.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

**`queen-agent/frontend/src/features/workspace/Stamp.jsx`, `Stamp`.** Bugün sözler tek bir metin:
`sent + answered` sıfır değilse `${when} · ${shorten(spent)} tokens`. Olacak: sözlerin `span`'ı önce
saati, sonra `usage?.sent` sıfır değilse ` · `, `<span className="msg__stamp-cached">` içinde
`${shorten(usage.cached)} cached`, ` · `, `<span className="msg__stamp-missed">` içinde
`${shorten(usage.sent - usage.cached)} missed` taşır. `answered` okunmaz. `shorten` ve `LiveStrip`
değişmez — süren cevap tek sayısını tutar.

- `missed`'in çıkarması burada, ekranda: `Usage`'ın belgesi dördüncü bir alanı açıkça reddediyor, ve
  bu iki sayının nasıl gösterileceği, bir kural değil *(FOUNDATION, Karar 4)*.
- `cached` sunucunun her cevapta gönderdiği bir alan (`routes.py` üçünü de hep yolluyor); `?? 0`
  gibi bir koruma yazılmaz, olmayan bir durum için.
- Sıfırın kuralı `sent`'e bağlanır, tasarımın dediği gibi: gönderilmeyen bir istek önbellekten de
  gelmez, kaçırmaz da.
- Bileşenin başındaki yorum düzelir: "one number out of the three" artık yanlış; neden iki sayı —
  önbellekten gelen elli kat ucuz, tek toplam maliyeti söylemiyordu — ve neden `answered` yok
  *(kullanıcı, tasarımın 192'si)*.

**`queen-agent/frontend/src/features/workspace/workspace.css`.** `.msg__stamp`'in altına, tasarımın
`kit.css`'indeki gibi:

```css
.msg__stamp-cached { color: #536747; }
.msg__stamp-missed { color: var(--destructive); }
```

Yeşil `app.css`'e değişken olarak girmez: uygulamanın öteki yeşili `#6f8a5f` de `workspace.css`'te,
yerinde yazılı, ve tasarım `#536747`'yi onun koyusu olarak aynı yere koyuyor. Yorum neden koyu
olduğunu *(`--canvas`'ta 5.7:1)* ve kırmızının burada bir yıkımı değil bir maliyeti işaret ettiğini
söyler.

**`queen-agent/backend/features/workspace/presentation/routes.py`, yalnız yorum.** "The breakdown
travels even though the screen draws one number out of it" artık yanlış: ekran `sent` ve `cached`'ı
okuyor, `answered`'ı okumuyor. Yorum bugünkü doğruyu söyler. Kod değişmez.

## Değişmeyenler

- Sunucu, `Usage`, sohbetin JSON'u: üç alan yerinde.
- `LiveStrip` ve `stream_answer.py`'nin `_volume`'u: süren cevabın sayısı v9-10'da.
- `ChatScreen.jsx`: `Stamp`'e yalnız cevabın `usage`'ını vermesi yerinde.
- `dist` derlenmez: yöneten birleştirirken bir kez derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel; dördü de yeşil. Tarayıcıda: biten bir cevabın altında
`09:38 · 49.2k cached · 12.1k missed`, cached yeşil, missed kırmızı; sayısız eski cevapta yalnız saat;
süren cevapta `round N/16 · N tokens ·`.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m354-cached-missed-uygulama-plan.md).
