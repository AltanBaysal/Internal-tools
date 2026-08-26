# Madde 77 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-26-queenagent-m77-secici-proje-ekraninda-testler-design.md](../specs/2026-08-26-queenagent-m77-secici-proje-ekraninda-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Yeni ad yok

`SkillPicker`, `ModelPicker` ve `Composer`'ın `foot`u duruyor ve `ChatScreen`'de kullanılıyor.
`ProjectScreen` yeni **prop**'lar alacak — `picker`, `onPicker`, `model`, `skill`, `onModelChange`,
`onSkillChange` — ama bir React bileşeni tanımadığı prop'u sessizce yok sayar, yani toplama hatası
riski yok.

## Dosyalar

`frontend/src/features/workspace/ProjectScreen.test.jsx` · `frontend/src/App.test.jsx`

Arka uca dokunulmuyor.

## Testler

### `ProjectScreen.test.jsx` — dört yeni test, bir silinen

Silinen: *"the composer here carries neither picker"*. Bu maddenin tam tersini söylüyor, ve
çevirmek yerine yerine geçen dördü yazılıyor — tek bir yokluk iddiası, dört varlık iddiasına
bölünüyor.

Yazma kutusunun altı `Skills`, model ve `Start`'ı **bu sırayla** taşıyor — `ChatScreen`'in
sırasının aynısı, çünkü iki ekranda farklı sıra aynı şeyi iki kez öğrenmek demek.

Seçilen skill yukarı veriliyor, ekranda tutulmuyor. Seçilen model de öyle. Hangi menünün açık
olduğu ekrana söyleniyor, ekran kendi karar vermiyor — Escape'i tek dinleyici sahiplendiği için.

### `App.test.jsx` — beş çevrilen, bir yeni, bir tersine dönen

**Çevrilenler** — hepsi 65'in testleri, soruları duruyor, cevapları değişiyor:

| Test | Yeni beklenti |
|---|---|
| Açılış nereye düşüyor | `/p/p1` ve `.screen__title`'da proje adı |
| `/settings` gibi tanınmayan adres | `/p/p1` |
| Fork tarihe yazılıyor mu | Adres `/p/p1`, `replace` çağrılmış, `push` çağrılmamış |
| Sunucuya `settings` sorulmuyor | İddia aynı; beklenen ekran proje ekranı |
| Hiçbir şey yazmadan skill seçilebiliyor | Aynı soru, **proje ekranında** soruluyor |

**Tersine dönen:** 65'te *"proje ekranı hâlâ sidebar'dan açılıyor mu"* diye soruluyordu. Proje
ekranı artık açılışın kendisi; sorulacak olan **taslak sohbetin hâlâ ulaşılabilir olduğu** —
sidebar'ın `New chat` düğmesiyle. Maddenin maliyeti bu tarafa geçti.

**Yeni:** seçilen skill başlayan sohbete geçiyor. Proje ekranında skill seçiliyor, bir cümle
yazılıp `Start`'a basılıyor, ve `POST /api/projects/p1/chats` gövdesi o skill'i taşıyor. **Görüntüyle
davranışı ayıran tek test bu** — düğmenin adının değişmesi bir görüntü, sohbetin o skill'le doğması
davranış.

**Dosyanın altındaki yorum düzeliyor.** Bugün *"Madde 65'ten beri fork taslak sohbete düşüyor, o
yüzden aşağıdaki her test kendi adresini itiyor"* diyor. Testlerin kendi adresini itmesi hâlâ
doğru ve hâlâ gerekli — sebep değişiyor: fork artık proje ekranına düşüyor, ve bir açılışı
beklemek 77'yi dokuzuncu kez test etmek olurdu.

## Beklenen kırmızı

**Ön yüzde 11 kırmızı:** dördü proje ekranının yeni testleri (seçiciler henüz yok), yedisi `App`'te
— beş çevrilen, bir tersine dönen, bir yeni.

**Yeni test — seçilen skill sohbete geçiyor — de kırmızı**, ama iki sebepten: seçici yok, ve
açılış proje ekranında değil. İkinci tur ikisini birden açar.

**Arka uçta değişiklik yok:** `2 failed, 432 passed`, ikisi defterin dalı.

**Var olan başka bir ön yüz testi bu yüzden düşmemeli.** `ProjectScreen`'in geri kalanı prop
eklenmesinden etkilenmez; `App`'in silme testleri zaten kendi adresini itiyor. Düşen olursa mekanik
değil gerçek bir kırılmadır.

**İlk koşuda 20 düştü, ve dokuzu benim hatamdı.** Ekranın beklediği başlığı toplu değiştirirken —
`replace_all` — aynı satırdan on bir tane olduğunu görmemişim: ikisi `Old` adlı projeyi, dokuzu
`Thesis` adlı projeyi bekliyordu. Dokuzunu da `Old`'a çevirmiş oldum ve hiçbiri bu maddeyle ilgili
değildi. **Ders:** aynı görünen satır aynı şeyi söylemiyor olabilir; toplu değiştirmeden önce kaç
tane olduğu sayılır.

## Bu turda yapılmayan

`App`'in fork yönlendirmesinin geri alınması · `ProjectScreen`'in `foot`u · prop'ların `App`'ten
geçirilmesi · `dist` derlemesi. Hepsi ikinci tur.
