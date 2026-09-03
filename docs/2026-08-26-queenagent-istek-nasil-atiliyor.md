# QueenAgent — bir istek nasıl atılıyor

> ⚠️ **Ayrıntıları 27 Ağustos'ta kaldı** *(not: 4 Eylül)*. **Tesisatın şekli hâlâ doğru** — uçlar,
> olaylar, tek bağlantı, kaydın tek evi: hepsi bugün de böyle. Eskiyen şey diyagramların içindeki
> sayılar ve adlar: 5'teki *"altı tane"* araç **17**, ve v6–v7 koşuları o gün olmayan bir şey daha
> ekledi — `write_frame_prompt` kare başına **kendi isteğini** atıyor, yani xAI'ye giden tek istek
> türü artık ana ajanınki değil.
>
> **Modele giden metinlerin listesi ve isteğin katmanları için:**
> [modele giden her metin](2026-08-28-queenagent-promptlar.md).

*İlk yazımı 26 Ağustos. 27 Ağustos'ta 87, 88, 90, 91, 92 ve 93 koştuktan sonra baştan doğrulandı.
En büyük değişiklik yapısal: eskiden ilk mesaj ile takip mesajı ayrı iki vakaydı, artık tek — Madde
87 iki kapıyı bire indirdi, ve bu belgenin o günkü "aynı şekil, aynı depo" notu tam olarak bunun
gerekçesiydi.*

Her kutu ilk satırda kendi adını, ikinci satırda ne tür bir şey olduğunu, altında da ne yaptığını
taşıyor.

## 1 · Bir cümle göndermek

```mermaid
flowchart TD
    subgraph FE1["ÖN YÜZ"]
        F1["<b>Composer + useChat.send</b><br/>ekran<br/>taslak metin · Enter · reddedilirse cümle geri gelir<br/>gövde: chat · text · skill · mode"]
    end
    subgraph BE1["ARKA UÇ"]
        E1["<b>post_message</b><br/>uç<br/>tek kapı · hangi sohbet gövdede bir alan<br/>boş olabilir, ve boş bir yol parçası başka bir adrestir"]
        G1["<b>is_full</b><br/>kural<br/>bağlam tavanı · 50.000 jeton<br/>hiçbir şey yazılmadan önce reddeder"]
        C1["<b>append_message</b><br/>kural<br/>chat boşsa sohbeti doğurur, doluysa ekler<br/>boş cümleyi reddeder · başlık ilk cümleden, 42 karakter"]
        S1["<b>FileChatStore</b><br/>adaptör<br/>yalnız bir şey taşıyan alanları yazar"]
        W1["<b>Store.write_text</b><br/>servis<br/>önce .writing dosyası, sonra yerine koyar<br/>yarım dosya diye bir şey yok"]
        E1 --> G1
        G1 --> C1
        C1 --> S1
        S1 --> W1
    end
    subgraph EX1["DIŞARISI"]
        D1["<b>chats/id.json</b><br/>yerel disk"]
    end
    F1 -->|"POST"| E1
    W1 --> D1
```

Burada model yok: sistem promptu yok, skill yönergesi yok, xAI yok. Bu ayak yalnız bir cümleyi diske
koyuyor. Skill mesajın üstüne yazılıyor ama onu okuyan ilk yer 5.

**İlk mesaj ile takip mesajı arasındaki tek fark gövdedeki `chat` alanının boş olup olmadığı.** Sohbet
ilk mesajıyla doğuyor — boş sohbet diye bir şey yok — ve başlığını o cümleden alıyor.

Aynı istek cevabı da başlatıyor; ikinci bir bağlantı açılmıyor. Devamı 5'te.

## 2 · Tekrar denemek

```mermaid
flowchart TD
    subgraph FE2["ÖN YÜZ"]
        F2["<b>useChat.retry</b><br/>kanca<br/>send(null) · metinsiz<br/>gövde: yalnız chat"]
    end
    subgraph BE2["ARKA UÇ"]
        E2["<b>post_message</b><br/>uç<br/>aynı kapı · metin yoksa yazacak bir şey de yok"]
        O2["<b>is_owed_an_answer</b><br/>kural<br/>son mesaj kullanıcınınsa cevap borçlu<br/>değilse 400 · cevaplanmış bir sohbet iki kez cevaplanmaz"]
        E2 --> O2
    end
    F2 -->|"POST"| E2
```

