# Madde 178 · uygulama turu — iki metin yeniden yazıldı

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m178-skill-testler-design.md).
Commit `74d6b20` 12 kırmızı bıraktı.

---

## Sınır nereye taşındı

**Start a scenario** artık dört şey yapıyor ve dördüncüsü yeni: planı yazıyor, senaryoyu açıp
haritaları dolduruyor, **ve kareleri yazıyor** — sahnesiyle, kadrosuyla, mekânıyla, **action'sız.**

Eski metinde 4. adım bir `.md` yazıyordu ve yapı dosyasının kareleri *"bilerek boş"* kalıyordu.
İkisi de gitti: sahne cümlesi artık karenin alanı, ve `add_scene` onu kadrosuyla birlikte alıyor.

**Generate prompts+** iki şey yapıyor: her `action`'sız kare için `write_frame_prompt`, sonra
`build_prompts`. *"Action'sız kare bekleyen iştir"* cümlesi eski *"cümlelerden az kare"* kuralının
yerini alıyor — aynı işi görüyor *(odası dolan bir sohbet nereden devam edeceğini dosyadan
okuyor)*, ama artık ikinci bir dosyaya bakmadan.

## Şikâyetin iki yolu

Metin ikisini de adlandırıyor, çünkü iki farklı şikâyete cevap veriyorlar:

- **Bir karenin cümlesi kötü** → o kare **notla** yeniden yazdırılıyor.
- **Biri her karede yanlış görünüyor** → haritadaki girdi, `update_character` / `update_outfit` /
  `update_location`; tek değişiklik o adı anan her kareye ulaşıyor.

Eskisi ikisini de `edit_file`'a bağlıyordu, ve 171'den beri o yol `.json` için kapalı.

## Kelime tavanı nasıl tutuldu

Metinlere yeni cümleler girdi; yerini **çıkanlar** açtı: sahne listesi paragrafı, iskelet cümlesi,
*"kareler asla burada yazılmaz"* yasağı *(artık yazılıyorlar)*, ve zanaat kuralları — ikisi de
`WRITE_FRAME_SYSTEM_PROMPT`'a taşındı, orada tek kopya. **Bir cümle ancak bir cümle silinerek
giriyor**, 123'ten beri kuralı bu.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **804 yeşil**, ilk koşuda. 12 kırmızının hepsi döndü.
3. Öteki üç takım rakamlarını korudu: **589 · 739 · 591.** `dist` derlenmedi.
