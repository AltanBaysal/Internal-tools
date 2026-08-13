# Görev 10 — Kare hover'da yerinden oynamasın

**Roadmap:** [v7](../plans/2026-08-13-queen-editor-v7-roadmap.md) · Blok 4

## Bulgu ve ne bulunabildi

Kullanıcı: *"Kare hover'da yerinden oynuyor; üstüne gelince kart garip biçimde ortalanıyor."*

Kodda hover anında değişen **iki** şey var ve ikisi aynı şey değil:

1. **Durum etiketi köşe değiştiriyor.** Seçim halkası ile etiket aynı köşeyi istiyor; halka fare
   gelince beliriyor ve etiket, çakışmasın diye üst-soldan alt-sola **atlıyor**. Yani karenin
   üstüne gelmek, karenin içindeki bir şeyi gerçekten yerinden oynatıyor.
2. **Başarısız katmanı olan karede karartma iniyor.** Fare gelince kareyi tamamen örten koyu bir
   katman ve **ortasında** "Tekrar dene" düğmesi beliriyor. Bu, tasarımın kendi kararı: başarısız
   render'ın geri dönüş yolu, fotoğrafı kalıcı olarak gizlememek için yalnız fare altında iniyor.

Kullanıcının gördüğü şeyin hangisi olduğu **kesin değil** — ve bulgu, üretimin hiç çalışmadığı
(Görev 1) bir turda yazıldı, yani ekrandaki her kare kırmızıydı ve her karede o karartma iniyordu.

## Kararlar

1. **Kesin olan düzeltilir: etiket artık atlamaz.** Durum etiketi her zaman alt-solda durur, seçim
   halkası üst-solda kalır. İkisi ayrı köşede olduğu için çakışma da yok, atlama da.
   Bu, karenin içinde hover ile hareket eden **tek** şeyi kaldırıyor.
2. **Karartma tasarım kararıdır, tahminle değiştirilmez.** Onu kaldırmak, başarısız bir karenin
   geri dönüş yolunu kaldırmak olur; ve kullanıcının kastettiği şeyin o olduğunu bilmiyoruz.
   Ne olduğu ve neden orada olduğu kullanıcıya söylenir, kararı ona bırakılır.
   Sebep uydurup davranış değiştirmek, bu deponun kendi kuralına aykırı.
3. **Kare hiç yer değiştirmez.** Izgarada hover'a bağlı hiçbir boyut değişmiyor — karonun adı her
   zaman yazılı, yükseklik sabit — dolayısıyla ızgaranın kendisi zaten oynamıyor. Bu görev, karenin
   *içindeki* hareketi kaldırıyor.

## Testler

- Durum etiketi alt köşede duruyor; hover için ayrı bir kural yok.
- Seçim halkası ile etiket aynı köşede değil.

## Öz eleştiri

- *Etiketi aşağı almak, "sahibi" rozetiyle çakışmaz mı?* — Çakışmıyor: rozet alt-sağda, etiket
  alt-solda. Aynı satırın iki ucu.
- *Kullanıcının kastettiği karartmaysa, bu görev boşa mı gitti?* — Gitmedi: hover'da gerçekten
  hareket eden bir şey vardı ve kalktı. Karartma da kendi kararını bekliyor; ikisini birden
  tahminle yapmak, ikisini de yanlış yapma riski taşırdı.
