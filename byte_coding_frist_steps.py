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

for i in range(0, len(blocks)):
    count_bytes = blocks[i]
    blocks[i] = data_ready[:count_bytes*8:]
    data_ready = data_ready[count_bytes*8::]
print(f"blocks: {blocks}")
print(f"data_ready: {data_ready}")
str_bytes_block = ""
for block in blocks:
    str_bytes_block += f" {len(block)}"
print(str_bytes_block)

#######
# создадим копию блоков данных: (она в принципе не нужна, блоки не изменяются при построении блоков коррекции
#######
blocks_copy = blocks.copy()
#######
# создадим список блоков коррекции:
#######
correction_blocks = []
#######
# создадим поля Голуа: (пока из статьи на хабре)
#######
inverse_galoi_256 = [None, 0, 1, 25, 2, 50, 26, 198, 3, 223, 51, 238, 27, 104, 199, 75,
                     4, 100, 224, 14, 52, 141, 239, 129, 28, 193, 105, 248, 200, 8, 76, 113,
                     5, 138, 101, 47, 225, 36, 15, 33, 53, 147, 142, 218, 240, 18, 130, 69,
                     29, 181, 194, 125, 106, 39, 249, 185, 201, 154, 9, 120, 77, 228, 114, 166,
                     6, 191, 139, 98, 102, 221, 48, 253, 226, 152, 37, 179, 16, 145, 34, 136,
                     54, 208, 148, 206, 143, 150, 219, 189, 241, 210, 19, 92, 131, 56, 70, 64,
                     30, 66, 182, 163, 195, 72, 126, 110, 107, 58, 40, 84, 250, 133, 186, 61,
                     202, 94, 155, 159, 10, 21, 121, 43, 78, 212, 229, 172, 115, 243, 167, 87,
                     7, 112, 192, 247, 140, 128, 99, 13, 103, 74, 222, 237, 49, 197, 254, 24,
                     227, 165, 153, 119, 38, 184, 180, 124, 17, 68, 146, 217, 35, 32, 137, 46,
                     55, 63, 209, 91, 149, 188, 207, 205, 144, 135, 151, 178, 220, 252, 190, 97,
                     242, 86, 211, 171, 20, 42, 93, 158, 132, 60, 57, 83, 71, 109, 65, 162,
                     31, 45, 67, 216, 183, 123, 164, 118, 196, 23, 73, 236, 127, 12, 111, 246,
                     108, 161, 59, 82, 41, 157, 85, 170, 251, 96, 134, 177, 187, 204, 62, 90,
                     203, 89, 95, 176, 156, 169, 160, 81, 11, 245, 22, 235, 122, 117, 44, 215,
                     79, 174, 213, 233, 230, 231, 173, 232, 116, 214, 244, 234, 168, 80, 88, 175]
galoi_256 = [1, 2, 4, 8, 16, 32, 64, 128, 29, 58, 116, 232, 205, 135, 19, 38,
             76, 152, 45, 90, 180, 117, 234, 201, 143, 3, 6, 12, 24, 48, 96, 192,
             157, 39, 78, 156, 37, 74, 148, 53, 106, 212, 181, 119, 238, 193, 159, 35,
             70, 140, 5, 10, 20, 40, 80, 160, 93, 186, 105, 210, 185, 111, 222, 161,
             95, 190, 97, 194, 153, 47, 94, 188, 101, 202, 137, 15, 30, 60, 120, 240,
             253, 231, 211, 187, 107, 214, 177, 127, 254, 225,  223, 163, 91, 182, 113, 226,
             217, 175, 67, 134, 17, 34, 68, 136, 13, 26, 52, 104, 208, 189, 103, 206,
             129, 31, 62, 124, 248, 237, 199, 147, 59, 118, 236, 197, 151, 51, 102, 204,
             133, 23, 46, 92, 184, 109, 218, 169, 79, 158, 33, 66, 132, 21, 42, 84,
             168, 77, 154, 41, 82, 164, 85, 170, 73, 146, 57, 114, 228, 213, 183, 115,
             230, 209, 191, 99, 198, 145, 63, 126, 252, 229, 215, 179, 123, 246, 241, 255,
             227, 219, 171, 75, 150, 49, 98, 196, 149, 55, 110, 220, 165, 87, 174, 65,
             130, 25, 50, 100, 200, 141, 7, 14, 28, 56, 112, 224, 221, 167, 83, 166,
             81, 162, 89, 178, 121, 242, 249, 239, 195, 155, 43, 86, 172, 69, 138, 9,
             18, 36, 72, 144, 61, 122, 244, 245, 247, 243, 251, 235, 203, 139, 11, 22,
             44, 88, 176, 125, 250, 233, 207, 131, 27, 54, 108, 216, 173, 71, 142, 1]
# print(f"Galoi 256 length: {len(galoi_256)}")
# print(f"Inverse galoi 256 length: {len(inverse_galoi_256)}")


# т.к. 16 версия и уровень корреции H то нужно
# 30 байтов коррекции на один блок
# коэффициенты генерирующего многочлена:
# 41, 173, 145, 152, 216, 31, 179, 182, 50, 48, 110, 86, 239, 96, 222,
# 125, 42, 173, 226, 193, 224, 130, 156, 37, 251, 216, 238, 40, 192, 180
generic_poly = [41, 173, 145, 152, 216, 31, 179, 182, 50, 48, 110, 86, 239, 96, 222,
                125, 42, 173, 226, 193, 224, 130, 156, 37, 251, 216, 238, 40, 192, 180]
