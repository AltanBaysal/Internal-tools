# Madde 192 · uygulama turu — dosyalar tazelenir

**Kaynağı:** [test turu](2026-09-06-queenagent-m192-tazeleme-testler-design.md), `3cb13cd`'de 13
kırmızı *(sekizinci test yokluğu ölçüyor ve bugün de yeşil)*.

---

## Değişen sekiz dosya

| Dosya | Ne oluyor |
|---|---|
| `useFile.js` | `reload` — açık dosyayı boşaltmadan yeniden okur |
| `useChat.js` | beşinci parametre `onTurnEnd`, `send`'in `finally`'sinde |
| `App.jsx` | `refresh` kurulur ve üç yere dağıtılır |
| `ChatScreen.jsx` | `onRefresh` raya geçirilir |
| `FileRail.jsx` | listeye ve panele geçirilir |
| `ProjectScreen.jsx` | sütuna ve panele geçirilir |
| `FilePanel.jsx` | başlıkta `↻` |
| `workspace.css` | düğmenin biçimi |

Artı `dist` — aynı commit'te, çünkü defter derlemiyor.

## `useFile.reload`

`getJson(path)`, sonra `setFile`. İlk okumadan iki farkı var, ikisi de bilerek:

- **`setFile(null)` yok.** İlk okuma hiçbir şeyin olmadığı yerden başlıyor; tazeleme okurken ekranda
  bir metin duruyor ve onu bir kare için silmek göz kırpması olur.
- **Uçuş sırasında dosya değiştiyse cevap atılır.** Effect'in `cancelled` bayrağıyla aynı kural,
  başka bir kapıda: `path` bir ref'te tutulur ve cevap döndüğünde çağrıldığı yolla karşılaştırılır.
  Yoksa okuma sürerken açılan ikinci dosyanın üstüne birincinin gövdesi yazılır.

404 dosyayı **gitmiş** işaretler ve gövdeyi de siler. `missing` altında eski metnin durması, iki
yalanın eskisi olurdu.

## `useChat.onTurnEnd`

`finally`'de, **sahiplik kapısının dışında**. Kapı ekrana çizen şeyleri koruyor — eski bir akış
yenisinin çizdiğini süpürmesin diye. Tazeleme çizmiyor, **diski soruyor**: turun yazdığı şey kim
bakıyor olursa olsun yazıldı. `file` çerçevesinin her ekran için duyurulmasıyla aynı gerekçe.

Turun nasıl bittiği de fark etmiyor. Hata bir bitiştir, ve o ana kadar diske yazılan yazılmıştır.

`onFileCreated` yerinde kalıyor. Adı hâlâ doğru: o **bir dosya doğdu** demek, bu **tur bitti**.

## `App.refresh`

```
Promise.all([reloadFiles(), reading.reload()])
```

`reloadProjects` bilerek yok. Proje kartındaki sayıyı değiştiren şey **doğan dosya**, ve onu
`onFileCreated` zaten tazeliyor. Madde 192 iki yer sayıyor: liste ve detay.

## Düğme

`↻`, adı `Refresh`, üç yerde — `FileRail`'in listesi, `ProjectScreen`'in sütunu, `FilePanel`'in
başlığı. Üçü de aynı `refresh`'i çağırıyor.

**Neden başlıkta değil de listenin içinde:** rayın başlığı **katlama düğmesinin kendisi**, ve bir
düğme başka bir düğmenin içinde duramaz. Listenin içinde olması aynı zamanda katlanmış şeritte
kaybolmasını sağlıyor — orada liste yok, düğmenin hakkında olacağı bir şey de yok.

İki ekran aynı `.file-list__bar` satırını paylaşıyor, yani biçim tek yerde yazılı.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. 13 kırmızı kapanır; arka uçlar ve `queen-editor`
kımıldamaz. Sonra `npm run build --prefix queen-agent/frontend`, ve `dist` bu commit'e girer —
`test_dist_is_committed` derlemeden sonra `git ls-files`'a bakıyor.
