# Madde 197 · test turu — düzenleme mesajın kendi yerinde

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 197.

---

## Bugün ne oluyor

195 kalemi bubble'ın **yanına** koydu ve ikisini bir satır sarmalayıcısına aldı *(`.msg__said`)*.
`.msg` bir sütun ve kullanıcı mesajlarında `align-items: flex-end`, yani sağa yaslanan artık
sarmalayıcı; bubble'ın `max-width: 78%`'i de `.msg`'in değil onun genişliğine göre çözülüyor. Her
mesajın sağ kenarı başka yere düşüyor.

Basınca cümle **sohbet kutusuna** iniyor: mesaj ekranın bir ucunda, düzeltmesi öteki ucunda.

## Ne kurulacak

- **Kalem bubble'ın altında.** Sarmalayıcı kalkıyor; bubble yine `.msg`'in doğrudan çocuğu, yani
  genişliği yine `.msg`'e göre ölçülüyor. Hizalama kusuru bir yamayla değil, **sarmalayıcı
  gittiği için** kapanıyor.
- **Basınca bubble'ın yerini yazılabilir bir alan alıyor**, içinde o cümle. Kutu hiç karışmıyor.
- **Altında iki ikon:** ✓ ve ✕ *(kullanıcı kararı, 8 Eylül)*. Adları `aria-label` ve `title`'da —
  `Confirm edit`, `Cancel edit`. Adı olmayan ikon ne klavyeye görünür ne teste.
- **✓** 195'in yolunu koşuyor: `onSend(text, index)`, yani o noktadan yeni sürüm ve tur.
  **✕** mesajı olduğu gibi bırakıyor ve hiçbir şey göndermiyor.
- **Klavye kutununkiyle aynı:** Enter onaylar, Shift+Enter satır açar, Escape vazgeçer.
- **`Composer`'ın `filled` alanı kalkıyor** — var olma sebebi 195'in kutuya doldurmasıydı.

### Düzenlerken kalem yok

Açık bir düzenlemenin altında ikinci bir *"düzenle"* durursa aynı işin iki kapısı olur, ve basıldığında
ne olacağı belirsizdir *(yazılanı atıp baştan mı başlıyor?)*. Alan açıkken kalem çekiliyor; kapatan
şey ✓ ya da ✕.

## Testler

### `ChatScreen.test.jsx`

195'in düzenleme testleri bu maddede yeniden yazılıyor: ikisi *(kalem yalnız soruda, gönderilen
metin sırayı taşır)* kalıyor, kutuya doldurmayı ölçenler yerini aşağıdakilere bırakıyor.

1. **kalem yalnız kullanıcı mesajında** — cevapta yok *(195'ten kalıyor)*.
2. **basınca bubble'ın yerini yazılabilir alan alır** — içinde o cümle, ve `.msg__bubble` o mesajda
   artık yok.
3. **sohbet kutusuna hiçbir şey inmez** — `.composer__input` boş kalır. Maddenin asıl cümlesi bu.
4. **✓ düzeltilmiş metni ve sırayı gönderir** — `onSend("...", 0)`.
5. **✕ hiçbir şey göndermez ve mesajı geri getirir** — bubble yerinde, alan yok.
6. **Enter onaylar, Shift+Enter onaylamaz** — kutunun kuralının aynısı.
7. **Escape vazgeçer** — ✕ ile aynı sonuç.
8. **düzenlerken kalem yok** — açık alanın altında ikinci bir kapı durmuyor.
9. **sıradan bir gönderim hâlâ sırasız** — `onSend("...", null)` *(195'ten kalıyor, ve kutunun yolu
   bu maddede bozulmamalı)*.

### `workspace.css.test.js`

10. **sarmalayıcı gitti** — `.msg__said` diye bir kural yok. Kaymanın kaynağı buydu.
11. **yazılabilir alan bubble'ın ölçüsünde** — `.msg__editing` da `max-width: 78%`, yani düzenleme
    açılınca mesaj ne genişliyor ne daralıyor.
12. **onay satırı alanın altında** — `.msg__editing-actions` bir satır, ve `.msg--user` sütununda
    sağa yaslanıyor.

### `App.test.jsx`

13. **baştan sona** — mesaj düzenlenir, ✓ ile gönderilir, sohbet oradan devam eder ve `‹ 1/2 ›` ile
    eskisine dönülür. 195'in aynı testi, kutu yerine yerinde düzenlemeyle.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. Ön yüzde **11 kırmızı** — `Confirm edit` diye bir düğme yok,
`.msg__editing` diye bir kural yok, ve basınca cümle hâlâ kutuya iniyor. Arka uç ve `queen-editor`
kımıldamıyor: **926 · 739 · 591** yerinde.
