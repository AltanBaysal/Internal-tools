# Madde 91 — Kip gelir: plan, sor, düzenle · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 5, Madde 91 ·
**Şartı yok**, ama 94'ten önce gelmesi gerekiyor
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder.

---

## Bugün ne oluyor

Modelin neyi yapıp yapamayacağı bir yönergeyle tutuluyor. En açık örneği kontrol skill'i:

> *"Do not fix anything. Do not create a file and do not edit one."*

Bir yetki kuralı ricaya çevrilmiş. Rica tutmadığında kontrol eden skill dosya düzeltiyor, ve
kimse bunu engellemiyor — araçlar isteğin içinde duruyor, model yalnız kendini tutmaya çalışıyor.

## Ne olur

Üç kip, ve kip **hangi araçların isteğe konduğunu** belirliyor:

| Kip | İsteğe konan araçlar |
|---|---|
| **sor** | `list_files`, `read_file` |
| **plan** | `list_files`, `read_file`, `write_plan` |
| **düzenle** | `list_files`, `read_file`, `create_file`, `edit_file`, `build_prompts` |

Sor kipinde model dosya yaratmıyor — kendini tuttuğu için değil, yaratacak aracı olmadığı için.

Varsayılan **düzenle**: bugünkü davranış.

## Plan kipi ve altıncı araç

*(kullanıcı kararı, 27 Ağustos)*

Plan kipine `create_file` verilseydi model aynı turda hem planı hem teslimatı yazabilirdi — yani
planlamak yerine işi yapabilirdi, ki maddenin şikâyet ettiği tam olarak bu. Kural bir sayaçta değil
araç kümesinde duracaksa, plan kipinin elinde **plandan başka bir şey yazacak araç olmamalı**.

Altıncı araç: **`write_plan(name, content)`**. Yaratır ya da üstüne yazar — "eldeki planı
güncelleyebilir veya plan oluşturabilir" bu. Model önce `read_file` ile eldekini okur, sonra
bütününü geri yazar; ayrı bir düzenleme yolu yok, çünkü plan kısa ve bütününü yazmak parça
yamamaktan güvenli.

Adı **`-plan.md`** ile bitmeye zorlanıyor. İki iş birden yapıyor: diskte planın plan olduğu
görünüyor, ve araç bir teslimat dosyası yazmak için kullanılamıyor.

`create_file`'ın aksine **üstüne yazıyor**. Bir planın ikinci sürümü `x-plan-2.md` olsaydı hangisinin
güncel olduğu kaybolurdu. İlk yazışta bir dosya doğuyor ve kart çıkıyor; sonrakiler aynı dosyayı
değiştiriyor, ve `edit_file` ile aynı kural gereği kart çıkmıyor.

**Tur `write_plan`'dan sonra biter.** Plan diske indi, sıra kullanıcıda: okur, isterse dosyanın
kendisinde düzeltir, sonra düzenle kipinde yürütür.

`write_plan` düzenle kipinde **yok**. Plan orada sıradan bir dosya, ve `edit_file` onu değiştiriyor.

## Kipin metni yok

Ne yapılacağını **aracın kendi açıklaması** söylüyor, ayrı bir kip yönergesi değil. Sebebi ikili:
bir aracın nasıl kullanılacağı zaten açıklamasında duruyor, ve Madde 93 yönergenin isteğin neresine
gireceğini yeniden düzenliyor — bu madde oraya yeni bir metin bırakmıyor.

## Kip nereye yazılır

Hiçbir yere. Kip istekle birlikte geliyor ve orada bitiyor.

Skill mesaja yazılıyor çünkü sonraki turlarda konuşma yeniden kurulurken yönergesi ondan
okunuyor. Kipin böyle bir okuyucusu yok: o anda hangi araçların konduğuna karar veriyor, ve o karar
verilmiş oluyor. Okuyanı olmayan bir alan `test_a_chat_carries_no_model`'ın yasakladığı şey.

