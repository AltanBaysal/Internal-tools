# Madde 417 — Agent'ın sohbetlerinin kaydı, test turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 417 · v9-4b · **Tur:** 1/2 — yalnız testler.

**Kullanıcıdan gereken — yok.** Madde hizalı; kararları yol haritasının *v9-4* bölümünde ve
tasarımın `BEHAVIOUR.md`'sinin *Agent panel* bölümünde *(queen-design `queen-editor-v2`, ana
klasörün `tmp/queen-design-queen-editor-v2/`'sinde)*. Kaydın biçimi teknik bir karar, Claude'un.
Madde çıktıyı değiştirmiyor: testler kırmızı commit'lenir.

## Bugün ne oluyor

Queen Editor'de agent da sohbet de yok. Projenin klasöründe ayarlar, plan, kayıt ve sıra dosyaları
duruyor *(CODE-STANDARD, Separation of concerns)*; sohbete ait hiçbir şey yok. Sunucunun
`/api/projects/<proje>/chats` diye bir kapısı yok — bugün o adrese giden GET, uygulamanın
`index.html`'ine düşüyor.

## Bu parçanın sınırı

417 yalnız **kaydı** ve **sunucunun kapısını** kurar. Agent 420'de — soruyu alan kapı, adımları ve
sonucu kayda yazan döngü, durdurma —, ekran 425'te. 417'nin kaydı ikisinin yazacağını ve
göstereceğini taşır:

- **420 yazar:** sorunun kendisi ve zamanı, her adımın sürerken ve bitince cümlesi, adımın bitmesi,
  sonuç — cevap, hata ya da durduruldu. Sonucu olmayan soru, agent'ı o sohbette çalışan sorudur.
- **425 gösterir:** sohbetin tamamı, ve liste — ilk soru ve son sorunun zamanı.

Kaydın yazan yöntemleri bu parçada kurulur ve testlenir — bitti sayılmanın *"sohbete soru ve sonuç
yazılıyor"*u —, ama onları çağıran bir kapı açılmaz: soru 420'de agent'ı başlatan kapıdan gelir, ve
cevabı tarayıcı hiçbir zaman yazamaz *(FOUNDATION, Karar 4)*.

## Kurallar

1. **Her projenin sohbetleri kendi klasöründe, tek dosyada** — `chats.jsonl`. Klasörün içinde
   oldukları için proje yeniden adlandırılınca onunla taşınır, silinince onunla silinir; arşiv
   yalnız bir işaret, sohbetler yerinde kalır. Başka projenin sohbeti görünmez: her proje yalnız
   kendi dosyasını okur.
2. **Kayıt yalnız eklenir, hiçbir satır yeniden yazılmaz** *(FOUNDATION 1 — fotoğraf kaydının
   kuralı)*: yazı sırasında ölen oturum en çok eklediği satırı kaybeder. Yarım kalmış son satır
   önündekileri gizlemez.
3. **Sunucu yeniden başlayınca her şey yerinde** *(FOUNDATION 2)*: kayıt bellekte tutulmaz; her
   okuma diskten.
4. **Bir sohbet** — `{"id": 1, "questions": [...]}`. Kimlik projenin içinde 1'den sayılır, en
   yüksek kimliğin bir fazlası; silme olmadığı için hiçbir kimlik yeniden kullanılmaz.
5. **Bir soru** — `{"text", "askedAt", "steps", "outcome"}`. `askedAt` yazanın verdiği zaman
   (ISO 8601, UTC, saniyeye kadar — öteki kayıtların biçimi). Soru metni olduğu gibi saklanır ve
   döner; tek satıra kesmek ekranın işi.
6. **Bir adım** — `{"running", "done", "finished"}`: sürerken cümlesi, bitince cümlesi, bitti mi.
   Adım başlarken iki cümlesiyle yazılır, `finished: false`; bitince işaretlenir. Adımlar ve sonuç
   sohbetin **son sorusuna** düşer.