for block in blocks:
    print("///////////// start of block ///////////////////")
    count_bytes = int(len(block) / 8)
    length_arr = max(30, count_bytes)
    # print(length_arr)
    arr = []
    for i in range(0, length_arr):
        if i < count_bytes:
            arr.append(block[:8:])  # добавляем байты из блока в массив
            block = block[8::]
        else:
            arr.append("0"*8)   # добавляем нулевые байты если данные кончились
    print(arr)
    print(len(arr))

    for i in range(0, count_bytes):
        generic_poly_copy = generic_poly.copy()
        A = arr[i]
        print(f"AAAAAAAA: {A}")
        # удаляем первый элемент, и двигаем все оставшиеся влево на один
        # print(f"old_arr: {arr}")
        for j in range(0, count_bytes - 1):
            arr[j] = arr[j+1]
        arr[count_bytes - 1] = "0" * 8
        # print(f"new_arr: {arr}")
        if int(A, 2) != 0:
            B = inverse_galoi_256[int(A, 2)]    # здесь А из строки приводится к иинтегер
            # прибавляем B по модулю 255 к каждому числу ген многочл
            ############### !!
            # ПОУБИРАТЬ ВСЯКИЕ ТЕМП СУМ ДЛЯ ВЫВОДА
            ############### !!
            for j in range(0, len(generic_poly_copy)):
                temp = generic_poly_copy[j]
                tempsum = generic_poly_copy[j] + B
                generic_poly_copy[j] = (B + generic_poly_copy[j]) % 255
                # print(f"B: {B} + poly: {temp} = sum: {tempsum}; temp_mod_255: {generic_poly_copy[j]}")
                # находим соотв-вие из галуа 256
                generic_poly_copy[j] = galoi_256[generic_poly_copy[j]]
                # print(f"galoi 256 generic: {generic_poly_copy[j]}")
                # побитовое сложение по модулю два с arr данных
                # сперва переведем в двоичный вид нормальный
                generic_poly_copy[j] = bin(generic_poly_copy[j])
                generic_poly_copy[j] = generic_poly_copy[j][2::]    # отрезали начало беспонтовое
                if len(generic_poly_copy[j]) < 8:
                    generic_poly_copy[j] = "0" * (8 - len(generic_poly_copy[j])) + generic_poly_copy[j]
                # print(f"galoi 256 (double) generic: {generic_poly_copy[j]}")
                # print(f"arr[j] double:              {arr[j]}")
                for k in range(0, len(arr[j])):
                    if (arr[j][k] == '0' and generic_poly_copy[j][k] == '0') or (arr[j][k] == '1' and generic_poly_copy[j][k] == '1'):
                        arr[j] = arr[j][:k:] + '0' + arr[j][k + 1::]    # разрезали строку, вставили символ
                    else:
                        arr[j] = arr[j][:k:] + '1' + arr[j][k + 1::]
                # print(f"arr[j] double SUM:          {arr[j]}")

            print(f"/// Generic + B: {generic_poly_copy}")
            print(f"/// cur ARR result (correction bytes): {arr}")

    print(f"//////////// ARR result (correction bytes): {arr}")
    print("///////////// end of block ///////////////////")
    correction_blocks.append(arr.copy())

# print(f"\nblocks: {blocks}\nblocks_copy:{blocks_copy}")
# for i in range(0, len(blocks)):
#     if blocks[i] != blocks_copy[i]:
#         print("FALSE!")
print(f"\nSo...\nblocks (data, len - {len(blocks)}): {blocks}\ncorrection bytes for blocks (len - {len(blocks)}):{correction_blocks}")
# for i in correction_blocks:
#     print(len(i))

###########################
# Объединение блоков:
###########################
# делим блоки данных на байты (ЛУЧШЕ ЭТО РАНЬШЕ СДЕЛАТЬ, ДА!!!)
for i in range(0, len(blocks)):
    temp = []
    for j in range(0, int(len(blocks[i]) / 8)):
        temp.append(blocks[i][:8:])
        blocks[i] = blocks[i][8::]
    blocks[i] = temp.copy()
print(f"Divided blocks (data, len - {len(blocks)}): {blocks}")
# for i in blocks:
#      print(len(i))

# создаем список итоговой последовательности (данные + коррекция, побайтово)
ready_data_flow = []
# сначала добавим данные
num_byte = 0    # номер текущего записываемого байта
is_empty_data = False
while not is_empty_data:
    is_empty_data = True
    for i in range(0, len(blocks)):
        if num_byte <= len(blocks[i]) - 1:   # если еще есть в блоке данные с таким номером
            ready_data_flow.append(blocks[i][num_byte])
            # print(f"add blocks[{i}][{num_byte}]...")
            is_empty_data = False
    num_byte += 1
print(f"DATA FLOW (data only, len - {len(ready_data_flow)}): {ready_data_flow}")    # данные добавлены верно, блоки коррекции добавляем аналогично

# хотя кол-во байтов коррекции для каждого блока одинаково... можно просто фором бежать
for i in range(0,30):
    for j in range(0, len(correction_blocks)):
        # print(f"add correction blocks[{j}][{i}]...")  # коррекционные тоже верно добавлены
        ready_data_flow.append(correction_blocks[j][i])

print(f"DATA FLOW (data + correct, len - {len(ready_data_flow)}): {ready_data_flow}")   # 733 - 253 = 480 B добавлено было, а это и есть 16 блоков по 30 байт
