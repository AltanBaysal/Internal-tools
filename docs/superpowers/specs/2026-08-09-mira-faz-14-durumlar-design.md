# Mira — Faz 14: Durumlar ve doğrulama (Madde 29-32)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) · [Faz 13](2026-08-09-mira-faz-13-arama-design.md)

**Kapsam:** yükleme iskeletleri (Madde 29) · çevrimdışı şeridi (Madde 30) · 1100px altı (Madde 31) ·
uçtan uca tur listesi (Madde 32, **kullanıcı koşar**).
**Kapsam dışı:** yeni özellik. Bu faz var olanın eksik hâllerini tamamlıyor.

---

## 1 · Yükleniyor

İçerik alanı yüklenirken **iskelet bloklar** çizilir; **kenar çubuğu normal çalışır** ve gezinme
hiçbir an engellenmez — zaten kenar çubuğunun verisi ayrı bir istekten geliyor.

**"Yükleniyor" nereden biliniyor?** Listeler bugün boş bir dizi ile başlıyor ve bu, "henüz gelmedi"
ile "hiç yok"u aynı gösteriyor. `useList` ve `useProjects` bir `loading` alanı kazanır: ilk yanıt
gelene kadar `true`. İki durum ayrılmadan iskelet ile boş-durum metni birbirinin yerine geçerdi.

| Ekran | İskelet |
|---|---|
| Home | proje kartlarının yerinde dört blok |
| Proje | sohbet ve dosya sütunlarında üçer satır bloğu |
| Sohbet | iki mesaj bloğu |

Boş-durum cümleleri (*"No files yet…"*) yalnız **yükleme bittikten sonra** çıkar; bugüne kadar bir an
için yanlış cümle görünüyordu.

## 2 · Çevrimdışı

İçerik alanının üstünde bir şerit ve **composer açık kalır**.

**Şerit ne der?** *"You're offline. Messages are saved; Mira will answer when the connection is
back."*

**Neden bu cümle.** Mira'nın sunucusu aynı makinede: ağ gidince mesaj yine diske yazılır. Ağın
gerektiği tek yer **motor** — xAI. Yani çevrimdışıyken kaybolan şey cevap, mesaj değil. Yol
haritasının "mesajlar saklanır ve bağlantı dönünce gönderilir" cümlesi bu araç için tam olarak bunu
söylüyor ve şerit de bunu söylemeli; bir kuyruk uydurmak, olmayan bir mekanizmanın sözünü vermek
olurdu.

**Bunun için yeni bir mekanizma yazılmıyor.** Faz 6'nın kuralı zaten şuydu: *son sözü kullanıcı
söylediyse sohbet bir cevap bekliyor.* Kurala tek bir koşul ekleniyor — **çevrimdışıyken sorulmaz.**
Bağlantı dönünce sohbet hâlâ cevap beklediği için cevap kendiliğinden istenir. Kuyruk, yeniden
gönderme, zamanlayıcı yok.

`navigator.onLine` ve `online` / `offline` olayları `shared/useOnline.js`'te tek bir yerde okunur.

## 3 · 1100px altı

Dar ekranda **düzen kırılmaz ve yatay kaydırma oluşmaz.**

- **Ray konuşmanın altına iner**, tam genişlikte. Sohbet okunabilir kalır.
- **Kenar çubuğu 280 → 208px'e daralır.** Katlanmak burada genişlikten vazgeçmektir, işlevden değil:
  gezinme dar ekranda da tam çalışır.
- Proje ızgarası ve okuma paneli de tek sütuna iner.

**"Overlay" neden yüzen bir katman değil?** Yüzen bir rayın açılıp kapanacak bir düğmesi olmalı ve
tasarımda öyle bir düğme yok. Altına almak aynı amacı — konuşmanın okunabilir kalması — hiçbir şey
uydurmadan sağlıyor. Bu, tasarımdan bilerek ayrılan tek yer ve gerekçesi burada yazılı.

Bu madde **CSS'tir**; jsdom stil hesaplamadığı için testi yok. Doğrulaması Madde 32'nin 16. adımı.

## 4 · Uçtan uca tur (Madde 32)

Kod bittikten sonra **kullanıcı** tek dalgada elle koşar; on yedi adımın listesi
[yol haritasında](../plans/2026-08-09-mira-v1-roadmap.md#madde-32--uçtan-uca-tur). 13-14. adımlar
(anahtarı bozup düzeltmek) ve 17. adım (sunucuyu kapat-aç) yalnız orada denenebilir: birinde gerçek
bir API anahtarı, öbüründe gerçek bir yeniden başlatma var.

## 5 · Katmanlar

| Katman | Ekleme |
|---|---|
| frontend/shared | `useList` ve `useProjects` `loading` verir · `useOnline.js` |
| frontend | `Skeleton.jsx` · `OfflineStrip.jsx` · üç ekranda iskelet · `useChat` çevrimdışıyken sormaz |
| css | 1100px altı için tek `@media` bloğu |

Arka uçta hiçbir değişiklik yok.

## 6 · Testler

1. `useList` ilk yanıt gelene kadar `loading`, sonra değil.
2. Home yüklenirken iskelet, yüklendikten sonra kartlar.
3. Proje ekranı yüklenirken iskelet; boş-durum cümlesi yükleme bitmeden çıkmıyor.
4. Sohbet ekranı yüklenirken iskelet.
5. Çevrimdışıyken şerit görünüyor, composer duruyor.
6. Çevrimdışıyken cevap **istenmiyor**; bağlantı dönünce isteniyor.
7. Çevrimdışıyken atılan mesaj yine de sunucuya gidiyor (kaydediliyor).

## 7 · Kabul kriteri

`pytest` ve `npm test` yeşil. Ekranda: yavaş yanıtta içerik alanında iskeletler var ve kenar
çubuğundan başka projeye geçilebiliyor; ağı kesince şerit çıkıyor ve composer kapanmıyor; pencere
1100px altına inince ray konuşmanın altına geçiyor ve yatay kaydırma oluşmuyor.