## Ekranda

Composer'ın ayağında, **Skills'in solunda**: Mode · Skills · model · Send. Kip skill'i yönetiyor —
modelin ne yapabileceği, hangi işi yaptığından önce gelen bir soru — ve satır dıştan içe okunuyor.

Skill seçicinin birebir eşi: adını taşıyan bir düğme ve üç satırlık bir menü. Bir fark var —
**seçili kipe basmak onu temizlemiyor.** Skill'in olmaması olağan hâl, kipin olmaması diye bir şey
yok.

İki seçici birbirini kapatıyor, ve Escape hangisi açıksa onu kapatıyor. Bu davranış Madde 82'de
model seçici düşene kadar vardı; ikinci seçici geri geldiği için geri geliyor.

## Kırmızıya dönecek testler

**`test_tools.py` — üç**

1. `write_plan` planı yazıyor ve adını `-plan.md` ile bitiriyor.
2. Aynı adla ikinci kez yazmak üstüne yazıyor — numaralı ikinci bir dosya doğmuyor — ve ikinci
   yazış bir dosya doğduğunu iddia etmiyor.
3. Zaten `-plan.md` ile biten bir ad ikilenmiyor.

**`test_modes.py` — beş *(yeni dosya)***

4. Sor kipi yalnız okuma araçlarını koyuyor.
5. Plan kipi okuma araçlarını ve `write_plan`'i koyuyor, başka hiçbir yazma aracını koymuyor.
6. Düzenle kipi eski beş aracı koyuyor, `write_plan`'i koymuyor.
7. Tanımadığı bir kip düzenle sayılıyor: eski bir tarayıcı ya da boş bir alan araçları sessizce
   düşürmüyor.
8. Turu bitiren tek çağrı plan kipindeki `write_plan`: aynı araç düzenle kipinde olsa bile turu
   bitirmiyor, ve plan kipindeki bir okuma da bitirmiyor.

**`test_stream_answer.py` — üç**

9. İsteğe konan araçları kip belirliyor — motorun gördüğü liste kipe göre değişiyor.
10. Plan kipinde tur plan yazılınca bitiyor: ikinci bir tur hiç sorulmuyor.
11. Kip söylenmemişse düzenle: beş araç gidiyor.

**`test_chats_api.py` — iki**

12. Kip istekle birlikte geliyor ve isteğe konan araçlara dönüşüyor.
13. Kip kayda yazılmıyor.

**`ModePicker.test.jsx` — üç *(yeni dosya)***

14. Düğme o anki kipin adını taşıyor.
15. Bir kip seçmek onu yukarı veriyor.
16. Seçili kipe basmak temizlemiyor — kipsizlik diye bir şey yok.

**`ChatScreen.test.jsx` — bir**

17. Ayakta kip seçici Skills'in solunda duruyor.

**`App.test.jsx` — üç**

18. Gönderilen mesaj o anki kiple gidiyor.
19. Bir seçiciyi açmak ötekini kapatıyor.
20. Escape açık olan seçiciyi kapatıyor.

Toplam **yirmi kırmızı.**

## Ölçüsü değişen test

`test_every_tool_is_declared_to_the_model` beş aracı sayıyor; altı oluyor. İddiası değişmiyor:
modele bildirilen küme ile kodun tanıdığı küme aynı kalmalı.

## Dokunulmayan

| Ne | Neden |
|---|---|
| Beş aracın kendisi | Değişen yalnız hangilerinin konduğu |
| Skill metinleri | 94'ün işi — bu madde onların yerine geçecek mekanizmayı kuruyor |
| Yönergenin isteğin neresine gireceği | 93'ün işi |
| `Message.skill` | Kip onun yerine geçmiyor, yanında duruyor |
| Tavan ve daire | 92 yerinde |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` bu turda derlenmiyor — uygulama turunda derlenip aynı commit'e giriyor.
