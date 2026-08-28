# Madde 104 — Yeni sohbet kendi adresinde kalır · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 104.
**Belirti** *(kullanıcı, 28 Ağustos, defter denemesi)*: yeni sohbet açılıp ilk mesaj atıldığında
ekran eski bir sohbete ışınlanıyor.

## Kök neden (koşuda bulundu)

Üç parçanın bileşimi, üçü de `useChat.js` + `App.jsx`:

1. **Taslağa geçiş hook'un elindeki kaydı temizlemiyor.** Yükleme etkisi `!chatId` görünce erken
   dönüyor (`useChat.js` — `if (!projectId || !chatId) return undefined;`) ve `chat` state'inde
   **bir önceki sohbetin kaydı** kalıyor. Ekran o sırada `DRAFT` çizdiği için görünmüyor.
2. **İyimser balon o bayat kayda ekleniyor.** `send` ilk mesajın balonunu `setChat(current => ...)`
   ile ekliyor; `current` eski sohbetin kaydı.
3. **Doğum adresi taşıyınca bayat kayıt giyiliyor.** İlk kare (`chat`) yeni sohbeti adlandırıyor,
   `born` adresi ona taşıyor *(Madde 88)* — `drafting` düşüyor ve ekran `chat.chat`'i, yani **eski
   sohbetin dökümünü + yeni balonu** çiziyor. Tur bitene kadar *(Madde 89'un kayıt okuması gelene
   kadar)* kullanıcı eski sohbete ışınlanmış görüyor.

**Işınlanma adres değil ekran:** adres doğru sohbete gidiyor, yanlış olan gösterilen döküm.

## Test — `App.test.jsx`, bir yeni

`a draft's first answer never wears the old chat's transcript`: eski sohbet c1 açık *(dökümünde
"The old answer.")*, kenar çubuğundan New chat, bir cümle gönderiliyor; akış `gatedSse` ile ilk
karelerden sonra tutuluyor. Adres `/p/p1/c/c2`'ye geçtiği anda — cevap hâlâ akarken — ekranda
eski dökümün olmadığı ve kullanıcının kendi balonunun durduğu doğrulanıyor; kapı bırakılınca tur
Madde 89'un okumasıyla kapanıyor.

**Bugün kırmızı olan iddia:** `queryByText("The old answer.")` null — bugün görünüyor.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `App.test.jsx` | 1 yeni |

Defter çifti *(`test_notebook`, 2)* bu maddenin değil.

## Bilerek yapılmayanlar

- **Kod yazılmaz** — tur kırmızı commit'lenir.
- **Akış durumunun sohbete anahtarlanması test edilmez** — o Madde 106'nın işi; buradaki tek iddia
  taslağın ilk cevabının eski dökümü giymemesi.
- **Kenar çubuğu satırı test edilmez** — seçili satır adresi izliyor ve adres bugün de doğru.
- **`dist` derlenmez.**
