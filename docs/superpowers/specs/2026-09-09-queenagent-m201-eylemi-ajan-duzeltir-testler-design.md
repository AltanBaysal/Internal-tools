# Madde 201 · test turu — eylem satırını ana ajan düzeltir

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 201.

---

## Bugün ne oluyor

`update_frame` sahneyi, kadroyu ve mekânı değiştiriyor; **action'a bilerek dokunmuyor**
*(Madde 174, ve metninde yazılı: "A frame's action is not among these")*. Bir satır yanlış
okunduğunda tek yol `write_frame_prompt`'u **notla** yeniden çağırmak — yani ajanın bildiği şeyi bir
nota sıkıştırıp ikinci bir modele vermek.

Gerekçesi Madde 176'nındı: ana model o cümleyi iyi yazmıyordu. **O gerekçe kalktı**
*(kullanıcı, 8 Eylül)*.

## Ne kurulacak

- `update_frame` bir **`action`** alanı alır. Öteki alanlar gibi: verilmezse dokunulmuyor, boş
  verilirse satır **kareden kalkıyor** *(Madde 173: karesiz doğan kare tam olarak böyle görünür)*.
- `UPDATE_FRAME` metni artık okuyucuyu başka bir araca göndermiyor.
- *Edit prompts* yanlış okunan satırı **ajanın kendi turunda** düzelttiriyor.

### İki yol değil, iki iş

`write_frame_prompt` duruyor, ve notu da duruyor. Ayrım söylenebilir: **satırın ne olması
gerektiğini biliyorsan** onu kendin yazıyorsun; **sahneden yeniden yazılmasını** istiyorsan yazara
gidiyorsun. Düzeltmek ile yeniden yazdırmak aynı iş değil.

## Testler

### `test_tools.py`

1. **ajan satırı kendi yazar** — `update_frame`'e verilen `action` dosyaya iner.
2. **boş verilen action satırı kaldırır** — alan kareden kalkar, boş string olarak kalmaz.
3. **şema action alıyor** — `update_frame`'in parametreleri arasında.
4. **metin başka araca göndermiyor** — `UPDATE_FRAME` action'dan söz ediyor, ve *"is not among
   these"* cümlesi gitti.
5. **verilmeyen action'a dokunulmuyor** — bugünkü test yerinde kalıyor *(yalnız verilen değişir)*;
   yorumu bu maddeye göre düzeltiliyor, çünkü bir yorum bugün doğru olanı söyler.

### `test_skills.py`

6. **düzeltme ajanın kendi turunda** — *Edit prompts* `update_frame`'i adıyla anıyor ve satırı
   **kendin yaz** diyor.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. Arka uçta **5 kırmızı**: `action` bugün sessizce
düşüyor, şemada yok, ve iki metin hâlâ okuyucuyu ikinci modele gönderiyor. Ön yüz ve `queen-editor`
kımıldamıyor: **648 · 739 · 591** yerinde.
