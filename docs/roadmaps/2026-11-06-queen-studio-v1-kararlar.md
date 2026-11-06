# Queen Studio v1 — Koşuda verilen kararlar

[Roadmap](2026-11-06-queen-studio-v1-roadmap.md) koşarken ana agent'ın kullanıcıya sormadan verdiği
kararlar. Koşu bitince kullanıcıyla bu belgenin üstünden geçilir.

Her karar: hangi maddede, ne karar verildi, neden, başka seçenekler neydi, hangi belge değişti.

## Sapmalar

Kod yazılırken tasarımdan ya da kurallardan farklı yapılanlar: hangi maddede, hangi adımın neyinden
neye, neden, hangi belge düzeltildi.

Henüz sapma yok.

## Koşudan önce, belgelerin gözden geçirilmesinde

1. **Kaynak karesi silinmiş `i2v` işi saklanan fotoğrafla yapılır** ([v1-18](2026-11-06-queen-studio-v1-roadmap.md#v1-18)).
   Neden: 4. adım fotoğrafı iş için zaten saklıyor; iş durmadan yapılabilir. Seçenek: kuyruğu
   `source_frame_missing` ile durdurmak; kaldırıldı. Değişen: 2., 4., 6. adım.
2. **Kuyruk maddesi ikiye bölündü** ([v1-17](2026-11-06-queen-studio-v1-roadmap.md#v1-17),
   [v1-18](2026-11-06-queen-studio-v1-roadmap.md#v1-18)): kuyruğun kendisi; kendiliğinden durması ve
   core'un yeniden başlaması. Neden: tek madde bir coder'a fazla büyüktü. Seçenek: tek madde. Değişen:
   roadmap, numaralar v1-32'ye kaydı.
3. **Dört Colab'ın hız sınırı bu makineden, deneme hesabıyla dört süreçle ölçülür**
   ([v1-4](2026-11-06-queen-studio-v1-roadmap.md#v1-4)). Neden: testte ücretli katman kullanılmaz ve ölçümler yalnız deneme hesabıyla yapılır.
   Seçenek: dört gerçek Colab. Değişen: 4. adım.
4. **Sürüm kuralı için yer tutucu sayfa** ([v1-3](2026-11-06-queen-studio-v1-roadmap.md#v1-3)): ekran
   yalnız "Queen Studio V1" yazar; tasarlanan ekranlar sonda yerine geçer. Neden: UI en sonda yapılır,
   ilk madde de kurulumdur; sürüm yine ilk ekranda görünür. Değişen: 13. adım, roadmap.
5. **VS Code'un Colab eklentisine düşülmez** ([v1-1](2026-11-06-queen-studio-v1-roadmap.md#v1-1)):
   yalnız Google'ın Colab CLI'ı. Neden: eklentide runtime'ı seçmek ve her hücreyi çalıştırmak
   kullanıcının tıklamasını istiyor; koşu kullanıcıyı beklemeden yürümeli. Seçenek: CLI olmazsa
   eklenti. Değişen: 10. adım, roadmap.
