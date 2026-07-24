# Queen Editor — Bölüm 1: Repo çekimi (tasarım)

**Tarih:** 2026-07-25 · **Durum:** onaylandı, implementasyon planı bekliyor
**Şemsiye tasarım:** [2026-07-24-queen-editor-v1-design.md](2026-07-24-queen-editor-v1-design.md)
**Yol haritası:** [2026-07-24-queen-editor-roadmap.md](../plans/2026-07-24-queen-editor-roadmap.md) — Bölüm 1
**Notebook standardı:** [collab-toolbox/NOTEBOOK-STANDARD.md](../../../collab-toolbox/NOTEBOOK-STANDARD.md)

## Amaç

Yol haritasının en riskli görünmez altyapı parçasını tek başına kanıtlamak: **private repo, token ile Colab'da klonlanıyor mu.** Başka hiçbir şey (sunucu, derleme, tünel, Drive, ComfyUI) karışmadan. Klon çalışırsa sonraki her bölüm kodu bu yoldan çekecek; çalışmazsa tüm proje bu adımda takılır — o yüzden önce burası.

## Kapsam

Bu bölüm bittiğinde çalışan şey:

1. `queen-editor/app.ipynb` Colab'a yüklenir, GitHub token Colab Secrets'a bir kez eklenir, Run all yapılır.
2. Notebook private repoyu `feat/queen-editor-v1` dalından `--depth 1` ile klonlar.
3. Hücre çıktısı `queen-editor/` içeriğini + klonlanan kısa commit hash'ini + dal adını basar.
4. Token hiçbir çıktıda görünmez.

## Kapsam dışı (sonraki bölümlere)

Sunucu, frontend derleme, cloudflared tünel, Drive mount, ComfyUI, model indirme, herhangi bir uygulama özelliği. Bölüm 1 yalnız klonun kendisini sınar.

## Kararlar

| Karar | Gerekçe |
|---|---|
| Klon = **tüm repo, `--depth 1`** | Kullanıcı kararı. Tek komut, geçmişsiz, birkaç MB. Bölüm 1'in tek işi klonun çalıştığını kanıtlamak; sparse-checkout'un ek komutları ve hata yüzeyi bu aşamada değmez. collab-toolbox da iner ama sorun değil. |
| Bölüm 1 repoda **yalnız `queen-editor/app.ipynb` + `queen-editor/README.md`** oluşturur | Kullanıcı kararı. `backend/`, `frontend/` Bölüm 2'de içi doldurulacağı zaman açılır — boş klasör "burada bir şey var" yanılsaması üretmez. |
| Doğrulama çıktısı: **dosya listesi + kısa commit hash + dal adı** | Kullanıcı kararı. "Doğru dal, doğru commit indi" gözle doğrulanır; yanlış dalı fark etmek kolaylaşır. |
| `GITHUB_TOKEN` **Colab Secrets**'ta saklanır; notebook `userdata.get("GITHUB_TOKEN")` ile okur | Kullanıcı kararı — "her oturumda yapıştırmak" itirazı üzerine yapıştır/getpass yerine bu seçildi. Token bir kez, Google hesabına bağlı girilir; her oturum/notebook'ta hazır, **notebook kaynağına ve repoya hiç girmez** → sızıntı engeli disipline değil yapıya bağlanır. Token yalnız klon URL'inde kullanılır, hiçbir çıktıya basılmaz. |
| Token = **fine-grained, yalnız bu repo, `Contents: read`** | Kullanıcı kararı. En dar yetki: token sızsa bile yalnız Internal-tools'u okur, başka hiçbir şeye dokunamaz. README kurulum adımları bu türe göre yazılır. |
| `README.md` **İngilizce** | Kullanıcı kararı. Diğer repo dokümanlarıyla (CLAUDE.md, NOTEBOOK-STANDARD.md) türdeş — geliştirici-yüzü doküman. Notebook markdown'ı ise Türkçe kalır (insan-yüzü). |
| `BRANCH` CONFIG'de değişken; şimdilik varsayılan `feat/queen-editor-v1` | Geliştirme bu dalda; merge sonrası `main` yapılır. Notebook'a gömülü sabit dal, yanlış dalı sessizce çekerdi. |
| Klon her çalıştırmada **sil-yeniden** | Şemsiye karar. Yerelde değişiklik olmadığı için çakışma kavramı yok; tek davranış: son kodu getir. `git pull` senaryosu (kirli ağaç, merge) hiç doğmaz. |
| Token **hiçbir çıktıda basılmaz**; hata olursa git'in stderr'i **token maskelenerek** basılır | Şemsiye karar + repo yorum kuralı (gerçek hata çıktısı basılır, sebep uydurulmaz). Notebook çıktısı paylaşılabilir; token oraya düşerse sızıntıdır. Klon URL'i de basılmaz (token içerir). |

## Notebook standardı (collab-toolbox)

`app.ipynb` bir collab-toolbox notebook'udur; `NOTEBOOK-STANDARD.md`'ye uyar. Bölüm 1'de fiilen geçerli maddeler:

