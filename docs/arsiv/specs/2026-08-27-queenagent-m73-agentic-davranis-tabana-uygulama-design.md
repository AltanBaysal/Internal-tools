# Madde 73 — Agentic davranış taban yönergeye iner · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Test turu:** [testler tasarımı](2026-08-27-queenagent-m73-agentic-davranis-tabana-testler-design.md) · kırmızı commit `eb46f7a`
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder. Yeni test yazılmaz.

---

## Tek dosya

`domain/prompt.py`. Başka hiçbir şey açılmıyor.

## Yedi paragraf

Dört paragraf yerinde kalıyor; ikisi genişliyor, üçü yeni. Sıra bir mantık taşıyor: önce ne olduğu,
sonra dosyalarla ilişkisi, sonra nasıl çalıştığı, en sonda ne söylemesi gerektiği.

| # | Ne der | Durumu |
|---|---|---|
| 1 | Kim olduğu, ve kullanıcının dilinde cevap verdiği | Aynı |
| 2 | Proje dosyaları, ve **cevap bir dosyaya dayanıyorsa önce onu okuduğu** | Genişliyor |
| 3 | Ne zaman dosya yarattığı | Aynı |
| 4 | **Sohbetteki düzeltmenin dosyaya da indiği** | Yeni |
| 5 | **Kararlaştırılmamış şeyi uydurmayıp sorduğu** | Yeni |
| 6 | **Uzun işi parça parça yaptığı, her parçanın bir sonraki yazılmadan indiği** | Yeni |
| 7 | Cevabın sohbete de yazıldığı, ve **sonunda ne yapıldığının söylendiği** | Genişliyor |

## İkinci paragraf niye genişliyor, yeni bir paragraf gelmiyor

Bugün zaten *"read_file to look inside one when the answer depends on it"* diyor. Yanına ikinci bir
paragraf koymak aynı kuralı iki kez söylemek olurdu. Eksik olan **sıra** — önce okumak — ve
sohbette görmüş olmanın okumuş olmak sayılmadığı. İkisi de var olan cümlenin içine giriyor.

## Sınır

Yeni cümlelerin hiçbiri bir görev adı taşımıyor. *"Parça parça yaz"* var, *"beşerli kare grupları"*
yok. *"Sohbetteki düzeltme dosyaya insin"* var, *"`bar-scene-frames.md`'yi düzelt"* yok.

Bekçi testi bunu yedi kelimeyle sınıyor, ve o test bu turda da yeşil kalıyor.

Tabanda `"English"` de geçmiyor — arayüzün İngilizce olması etiketlerle ilgili bir kural, cevabın
dilini kullanıcı belirliyor. Var olan test bunu tutuyor.

## Ne değişmiyor

`skills.py`'nin tek bir cümlesi bile. Bu madde **yalnız ekliyor**; kopyaların silinmesi 94'ün işi ve
94 onları adıyla sayıyor. Ters sırada silinen şey hiçbir yerde olmayan şey olurdu.

Kip de değişmiyor: 91 *yetki* kurallarını devraldı — neyin yapılabileceğini araç listesi söylüyor.
Bu madde *davranışı* söylüyor — yapılabilen şeyin nasıl yapıldığını.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

`eb46f7a`'nın beş kırmızısı yeşile döner; bekçi ve iki dil testi yeşil kalır.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` derlenmiyor.
