# Backlog — QueenAgent

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

---

### Kalabalık karede karakterleri BREAK ile ayırmak

Bir karede iki karakter olunca tanımları birbirine bulaşıyor — birinin saçı ötekinin üstüne
geçiyor. Sebebi SDXL'in metin kodlayıcısı: promptu 75 jetonluk parçalar hâlinde okuyor, ve karışma
o parçanın **içinde** oluyor. `BREAK` bunun bilinen ilacı; yazıldığı yerde parçayı kapatıp yenisini
açıyor, iki karakter ayrı ayrı kodlanıyor.

**Bugün seçilen ilaç sıra:** ana karakter promptun başında, geri kalan `camera`'dan sonra — arayı
açmak. Kullanıcı bunu elle deneyip işe yaradığını gördü *(27 Ağustos)*, o yüzden önce o yapılıyor.
Bilinen tek şüphe duruyor ve kayda geçiyor: erken jetonlar daha fazla ağırlık taşıyor, yani ikinci
karakteri sona atmak onu ayırmakla kalmayıp zayıflatabilir. `BREAK`'te bu bedel yok — parçalar
bağımsız kodlandığı için ikisi de kendi parçasının başında duruyor.

**Bu tarafta tek başına yapılamaz.** `BREAK` bir model özelliği değil, promptu okuyan arayüzün
özelliği, ve promptlar buradan kullanıcının ComfyUI tabanlı arayüzüne — queen-editor'e — düz metin
olarak gidiyor. Orası bugün desteklemiyor: pozitif yolda tek bir `CLIPTextEncode` var ve `BREAK`
kelime olarak kodlanıyor. Açılacak düğüm ve bedeli
[queen-editor backlog'unda](../queen-editor/BACKLOG.md).

**Sırası:** queen-editor o düğümü açtıktan sonra. O gün `build_prompts` karakter bloklarının arasına
`BREAK` koyar, ve sıra düzeltmesinin hâlâ bir işi olup olmadığı yeniden sorulur — ikisi aynı derde
iki ayrı ilaç, ve biri ötekini gereksiz kılabilir.

Araştırmanın tamamı ve kaynakları:
[skill problemleri belgesi](../docs/2026-08-27-queenagent-skill-problemleri.md).