1 ile aynı kapı, ve fark tek bir soru: gövdede cümle var mı. Cümle varsa önce yazılır, yoksa diskte
bekleyen soru cevaplanır. **Boş cümle ile hiç cümle aynı şey değil** — boş bir cümle klavyeye
yaslanmış biridir ve reddedilir.

Bu ayak diske hiçbir şey yazmıyor; yaptığı tek şey 5'i başlatmak.

## 3 · Durdurmak

```mermaid
flowchart TD
    subgraph FE3["ÖN YÜZ"]
        F3["<b>gönder düğmesi</b><br/>ekran<br/>cevap akarken kareye dönüşür"]
    end
    subgraph BE3["ARKA UÇ"]
        E3["<b>post_stop</b><br/>uç<br/>arada kural yok"]
        S3["<b>MemoryStops.want</b><br/>adaptör<br/>elindeki kesme çağrısını çalıştırır<br/>bellekte, kilidin arkasında"]
        K3["<b>XaiClient._cut</b><br/>servis<br/>soketi kapatır · bekleyen okuma uyanır"]
        E3 --> S3
        S3 --> K3
    end
    F3 -->|"POST"| E3
```

Diske hiç uğramayan tek zincir, ve **bir bayrak değil bir kesme**. İstemci soketi eline geçirdiği an
onu kesmenin yolunu `MemoryStops`'a bırakıyor; durdurma o yolu çağırıyor. Bekleyen okumayı uyandıran
şey bu — bir bayrak sorulmayı beklerdi, ve ilk kelimeden önceki bekleyişte sorulacak bir yer yok.

Kesilen bağlantı ile kopan bir ağ aynı istisnayla geliyor, o yüzden `stream_answer` inanmadan önce
kayda soruyor: *bu kesmeyi biz mi istedik.* Cevap bellekte yaşıyor ve durdurduğu cevapla ölüyor —
yazılsaydı kendi cevabından uzun yaşar ve bir sonrakini doğarken keserdi.

Bu istek kendi bağlantısında geliyor, çünkü durdurduğu cevap hâlâ bir başkasından akıyor.

## 4 · Bir sohbeti açmak

```mermaid
flowchart TD
    subgraph FE4["ÖN YÜZ"]
        F4["<b>useChat</b><br/>kanca<br/>bir sohbet açılınca, ve her cevap bitince"]
    end
    subgraph BE4["ARKA UÇ"]
        E4["<b>get_chat</b><br/>uç<br/>arada kural yok<br/>context: sent + ceiling de gider"]
        S4["<b>FileChatStore</b><br/>adaptör<br/>JSON bir Chat olur · eski kayıtta olmayan alan boş okunur"]
        E4 --> S4
    end
    subgraph EX4["DIŞARISI"]
        D4["<b>chats/id.json</b><br/>yerel disk"]
    end
    F4 -->|"GET"| E4
    S4 --> D4
```

En kısa yol: uç doğrudan adaptöre iniyor, arada kural yok, çünkü bir kaydı geri okumanın uygulanacak
kuralı yok.

**Kaydın tek evi burası.** Bir cevap bittiğinde tarayıcı akışta biriktirdiğini atıp kaydı buradan
okuyor — akıştaki bir tahmin, diskteki ise kayıt.

## 5 · Cevabın kendisi

