# Madde 364 — All projects ve ad sorma ekranı yüklenirken ve yüklenemeyince · uygulama turu

**Kaynak:** [test turunun spec'i](2026-09-29-queenagent-m364-yukleme-ve-hata-testler-design.md) —
kararlar orada; bu tur kırmızı commit'lenen testlerin anlattığını yapar, fazlasını değil.
FOUNDATION'ın 1. ilkesi (kullanıcının işi kutsal) ve 4. ilkesi (kısa, yeniden yazılabilir birimler),
CODE-STANDARD'ın *Frontend*'i (bileşen özelliğin içinde, `shared/` hiçbir şey çizmez).

**Kullanıcıdan gereken:** hiçbir şey.

## Parçalar

1. **`CopyButton.jsx` (yeni, `features/workspace/`).** `FilePanel.jsx`'teki `CopyButton` olduğu gibi
   kendi dosyasına taşınır — pano yazımı basıştan hemen, `Copied` / `Could not copy`, 2.5 saniye sonra
   yeniden `Copy`, `data-said`, yazı yokken soluk. Tek değişiklik: sınıfı çağıran verir
   (`className`), düğme `ghost ${className}` taşır. `FilePanel` `className="reader__copy"` ile
   kullanır; 342'nin testleri değişmeden geçer. İkinci bir kopyalama yazılmamış olur.
2. **`ProjectsFailure.jsx` (yeni).** İki ekranın ortak hata ekranı, tasarımın `failed`'i:
   `.empty > p.empty__error` `Couldn't load projects.` ve `.empty__actions` içinde
   `button.failure__retry` `Try again` (`onRetry`) ve `CopyButton` (`className="empty__copy"`,
   `text={error}`). Tek yerde, çünkü iki ekran aynısını gösterir (tasarımın 172'si).
3. **`useProjects.js`.**
   - `reload` başarıyla okuyunca `error`'u kaldırır; okuyamazsa `error` sunucunun sözü.
   - `retryProjects`: `setLoading(true)` ve `reload()`. Yüklenme ekranlarda hatadan önce geldiği
     için Try again'in beklemesi spinner'dır.
   - `writeError`: `editProject` ve `removeProject` başlarken kaldırır, reddedilince sunucunun sözü.
     Dönüş değerleri aynı kalır.
   - `createProject` yakalamaz: ret çağırana fırlar; başarıda eskisi gibi listeyi yeniden okur ve
     yeni projeyi döndürür.
4. **`AllProjectsScreen.jsx`.** Sıra: `loading` değilse ve `error` varsa `ProjectsFailure`; yoksa
   çerçeve (başlık, `+ New project`, `.all-projects__tools`), ardından `writeError` varsa
   `p.list-error`, ardından `loading` iken `.all-projects__spinner` içinde `Spinner`, değilse liste.
   Yeni prop'lar `writeError`, `onRetry`.
5. **`NameProjectScreen.jsx`.** `loading` → `.empty` içinde yalnız `Spinner`; `error` →
   `ProjectsFailure`. Kendi durumu `refused`: `onCreate`'in sözü reddedilirse `failure.message`;
   form kalır, `.empty__row`'un ardında `p.empty__refused`. Hook'lar erken dönüşlerden önce çağrılır
   (bugünkü `useRef`/`useState` sırası korunur).
6. **`App.jsx`.** `useProjects`'ten `writeError` ve `retryProjects` alınır; `AllProjectsScreen`'e
   `writeError`, iki ekrana `onRetry={retryProjects}`. `createNamed` `createProject`'in sonucunu
   koşulsuz izler — ret fırlarsa `NameProjectScreen` yakalar.
7. **`workspace.css`.** `.all-projects__spinner` (`.chat__spinner`'ın ölçüleri, ayrı kural —
   `.chat__spinner`'ın testi kuralın kendi başına durmasını ister), `.empty__actions`,
   `.empty__copy[data-said="yes"|"no"]`, `.empty__refused`. `.empty` ve `.empty__error`'ın yorumları
   bugünkü hâle göre düzeltilir.

## Yapılmayanlar

Sekmeler (363), reddedilen yeniden adlandırmanın yazılan adı geri getirmesi (360'ın satırı), sunucu,
`dist`.

## Nasıl görülür

Dört satır, paralel: dördü de yeşil. Adım adım dökümü
[uygulama planında](../plans/2026-09-29-queenagent-m364-yukleme-ve-hata-uygulama-plan.md).
