from money_data import MoneyOpen

Valek = "Valek"
Timoha = "Timoha"
Ilya = "Ilya"
Timofey = "Timofey"
All = "all"


with MoneyOpen("data.bin") as work:
    # work.pay(Timoha, All, 2000)
    # work.pay(Valek, All, 500)
    print(work)


