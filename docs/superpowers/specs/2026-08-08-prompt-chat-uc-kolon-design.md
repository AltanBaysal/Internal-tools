# prompt-chat — üç kolonlu yerleşim

**Amaç:** Projeler, dosyalar ve sohbetler tek bir sol kolona sığmıyor. Üçünü üç kolona ayır: solda
seçili projenin sohbetleri, ortada açık sohbet, sağda projenin dosyaları.

## Bugünkü durum ve sorun

Bugün sol kolon iki seviyeli bir ağaç: her proje bir satır, açık projenin altında hem `dosyalar`
hem `sohbetler` grubu, ikisi de girintili. Açık dosya ayrıca sağda dördüncü bir panel olarak
beliriyor.

İki şey birden bozuluyor:

- **Sol kolon üç listeyi 260 pikselde taşıyor.** Projeler, dosyalar ve sohbetler alt alta; üç
  dosya ve üç sohbetten sonra kaydırma başlıyor ve hangi grupta olduğun kayboluyor.
- **Dosya paneli dördüncü kolon açıyor.** Dosya açıkken ekranda sol ağaç + sohbet + dosya var;
  sohbet ortada kalmıyor, sıkışıyor.

## Yerleşim

```
+-----------------+--------------------------+-----------------+
| < Genel         |   sen: @plan.md ne var   | DOSYALAR        |
|-----------------|                          |  plan.md        |
| SOHBETLER       |   grok: planda 3 adim... |  notlar.md      |
|  @plan.md ne... |                          |  + Yeni dosya   |
|  hikaye taslagi |                          |                 |
|  + Yeni sohbet  |                          |                 |
|                 | [ mesaj yaz          ]   |                 |
| (c) Ayarlar     | [ Gonder             ]   |                 |
+-----------------+--------------------------+-----------------+
      260px                 esner                  300px
```

Üç kolon da **tek projeye** bakar: solda o projenin sohbetleri, sağda o projenin dosyaları, ortada
seçili sohbet. Proje değişince üçü birden değişir.

## Sol kolon — iki hâl

Üstte seçili proje bir başlık düğmesi: `‹ Genel`. Basınca **aynı kolon** proje listesine döner.

```
SOHBETLER HALI              PROJELER HALI
+-----------------+         +-----------------+
| < Genel         |   <     | PROJELER        |
|-----------------|  --->   |-----------------|
| SOHBETLER       |         |  Genel        x |   secili
|  @plan.md ne... |         |  Kampanya     x |
|  hikaye taslagi |   tikla |  Deneme       x |
|  + Yeni sohbet  |  <---   |  + Yeni proje   |
| (c) Ayarlar     |         | (c) Ayarlar     |
+-----------------+         +-----------------+
```

- **Sohbetler hâli** açılış hâlidir. `SOHBETLER` başlığı altında projenin sohbetleri, altta
  `+ Yeni sohbet`.
- **Projeler hâli**ne yalnız başlık düğmesinden girilir. `PROJELER` başlığı altında bütün projeler,
  seçili olan işaretli, altta `+ Yeni proje`. Bir projeye tıklamak onu açar ve sohbetler hâline
  döner; yeni proje açmak da öyle.
- **Proje silme (`×`) ve `+ Yeni proje` sadece projeler hâlinde görünür.** Proje seçiliyken tek
  gördüğün şey o projenin içi.
- **Hangi hâlde olduğun hatırlanmaz.** Sayfa yenilenince sohbetler hâline dönülür — açık bir proje
  her zaman vardır, dolayısıyla gösterilecek bir içerik hep vardır.
- Ayarlar paneli iki hâlde de kolonun dibindedir.

## Orta kolon

Değişmez: mesaj listesi, `/` ve `@` seçicileri, hata kutusu, yazma alanı ve **Gönder**. Tek farkı
artık iki kolon arasında olması.

## Sağ kolon — iki hâl

Dosya listesi ve açık dosya **aynı yeri** paylaşır.

```
+-----------------+         +---------------------------+
| DOSYALAR        |  tikla  | < plan.md  Indir  Kopyala |
|  plan.md        |  --->   |---------------------------|
|  notlar.md    x |         | # Plan                    |
|  + Yeni dosya   |  <---   | 1. Hikayeyi netlestir     |
|                 |    <    | 2. Sahneleri boil         |
+-----------------+         +---------------------------+
      300px                          460px
```

- **Liste hâli** varsayılan: `DOSYALAR` başlığı, projenin dosyaları, `+ Yeni dosya`.
- **Dosya hâli**nde başlık `‹` geri oku + dosya adı + **İndir** + **Kopyala** olur. Bugünkü `×`
  kaldırılır: geri oku zaten aynı işi yapıyor, iki düğme aynı yere gitmesin.
- **Dosya açıkken kolon 300'den 460 piksele genişler.** Bir markdown dosyası 300 pikselde
  yazılabilir bir şey değil; liste hâlinde ise 460 piksel boş yer demek.
- Proje değişince açık dosya kapanır — bugünkü davranış aynen kalır, `useWorkspace` zaten yapıyor.
- Sohbet değişince açık dosya **kapanmaz**: dosya projeye ait, sohbete değil.

## Bileşenler

`ProjectTree.jsx` silinir; işi dört küçük parçaya bölünür. Her parça tek bir liste çizer ve kendi
durumunu tutmaz — hepsi `App`'ten prop alır.