```mermaid
flowchart TD
    subgraph FE5["ÖN YÜZ"]
        F5["<b>streamEvents</b><br/>servis<br/>1 veya 2'nin açtığı bağlantıdan okur<br/>kendiliğinden hiçbir şey başlatmaz"]
    end
    subgraph BE5["ARKA UÇ"]
        E5["<b>_sse</b><br/>uç<br/>1 ve 2 ile aynı bağlantı · olay akışı olarak cevaplar"]
        L5["<b>stream_answer</b><br/>kural<br/>tur döngüsü · en fazla 16 tur"]
        R5["<b>FileChatStore</b><br/>adaptör<br/>kaydı geri okur — az önce yazılan mesajı da"]
        V5["<b>_conversation</b><br/>metin<br/>kayıt bir mesaj listesi olur"]
        A5["<b>_asked</b><br/>metin<br/>skill yönergesini listenin SONUNA ekler<br/>her turda yeniden, çünkü liste büyüyor"]
        K5["<b>skills.py</b><br/>metin<br/>tek yönerge · en yeni kullanıcı mesajının skill'i"]
        N5["<b>modes.py</b><br/>kural<br/>kip hangi araçların gönderileceğini seçer"]
        G5["<b>XaiEngine → XaiClient</b><br/>adaptör"]
        P5["<b>prompt.py</b><br/>metin<br/>SYSTEM_PROMPT, her isteğin en başına"]
        T5["<b>run_tool</b><br/>araç<br/>altı tane · sonuç listeye geri girer"]
        W5["<b>append_message</b><br/>kural<br/>bütün turlarda söylenen tek bir mesaj olur"]

        E5 --> L5
        L5 --> R5
        R5 --> V5
        V5 --> A5
        K5 --> A5
        A5 --> G5
        N5 --> G5
        G5 --> P5
        L5 -->|"model bir araç istedi"| T5
        L5 -->|"çağrı kalmadı · durduruldu · plan yazıldı · 16 tur doldu"| W5
    end
    subgraph EX5["DIŞARISI"]
        X5["<b>xAI</b><br/>api.x.ai · Grok Build"]
        D5["<b>yerel disk</b><br/>files/ ve chats/"]
    end
    F5 -->|"SSE · chat · chunk · call · file-start · file · done · error"| E5
    G5 -->|"HTTPS · bütün liste, her tur"| X5
    T5 --> D5
    W5 --> D5
```

1'de veya 2'de gönderilen isteğin geri kalanı: soru diskten okunuyor, bir mesaj listesine dönüyor ve
xAI'ye bütün hâlinde gidiyor. **Her tur baştan bir istek** ve bütün konuşmayı taşıyor; cevap aynı
bağlantıdan SSE kareleri olarak geri iniyor ve sonunda tek bir mesaj olarak yazılıyor.

Sistem promptu en başta duruyor, skill yönergesi en sonda — dikkat bir bağlamın iki ucunda en
yüksek, ve önbellek sabit olanın başta kalmasını istiyor.

## Sıra

```mermaid
sequenceDiagram
    participant T as Tarayıcı
    participant F as Flask
    participant D as Disk
    participant X as xAI

    T->>F: 1. bağlantı · POST .../messages · chat + text + skill + mode
    Note over F: bağlam tavanı burada sorulur<br/>dolu ise 400, ve hiçbir şey yazılmaz
    F->>D: mesajı chats/id.json içine yaz
    F->>D: kaydı geri oku — az önce yazılanı da
    loop en fazla 16 tur
        F->>X: sistem promptu + bütün konuşma + skill yönergesi
        X-->>F: metin parçaları, ya da bir araç çağrısı
        F-->>T: SSE · metin geldikçe
        alt model bir araç istedi
            F->>D: bir proje dosyasını oku ya da yaz
            F-->>T: SSE · çağrı kartı
        end
    end
    F->>D: cevabı tek bir mesaj olarak yaz
    F-->>T: SSE · done
    T->>F: GET .../chats/:c · kaydı oku
    Note over T: akıştaki bir tahmin, diskteki kayıt

    T->>F: 2. bağlantı · POST .../stop
    Note over F: elindeki kesme çağrısı çalışır<br/>1. bağlantının soketi kapanır, okuma uyanır
```

Diski dinleyen hiçbir şey yok: her adımı tarayıcı başlatıyor, ve **bir cümle ile onun cevabı tek
bağlantı**. Sohbet kaydı hem girdi hem çıktı, ve sunucu iki istek arasında hiçbir şey hatırlamıyor.

Ayrıntı — hangi fonksiyon, hangi olay, hangi alan — [AI yolu
haritasında](2026-08-26-queenagent-ai-yolu-haritasi.md).
