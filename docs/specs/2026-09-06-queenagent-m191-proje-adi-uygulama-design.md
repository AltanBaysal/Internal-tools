# Madde 191 · uygulama turu — yeni proje adı numaralanır

**Kaynağı:** [test turu](2026-09-06-queenagent-m191-proje-adi-testler-design.md), `79dc30f`'de
9 kırmızı.

---

## Tek dosya

`create_project.py`. Depo zaten `list_all()` sunuyor, yani numaranın okunacağı yer yerinde;
başka hiçbir şeye dokunulmuyor.

## Numara nasıl bulunuyor

Var olan adların içinden **tam olarak** `New project <sayı>` olanların sayıları toplanıyor, ve
1'den başlayarak **kümede olmayan ilk sayı** alınıyor. Süzgeç bir kalıp değil, iki parçalı bir
ayrıştırma: önce ön ek, sonra kalanın rakamlardan oluşup oluşmadığı. Sebebi, *New project 2 kopya*
gibi bir adın 2'yi tutmaması — o ad ekranda kendini zaten ayırt ediyor.

`unique_name` çağrılmıyor, ve neden ayrıldığı kırmızı turda yazılı: tire ile boşluk, ve ilkinin de
numara alması.

## `NEW_PROJECT_NAME` kalıyor, ama artık bir kök

Sabit gitmiyor; anlamı değişiyor — **doğan ad** değil, adın **kökü**. Adı aynı kaldığı için
`test_project_usecases.py` onu hâlâ import ediyor ve beklenen adı ondan kuruyor: kök tek yerde
yazılı, ve testler onu tekrar yazmıyor.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. 9 kırmızı kapanıyor; ön yüz ve `queen-editor`
kımıldamıyor.
