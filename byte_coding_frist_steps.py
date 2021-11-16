#########################
# SUMMARY
#########################
# Программа для кодирования информации
# и представления ее в виде qr кода.
# Был выбран байтовый способ кодирования, так как в тексте
# будут содержаться спец символы и буквы русского алфавита
#########################

# библиотека для рисования
from PIL import Image, ImageDraw, ImageColor, ImageFont


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


def get_mask(x, y):
    # 0 маска
    return (x + y) % 2
    # 2 маска
    # return x % 3


def invert(num):
    if num == 0:
        return 1
    elif num == 1:
        return 0
    else:
        return -1


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
    #print("///////////// start of block ///////////////////")
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
    #print(arr)
    #print(len(arr))

    for i in range(0, count_bytes):
        generic_poly_copy = generic_poly.copy()
        A = arr[i]
        #print(f"AAAAAAAA: {A}")
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

            #print(f"/// Generic + B: {generic_poly_copy}")
            #print(f"/// cur ARR result (correction bytes): {arr}")

    #print(f"//////////// ARR result (correction bytes): {arr}")
    #print("///////////// end of block ///////////////////")
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


############################################
# НОВЫЙ СПОСОБ ПРЕДСТАВЛЕНИЯ КОДА!!!
############################################
# метод выводит матрицу в файл там удобнее смотреть
def print_matr_file(matrix):
    output = open('matrix.txt', 'w')
    for strin in matrix:
        output.write(str(strin) + "\n")
    output.close()


def color_str_matr(matrix, color, strings=[0]):
    for string in strings:
        matrix[string] = [color] * len(matrix[string])


def color_col_matr(matrix, color, columns=[0]):
    for column in columns:
        for string in range(len(matrix)):
            matrix[string][column] = color


def color_empty_rect_matr(matrix, color, coordinates=[0, 0, 3, 3]):
    # рисуем, при смещении по иксу
    for elem in range(coordinates[0], coordinates[2] + 1):
        matrix[coordinates[1]][elem] = color
        matrix[coordinates[3]][elem] = color
    # рисуем, при смещении по игреку
    for elem in range(coordinates[1], coordinates[3] + 1):
        matrix[elem][coordinates[0]] = color
        matrix[elem][coordinates[2]] = color


def color_rect_matr(matrix, color, coordinates=[0, 0, 3, 3]):
    # первый фор - по иксу
    for i in range(coordinates[0], coordinates[2] + 1):
        # второй фор - по игреку
        for j in range(coordinates[1], coordinates[3] + 1):
            matrix[j][i] = color


def color_vert_line_matr(matrix, color, coordinates=[0, 0, 0, 3]):
    for i in range(coordinates[1], coordinates[3] + 1):
        matrix[i][coordinates[0]] = color


def color_horiz_line_matr(matrix, color, coordinates=[0, 0, 3, 0]):
    for i in range(coordinates[0], coordinates[2] + 1):
        matrix[coordinates[1]][i] = color


def draw_qr(matrix):
    im_wid_heig = 890
    module = im_wid_heig / 89  # pixels - ширина длина блока модуля
    image = Image.new("RGB", (im_wid_heig, im_wid_heig))
    draw = ImageDraw.Draw(image)
    # заливаем белый фон
    draw.rectangle((0, 0, im_wid_heig, im_wid_heig), fill=ImageColor.getrgb("white"))
    # рисуем блоки
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i][j] == 1:
                draw.rectangle((j * module, i * module, j * module + module, i * module + module), fill=ImageColor.getrgb("black"))
    image.save("my_qr.png", "PNG")


