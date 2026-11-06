# Madde 526 · Aracın kuralları, tasarımcı ve tasarım reviewer'ı — tasarım

**Tarih:** 6 Kasım 2026 · **Madde:** [v1 yol haritası](../roadmaps/2026-11-06-queen-studio-v1-roadmap.md#v1-2),
526 · v1-2 · **Dal:** `feat/queen-studio-v1`

## Ne ve neden

queen-studio'nun kodu bir sonraki maddede ([v1-3](../roadmaps/2026-11-06-queen-studio-v1-roadmap.md#v1-3))
yazılmaya başlar. Ondan önce coder'ın ve reviewer'ın baktığı kural dosyaları, CLAUDE.md'nin dördüncü
aracı, ekranları tasarlayacak iki agent ve yolda bulunan işin gideceği backlog yerinde olmalı. Yalnız
belgeler değişir; kod ve test yok, QA yok.

## Ne yazılır

- **`queen-studio/FOUNDATION.md`:** öbür iki uygulamanınki gibi ilkeler ve kararlar, her birinin
  nedeniyle. Kararlar 5. adımdan (yığın) ve tasarımın öbür adımlarından gelir; ayrıntı kopyalanmaz,
  adımına link verilir.
- **`queen-studio/CODE-STANDARD.md`:** 11. adımın düzeni, dili, mesajları, maliyeti ve kontrol
  araçları, nedenleriyle; testlerin çerçevesi 12. adıma, hata biçiminin ayrıntısı 6. adıma gösterir.
  Klasör adları ve komutlar burada uydurulmaz: onları v1-3 kodu yazarken koyar.
- **`queen-studio/BACKLOG.md`:** öbürlerininki gibi; bugün boş, tasarımda sonraya bırakılanlar için
  "Sonraya kalanlar"a gösterir.
- **`.claude/agents/designer.md`:** ekranları gerçek UI kodunda, OpenAPI türleriyle yazılı örnek
  veriyle kurar; `frontend-design`'ı ve kısa UX kontrol listesini kullanır; bağlantı yazmaz; 9. adımın
  yeteneklerinin dışına çıkmaz. Kontrol listesi yalnız burada durur (9. adım: "tanımına … eklenir").
- **`.claude/agents/design-reviewer.md`:** deneyime bakar — kontrol listesi ve 9. adımın sınırı;
  ekranlara Playwright'la, örnek veriye karşı. Kodu okumaz, o reviewer'ındır.
- **CLAUDE.md:** dört araç; queen-studio'nun kural dosyaları; UI'ı İngilizce (Style); bir queen-studio
  maddesi yalnız onun suite'lerini koşar, bütün araçlarınkiler `main`'den önce bir kez (Commands);
  ekranları queen-design'da değil bu repoda tasarımcıyla (Designs); Subagents'ta iki agent ve iki akış:
  kod maddesi coder → reviewer → QA → ana agent, tasarım maddesi tasarımcı → tasarım reviewer'ı →
  reviewer → QA → ana agent.

## Kararlar

- **Kontrol listesi tek yerde:** `designer.md`'de; tasarım reviewer'ı ona gösterir. Kural iki yerde
  yazılmasın diye.
- **Liste UI UX Pro Max'ten:** ana agent kaynağı getirdi — `ux-guidelines.csv`'nin kuralları ve
  README'nin teslim öncesi listesi (MIT). Yalnız ekranda bakılabilen ve bu araca uyanlar alındı.
  Kaynak dosyada yazar. 150–300 ms gibi tek bir süre yazılmadı: CSV onu genel kural saymıyor.
- **Tarayıcı:** CLAUDE.md Playwright'ı ana agent'ın ve QA'nın sayıyor. 12. adım UI'ın görünüşüne
  tasarım reviewer'ının "gözle" baktığını söylüyor; tasarımcı da kurduğunu görmeli. Maddeler tek tek
  yürüdüğü için ikisi de tarayıcıyı sırayla kullanır; Browser bölümü bunu ekler.
- **"Dört suite":** CLAUDE.md, coder ve QA "dört suite" diyor; queen-studio'nun maddesinde bu yanlış
  olur. Commands bölümü bir maddenin hangi suite'leri koştuğunu bir kez söyler; öbür yerler "maddenin
  suite'leri" der ve oraya gösterir. queen-editor ve queen-agent maddeleri için bir şey değişmez:
  onların suite'leri yine dördü.

## Maliyet ve risk

Çalışma anında hiçbir şey değişmez; hiçbir test belge okumaz (CLAUDE.md, madde 431). Risk kırık link:
yeni dosyaların her linki elle açılarak denenir.

## Bitti sayılır

Kabul koşulunun altı satırı: üç dosya `queen-studio/`'da, iki agent `.claude/agents/`'ta, CLAUDE.md dört
aracı, kuralları, dili, suite'leri, tasarımın yerini ve iki akışı söylüyor; yeni linklerin hepsi açılıyor.
