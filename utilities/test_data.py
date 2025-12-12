class TestData:
    VALID_USERS = [
        ("standard_user", "secret_sauce"),
        ("probl2em_user", "sec2ret_sauce"),
        ("performance_glitch_user", "secret_sauce")
    ]

    # BURADA ARTIK DB BAĞLANTISI YOK (Hata riskini sıfırladık)
    # Sadece veritabanından hangi mesajı çekeceğimizin KODUNU (Key) yazıyoruz.
    # Veriyi testin kendisi, çalışma anında çekecek.
    INVALID_LOGIN_DATA = [
        ("locked_out_user", "secret_sauce", "LOCKED"),
        ("standard_user", "yanlis_sifre", "INVALID"),
        ("olmayan_kullanici", "secret_sauce", "INVALID")
    ]