def add_up(c_x, c_y, matr, data_f, log_file, is_end_f):
    while c_y != 3:
        # рисуем текущий уровень
        if matr[c_y][c_x] == 2:
            # print(f"data_flow[0] = {data_flow[0]}")
            if get_mask(c_x, c_y) == 0 and not is_end_f:
                matr[c_y][c_x] = invert(int(data_f[0]))
            elif get_mask(c_x, c_y) == 1 and not is_end_f:
                matr[c_y][c_x] = int(data_f[0])
            # если уже данных нет, то единица если инвертируем
            elif get_mask(c_x, c_y) == 0 and is_end_f:
                matr[c_y][c_x] = 1
            elif get_mask(c_x, c_y) == 1 and is_end_f:
                matr[c_y][c_x] = 0

            # проверяем, конец ли данных
            if len(data_f) == 1:
                is_end_f = True
                data_f = ""
                print("!!!END OF FLOW!!!")
            elif len(data_f) > 1:
                log_file.write(
                    f"\nif 1: ({c_x}, {c_y}): {matr[c_y][c_x]} (data_flow - {data_f[0]}, mask - {get_mask(c_x, c_y)}, end? - {is_end_f}")
                data_f = data_f[1::]  # отсекаем зарисованный символ
                log_file.write(f"\nnew data flow - {data_f[:10:]}...")

            # print(f"data_flow[0] = {data_flow[0]} END")
        if matr[c_y][c_x - 1] == 2:
            # print(f"data_flow[0] = {data_flow[0]}")
            if get_mask(c_x - 1, c_y) == 0 and not is_end_f:
                matr[c_y][c_x - 1] = invert(int(data_f[0]))
            elif get_mask(c_x - 1, c_y) == 1 and not is_end_f:
                matr[c_y][c_x - 1] = int(data_f[0])
            # если уже данных нет, то единица если инвертируем
            elif get_mask(c_x - 1, c_y) == 0 and is_end_f:
                matr[c_y][c_x - 1] = 1
            elif get_mask(c_x - 1, c_y) == 1 and is_end_f:
                matr[c_y][c_x - 1] = 0

            # проверяем, конец ли данных
            if len(data_f) == 1:
                is_end_f = True
                data_f = ""
                print("!!!END OF FLOW!!!")
            elif len(data_f) > 1:
                log_file.write(
                    f"\nif 2: ({c_x - 1}, {c_y}): {matr[c_y][c_x - 1]} (data_flow - {data_f[0]}, mask - {get_mask(c_x - 1, c_y)}, end? - {is_end_f})")
                data_f = data_f[1::]  # отсекаем зарисованный символ
                log_file.write(f"\nnew data flow - {data_f[:10:]}...")

        c_y -= 1
    return data_f, is_end_f


def add_down(c_x, c_y, matr, data_f, log_file, is_end_f):
    while c_y != 85:
        # рисуем текущий уровень
        if matr[c_y][c_x] == 2:
            # print(f"data_flow[0] = {data_flow[0]}")
            if get_mask(c_x, c_y) == 0 and not is_end_f:
                matr[c_y][c_x] = invert(int(data_f[0]))
            elif get_mask(c_x, c_y) == 1 and not is_end_f:
                matr[c_y][c_x] = int(data_f[0])
            # если уже данных нет, то единица если инвертируем
            elif get_mask(c_x, c_y) == 0 and is_end_f:
                matr[c_y][c_x] = 1
            elif get_mask(c_x, c_y) == 1 and is_end_f:
                matr[c_y][c_x] = 0

            # проверяем, конец ли данных
            if len(data_f) == 1:
                is_end_f = True
                data_f = ""
                print("!!!END OF FLOW!!!")
            elif len(data_f) > 1:
                log_file.write(
                    f"\nif 1: ({c_x}, {c_y}): {matr[c_y][c_x]} (data_flow - {data_f[0]}, mask - {get_mask(c_x, c_y)}, end? - {is_end_f}")
                data_f = data_f[1::]  # отсекаем зарисованный символ
                log_file.write(f"\nnew data flow - {data_f[:10:]}...")

            # print(f"data_flow[0] = {data_flow[0]} END")
        if matr[c_y][c_x - 1] == 2:
            # print(f"data_flow[0] = {data_flow[0]}")
            if get_mask(c_x - 1, c_y) == 0 and not is_end_f:
                matr[c_y][c_x - 1] = invert(int(data_f[0]))
            elif get_mask(c_x - 1, c_y) == 1 and not is_end_f:
                matr[c_y][c_x - 1] = int(data_f[0])
            # если уже данных нет, то единица если инвертируем
            elif get_mask(c_x - 1, c_y) == 0 and is_end_f:
                matr[c_y][c_x - 1] = 1
            elif get_mask(c_x - 1, c_y) == 1 and is_end_f:
                matr[c_y][c_x - 1] = 0

            # проверяем, конец ли данных
            if len(data_f) == 1:
                is_end_f = True
                data_f = ""
                print("!!!END OF FLOW!!!")
            elif len(data_f) > 1:
                log_file.write(
                    f"\nif 2: ({c_x - 1}, {c_y}): {matr[c_y][c_x - 1]} (data_flow - {data_f[0]}, mask - {get_mask(c_x - 1, c_y)}, end? - {is_end_f})")
                data_f = data_f[1::]  # отсекаем зарисованный символ
                log_file.write(f"\nnew data flow - {data_f[:10:]}...")

        c_y += 1
    return data_f, is_end_f


