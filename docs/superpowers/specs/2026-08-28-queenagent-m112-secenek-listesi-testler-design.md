# Madde 112 — Cevabın sonuna seçenek listesi eklenmez · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 112.
**Gözlenen** *(28 Ağustos)*: model her turun sonuna beş şıklı bir menü yazıyor — *"Bütün 10
prompt'u görmek ister misin · Birkaç tanesini değiştirelim mi · Başka bir şey ekleyelim mi ·
Hiçbir şey yapmamak"*. Akış zaten adım başına tek soru soruyor; menü cevabı uzatıyor ve kararı
kullanıcıya kalabalık hâlde geri veriyor.

## Nereye yazılır

**Taban yönergeye** — akışa değil. Menü koşuda yalnız akış adımlarının değil, kurulum ve kapanış
turlarının sonunda da çıktı; her skill'in üstünde duran davranış taban yönergenin işi *(Madde 73)*.
Yeri kapanış paragrafı: *"End by saying what you did"* cümlesinin hemen ardı, çünkü mesele turun
nasıl **bittiği**.

## Kural

Bir tur ya kararı belirleyen **tek soruyla** biter ya da hiç soru olmadan. Yapılabileceklerin
listesi bir bitiş değil — işi kullanıcıya geri vermektir.

## Test — `test_prompt.py`, bir yeni

Taban metinde `"list of things you could do next"` ve `"ask the one question"` geçiyor.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_prompt.py` | 1 |

Defter çifti bu maddenin değil.

## Bilerek yapılmayanlar

- **Akış metnindeki onay döngüsü ellenmez** — o zaten tek soru soruyor; sorun onun üstüne eklenen
  liste.
- **"Ask rather than invent" paragrafı ellenmez** — eksik bilgiyi sormak sürüyor; kalkan şey
  yapılabilecekler menüsü.
- **`dist` derlenmez.**
