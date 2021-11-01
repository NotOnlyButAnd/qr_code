#########################
# SUMMARY
#########################
# Программа для кодирования информации
# и представления ее в виде qr кода.
# Был выбран байтовый способ кодирования, так как в тексте
# будут содержаться спец символы и буквы русского алфавита
#########################

# на входе - байтовое представление строки
# на выходе - бинарное представление
def binaryEncodingUTF(my_bytes):
    binary_enc = ""
    for byte in my_bytes:
        temp_bin = bin(byte)[2::]   # отсекаем первые два символа беспонтовые эти 0b
        # print(type(temp_bin))
        if len(temp_bin) < 8:
            binary_enc += "0" * (8 - len(temp_bin)) + temp_bin  # добавляем нулей вперед, если длина меньше 8
        else:
            binary_enc += temp_bin
        # binary_enc += " | "
    return binary_enc


# Строка данных для кодирования (пример, общий вид)
encoding_string = "s15Njg81Ldj64LvzkH8A|\"01.11.2021 21:29:25\"|\"36/1\"|1|\"Компьютерные сети\"|\"Приходько Татьяна Александровна\""
# encoding_string = "\"Компьютерные сети\""


##############################
# побайтовое кодирование
##############################
# получаем байтовое представление UTF-8
bytes_encoded = encoding_string.encode(encoding='utf_8', errors='replace')

# получаем бинарное представление UTF-8
binary_encoded = binaryEncodingUTF(bytes_encoded)

print(f"Original string: {encoding_string}")
print(f"Original string length: {len(encoding_string)}")
print(f"Bytes encoded string (utf_8): {bytes_encoded}")
print(f"Bytes list [0:2]: {list(bytes_encoded[0:2])}")
# for i in bytes_encoded:
#     print(bin(i))
# out = open('out.txt', 'w')
# out.write(str(bytes_encoded))
# out.close()
print(f"Binary encoded string: {binary_encoded}")
print(f"Binary encoded string length: {len(binary_encoded)}")
print(f"Count of bites in binary enc: {len(binary_encoded) / 8}")


##############################
# добавление служебных полей
##############################
# способ кодирования - байтовый => в начало добавляем 0100
# сразу сделаем qr код с заделом на добавление логотипа кубгу: версия 16 и уровень коррекции H
# длина поля количества данных в любом случае будет 16 бит т.е. 2 байта (11, 12, 16, 17 версии)
# количество данных - len(binary_encoded) / 8 - кол-во байт в исходной посл-ти
dec_amount_data = int(len(binary_encoded) / 8)   # кол-во данных = кол-во байт (decimal)
# dec_amount_data = 39746
bin_amount_data = bin(dec_amount_data)[2::]
if len(bin_amount_data) < 16:
    bin_amount_data = "0" * (16 - len(bin_amount_data)) + bin_amount_data

print(f"Binary amount data: {bin_amount_data}")
encoding_method = "0100"

data_ready = encoding_method + bin_amount_data + binary_encoded

print(f"Data ready: {encoding_method} | {bin_amount_data} | {binary_encoded}")
# print(data_ready)


###############
# заполнение
###############
# т.к. 16 версия и H уровень коррекции, то макс данные = 2024 бит = 253 байт
# сперва выясняем ск-ко незначащих нулей в конце надо добваить:
count_zero = len(data_ready) % 8    # остаток от деления на 8 берем
data_ready += "0" * count_zero
print(data_ready)
# заново считаем кол-во байт, чтобы узнать, сколько заполняющих в конце надо добавить байт
# print(int(len(data_ready) / 8))
count_bites_data = int(len(data_ready) / 8)
if count_bites_data < 253:
    flag = True
    for i in range(0, 253 - count_bites_data):
        if flag:
            data_ready += "11101100"    # первый какой-то особый байт заполняющий
            flag = False
        else:
            data_ready += "00010001"    # второй какой-то особый байт заполняющий
            flag = True
print(data_ready)
count_bites_data = int(len(data_ready) / 8)
print(count_bites_data)


####################################
# разделение информации на блоки
####################################
print(len(data_ready))
length_block = int(count_bites_data / 16)  # 253 / 16 = 15,815 => 15 длина каждого блока
remainder_div = count_bites_data % 16
print(f"Length: {length_block}; Remain: {remainder_div}")
blocks = [length_block] * 16
print(blocks)
# идем от последнего индекса назад, добавляя в каждый блок по 1 байту
for i in range(15, 15 - remainder_div, -1):
    blocks[i] += 1
print(blocks)