# строка не использ блоков, с учетом модулей отступа (по 4 с каждой стороны,
# следовательно на сам код - 81 модуль!!!!!)
count_modules = 89

# 2 - не использ, 0 - белый, 1 - черный
black = 1
white = 0
not_used = 2
# матрица показывает, какие модули окрашены в белый, какие в черный, а какие не использованы
def_str = [not_used] * count_modules
used_c_1 = []
for i in range(count_modules):
    temp_str = def_str.copy()
    used_c_1.append(temp_str)

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# закрашиваем отступы т.е. по 4 модуля слева, справа, сверху и снизу - белые
#########
indents = [0, 1, 2, 3, 85, 86, 87, 88]
indent = 4
# верхний и нижний
color_str_matr(used_c_1, white, indents)
# левый и правый
color_col_matr(used_c_1, white, indents)
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# Верхний левый поисковый узор:
#########
# внеш черн
color_empty_rect_matr(used_c_1, black, [4, 4, 10, 10])
# средн бел
color_empty_rect_matr(used_c_1, white, [5, 5, 9, 9])
# внутр черн
color_rect_matr(used_c_1, black, [6, 6, 8, 8])
# внешн бел, две стороны
color_vert_line_matr(used_c_1, white, [11, 4, 11, 11])
color_horiz_line_matr(used_c_1, white, [4, 11, 11, 11])
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# Верхний правый поисковый узор:
#########
# внеш черн
color_empty_rect_matr(used_c_1, black, [78, 4, 78 + 6, 10])
# средн бел
color_empty_rect_matr(used_c_1, white, [79, 5, 78 + 6 - 1, 9])
# внутр черн
color_rect_matr(used_c_1, black, [80, 6, 78 + 6 - 2, 8])
# внешн бел, две стороны
color_vert_line_matr(used_c_1, white, [77, 4, 77, 11])
color_horiz_line_matr(used_c_1, white, [77, 11, 84, 11])
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# Нижний левый поисковый узор:
#########
# внеш черн
color_empty_rect_matr(used_c_1, black, [4, 78, 10, 78 + 6])
# средн бел
color_empty_rect_matr(used_c_1, white, [5, 79, 9, 78 + 6 - 1])
# внутр черн
color_rect_matr(used_c_1, black, [6, 80, 8, 78 + 6 - 2])
# внешн бел, две стороны
color_horiz_line_matr(used_c_1, white, [4, 77, 11, 77])
color_vert_line_matr(used_c_1, white, [11, 77, 11, 84])
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# Вертикальная полоса синхронизации:
#########
cur_x = 10
cur_y = 12
is_white = False
while used_c_1[cur_y][cur_x] == 2:
    if is_white:
        used_c_1[cur_y][cur_x] = white
        is_white = False
    else:
        used_c_1[cur_y][cur_x] = black
        is_white = True
    cur_y += 1
# print(f"cur_x: {cur_x}, cur_y: {cur_y}")
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# Горизонтальная полоса синхронизации:
#########
cur_x = 12
cur_y = 10
is_white = False
while used_c_1[cur_y][cur_x] == 2:
    if is_white:
        used_c_1[cur_y][cur_x] = white
        is_white = False
    else:
        used_c_1[cur_y][cur_x] = black
        is_white = True
    cur_x += 1
