# Madde 191 · test turu — yeni proje adı numaralanır

**Kaynağı:** [yol haritası, Madde 191](../plans/2026-09-06-queenagent-v8-roadmap.md).
187 `a390078`'de kapandı.

---

## Ne kanıtlanacak

Her yeni proje **"New project"** adıyla doğuyor, ve aynı adı taşıyan üç proje kenar çubuğunda
ayırt edilemiyor. Yarın her proje **numaralı** doğuyor — *New project 1*, *New project 2*,
*New project 3* *(kullanıcı kararı, 6 Eylül)* — ve sıradaki **boş** numarayı alıyor: 2 silinip
yenisi açılırsa boşluk dolar.

## İlki de numara alıyor, ve ayırıcı boşluk

Emsal var ama birebir değil, ve fark bilerek. `naming.unique_name` **ilkine dokunmuyor** ve
ikinciden itibaren **tireyle** numaralıyor — `plan.md`, sonra `plan-2.md`.

- **Tire dosya adının işareti**, proje başlığının değil. Kullanıcının ekranda okuduğu şey bir
  başlık.
- **Numarasız bir ilk proje sonsuza kadar özel kalır.** Yeniden adlandırıldığı gün numaralamada
  bir delik açar, ve o deliği kimse görmez.

## Numarayı ne bloklar, ne bloklamaz

Yalnız **tam olarak** `New project <sayı>` biçimindeki bir ad bir numarayı tutuyor. Sonucu:

- *Thesis* adında bir proje hiçbir numarayı tutmuyor — adı zaten onu ayırt ediyor.
- **Yeniden adlandırma numarayı serbest bırakıyor.** *New project 1* → *Thesis* olduğunda bir
  sonraki proje **1** oluyor. Doğru olan bu: numara, hâlâ *New project* diye duran projeleri
  birbirinden ayırmak için var, ve ekranda öyle duran kimse kalmadıysa tutulacak bir şey de yok.
- Kullanıcı bir projeye elle *New project 3* derse, 3 **tutulur**. İki proje aynı adı taşısaydı
  numaranın bütün amacı giderdi.

## Testler

| # | Test | Ne söylüyor |
|---|---|---|
| 1 | ilk proje *New project 1* doğar | maddenin kendisi, ve ilkin de numaralı olduğu |
| 2 | üst üste üçü 1, 2, 3 olur | sıradaki boş numara |
| 3 | ortadaki silinince boşluk dolar | *"sıradaki"* değil, *"boş olan"* |
| 4 | yeniden adlandırılan bir proje numarasını bırakır | numara neyi ayırt ediyorsa onu tutar |
| 5 | ilgisiz adlı bir proje hiçbir numarayı tutmaz | *Thesis* saymıyor |
| 6 | elle konmuş *New project 3* tutulur | iki proje aynı adı taşımaz |
| 7 | ayırıcı boşluk, tire değil | `unique_name`'den bilerek ayrılıyor |
| 8 | uçtan uca: API `New project 1` döndürür | ekranda görünen ad |

## Kırmızı turun tuzağı

Bu koşuda on üç kez görüldü. Buradaki hâli **3 ve 4**: ikisi de *"bir sonraki proje 1 olur"*
diyor, ve bugün **her** proje adsız-numarasız doğduğu için ikisi de yanlış sebeple geçebilirdi.
İkisinde de önce **ilk üç projenin numaralarının gerçekten 1, 2, 3 olduğu** ölçülüyor; ondan sonra
silme ya da yeniden adlandırma yapılıyor.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent`'ın arka yüzü kırmızı verir; ön yüz
kımıldamaz — ad sunucudan geliyor, ve ön yüzdeki *"+ New project"* bir düğme yazısı, bir proje adı
değil. `queen-editor` de kımıldamaz.
