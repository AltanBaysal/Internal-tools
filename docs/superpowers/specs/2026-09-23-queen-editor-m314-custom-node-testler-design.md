# Madde 314 — Custom node hücresi kısalıyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Deneme kullanıcının, iş bittikten sonra: yeni bir makinede
Impact-Pack'in süresi, ve bir foto koşusunda yüz düzeltmesi.

## Bugün ne oluyor

Custom node hücresi *(`8e4cc402`)* 21 node'u sırayla, kendi döngüsüyle kuruyor: yerinde duranı
atlıyor, kalanı `git clone --depth 1 --recurse-submodules` ile klonluyor, klasör boş kalırsa duruyor,
`requirements.txt` varsa `pip install -q -r` ile kuruyor. Döngü hücrede olduğu için hiçbir test onu
çalıştırmıyor. Kullanıcının koşusunda hücre 6 dk 2 sn sürdü, bunun 3 dk 13 sn'si Impact-Pack'ti.

## Kural

**(1) Impact-Pack'in listesi `sam2` satırı olmadan kuruluyor.** Satır
`git+https://github.com/facebookresearch/sam2`. Hazır paket değil: pip onu GitHub'dan çekip makinede
derliyor, ve `sam2`'nin `pyproject.toml`'u derleme için `torch>=2.5.1` istediğinden pip, derleme
ortamına torch'u CUDA kütüphaneleriyle baştan kuruyor. Grafiğimiz SAM'in ilk sürümünü
(`sam_vit_b_01ec64.pth`) `segment-anything` ile yüklüyor; Impact-Pack `sam2`'yi yalnız kuruluysa import
ediyor *(`core.py`, `find_spec("sam2")`)*. Listenin geri kalanı eksiksiz ve sırasıyla kuruluyor; pip'e
bugünkü gibi bir liste dosyası (`-r`) veriliyor.

**(2) Konsol atlananı söylüyor** — node'un adı ve `sam2` aynı satırda. ComfyUI log'unda *"SAM2
kullanılamıyor"* notunu gören, sebebini defterin çıktısında buluyor.

**(3) Başka hiçbir node'un listesine dokunulmuyor.**

**(4) Node kurulumu `colab/nodes.py`'de: `install_node(ad, adres, klasör)`.** Bugünkü döngünün
yaptığını yapıyor: yerinde ve dolu duran node'a dokunmuyor, *"zaten var"* diyor; başlarken adını
saatle yazıyor — kullanıcı her node'un süresini bu satırların arasından okuyor, 3 dk 13 sn de böyle
bulundu; `git clone --depth 1 --recurse-submodules` ile `klasör/ad`'a klonluyor; klon boş kalırsa
node'un adıyla duruyor; `requirements.txt` varsa pip'e veriyor, yoksa pip çağrılmıyor. **Liste
defterde kalıyor** — 310'daki indirme listeleri gibi; döngü `install_node`'u çağırıyor, ad yardımcılar
hücresinde `colab.nodes`'tan import ediliyor.

## Yazılacak testler

### `test_colab_nodes.py` — yeni; koşularak

Ağ sahte, klasörler gerçek. `run` yerine geçen sahte git ve pip: klon, testin verdiği dosyaları
komutun adlandırdığı klasöre yazıyor; pip, `-r`'den sonraki dosyanın satırlarını çağrıldığı an okuyup
saklıyor. Impact-Pack'in ve DaSiWa'nın listeleri 23 Eylül'deki hâlleriyle, kelimesi kelimesine.

1. **Impact-Pack `sam2`'siz kuruluyor** — pip'e giden satırlar, listenin `sam2` dışındaki dokuz
   satırı, sırasıyla.
2. **Konsol `sam2`'nin atlandığını söylüyor** — `ComfyUI-Impact-Pack` ve `sam2` aynı satırda.
3. **Başka bir node'un listesi eksiksiz kuruluyor** — DaSiWa'nın sekiz satırı, `torch` dahil.
4. **Liste dosyası olmayan node'a pip çağrılmıyor** — tek komut, klon.
5. **Yerinde duran node'a dokunulmuyor** — hiçbir komut yok, konsol *"zaten var"*.
6. **Boş kalan klon koşuyu durduruyor** — `RuntimeError`, cümlesinde node'un adı.
7. **Node sığ ve alt modülleriyle, kendi adlı klasörüne klonlanıyor** — komut `git clone`,
   `--depth 1`, `--recurse-submodules`; dosyalar `klasör/ad`'da; konsolda saatin hemen ardından
   node'un adı gelen bir satır — `[19:16:39] ComfyUI-Impact-Pack: …` gibi.

### `test_notebook_installs_the_producer_groups.py` — defter, okunarak

8. **Defter node'larını `install_node` ile kuruyor** — `CUSTOM_NODES` hücresinde
   `for name, url in CUSTOM_NODES:` döngüsü `install_node(name, url, ` çağırıyor, ve ad
   `colab.nodes`'tan import ediliyor.

**Değişen:** yok.

**Bekçiler, bugün de yeşil:** `test_the_notebook_says_how_many_custom_nodes_it_installs` ve
`test_the_intro_agrees_with_the_custom_node_list` — liste defterde, satırları aynı;
`test_the_notebook_installs_the_nodes_the_h3_graph_asks_for` ve
`test_the_notebook_installs_the_encoder_the_graph_asks_for`;
`test_every_name_the_notebook_imports_from_its_code_exists` — defter `install_node`'u import etmeye
başlayınca o adı da o tutar; `test_the_notebook_defines_none_of_the_code_it_imports`; `hf_xet`'in
kurulduğunu arayan satır *(hücrede kalıyor)*; ve `test_notebook_stays_readable.py` — defter kısalıyor.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — yalnız 1–8 *(1–7 modül henüz olmadığı için
kurulumda hata olarak)*.