# print(f"cur_x: {cur_x}, cur_y: {cur_y}")
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# Выравнивающие узоры:
#########
# 16 версия => 6, 26, 50, 74 - места расположения выравнивающих узоров
# т.е. (6, 6) (6, 26) (6, 50) (6, 74) - центры выравнивающих узоров первых
# т.е. (26, 6) (26, 26) (26, 50) (26, 74) - центры выравнивающих узоров вторых и тд...
# чтобы не было наслоения на поисковые, не рисуем точки (6,6) (6,74) и (74,6)
# составляем координаты выравнивающих узоров (центров их)
flat_list = [6, 26, 50, 74]
flat_coords = []
for i in range(len(flat_list)):
    for j in range(len(flat_list)):
        flat_coords.append((flat_list[i], flat_list[j]))
print(f"\n{flat_coords}")
# удаляем ненужные координаты:
del flat_coords[0]
del flat_coords[2]
del flat_coords[len(flat_coords) - 4]
print(flat_coords)
# рисуем узорчики
for center in flat_coords:
    # внутр точка
    # не забываем про отступ от начала!!!
    temp_x = indent + center[0]
    temp_y = indent + center[1]
    used_c_1[temp_y][temp_x] = black
    # бел квадр
    color_empty_rect_matr(used_c_1, white, [temp_x - 1, temp_y - 1, temp_x + 1, temp_y + 1])
    # чер внеш квадр
    color_empty_rect_matr(used_c_1, black, [temp_x - 2, temp_y - 2, temp_x + 2, temp_y + 2])
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# дальше рисуем код версии
# 16 - 011100 010001 011100
ver_code = [0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0]
index = 0
#########
# Вертикальный:
for i in range(74, 77):
    for j in range(4, 10):
        used_c_1[j][i] = ver_code[index]
        index += 1
# Горизонтальный:
index = 0
for i in range(74, 77):
    for j in range(4, 10):
        used_c_1[i][j] = ver_code[index]
        index += 1
#########

#####################################################
# в генераторах
# 001101 100100 011010 - 12 версия
# код маски и уровня коррекции: 00111001 1100111 - H 2
#####################################################

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# код маски и уровня коррекции (0 и H пока что)
# на сайте чтения кодов - 10 000 должно быть начало для H 0 (где 0 - (x + y)%2)
# т.е если брать такую маску с сайта генерации кодов, то это будет: 10000001 1001110
mask_cor_code = [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0]
# H	0	00 101 10 10001001
# mask_cor_code = [0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1]
# H 2   00 111 001 1100111
# mask_cor_code = [0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1]

#########
index = 0
# верхн левый
for i in range(4, 13):
    if used_c_1[12][i] == 2:
        used_c_1[12][i] = mask_cor_code[index]
        index += 1
for i in range(11, 3, -1):
    if used_c_1[i][12] == 2:
        used_c_1[i][12] = mask_cor_code[index]
        index += 1
# нижн левый
index = 0
for i in range(84, 77, -1):
    used_c_1[i][12] = mask_cor_code[index]
    index += 1
# этот бит всегда черный
used_c_1[77][12] = black
# верхн правый
for i in range(77, 85):
    used_c_1[12][i] = mask_cor_code[index]
    index += 1
#########

# Ура. заполням данные!!!
# начинаем с нижнего правого пустого угла
# координаты полосы синхронизации вертикальной, кот пропускаем: cur_x = 10, cur_y = 12
# маска 0 - (X+Y) % 2
# считаем маску для каждого модуля (Х - столбец, Y - строка, % — остаток от деления, / — целочисленное деление)
# если значение = 0, то инвертируем цвет. если = 1 то оставляем как есть
log_file = open("log.txt", 'w')
cur_x = 84
cur_y = 84
# преобразуем поток данных чтобы было проще оттуда данные брать
data_flow = ""
for byte in ready_data_flow:
    data_flow += byte
