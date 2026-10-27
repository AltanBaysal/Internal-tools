# Madde 357 — Kırpılmış sohbette çizgi · uygulama turu

**Kaynak:** [test turunun spec'i](2026-09-29-queenagent-m357-kirpma-cizgisi-testler-design.md) ve
kırmızı commit'i (`f31fe2c9`): `ChatScreen.test.jsx`'in iki, `workspace.css.test.js`'in iki ve
`App.test.jsx`'in bir testi. Uygulama bu testlerin tarif ettiğini yapar, fazlasını değil.

## Ne değişir

**Yalnız ön uç, iki dosya.** Arka uç `trimmed`'ı 345'ten beri veriyor, `useChat` kaydı olduğu gibi
tutuyor, `App` onu `ChatScreen`'e olduğu gibi veriyor — üçüne dokunulmaz.

### `ChatScreen.jsx`

Mesajları çizen `map` her mesajı bir `Fragment`'la sarar; anahtar (`${message.at}-${index}`)
`div`'den `Fragment`'a geçer. `Fragment`'ın içinde, mesajın önünde:

```jsx
{index > 0 && index === chat.trimmed ? <p className="trimmed">{TRIMMED_LINE}</p> : null}
```

- `index > 0`: `trimmed` `0` kırpılmamış demek, ve ilk mesajın önüne çizgi düşmemeli.
- `trimmed` taşımayan kayıtta `undefined` hiçbir sıraya eşit değil — çizgi yok, ayrı bir koruma
  gerekmez.
- `TRIMMED_LINE` dosyanın başında sabit, tasarımdaki adla: `Messages above this line are no longer
  sent to the model`. Yorumu neden: satırın yeri sunucunun sayısı, ekran hesaplamaz *(FOUNDATION,
  Karar 4)*.

**Yaklaşımlar:** (a) `map`'te `Fragment` — çizgi ait olduğu mesajın yanında, dizi kurmak yok; (b)
tasarımın yaptığı gibi çizilmiş listeye `splice` — React'te önce diziyi kurup sonra araya eleman
sokmak, anahtarı ayrı düşünmek ister. **(a) seçildi:** daha az parça.

### `workspace.css`

`.full__actions`'ın arkasına, tasarımın `kit.css`'indeki iki kural olduğu gibi:

- `.trimmed`: `position: sticky; bottom: 0;` — eski mesajlar okunurken `chat__scroll`'un alt
  kenarında bekler —, `display: flex; align-items: center; gap: 12px; margin: 0; padding: 8px 0;
  background: var(--canvas); font-family: var(--font-mono); font-size: 11.5px; line-height: 1.6;
  color: #6b6259; text-align: center;`
- `.trimmed::before, .trimmed::after`: `content: ""; flex: 1 1 16px; border-top: 1px solid
  var(--line);`

Yorum neden'i söyler: `--muted` değil `#6b6259`, çünkü okunacak bir cümle; zemin `--canvas`, çünkü
altından kayan yazı görünmesin.

**Hareket yok:** `sticky` bir animasyon değil, `@keyframes` eklenmez; CODE-STANDARD'ın hareket
paragrafı değişmez.

## Değişmeyen

- `msg--trimmed` eklenmez (test spec'inin 2. kararı).
- Düzeltme sürerken `trimmed` eski kayıttan kalır (test spec'inin 3. kararı).
- 380'in `following` kuralı: çizgi mesaj sayısını değiştirmez, kaydırma etkilerine dokunmaz.

## Nasıl görülür

Dört satır, paralel: dört süit yeşil. Tarayıcıda Claude bakar: kırpılmış sohbette çizgi ilk giden
mesajın üstünde; yukarı kaydırınca alt kenarda duruyor.

Adım adım dökümü [uygulama planında](../plans/2026-09-29-queenagent-m357-kirpma-cizgisi-uygulama-plan.md).
