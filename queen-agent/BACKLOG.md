# Backlog — QueenAgent

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

## `read_file` yapı dosyasını da okuyamasın

Madde 151 `create_file` ile `edit_file`'ı yapı dosyasına kapattı, `read_file`'ı **bilerek** açık
bıraktı: o gün yerine geçecek bir şey yoktu ve okumayı yasaklamak modeli körleştirirdi.

`structure_frames.read` geldiğinde soru yeniden sorulabilir — yapı dosyası tamamen kendi
araçlarının arkasına geçsin mi. Kazancı, modelin 40 karelik bir dosyayı baştan sona okuyup bağlamı
doldurması yerine yalnız ihtiyacı olan kareyi alması.

Kapalı kalan taraf: dosya bozulduğunda onu okuyacak bir şey de kalmaz — 151'in `edit_file` için
açık tuttuğu tamir yolunun okuma tarafı da düşünülmeli.
