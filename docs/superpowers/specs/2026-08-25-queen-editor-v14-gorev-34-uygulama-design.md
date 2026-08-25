# v14 Görev 34 — Açık panel geri dönüşte yerinde kalır: UYGULAMA döngüsü tasarımı

**Tarih:** 2026-08-25 · **Kaynak:** Colab turu, 24 Ağustos
**Öncesi:** [Görev 34 test spec'i](2026-08-25-queen-editor-v14-gorev-34-testler-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 34

## Ne yeşile döndürülüyor

İki kırmızı test: açık panel ikinci mount'ta yerinde, kapalı sütun kapalı geri geliyor. Yanlarında
iki tutucu var ve onlar da yeşil kalmalı: hatırlanan yokken sütun *Fotoğraf üret* ile açılıyor, ve
başka bir proje kendi varsayılanıyla açılıyor.

## Değişikliğin şekli

Bugün:

```jsx
const [open, setOpen] = useState("photo");
```

Yarın aynı satır, başlangıcını modül seviyesindeki bir depodan alıyor. Bileşenin dışa açık yüzü
değişmiyor — yeni prop yok, `ProjectScreen` ve `App` hiç açılmıyor. Depo tamamen bu dosyanın içinde
doğuyor ve dışarıdan kimse okumuyor.

Bu, koşunun yedinci deposu ve kalıbı diğer altısıyla aynı: `REMEMBERED` (kare listesi), `REMEMBERED`
(proje kaydı), `shownPictures`, `KEPT`, model listesi, üretici listesi.

## Tuzak: kapalı da bir cevap

Kapalı sütunun değeri `null`. "Hiçbir şey hatırlanmıyor" da `null` görünür. İkisi aynı sayılırsa,
kullanıcının bilerek kapattığı sütun her dönüşte yeniden açılır — yani düzeltilen hatanın aynısı,
ters yönde.

Bu yüzden depo `has()` ile sorulur, `get()`'in cevabına bakılarak değil. `?? "photo"` yazmak burada
sessizce yanlış olurdu.

## Anahtar proje

Hangi panele bakıldığı kullanıcının o projedeki işi. Başka bir proje kendi varsayılanıyla açılır;
bir projenin paneli ötekine taşınmaz.

## Ömür

Bellekte. Sayfa yenilenince sütun yine *Fotoğraf üret* ile açılır — diğer altı depo ne kadar
yaşıyorsa o kadar. Diske hiçbir şey yazılmaz.

## Bilerek yapılmayan: proje değişimi koruması

`useProjectSettings` ve `useGeneration`, proje sökülmeden değişebildiği için bir `shownProject` ref'i
taşıyor. Buraya eşi eklenmiyor.

Sebep: bugün iki proje arasında geçmenin tek yolu proje listesinden geçmek. Bir projeye gitmek
yalnız `ProjectsScreen`'in kartlarından oluyor, ve o ekran `ProjectRoute`'u — dolayısıyla
`SidePanel`'i — söküyor. `SidePanel` iki proje arasında hiç ayakta kalmıyor.

Onların ref'i taşımasının sebebi de ayrı: yanlış projenin kaydını göstermek, sonra onu yanlış
projeye kaydetmek demekti. Burada en kötü ihtimalle yanlış panel açık kalır.

Ekleseydik test edilemeyen kod yazmış olurduk; testlerin dördü de sökülüp yeniden kurulan bir sütunu
anlatıyor.

## Kapsam dışı

- **Test dosyası değişmiyor.**
- **Galeri seçimi** — kullanıcı kararıyla 34'ten çıktı, kaydı [backlog](../../../queen-editor/BACKLOG.md)'da.
- **Yazılmış ama gönderilmemiş metin** — 35. madde.

## Derlenmiş çıktı

Ön yüz kaynağı değiştiği için `dist` aynı commit'e girer (CLAUDE.md). Defter derlemiyor; itilmemiş
bir `dist` Colab'da görünmez.
