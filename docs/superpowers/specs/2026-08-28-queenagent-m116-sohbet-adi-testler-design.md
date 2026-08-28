# Madde 116 — Sohbetin adı ilk mesajın kısaltılmışı olur · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 116.
**Gözlenen** *(28 Ağustos, dördüncü deneme)*: yeni sohbet uzun bir ilk mesajla açılınca ad mesajın
tamamı çıkıyor — oysa `chat.py`'de `TITLE_LIMIT = 42` var ve `chat_title` kesiyor.

## Kök neden — bulundu

Maddenin sorusu *"ya ad oradan gelmiyor, ya kesilmiş metin ekranda kesilmiş görünmüyor"* idi;
cevap birincisi. Doğum yolunun iki ucu iki ayrı ad taşıyor:

- **Sunucu doğru:** `append_message` doğumda `chat_title(trimmed)` yazıyor, özet uçları da kayıt
  ucu da onu döndürüyor. Kenar çubuğu ile proje ekranı sunucudan okuyor ve ikisinin CSS'i de tek
  satır — orada yanlış bir şey yok.
- **Ekran doğumda başka bir kayıt gösteriyor:** taslaktan gönderilen ilk mesaj için `useChat.send`
  iyimser bir kayıt ayağa dikiyor — `{ id: null, title: text, ... }` — ve `title` mesajın
  **tamamı**. Sohbet başlığı (`.chat__title`) bu kaydı basıyor. Sunucunun kırpılmış adı ekrana
  ancak turun sonunda, kayıt diskten geri okununca geliyor; akışın ilk turu dakikalar sürdüğü
  için kullanıcı o boyunca mesajın tamamını ad olarak görüyor.

## Kural

Ayağa dikilen kayıt da adını sunucunun kuralıyla alır: ilk mesaj kırpılarak — 42, kaybı olana
`…` — başlık olur. Kural ön yüzde `chatTitle` olarak bir kez yazılır ve `chat_title`'a
sabitlenir; iki taraf birbirini kendi testiyle tutar.

## Testler

**`chatTitle.test.js`** *(yeni dosya, `src/features/workspace/`)* — iki test:

1. Kısa metin olduğu gibi döner, kenar boşlukları atılmış hâlde.
2. Uzun metin 42'de kesilir ve `…` alır; tam 42'lik metin işaretsiz kalır — işaret yalnız bir şey
   kaybedene.

**`App.test.jsx`** — bir test: taslaktan 42'yi aşan bir ilk mesaj gönderiliyor, cevap akmaya devam
ederken *(stream bekletilir)* `.chat__title` mesajın tamamını değil kırpılmışını gösteriyor.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `chatTitle.test.js` | dosya — modül henüz yok |
| `App.test.jsx` | 1 |

Backend suite'e dokunulmuyor; `test_notebook`'un ikisi dal yaşadıkça bilinen kırmızı.

## Bilerek yapılmayanlar

- **`chat_title` (backend) ellenmez** — doğru çalışıyor; satır sonlarını da indirmiyor ve
  indirmesi gerekmiyor: HTML boşluk kuralı `\n`'i zaten boşluk basıyor.
- **Kenar çubuğu ve proje ekranı ellenmez** — ikisi de sunucudan okuyor ve tek satır.
- **`dist` bu turda derlenmez** — kaynak tur 2'de değişiyor.
