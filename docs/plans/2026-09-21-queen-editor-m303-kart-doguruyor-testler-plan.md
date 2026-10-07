# Madde 303 — Kart doğuruyor, test turunun planı

**Spec:** [m303 test turu](../specs/2026-09-21-queen-editor-m303-kart-doguruyor-testler-design.md)

Tek test dosyası: `backend/tests/test_photo_usecases.py`. Kaynak koda dokunulmuyor.

## Neden orada

Referans üretimi bir **koşu**: runner, kayıt, plan, üretici ister. O sahtelerin hepsi bu dosyada
duruyor, ve referans havuzunun sahtesi altı satır. Testleri `test_reference_usecases.py`'a koymak
kuyruğun bütün kurgusunu ikinci kez yazmak olurdu.

Maddenin *"görülür"* cümlesi de burada: galeriyi aynı dosya zaten okuyor.

## Adımlar

1. İki küçük sahte *(havuz ve sıra)*, ve bir `run_references` yardımcısı.
2. Altı test.
3. **Dört test satırı koşulur.**

## Beklenen kırmızı

`queue_references` bugün beş argüman alıyor ve sıfır dönüyor; altısı da düşer.