print(f"data_flow len: {len(data_flow)}: {data_flow}")  # 733 * 8 = 5864 - верно
# заполняем первые 74 блока, до полосы синхронизации. т.е. 37 полос по два блока
is_end_flow = False
is_go_up = True
for i in range(0, 37):
    if is_go_up:
        data_flow, is_end_flow = add_up(cur_x, cur_y, used_c_1, data_flow, log_file, is_end_flow)
        cur_x -= 2
        cur_y = 4
        is_go_up = False
    else:
        data_flow, is_end_flow = add_down(cur_x, cur_y, used_c_1, data_flow, log_file, is_end_flow)
        cur_x -= 2
        cur_y = 84
        is_go_up = True
    # print(f"cur_x - {cur_x}; cur_y - {cur_y}")
    # print(len(data_flow))


# после вертикальной полосы синхронизации:
cur_x = 9
cur_y = 84
for i in range(0, 3):
    if is_go_up:
        data_flow, is_end_flow = add_up(cur_x, cur_y, used_c_1, data_flow, log_file, is_end_flow)
        cur_x -= 2
        cur_y = 4
        is_go_up = False
    else:
        data_flow, is_end_flow = add_down(cur_x, cur_y, used_c_1, data_flow, log_file, is_end_flow)
        cur_x -= 2
        cur_y = 84
        is_go_up = True
    # print(f"cur_x - {cur_x}; cur_y - {cur_y}")
    # print(len(data_flow))
log_file.close()

# ТЕСТЫ:
###########
# color_empty_rect_matr(used_c_1, 1, [11, 11, 16, 13])
# color_rect_matr(used_c_1, 1, [11, 11, 16, 13])
###########

print_matr_file(used_c_1)

draw_qr(used_c_1)


####################
# ПЕЧАТЬ ПЕРВЫХ ДВУХ СТОЛБЦОВ (по 2 блока) в файл
####################
from_matr = ""
count = 0
tfile = open("from_matr.txt", 'w')
for i in range(84, 12, -1):
    if count == 8:
        tfile.write(f" {used_c_1[i][84]}{used_c_1[i][83]}")
        count = 2
    else:
        tfile.write(f"{used_c_1[i][84]}{used_c_1[i][83]}")
        count += 2
for i in range(13, 85):
    if count == 8:
        tfile.write(f" {used_c_1[i][82]}{used_c_1[i][81]}")
        count = 2
    else:
        tfile.write(f"{used_c_1[i][82]}{used_c_1[i][81]}")
        count += 2
tfile.write("\n")
count = 0
for i in range(84, 12, -1):
    if count == 8:
        if get_mask(84, i) == 0:
            tfile.write(f" {invert(used_c_1[i][84])}")
        else:
            tfile.write(f" {used_c_1[i][84]}")
        if get_mask(83, i) == 0:
            tfile.write(f"{invert(used_c_1[i][83])}")
        else:
            tfile.write(f"{used_c_1[i][83]}")
        count = 2
    else:
        if get_mask(84, i) == 0:
            tfile.write(f"{invert(used_c_1[i][84])}")
        else:
            tfile.write(f"{used_c_1[i][84]}")
        if get_mask(83, i) == 0:
            tfile.write(f"{invert(used_c_1[i][83])}")
        else:
            tfile.write(f"{used_c_1[i][83]}")
        count += 2

for i in range(13, 85):
    if count == 8:
        if get_mask(82, i) == 0:
            tfile.write(f" {invert(used_c_1[i][82])}")
        else:
            tfile.write(f" {used_c_1[i][82]}")
        if get_mask(81, i) == 0:
            tfile.write(f"{invert(used_c_1[i][81])}")
        else:
            tfile.write(f"{used_c_1[i][81]}")
        count = 2
    else:
        if get_mask(82, i) == 0:
            tfile.write(f"{invert(used_c_1[i][82])}")
        else:
            tfile.write(f"{used_c_1[i][82]}")
        if get_mask(81, i) == 0:
            tfile.write(f"{invert(used_c_1[i][81])}")
        else:
            tfile.write(f"{used_c_1[i][81]}")
        count += 2
tfile.close()



# print(used_c_1)
# print(len(used_c_1[0]))
# print(len(used_c_1))