| Dosya | Sorumluluk |
|---|---|
| `Sidebar.jsx` | Sol kolon: `‹ <proje>` başlık düğmesi, iki hâl arasında geçiş, ayarlar paneli |
| `ProjectList.jsx` | `PROJELER` başlığı, proje satırları, `+ Yeni proje` |
| `ChatList.jsx` | `SOHBETLER` başlığı, sohbet satırları, `+ Yeni sohbet` |
| `FilePane.jsx` | Sağ kolon: liste hâli ile dosya hâli arasında geçiş |
| `FileList.jsx` | Dosya listesi |
| `FileView.jsx` | Açık dosya — başlığı geri oklu hâle gelir, `×` kalkar |

Sol kolonun hangi hâlde olduğu `Sidebar` içinde `useState`'tir: kalıcı değil, `App`'i ilgilendirmez,
tek kullanıcısı o kolondur.

Her satırın üstüne gelince beliren silme `×`'i bugünkü gibi kalır — sohbet satırında sohbeti, dosya
satırında dosyayı, proje satırında projeyi siler; üçünün de onay metni ve `aria-label`'ı aynen
korunur.

## Kapsam dışı

- **Kolon genişliklerini sürükleyerek değiştirmek.** Sabit genişlikler yeter.
- **Dar ekran / mobil düzeni.** Araç masaüstünde kullanılıyor.
- **Markdown'ı biçimlendirerek göstermek.** `FileView` ham metin göstermeye devam eder.
- **Dosya adını değiştirmek, taşımak, sürükleyip bırakmak.**
- **Sol kolonun hangi hâlde kaldığını hatırlamak.**
- **Davranış değişikliği.** Gönderme, `/skill`, `@dosya`, kaydetme, silme onayları, `localStorage`
  anahtarları — hiçbiri değişmez.

## Kararlar

- **Sohbetler solda, dosyalar sağda.** Sohbet listesi gezinme aracıdır, gezinme solda durur; dosya
  ise okunan/yazılan içeriktir ve sohbetin yanında, sağda açılır.
- **Proje listesi sohbet listesiyle aynı yeri paylaşır, üstünde durmaz.** Proje değiştirmek seyrek
  bir iştir; sürekli ekranda duran bir liste, her gün kullanılan sohbet listesinden yer çalar.
- **Dosya listesi ve açık dosya aynı kolonda.** İkisi ayrı yer kaplarsa sohbet ortada üçüncü sıraya
  düşer; asıl iş sohbette.
- **Açık dosya kolonu genişletir.** Genişliğin sabit kalması ya listeyi savurgan ya düzenleyiciyi
  kullanılmaz yapardı; hâle göre değişmesi ikisini de çözer.
- **Geri oku tek çıkış yolu.** `‹` ve `×` yan yana durursa hangisinin nereye götürdüğü belirsizdir.
- **Hiçbir mantık dosyasına dokunulmaz.** `chat.js`, `files.js`, `skills.js`, `storage.js`,
  `projects.js`, `useWorkspace.js`, `api.js` ve testleri **olduğu gibi** kalır. Bu turun tamamı
  çizim katmanıdır; mantığın testleri değişmeden geçmek zorundadır.

## Doğrulama

1. **`cd prompt-chat && npm test` yeşil.** Mantık katmanının test dosyaları
   (`chat.test.js`, `files.test.js`, `skills.test.js`, `skillSource.test.js`, `storage.test.js`,
   `projects.test.js`, `api.test.js`, `usePersisted.test.js`) **tek satır değişmeden** geçer —
   bunun kanıtı, yerleşim değişikliğinin mantığa sızmadığıdır. `Message.test.jsx` ve
   `MentionPicker.test.jsx` de değişmez; o iki bileşene dokunulmuyor.
2. **`useWorkspace`'in onarım davranışı kendi test dosyasına taşınır.** Bugün `App.test.jsx`
   içinde yaşıyor ve `App.test.jsx` bu turda baştan yazılıyor; kendi dosyasına alınmazsa sessizce
   kaybolabilir. Taşınacak durumlar: proje yokken varsayılan proje açılması, sahipsiz sohbetlerin
   açık projeye bağlanması, silinen sohbet/proje sonrası açık kimliğin düzelmesi, başka projenin
   dosyası açıkken kapanması.
3. Açılışta üç kolon görünür: solda `‹ <proje>` + `SOHBETLER`, ortada sohbet, sağda `DOSYALAR`.
4. Başlığa basınca sol kolon projeler listesine döner; `+ Yeni proje` ve proje `×`'leri orada,
   sohbetler hâlinde değil.
5. Listeden bir projeye tıklayınca o proje açılır ve kolon sohbetler hâline döner; solda o projenin
   sohbetleri, sağda o projenin dosyaları görünür.
6. Sağdaki bir dosyaya tıklayınca kolon o dosyayı gösterir ve genişler; `‹` listeye döndürür.
7. Dosya açıkken sohbet değiştirmek dosyayı kapatmaz; proje değiştirmek kapatır.
8. Dosyada yazılanlar tuşa basıldıkça kaydedilir; `İndir` ve `Kopyala` çalışır.
9. `/skill` çağrısı, `@dosya` anması ve iki seçici de eskisi gibi çalışır.