- **§1 CONFIG tek hücre** — tüm ayarlar tek CONFIG hücresinde. *Drive mount first* kuralı bu bölümde uygulanamaz çünkü Drive yok (kapsam dışı); Drive Bölüm 3'te geldiğinde en başa mount edilir.
- **§2 Gür hata** — klon başarısızlığı sessiz geçmez: `RuntimeError`, mesaj **ham** (git'in kendi stderr'i, token maskeli). Sebep uydurulmaz.
- **§7 Dil** — markdown ve `print`/`assert` çıktısı Türkçe, kod yorumları/docstring İngilizce.

Bu bölümde geçmeyen maddeler (§3 model indirme, §4 Civitai, §5 batch, §6 Drive↔disk), `app.ipynb` **Bölüm 4'te** ComfyUI + model kazandığında devreye girer — o turda nova-3dcg'nin kanıtlı desenleri (`fetch`/`check_safetensors`/`civitai_probe`/`process_all`) olduğu gibi devralınır. Referans notebook'un (`loop_maker/comfy_ui.ipynb`) tam kopyalanması Bölüm 1'de yapılmaz: o iskelet model-indirme makinesini getirir, bu bölümün işi yalnız klon. Bölüm 1 notebook'u standardın CONFIG + hata + dil temelini kurar; indirme/batch makinesi sırası gelince eklenir.

## Notebook akışı

`queen-editor/app.ipynb` — üç hücre + başlık markdown'ı. Dil ayrımı: markdown ve `print`/`assert` çıktısı Türkçe, kod yorumları İngilizce.

| Hücre | İçerik |
|---|---|
| 0) Markdown | Ne yapar + kullanım: `app.ipynb`'yi Colab'a yükle → 🔑 Secrets'a `GITHUB_TOKEN` ekle (bir kez) → Run all. |
| 1) CONFIG | `GITHUB_TOKEN = userdata.get("GITHUB_TOKEN")` (Colab Secrets), `BRANCH = "feat/queen-editor-v1"`, `REPO = "AltanBaysal/Internal-tools"`, `CLONE_DIR = "/content/Internal-tools"`. Secret yoksa/erişim kapalıysa `assert` Türkçe fail-loud (🔑 Secrets'a ekle der). |
| 2) Klon | `CLONE_DIR` varsa `shutil.rmtree`; `git clone --branch <BRANCH> --depth 1 https://<token>@github.com/<REPO>.git <CLONE_DIR>`. Non-zero exit → git stderr, token `<token>` ile maskelenmiş, `RuntimeError`. |
| 3) Doğrula | `queen-editor/` içeriğini listele; `git -C <CLONE_DIR> rev-parse --short HEAD` ve dal adını bas. `queen-editor/app.ipynb` yoksa fail-loud (yanlış dal / eksik dosya). |

Klon için `subprocess.run` (shell değil, argüman listesi) — token'ın shell geçmişine ya da log'a sızmasını önler; komutun tam çıktısı yakalanıp maskelenerek basılır.

## README.md (İngilizce)

Geliştirici/operatör kılavuzu, kısa: (1) fine-grained token oluşturma — GitHub → Settings → Developer settings → Fine-grained tokens → yalnız `Internal-tools`, `Repository permissions → Contents: Read-only`; (2) `queen-editor/app.ipynb`'yi Colab'a yükleme; (3) token'ı 🔑 Secrets'a `GITHUB_TOKEN` adıyla ekleyip (notebook erişimi açık) Run all; (4) çıktıda ne görüleceği. Token'ın Secrets'ta durup notebook'a hiç girmediği burada da belirtilir.

## Bootstrap ikiliği (bilinçli)

Colab'da çalışan `app.ipynb` = kullanıcının yüklediği kopya. Klon, diske ikinci bir kopya indirir (`<CLONE_DIR>/queen-editor/app.ipynb`). Bölüm 1'de bu ikinci kopya yalnız "indi mi" kanıtı. Bölüm 2'den itibaren sunucu klonlanan `queen-editor/`'dan başlar; kullanıcının yüklediği notebook yalnız bootstrap eder.

## Doğrulama (kullanıcı, Colab)

1. `queen-editor/app.ipynb`'yi GitHub'dan indir → Colab **File → Upload notebook**.
2. 🔑 Secrets panelinden `GITHUB_TOKEN` ekle (fine-grained, yalnız bu repo, Contents: read), notebook erişimini aç — **bir kez** → **Run all**.
3. Hücre çıktısında `queen-editor/` içeriği (`app.ipynb`, `README.md`), kısa commit hash ve `feat/queen-editor-v1` görünür.
4. Çıktının hiçbir yerinde token yok.
5. Secret yok/erişim kapalı iken çalıştır → Türkçe "GITHUB_TOKEN yok" hatası, klon denenmez.
6. (Negatif) Yanlış/expired token → git'in kendi hata mesajı (401/403), token maskeli.
7. Sonraki oturumlarda token tekrar girilmez — Secrets'tan gelir.

## Riskler

- **Colab'da `git clone` private repoya token'la erişemezse** — bu bölümün asıl sınadığı şey. Hata git'in kendi çıktısıyla görünür; sebep uydurulmaz.
- **Token artık notebook'a hiç girmez** (Colab Secrets'ta durur) — "yanlışlıkla commit'leme" riski yapısal olarak kalkar.
