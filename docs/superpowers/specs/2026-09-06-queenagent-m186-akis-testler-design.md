# Madde 186 · test turu — Generate prompts+ kalkar, akış altı adım olur

**Kaynağı:** [yol haritası, Madde 186](../plans/2026-09-06-queenagent-v8-roadmap.md).
185 `2a1304e`'de kapandı, ve bu madde onun üstünde duruyor.

---

## Neden 185'ten sonra olmak zorundaydı

Deneme 3'te 23 karenin action'ı **tek tura sığmadı**; araya bir saat girerek ikiye bölündü. Akışın
kuralı *"bir adım kullanıcı onaylayınca biter"* — sığmayan bir aşama o kuralın içinde yaşayamaz.
185 aşamayı tek çağrıya indirdi, ve ancak şimdi akışın son adımı olabiliyor.

## Ne değişiyor

**Akış altı adım.** Bugünkü beşin önüne **bağlam** giriyor, ve sondaki **devir** yerini
**promptların üretilmesine** bırakıyor:

| | Adım | Bugünden farkı |
|---|---|---|
| 1 | Bağlam sorulur — ne yapılıyor, ne için | **yeni** |
| 2 | Plan yazılır, ve `start_scenario` dosyayı açar | plan bugün 1., `start_scenario` bugün 2. adımda |
| 3 | Karakterler *(+ kıyafetler, + `pov_`)* | numarası kaydı |
| 4 | Mekânlar | numarası kaydı |
| 5 | Sahneler | numarası kaydı |
| 6 | `write_missing_actions`, sonra `build_prompts` | bugün burada **devir** var |

Asıl kazanç 1 ile 2'nin sırasında. Planın açılış satırı bugün de *"ne yapılıyor, ne için"* diyor —
ama o satırı model **hiçbir şey bilmeden kendi yazıyor**. Sorulunca plan bir tahmini değil bir
cevabı taşıyor, ve plan taze sohbetin belleği olduğu için bugün o tahmin sonraki turlara da miras
kalıyor.

**`Generate prompts+` kalkıyor, yerine `Edit prompts` geliyor.** Yeni skill'in tek işi **var olanı
düzeltmek**. Adı ne yaptığını söylüyor ve kalkan adla karışmıyor; id'si `edit-prompts`, ve eski id
silinmiş skill'lerin listesine katılıyor — eski bir kayıt onu adlandırdığında tur talimatsız koşar,
Madde 94'ten beri işleyen yol.

## Metinlerin şekli: `superpowers:writing-skills`

Rehber Claude Code'un kendi skill dosyaları için yazıldı; geçen kısmı **bir modelin gerçekten
uyduğu talimat nasıl yazılır** kısmı. Buradan alınan üç şey:

- **Biçim, hataya göre seçilir.** Yasak listesi, kuralı bilip baskı altında çiğneyen bir okuyucu
  için. Çıktının *şekli* yanlışsa doğru biçim **tarif**: çıktının ne olduğunu, parçalarıyla ve
  sırasıyla söylemek. Akış zaten bir tarif — numaralı, sıralı — ve öyle kalıyor.
- **Nüans cümlesi yok.** *"Şunu yapma, tabii önemliyse yap"* pazarlığı yeniden açar. Gerçek istisna
  kendi koşulu olarak yazılır, ve koşul **gözlenebilir** bir şeye bağlanır — *"kullanıcı sen karar
  ver dediyse"* gibi.
- **Muafiyet cümlesi kapsamaz.** Bir kuralın ulaşmaması gereken bir parça varsa, kural yeniden
  kurulur.

*Edit prompts* bu yüzden **arıza nerede yaşıyorsa oraya** göre bölünmüş bir tarif: bir karenin
cümlesi mi, bir haritadaki giriş mi, karenin kendisi mi. Model *"neyi düzelteceğim"* sorusunu
metnin şeklinden okuyor.

## Kelime tavanı: akış 450'de kalıyor, öteki 300'den 200'e iniyor

Yol haritası *"yükselterek değil"* dedi ve harfiyen tutuluyor. Akış bir adım kazanıyor ama bir
adım da kaybediyor — devir paragrafı gidiyor — yani 450 duruyor. *Edit prompts* ise işinin yarısını
bırakıyor: kurma tarafı akışa geçti, elinde yalnız düzeltme kaldı. Tavanı **200**.

Bir tavanın inmesi de bir karar, ve kaydı burada: metin küçüldüğü için iniyor, ve indiği için bir
daha eski işi geri alamıyor.

## Testler

**Yeni:** altı adımın sırası; 1. adımın bağlam olduğu ve plandan önce geldiği; `start_scenario`'nun
2. adımda oturduğu; 6. adımın önce `write_missing_actions` sonra `build_prompts` çağırdığı; akışın
artık **kimseye devretmediği**; `edit-prompts`'un menüde ve `INSTRUCTIONS`'ta olduğu; eski id'nin
hiçbir şey taşımadığı.

**Taşınan:** 185'te yazılan üç skill testi — *boş kareleri tek çağrıda doldur*, *tek tek yürüme*, ve
*düzeltme tek kareli aracı anar*. İlk ikisi **akışa** geçiyor, üçüncüsü *Edit prompts*'ta kalıyor.
Bir madde önce yazılıp bir madde sonra taşınmaları sırayla ilgili değil: 185 aracı yaptı, 186 onu
kimin çağırdığını değiştirdi.

**Düşen:** devirle ilgili olan her şey — *"Generate prompts+"* adını arayan, *"5. The handoff"*
diyen, ve `build_prompts is never called here` diye **tersine dönmüş** olan.

## Kırmızı turun tuzağı

Bu koşuda on bir kez görüldü. Buradaki en tehlikeli hâli **akışın artık devretmediği**: metinde bir
adın *yokluğunu* arayan bir test, metin hiç okunmasa da geçer. O yüzden aynı testte önce **altıncı
adımın var olduğu** ölçülüyor.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent`'ın **iki takımı da** kırmızı verdi:
arka yüz **27**, ön yüz **23**. Dördü `test_stream_answer` ve `test_chats_api`'de — orada skill
adı yalnız *"bir skill"* demek, ve id değişince `instruction_for` boş dönüyor; doğru sebeple
kırmızılar. `queen-editor` kımıldamadı — **739 · 591.**
