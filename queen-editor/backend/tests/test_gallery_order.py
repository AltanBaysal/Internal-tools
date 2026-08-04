from backend.features.photo_generation.domain.gallery_order import apply_order


def rows(*files):
    return [{"file": f, "prompt": "p"} for f in files]


def files(result):
    return [row["file"] for row in result]


def test_sirasiz_kayit_kendi_sirasinda_kalir():
    assert files(apply_order(rows("2_a.png", "1_a.png"), [])) == ["2_a.png", "1_a.png"]


def test_saklanan_sira_uygulanir():
    result = apply_order(rows("2_a.png", "1_a.png", "0_a.png"),
                         ["0_a.png", "2_a.png", "1_a.png"])
    assert files(result) == ["0_a.png", "2_a.png", "1_a.png"]


def test_sirada_olmayan_yeni_fotograflar_en_uste_gelir():
    # The record is newest-first, so 4_a is newer than 3_a and stays above it.
    result = apply_order(rows("4_a.png", "3_a.png", "1_a.png", "0_a.png"),
                         ["0_a.png", "1_a.png"])
    assert files(result) == ["4_a.png", "3_a.png", "0_a.png", "1_a.png"]


def test_kayitta_olmayan_ad_yok_sayilir():
    result = apply_order(rows("1_a.png"), ["silinmis.png", "1_a.png"])
    assert files(result) == ["1_a.png"]


def test_ayni_ad_iki_kez_gecerse_bir_kez_dizilir():
    result = apply_order(rows("1_a.png", "0_a.png"), ["1_a.png", "1_a.png", "0_a.png"])
    assert files(result) == ["1_a.png", "0_a.png"]


def test_bos_kayit_bos_doner():
    assert apply_order([], ["1_a.png"]) == []