7. **Sonuç** — `null` (sürüyor), `{"kind": "answer", "text"}`, `{"kind": "failure", "text"}` ya da
   `{"kind": "stopped"}`. Hata tek bir türdür ve kendi metnini taşır — ret cümlesi de *("Model hata
   döndü, farklı şekilde dene.")*, teknik hatanın kendi metni de: tasarım ikisini aynı kart olarak
   çizer, yalnız metin değişir.
8. **Yeni sohbet:** projede sorusu olmayan bir sohbet bekliyorsa o döner, yenisi yapılmaz; yoksa
   bir sonraki kimlikle boş bir sohbet yazılır ve döner.
9. **Liste:** yalnız sorusu olan sohbetler; son sorusu en yeni olan en üstte; her satır
   `{"id", "firstQuestion", "lastAskedAt"}` — ilk sorunun bütün metni ve son sorunun zamanı.
10. **Açmak:** sohbet her şeyiyle döner. Olmayan sohbet: *"Sohbet yok: 7"*.
11. **Olmayan proje:** üç kapı da *"Proje yok: <ad>"* der *(projeler özelliğinin cümlesi)*, ve yeni
    sohbet isteği proje klasörü yaratmaz — kökün her klasörü bir projedir.
12. **Silmenin kapısı yok.**
13. **Disk hatası** — işletim sisteminin kendi sözleri, 500 *(öteki kapıların kuralı)*.

## Arayüz — uygulama turunun vereceği

Yeni özellik: `backend/features/agent/` *(CODE-STANDARD — kullanıcının gördüğü yeni bir yetenek;
420'nin agent'ı da buraya gelir)*.

- **`data/chat_record.py`** — `DriveChatRecord(storage)`:
  `project_exists(project) -> bool`; `chats(project) -> list[dict]` (her sohbet, açıldığı sırayla);
  `add_chat(project, chat_id)`; `add_question(project, chat_id, text, at)`;
  `add_step(project, chat_id, running, done)`; `finish_step(project, chat_id)`;
  `answer(project, chat_id, text)`; `fail(project, chat_id, text)`; `stop(project, chat_id)`.
- **`domain/usecases/chats.py`** — `ProjectMissing`, `ChatMissing`; `new_chat(record, project)`,
  `list_chats(record, project)`, `open_chat(record, project, chat_id)`.
- **`presentation/routes.py`** — `make_chats_blueprint(new_chat, list_chats, open_chat)`:
  - `POST /api/projects/<proje>/chats` → 200, sohbet (yeni ya da bekleyen boş olan).
  - `GET /api/projects/<proje>/chats` → 200, `{"chats": [satırlar]}`.
  - `GET /api/projects/<proje>/chats/<id>` → 200, sohbet.
  - 404 `{"error": "Proje yok: …"}` / `{"error": "Sohbet yok: …"}`; 500 `{"error": <OS'un metni>}`.
- **`main.py`** kapıyı bağlar.

## Nasıl kanıtlanıyor

Kayıt gerçek `DriveStorage`'la, geçici bir klasörde koşar — öteki kayıtların testleri gibi. Use
case'ler sahte bir kayıtla *(CODE-STANDARD, Tests)*. Kapı, `main.py`'nin yaptığı bağlamayla elle,
geçici klasörde; 420'nin yazacaklarını test kaydın kendi yöntemleriyle yazar. `main.py`'nin bağlaması
`test_composition_root.py`'de, kapının olmayan projeye cevabıyla. Yeni modüller testlerin içinde
import edilir: dosyanın başındaki bir import, modül yazılmadan önce bütün toplamayı durdurur.

## Yazılacak testler

### `backend/tests/test_chat_record.py` — yeni; kayıt, geçici klasörde

1. **Sohbeti olmayan proje boş okunur** — `chats("düğün") == []`.
2. **Yeni sohbet sorusuz okunur** — `add_chat(1)` → `[{"id": 1, "questions": []}]`.
3. **Soru adımlarıyla ve cevabıyla okunur** — iki adım, ikisi de bitti, cevap: sorunun tamamı
   beklenen sözlük.
4. **Süren adım bitmemiş okunur, sorunun sonucu yok** — `finished: false`, `outcome: None`.
5. **Hata kendi metnini taşır** — parametreli: ret cümlesi, ve bir teknik hatanın kendi metni.
6. **Durdurulan soru durdurulduğunu söyler** — `{"kind": "stopped"}`; biten adım yerinde.
7. **Adımlar ve sonuç sohbetin son sorusuna düşer** — iki soru; ikincinin adımı ve cevabı birinciye
   dokunmaz.
8. **Aynı anda yazılan iki sohbet birbirine karışmaz** — iki sohbetin satırları sırayla, iç içe:
   her biri kendi sorusunu, adımını ve cevabını taşır; açıldıkları sırayla okunur.
9. **Başka projenin sohbeti bu projede yok** — `düğün`'e yazılan, `kına`'da okunmaz.
10. **Kayıt projenin kendi klasöründe tek dosya** — klasörde yalnız `chats.jsonl`.
11. **Yazmak yalnız ekler** — sonraki yazıdan sonra dosyanın başı öncekiyle aynı.
12. **Yarım kalmış son satır önündekileri gizlemez.**
13. **Yeni bir kayıt, öncekinin yazdığını okur** — yeniden başlama.
14. **Proje klasörüdür** — `project_exists` var olan klasöre evet, olmayana hayır.

### `backend/tests/test_chat_usecases.py` — yeni; use case'ler, sahte kayıtla

15. **Bekleyen yoksa yeni sohbet yapılır** — boş proje: `{"id": 1, "questions": []}`, kayda
    `("düğün", 1)` yazıldı.
16. **Yeni sohbet en yüksek kimliğin bir fazlası** — sorulu 1 ve 2: 3.
17. **Bekleyen boş sohbet, yenisinin yerine döner** — sorulu 1, boş 2: 2 döner, kayda yazılan yok.
18. **Liste yalnız sorulu sohbetler, son sorusu en yeni olan üstte** — 1: iki satırlık ilk soru 10:00,
    ikinci soru 12:00; 2: tek soru 11:00; 3: boş → `[{1, ilk sorunun bütün metni, 12:00},
    {2, …, 11:00}]`.
19. **Hiç soru sorulmamış proje boş liste verir.**
20. **Sohbet her şeyiyle açılır** — kaydın verdiği sohbet aynen.
21. **Olmayan sohbet reddedilir** — `ChatMissing`, *"Sohbet yok: 7"*.
22. **Üç use case da olmayan projeyi reddeder, kayda hiçbir şey yazmadan** — parametreli: yeni,
    liste, aç; `ProjectMissing`, *"Proje yok: yok"*.

### `backend/tests/test_chats_routes.py` — yeni; kapı, elle bağlı, geçici klasörde

23. **Yeni sohbet boş gelir** — POST → 200, `{"id": 1, "questions": []}`.
24. **İki kez yeni sohbet istemek bekleyeni verir** — ikisi de 1; liste boş.
25. **Sorulu sohbet listede, ve her şeyiyle açılıyor** — kayda soru, iki adım ve cevap yazılır: liste
    satırı ve sohbetin tamamı.
26. **Sorudan sonra yeni sohbet yenisidir** — 1'e soru yazıldı: POST → 2.
27. **Sunucu yeniden başlayınca sohbetler yerinde** — aynı klasör üstünde yeni bir uygulama: liste ve
    sohbet aynı.
28. **Başka projenin sohbeti görünmez** — `düğün`'ün 1'inde soru var: `kına`'nın listesi boş,
    `kına`'nın 1'i 404 *"Sohbet yok: 1"*.
29. **Olmayan proje 404** — üç kapı da *"Proje yok: yok"*.
30. **Yeni sohbet isteği proje yaratmaz** — `yok` klasörü açılmadı.
31. **Olmayan sohbet 404** — *"Sohbet yok: 7"*.
32. **Silmenin kapısı yok** — `DELETE …/chats/1` → 405; sohbet hâlâ açılıyor.
33. **Disk hatası sistemin kendi sözleriyle** — use case'leri `OSError` atan bir kapı: üçü de 500,
    hatanın metni.

### `backend/tests/test_composition_root.py`

34. **Uygulama agent'ın sohbetlerini sunar** — iki video modeliyle: `GET
    /api/projects/m417-yok/chats` → 404, *"Proje yok: m417-yok"*.

## Kırmızı beklenen

- `test_chat_record.py`, `test_chat_usecases.py`, `test_chats_routes.py`: hepsi
  `ModuleNotFoundError` — `backend.features.agent` yok.
- 34: iki durumu da kırmızı — kapı yok, GET `index.html`'e düşüyor, 200.
- Öteki her şey yeşil; öteki üç satır yeşil.

## Bilinçli olarak yapılmayan

- **Soruyu alan, agent'ı başlatan ve durduran kapılar** — 420. Bu parçada kayda soru ve sonuç
  yalnız kaydın yöntemleriyle yazılır.
- **Durdurmanın ve cevabın adımlara etkisi** — süren adımın düşmesi, cevabın son adımı bitirmesi
  *(BEHAVIOUR.md)* 420'nin kuralı; kayıt yazılanı olduğu gibi taşır.
- **Agent'ın çalışıp çalışmadığı** listede yok: çalışan agent sürecin belleğinde, 420'nin. Listenin
  canlı noktasını 425, 420'nin söylediğinden çizer.
- **Hangi sohbetin açık olduğu ve kutudaki taslak** kayıtta yok — ekranın, 425.
- Kayıt önbelleğe alınmaz; ölçülmüş bir yavaşlık yok.
- `dist`'e, yol haritasına ve ekrana dokunulmaz.
