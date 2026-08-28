# Madde 116 — Sohbetin adı ilk mesajın kısaltılmışı olur · Tur 2 (uygulama) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 116 ve
[tur 1'in tasarımı](2026-08-28-queenagent-m116-sohbet-adi-testler-design.md). Testler kırmızı
commit'te; kök neden orada yazılı: ayağa dikilen kayıt adını mesajın tamamından alıyor.

## Değişen iki yer

**1. `chatTitle.js` doğar** *(`src/features/workspace/`)* — sunucunun adlandırma kuralının aynası:

```js
const TITLE_LIMIT = 42;

export function chatTitle(text) {
  const trimmed = text.trim();
  if (trimmed.length <= TITLE_LIMIT) return trimmed;
  return trimmed.slice(0, TITLE_LIMIT) + "…";
}
```

Kural iki yerde duruyor ve bu bilinen bir bedel: `chat.py` Python'u, burası tarayıcıyı besliyor ve
ikisinin arasında paylaşılabilen bir modül yok. Kopya tek pencere için var — taslağın ilk turu
akarken duran kayıt — ve iki taraf da kendi testiyle 42'ye ve işaretin yalnız kaybedene
verilmesine sabitli; ayrışırlarsa iki suite'ten biri kırmızıya düşer.

**2. `useChat.send`'in ayağa diktiği kayıt** — `title: text` yerine `title: chatTitle(text)`.
Sunucu turun sonunda aynı adı döndüreceği için kayıt geri okunduğunda başlık değişmez; pencere
boyunca da sonrasında da aynı ad durur.

## Bilerek yapılmayanlar

- **`chat_title` (backend) ellenmez** — doğru çalışıyor.
- **Kenar çubuğu, proje ekranı, CSS ellenmez** — sunucudan okuyorlar ve tek satırlar.
- **İyimser baloncuğun metni ellenmez** — kırpılan yalnız ad; mesajın kendisi olduğu gibi
  görünmeye devam eder.

## Beklenen yeşil

Tur 1'in üçü dahil frontend suite'in tamamı; backend'e dokunulmuyor. Ön yüz kaynağı değiştiği
için `dist` aynı commit'te derlenir.
