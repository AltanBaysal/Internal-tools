# Madde 73 — Agentic davranış taban yönergeye iner · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Madde 73 ·
**Neden burada:** Blok 5 tek istisna olarak içine aldı — 94'ün şartı
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder.

---

## Bugün ne oluyor

Taban yönerge dört kısa paragraf: kim olduğu, proje dosyalarını görebildiği, ne zaman dosya
yazacağı, ve cevabı sohbete de yazması.

Ne zaman okuyacağı, ne zaman soracağı, uzun bir işi neden böleceği, sonunda ne yaptığını söylemesi
gerektiği — hiçbiri orada değil. Hepsi tek tek skill metinlerinin içinde, ve aynı cümle üç ayrı
metinde tekrar ediyor:

> *"Quality falls away towards the end of a long stretch"* — üç skill'de.
> *"A correction that only lands in the chat leaves two..."* — iki skill'de.
> *"ask ... rather than inventing it"* — üç skill'de.

Sonucu iki türlü kötü. Skill seçilmemiş bir konuşmada bu davranışların **hiçbiri** yok. Ve aynı
kural üç yerde durduğu için biri değişince ötekiler eskiyor.

## Ne olur

Hangi skill seçili olursa olsun geçerli olan davranış tabana iner. Dört kural:

1. **Yazmadan önce bak.** Cevap bir dosyaya dayanıyorsa o dosya okunur — sohbette geçmiş olması
   okumuş olmak değil.
2. **Uydurma, sor.** Kullanıcının kararlaştırmadığı bir şey tahmin edilmez.
3. **Uzun iş parça parça.** Uzun bir yazının sonuna doğru kalite düşüyor, ve her parça bir
   sonraki yazılmadan diske iniyor — kesinti o zaman her şeye değil bir parçaya mal oluyor.
4. **Ne yaptığını söyle.** Değişmesi gereken bir şey olmadığında da: sessizlik bir cevap değil.

## Bu maddenin sınırı

**Tabana yalnız agentic olan iner** *(kullanıcı kararı, 27 Ağustos)*. Göreve özel hiçbir şey
girmiyor — senaryo, kare, karakter, prompt, SDXL, yapı dosyası. Onlar skill'in bilgisi ve orada
kalıyor.

Ayrım şurada: *"parça parça yaz"* agentic, *"beşerli gruplar hâlinde kare ekle"* göreve özel.
*"Sohbetteki düzeltme dosyaya da insin"* agentic, *"`bar-scene-frames.md`'yi `edit_file` ile
düzelt"* göreve özel.

Bu sınırın bir bekçisi var, ve testlerden biri o: **taban yönerge hiçbir görev adı taşımıyor.**

## Bu madde skill metinlerini silmiyor

Yalnız ekliyor. Silme 94'ün işi, ve 94 bunu adıyla sayıyor: *"Yanında düşen: skill metinlerindeki
yapma-etme cümleleri, ve uzun işi gruplara bölmeyi rica eden paragraflar."*

Sıra bu yüzden böyle. 73 davranışı tabana koyuyor, 94 kopyaları güvenle siliyor. Ters sırada
silinen şey hiçbir yerde olmayan şey olurdu.

## Kırmızıya dönecek testler

**`test_prompt.py` — altı**

1. Taban, cevap bir dosyaya dayanıyorsa önce okumayı söylüyor.
2. Kararlaştırılmamış bir şeyin uydurulmayıp sorulmasını söylüyor.
3. Uzun işin parça parça yürüdüğünü, ve her parçanın bir sonraki yazılmadan indiğini söylüyor.
4. Sohbetteki bir düzeltmenin dosyaya da inmesini söylüyor.
5. Turun sonunda ne yapıldığının söylenmesini istiyor — değişecek bir şey çıkmadığında da.
6. **Bekçi:** taban hiçbir görev adı taşımıyor.

Toplam **altı kırmızı.**

## Dokunulmayan

| Ne | Neden |
|---|---|
| `skills.py`'nin tamamı | Silme 94'ün işi; bu madde yalnız ekliyor |
| `test_skills.py`'nin tamamı | Aynı sebep — hiçbir skill metni değişmiyor |
| Tabanın var olan dört paragrafı | Doğrular ve yerlerinde kalıyorlar |
| Kip | 91 yetki kurallarını devraldı; bu madde davranışı söylüyor, yetkiyi değil |
| Ön yüz | Bir metin değişiyor, ekran değil |

## Yeşil kalması gerekenler

`test_the_app_forces_no_language_of_its_own` — tabanda `"English"` geçmiyor, ve yeni cümleler de
geçirmiyor. `test_the_answer_follows_the_language_it_was_asked_in` de yerinde.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Ön yüz baştan sona yeşil kalır. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` derlenmiyor.
