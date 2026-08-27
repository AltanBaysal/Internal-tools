# Madde 101 — Start a scenario doğar · **test turu**

**Tarih:** 2026-08-28 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [akış tasarımı](../../2026-08-27-queenagent-akis-tasarimi.md) — ve
[v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Blok 6, Madde 101 ·
**Şartı:** 96, 97, 98 — şema aracı, edit kipinde plan, karakter denemesi. Üçü de bitti.
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod bir sonraki turda.

---

## Ne doğuyor

İki şey: bir yönerge metni *(`domain/skills.py`)* ve seçicide ikinci bir satır
*(`frontend/.../skills.js`)*. Başka hiçbir şey — akışın kullandığı beş aracın hepsi yerinde, ve
akışın kendisi bir kod parçası değil, modele söylenen bir yol.

## Metnin taşıması gerekenler

Tasarımın kararları teker teker sınanıyor. Testler **metnin içindeki sözcükleri** tutuyor, çünkü
tutulabilecek başka bir şey yok: yönerge bir ürün davranışı, ve doğruluğu ne dediğidir.

| Karar | Nerede yazılı |
|---|---|
| İlk iş plan, kullanıcı ne yazmış olursa olsun | Adım 1 |
| Yarım kalan plan sürdürülüyor, yenisi yazılmıyor | Adım 1, *"yeni sohbetten devam"* |
| Yazmadan önce şema okunuyor | *"Şema araçtan okunuyor"* |
| Her adım onaya kadar dönüyor | İki kural |
| Anlatılmayan için yer tutucu, akış durmuyor *(K34)* | Adım 2 ve 3 |
| Sahneler iki yerde: yapı dosyası ve okunacak liste *(K33)* | Adım 4 |
| Promptları akış kendisi kuruyor *(K32)* | Adım 5 |

## Devrilen iki iddia

Bugün iki test *"tek skill var"* diyor — biri arka yüzde, biri ön yüzde. İkisi de bu maddenin
devirdiği cümleler, ve test turunda yerlerini iki satırı sayan hâllerine bırakıyorlar.

## Kırmızılar

### A · `test_skills.py` — yönerge

1. `ALL_SKILLS` ikinciyi alıyor, ve parametreli test onun da bir yönergesi olduğunu soruyor.
2. Menü ile yönergeler aynı iki adı taşıyor — *"tek skill"* testinin yerine geçen.
3. Plan yazmak ilk iş: `write_plan`, `read_schema`'dan önce anılıyor.
4. Projede duran bir plan sürdürülüyor, yenisi yazılmıyor.
5. Adım kullanıcı onaylayınca bitiyor, cevap yazılınca değil.
6. Anlatılmayan şey yer tutucu oluyor, ve akış durmuyor.
7. Sahneler iki yere yazılıyor: biri okunacak liste, her sahne bir cümle.
8. Promptları akış kuruyor, ve kullanıcı son adımda skill değiştirmiyor.

Bugünkü iki süpürme testi — *"hiçbir yönerge kareye shot demiyor"* ve *"hiçbir yönerge kural
kitabını taşımıyor"* — yeni metni **kendiliğinden** kapsıyor. Yeşiller, ve öyle kalmaları gerekiyor.

### B · `skills.test.js` — seçici

9. Seçici iki satır taşıyor, ve sırası akış önce.
10. `skillName("start-a-scenario")` adı veriyor.
11. İki satırın açıklaması birbirini ayırıyor: prompt+ **elde olan** bir yapı dosyasından
    çalıştığını söylüyor.

Onbirincisi seçicinin asıl işi. İki satır aynı işi anlatıyorsa seçici kullanıcıya bir şey
söylemiyor demektir.

## Dokunulmayan

| Ne | Neden |
|---|---|
| Araçlar | Beşi de yerinde; akış yeni bir araç istemiyor |
| `prompt.py` | Nasıl çalışılacağı orada, ve her skill'e uyuyor |
| `schema.py` | Şema araçtan geliyor *(Madde 96)*; metne girmiyor |
| Kip | Akış dosya yazıyor, yani edit — ya da soru kipinde izin isteyerek *(Madde 99)* |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Arka yüzde dokuz kırmızı, ön yüzde üç. **İki kırmızı bu maddenin değildir:** `test_notebook`'un
ikisi — defterin `BRANCH`'i koşu bitince `main`'e dönecek.
