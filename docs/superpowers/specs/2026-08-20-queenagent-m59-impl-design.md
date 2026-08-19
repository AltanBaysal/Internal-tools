# Madde 59 · Tur 2 (uygulama) — Tasarım

**Madde:** [v4 yol haritası Madde 59](../plans/2026-08-20-queenagent-v4-colab-roadmap.md)
**Turun kırmızısı:** [Tur 1 tasarımı](2026-08-20-queenagent-m59-test-design.md) — `test_store.py`,
üç test.
**Bu belgenin konusu:** yazmanın yeni şekli, ve seçilen her ayrıntının sebebi.

---

## Şekil

Hedefe hiç dokunulmaz; yazma bir yan dosyaya yapılır, sonra `os.replace` ile hedefin **üstüne
geçilir**. `os.replace` işletim sisteminin atomik taşıması: ya eski dosya durur ya yeni dosya durur,
arada bir hâl yoktur. Store bu ilkeli zaten tanıyor — `move` onu kullanıyor, `write_text` kullanmıyordu.

## Geçici dosya nerede doğar

**Hedefin yanında**, sistemin temp dizininde değil. `os.replace` dosya sistemi geçemez; Colab'da kök
bir Drive bağlaması, `/tmp` ise yerel disk — temp dizinine yazmak her taşımayı `OSError` yapardı ve
bu, geliştirme makinesinde **hiç** görünmezdi.

`tempfile.NamedTemporaryFile` kullanılmıyor: varsayılanı sistemin temp dizini, ve `dir=` vererek
düzeltilse bile geriye rastgele adlar kalır — düşen bir koşudan sonra klasörde ne bulunacağı
okunabilir olmalı.

Ad: hedefin adı + `.writing`. Bitmiş bir dosyayla karışmayacak kadar açık, ve klasöre bakan biri ne
olduğunu anlıyor.

## Düşünce: aynı anda iki yazma

İki yazma aynı hedefe aynı anda giderse ikisi de aynı `.writing` adını kullanır ve biri diğerinin
dosyasını taşır. Bu **kabul ediliyor**: uygulamanın varsayımı tek kullanıcı tek oturum, ve o varsayım
Madde 58'de kullanıcıya yazılıyor. Rastgele bir sonek eklemek bu yarışı kapatmaz — yalnız daha az
görünür kılar — ve kapatmanın yolu kilit, ki o ayrı bir karar.

## Düşen yazma arkasını toplar

Yarım bir `.writing` çöptür, delil değil. Ve bu klasörler **arayüzde listeleniyor**
(`file_file_store` `files/` dizinini doğrudan okuyor), yani kalan bir dosya kullanıcının kendi
dosyalarından biri gibi görünürdü.

Temizlik `except` içinde ve `raise` ile devam eder: hata **yutulmaz**, yalnız arkası toplanır.
`BaseException` yakalanır çünkü `KeyboardInterrupt` de yarım bir dosya bırakır ve o da temizlenmeli.

Temizliğin kendisi patlarsa bastırılır — asıl hatanın üstüne binen bir ikinci hata, kullanıcıya
sebebi yanlış söyler ve bu deponun kuralı sebep uydurmamak.

## Değişmeyen

`write_text`'in imzası, kök hapishanesi (`_full`), eksik dizinlerin oluşturulması. Çağıranların
hiçbiri değişmiyor: aynı fonksiyon, aynı sözleşme, farklı garanti.
