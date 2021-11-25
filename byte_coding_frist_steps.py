#########################
# SUMMARY
#########################
# Программа для кодирования информации
# и представления ее в виде qr кода.
# Был выбран байтовый способ кодирования, так как в тексте
# будут содержаться спец символы и буквы русского алфавита
#########################
# ЧТО СДЕЛАТЬ:
# русские буквы, нормально кодировал чтобы и декодил
# лого вставка, подгон по размеру холста (чтобы не сильно большой и не сильно маленький)
# сделать проверку почти в самом конце кодирования данных, а не вылезли ли мы за предели максимума для данной версии и не нужно ли нам еще раз все рассчитать?
# как создавать эту идентификационную посл-ть в начале
#########################


# библиотека для рисования
from PIL import Image, ImageDraw, ImageColor, ImageFont


# на входе - байтовое представление строки
# на выходе - бинарное представление (строка)
def binaryEncodingUTF(my_bytes):
    binary_enc = ""
    for byte in my_bytes:
        temp_bin = bin(byte)[2::]  # отсекаем первые два символа беспонтовые эти 0b
        # print(type(temp_bin))
        if len(temp_bin) < 8:
            binary_enc += "0" * (8 - len(temp_bin)) + temp_bin  # добавляем нулей вперед, если длина меньше 8
        else:
            binary_enc += temp_bin
        # binary_enc += " | "
    return binary_enc


# перевод
def binary_encoding_amount_data(num, len_amount_data):
    temp_str = bin(num)[2::]
    if len_amount_data == 8:
        if len(temp_str) < 8:
            return "0" * (8 - len(temp_str)) + temp_str
    elif len_amount_data == 16:
        if len(temp_str) < 16:
            return "0" * (16 - len(temp_str)) + temp_str
    else:
        return "-1"


# маска qr кода
def get_mask(x, y):
    # 0 маска
    return (x + y) % 2
    # 2 маска
    # return x % 3


# 0 меняет на 1, 1 на 0. если не эти числа то -1
def invert(num):
    if num == 0:
        return 1
    elif num == 1:
        return 0
    else:
        return -1


# делит входную строку по байтам (ну на блоки по 8 эл-тов
# если не делится на 8 то в конце обрубок
# return - list
def divide_by_bytes(bin_string):
    count = 0
    t_str = ""
    result = []
    for symb in bin_string:
        if count == 8:
            result.append(t_str)
            t_str = f"{symb}"
            count = 1
        else:
            t_str += f"{symb}"
            count += 1
    result.append(t_str)
    return result


def divide_by_bytes_str(bin_string):
    count = 0
    result = ""
    for symb in bin_string:
        if count == 8:
            result += f" {symb}"
            count = 1
        else:
            result += f"{symb}"
            count += 1
    return result


# кол-во русских букв в строке (на них по 2 байта)
def count_letters_ru(string):
    return len(list(filter(lambda x: ord(x.lower()) in range(1072, 1104), string)))


def get_version(max_d, bit_amount):
    ver = 0
    for i in range(len(max_d)):
        # первое число данных, которое больше чем наши данные - наша версия
        if max_d[i] >= bit_amount:
            ver = i + 1
            break
    return ver


# длина поля "количество данных"
# 8: 1-9 версия, 16: 10-40 версия, -1: что-то другое
def get_length_amount_data_byte_code(ver):
    if version <= 9:
        return 8  # бит
    elif 9 < version <= 40:
        return 16  # бит
    else:
        return -1


# получить массив, кот содержит, сколько байтов данных в каждом блоке данных
def get_blocks(len_b, amount_b, remain_B):
    b = [len_b] * amount_b
    # идем от последнего индекса назад, добавляя в каждый блок по 1 байту
    for i in range(amount_b - 1, amount_b - 1 - remain_B, -1):
        b[i] += 1
    return b


# получить данные разбитые по блокам
def get_data_by_blocks(b, data_bytes):
    # пустой список блоков
    b1 = []
    new_start = 0
    # идем по каждому блоку
    for i in range(len(b)):
        new_end = new_start + b[i]
        temp = []
        # забираем из данных столько байт, сколько надо для текущего блока
        for j in range(new_start, new_end):
            temp.append(data_bytes[j])
            new_start += 1
        b1.append(temp.copy())
    return b1


# все бинарные числа в строках и до 8 бит
def sum_bin_dec_mod_2(bin_1, dec_2):
    # переводим десятич число в двоичн
    bin_2 = bin(dec_2)[2::]
    # print(f"\nBin dec = {bin_2}")
    # дополняем незначащими нулями если нужно
    if len(bin_2) < 8:
        # print(f"len < 8! => add {8 - len(bin_2)} 0")
        bin_2 = "0" * (8 - len(bin_2)) + bin_2
    # print(f"Bin dec = {bin_2}")
    res = ""
    for i in range(0, 8):
        # print(f"bin_1[{i}]={bin_1[i]}; bin_2[{i}]={bin_2[i]};")
        if (bin_1[i] == '0' and bin_2[i] == '0') or (bin_1[i] == '1' and bin_2[i] == '1'):
            res += "0"
        else:
            res += "1"
    return res

# создание байтов коррекции
def get_corr_bytes(blocks_data, amount_corr_bytes, gener_poly):
    # создаем копию полинома для работы
    gener_poly_copy = gener_poly.copy()

    # док-ты для записи логов
    corr_log = open("correction_log.txt", 'w')
    only_arrs = open("only_arrs_log.txt", 'w')

    num_block = 0
    correct_blocks = []
    for block in blocks_data:
        corr_log.write(f"########################\n######### {num_block} БЛОК ##########\n########################\n")
        only_arrs.write(f"########################\n######### {num_block} БЛОК ##########\n########################\n")
        # кол-во байтов в текущем блоке данных
        count_bytes = len(block)
        # вычисляем длину массива байтов коррекции
        length_arr = max(amount_corr_bytes, count_bytes)

        # создаем пустой временный массив. Бинарный и десятичный
        arr = []
        for i in range(length_arr):
            if i < count_bytes:
                arr.append(block[i])  # добавляем байты из блока данных в массив
            else:
                arr.append("0" * 8)  # добавляем нулевые байты если данные кончились

        dec_arr = []
        for num in arr:
            dec_arr.append(int(num, 2))

        # повторяем столько раз, сколько байтов данных в текущем блоке
        for i in range(count_bytes):
            corr_log.write(f"|||||||||||||||||||||||\n|||||||| {i} итерация в блоке||||||\n|||||||||||||||||||||||\n")
            only_arrs.write(f"||||||||||||||||\n||||| {i} итерация ||||||\n||||||||||||||||\n")
            only_arrs.write(f"Генерирующий многочлен (его не трогаем):\n {gener_poly_copy}")
            only_arrs.write(f"\nМассив dec_arr:\n {dec_arr}")
            # берём первый эл-т массива и сохраняем его в переменной А
            dec_A = dec_arr[0]
            bin_A = arr[0]
            corr_log.write(f"Первый эл-т А = {dec_A} = {bin_A}\n")
            # смещаем все эл-ты влево на один. в конец - нолик
            for j in range(len(dec_arr) - 1):
                dec_arr[j] = dec_arr[j + 1]
            dec_arr[len(dec_arr) - 1] = 0
            only_arrs.write(f"\nМассив dec_arr:\n {dec_arr}")
            only_arrs.write(f"\nМассив arr:\n {arr}")
            for j in range(len(arr) - 1):
                arr[j] = arr[j + 1]
            arr[len(arr) - 1] = "00000000"
            only_arrs.write(f"\nМассив arr:\n {arr}\n")

            if dec_A != 0:
                # ищем соответствующее А число в обратном поле Галуа
                dec_B = inverse_galoi_256[dec_A]
                corr_log.write(f"А != 0 => B из обратного поля гауа = {dec_B}\n\n")
                # прибавляем B к каждому числу генерирующего многочлена по модулю 255
                for j in range(len(gener_poly_copy)):
                    t_sum = dec_B + gener_poly_copy[j]
                    corr_log.write(f"Dec_b {dec_B} + gen_poly[{j}] {gener_poly_copy[j]} = {t_sum}\n")
                    # если B > 254 то записываем остаток от деления на 255 (т.е. складываем оп модулю 255)
                    if t_sum > 254:
                        t_sum = t_sum % 255
                        corr_log.write(f"t_sum > 254 => складываем по модулю 255, сумма =  {t_sum}\n")
                    gener_poly_copy[j] = t_sum
                    corr_log.write(f"Итого, gen_poly[{j}] =  {gener_poly_copy[j]}\n")
                corr_log.write(f"\n")
                only_arrs.write(f"\nГенер многочл после прибавления {dec_B} по модулу 255:\n {gener_poly_copy}\n")
                # для каждого полученного эл-та полинома ищем соответствие в поле галуа
                for j in range(len(gener_poly_copy)):
                    corr_log.write(f"Находим соответсвие {gener_poly_copy[j]} в поле Галуа,")
                    # print(f"Gen_poly[{j}] = {generic_poly_copy[j]}")
                    gener_poly_copy[j] = galoi_256[gener_poly_copy[j]]
                    corr_log.write(f"тогда новый эл-т  =  {gener_poly_copy[j]}\n")
                only_arrs.write(f"\nГенер многочл после замены эл-тов из поля Галуа:\n {gener_poly_copy}\n")
                # почленно проводим операцию побитового сложения по модулю два с подготовленным массивом
                corr_log.write(f"\nПобитово складываем массив arr и полученный полином:\n")
                for j in range(len(gener_poly_copy)):
                    corr_log.write(f"arr[{j}] = {arr[j]} + gen_poly[{j}] = {gener_poly_copy[j]} == ")
                    arr[j] = sum_bin_dec_mod_2(arr[j], gener_poly_copy[j])
                    corr_log.write(f"{arr[j]}\n")
                # перезаписываем десятичный массив arr
                corr_log.write(f"\nПерезаписываем десятичный массив arr:")
                for j in range(len(arr)):
                    dec_arr[j] = int(arr[j], 2)
                    corr_log.write(f"\ndec_arr[{j}] = {arr[j]} (2) = {dec_arr[j]} (10)")
                only_arrs.write(f"\nМассив dec_arr после слож по модулю 2 с генер многочл:\n {dec_arr}\n\n\n")
            # возвращаем назад полином тот самый, так как я его менял
            gener_poly_copy = gener_poly.copy()

            corr_log.write(
                f"|||||||||||||||||||||||\n|||||||| КОНЕЦ {i} итерации в блоке||||||\n|||||||||||||||||||||||\n\n\n")

        # for i in range(count_bytes):
        #     gen_poly_copy = gener_poly.copy()
        #     A = arr[i]
        #     # удаляем первый элемент, и двигаем все оставшиеся влево на один
        #     for j in range(count_bytes - 1):
        #         arr[j] = arr[j + 1]
        #     arr[count_bytes - 1] = "0" * 8
        #     if int(A, 2) != 0:
        #         B = inverse_galoi_256[int(A, 2)]  # здесь А из строки приводится к иинтегер
        #         for j in range(len(gen_poly_copy)):
        #             temp = gen_poly_copy[j]
        #             tempsum = gen_poly_copy[j] + B
        #             gen_poly_copy[j] = (B + gen_poly_copy[j]) % 255
        #             # находим соотв-вие из галуа 256
        #             gen_poly_copy[j] = galoi_256[gen_poly_copy[j]]
        #             # побитовое сложение по модулю два с arr данных
        #             # сперва переведем в двоичный вид нормальный
        #             gen_poly_copy[j] = bin(gen_poly_copy[j])
        #             gen_poly_copy[j] = gen_poly_copy[j][2::]  # отрезали начало беспонтовое
        #             if len(gen_poly_copy[j]) < 8:
        #                 gen_poly_copy[j] = "0" * (8 - len(gen_poly_copy[j])) + gen_poly_copy[j]
        #             for k in range(len(arr[j])):
        #                 if (arr[j][k] == '0' and gen_poly_copy[j][k] == '0') or (
        #                         arr[j][k] == '1' and gen_poly_copy[j][k] == '1'):
        #                     arr[j] = arr[j][:k:] + '0' + arr[j][k + 1::]  # разрезали строку, вставили символ
        #                 else:
        #                     arr[j] = arr[j][:k:] + '1' + arr[j][k + 1::]
        correct_blocks.append(arr.copy())
        corr_log.write(f"########################\n######### КОНЕЦ {num_block} БЛОКА ##########\n########################\n")
        only_arrs.write(f"########################\n######### КОНЕЦ {num_block} БЛОКА ##########\n########################\n")
        num_block += 1

    corr_log.close()
    only_arrs.close()
    return correct_blocks


# объединение системной инфы, данных, коррекционных байтов
#НУЖНО НЕ ПРОСТО ПОДРЯД ДОБАВЛЯТЬ, А ЕЩЕ И ПЕРЕМЕШИВАТЬ, КАК В СТАТЬЕ!!!
def combine_sys_data_corr_bytes(data, corr_data):
    # ПРОСТО ВТУПУЮ СПЕРВА БАЙТЫ ДАННЫХ ВСЕ, ПОТОМ БАЙТЫ КОРРЕКЦИИ
    # flow = []
    # # добавляем системное начало (тип кодирования + кол-во данных)
    # # добавляем байты данных
    # for d in data:
    #     for byte in d:
    #         flow.append(byte)
    # # добавляем коррекционные байты
    # for c in corr_data:
    #     for byte in c:
    #         flow.append(byte)
    # return flow
    ready_d_flow = []
    # сначала добавим данные
    num_B = 0  # номер текущего записываемого байта
    is_empty_d = False
    while not is_empty_d:
        is_empty_d = True
        for i in range(0, len(data)):
            if num_B <= len(data[i]) - 1:  # если еще есть в блоке данные с таким номером
                ready_d_flow.append(data[i][num_B])
                # print(f"add blocks[{i}][{num_byte}]...")
                is_empty_d = False
        num_B += 1
    # теперь добавляем байты коррекции
    count_corr = len(corr_data[0])  # кол-во байтов коррекции в каждом блоке, оно одинаковое
    for i in range(0, count_corr):
        for j in range(0, len(corr_data)):
            # print(f"add correction blocks[{j}][{i}]...")  # коррекционные тоже верно добавлены
            ready_d_flow.append(corr_data[j][i])
    return ready_d_flow


# объединение байтов потока в один поток бит-
def combine_flow_bit(flow_bytes):
    flow = ""
    for byte in flow_bytes:
        flow += byte
    return flow


# кодовые слова-заполнители - 11101100 и 00010001 (поочередно)
def fill_data(data_str, c_bytes_ver):
    l_data_str = len(data_str)
    # если длина не делится на 8, то дополняем нулями в конец, чтобы делилась
    if l_data_str % 8 != 0:
        data_str += '0' * (len(data_str) % 8)
    t_count_bytes = len(data_str) / 8   # сколько байт у нас щас есть?
    fl = t_count_bytes < c_bytes_ver    # флаг проверки, меньше ли у нас байтов, чем нужно для версии
    fill_code_word = "11101100"
    while fl:
        if fill_code_word == "11101100":
            data_str += "11101100"
            fill_code_word = "00010001"
            t_count_bytes = len(data_str) / 8  # сколько байт у нас щас есть?
            fl = t_count_bytes < c_bytes_ver
        else:
            data_str += "00010001"
            fill_code_word = "11101100"
            t_count_bytes = len(data_str) / 8  # сколько байт у нас щас есть?
            fl = t_count_bytes < c_bytes_ver
    return data_str


# Строка данных для кодирования (пример, общий вид)
# encoding_string = "s15Njg81Ldj64LvzkH8A|\"01.11.2021 21:29:25\"|\"36/1\"|1|\"Компьютерные сети\"|\"Приходько Татьяна Александровна\""
# encoding_string = "I love you, Dashen'ka! <3"
#encoding_string = "s15Njg81Ldj64LvzkH8A|\"01.11.2021 21:29:25\"|\"36/1\"|1|\"Computer net\"|\"Prihod'ko Tatyana Alexandrovna\""
encoding_string = "I <3 Department of Information Tecnology (KIT's)"

##############################
# побайтовое кодирование
##############################
# получаем байтовое представление UTF-8
bytes_encoded = encoding_string.encode(encoding='ascii', errors='replace')

# получаем бинарное представление UTF-8
binary_encoded = binaryEncodingUTF(bytes_encoded)

# выводим все полученные данные чтобы поглядеть на правильность
print(f"Исходная строка: \"{encoding_string}\"")
print(f"Длина исходной строки: {len(encoding_string)}")
print(f"Кол-во русских букв: {count_letters_ru(encoding_string)}")
print(f"\nBytes encoded string (utf_8): {bytes_encoded}")
print(f"Bytes list [0:2]: {list(bytes_encoded[0:2])}")
# for i in bytes_encoded:
#     print(bin(i))
# out = open('out.txt', 'w')
# out.write(str(bytes_encoded))
# out.close()
print(f"\nСтрока в бинарной кодировке: {binary_encoded}")

# количество данных в битах
bit_amount_data = len(binary_encoded)

print(f"Длина строки в бинарной кодировке (кол-во бит данных): {bit_amount_data}")

# количество данных в байтах
byte_amount_data = int(len(binary_encoded) / 8)   # В байтах количество данных закодированных

print(f"Количество байт в бинарной кодировке: {byte_amount_data}")

# пусть будем делать код, который всегда имеет уровень коррекции ошибок H - высокий
# тогда создадим массив максимального кол-ва битов данных в коде для каждой версии
# номера версий: 1, 2, 3, 4, ...
# ВООБЩЕ -16 НАДО НАВЕРНОЕ СДЕЛАТЬ, Т.К. БАЙТОВОЕ КОДИРОВАНИЕ У НАС ИДЕТ
max_data_amount_h_corr = [72 - 16, 128 - 16, 208 - 16, 288 - 16, 368 - 16, 480 - 16, 528 - 16, 688 - 16, 800 - 16, 976 - 16,
                          1120 - 16, 1264 - 16, 1440 - 16, 1576 - 16, 1784 - 16, 2024 - 16, 2264 - 16, 2504 - 16, 2728 - 16, 3080 - 16,
                          3248 - 16, 3536 - 16, 3712 - 16,  4112 - 16, 4304 - 16, 4768 - 16, 5024 - 16, 5288 - 16, 5608 - 16, 5960 - 16,
                          6344 - 16, 6760 - 16, 7208 - 16, 7688 - 16, 7888 - 16, 8432 - 16, 8768 - 16, 9136 - 16, 9776 - 16, 10208 - 16]


# определяем, какая версия нам нужна с уровнем коррекции H
version = get_version(max_data_amount_h_corr, bit_amount_data)   # сюда запишем номер версии, которая нам нужна
print(f"\nВерсия кода для ваших данных ({bit_amount_data} bit): {version}")

# максимальное кол-во байтов данных для версии
max_count_bytes_for_ver = (max_data_amount_h_corr[version - 1] + 16) / 8

# Уровыень коррекции, Метод кодирования (байтовый)
correction_level = 'H'
encoding_method = "0100"

# длина количества поля данных в битах (!!!для побайтового кодирования!!!)
length_amount_data_field = get_length_amount_data_byte_code(version)
print(f"Длина поля для количества данных: {length_amount_data_field}")

# Кол-во байтов данных в двоичном представлении (два первых символа отсекли)
binary_byte_amount_data = binary_encoding_amount_data(byte_amount_data, length_amount_data_field)
print(f"Двоичное представление кол-ва байт данных ({byte_amount_data}): {binary_byte_amount_data} (str)")

# Далее нужно объединить служебную информацию, добавить ее в начало данных
# затем добавить нулей в конце, чтобы поток можно было разбить на байты (по 8 бит)
# и затем, если нужно, добавить незначащих байтов в конец, до максимального кол-ва данных кода
# кодовые слова-заполнители - 11101100 и 00010001 (поочередно)
temp_data_flow = encoding_method + binary_byte_amount_data + binary_encoded
print(f"\nМетод, кол-во данных, и сами данные (длина-{len(temp_data_flow)}): {temp_data_flow}\n")

# заполняем нашу строку битами нулевыми и байтами
temp_data_flow = fill_data(temp_data_flow, max_count_bytes_for_ver)
print(f"\nМетод, кол-во данных, и сами данные (длина-{len(temp_data_flow)}): {temp_data_flow}\n")

# количество данных в байтах
byte_amount_data = int(len(temp_data_flow) / 8)   # В байтах количество данных закодированных

# байтовое представление данных (список)
binary_encoded_bytes = divide_by_bytes(temp_data_flow)
# байтовое представление данных (строка)
binary_encoded_bytes_str = divide_by_bytes_str(temp_data_flow)

print(f"Вид двоичного представления по байтам в строке (count={len(binary_encoded_bytes_str)}): {binary_encoded_bytes_str}")
print(f"Вид двоичного представления по байтам в списке (count={len(binary_encoded_bytes)}): {binary_encoded_bytes}")

# кол-во блоков, на которые нужно поделить данные (для уровня коррекции H и версий 1, 2, 3, ...)
blocks_amount_corr_h = [1, 1, 2, 4, 4, 4, 5, 6, 8, 8,
                        11, 11, 16, 16, 18, 16, 19, 21, 25, 25,
                        25, 34, 30, 32, 35, 37, 40, 42, 45, 48,
                        51, 54, 57, 60, 63, 66, 70, 74, 77, 81]

# кол-во блоков для нашего случая:
amount_blocks = blocks_amount_corr_h[version - 1]

# сколько байт инфы в каждом блоке:
amount_data_in_block = int(byte_amount_data / amount_blocks)

# сколько байт осталось?
amount_data_in_block_remains = byte_amount_data % amount_blocks

print(f"\nНужно {amount_blocks} блоков данных. В каждом блоке по {amount_data_in_block} байтов. Остаток: {amount_data_in_block_remains}")

# создаем массив блоков информации (сколько байт данных в каждом блоке)
blocks = get_blocks(amount_data_in_block, amount_blocks, amount_data_in_block_remains)
print(f"Блоки данных (байты): {blocks}")

################
# ЗАПОЛНЕНИЕ ЭТИХ БЛОКОВ ДАННЫХ
################

# данные, разбитые по блокам (байты)
data_block_divided = get_data_by_blocks(blocks, binary_encoded_bytes)
print("Сами эти блоки, заполненные данными:")
for bl in data_block_divided:
    print(f"(len = {len(bl)}): {bl}")

print(f"Блоки, заполненные данными: {combine_flow_bit(data_block_divided[0])}")

################
# БАЙТЫ КОРРЕКЦИИ
################
# кол-во байтов коррекции на один блок данных (для уровня коррекции H и версий 1, 2, 3, ...)
corr_bytes_by_block_h = [17, 28, 22, 16, 22, 28, 26, 26, 24, 28,
                         24, 28, 22, 24, 24, 30, 28, 28, 26, 28,
                         30, 24, 30, 30, 30, 30, 30, 30, 30, 30,
                         30, 30, 30, 30, 30, 30, 30, 30, 30, 30]

# кол-во байтов коррекции для нашего случая:
amount_corr_bytes_by_block = corr_bytes_by_block_h[version - 1]
print(f"\nКол-во байтов коррекции на 1 блок данных: {amount_corr_bytes_by_block}")

# !!!!!! КАК ПРОВЕРИТЬ??? !!!!!!
# генерирующие многочлены. Ключ - кол-во байтов коррекции, знач - коэффициенты полинома
generic_polys = {7: [87, 229, 146, 149, 238, 102, 21],
                 10: [251, 67, 46, 61, 118, 70, 64, 94, 32, 45],
                 13: [74, 152, 176, 100, 86, 100, 106, 104, 130, 218, 206, 140, 78],
                 15: [8, 183, 61, 91, 202, 37, 51, 58, 58, 237, 140, 124, 5, 99, 105],
                 16: [120, 104, 107, 109, 102, 161, 76, 3, 91, 191, 147, 169, 182, 194, 225, 120],
                 17: [43, 139, 206, 78, 43, 239, 123, 206, 214, 147, 24, 99, 150, 39, 243, 163, 136],
                 18: [215, 234, 158, 94, 184, 97, 118, 170, 79, 187, 152, 148, 252, 179, 5, 98, 96, 153],
                 20: [17, 60, 79, 50, 61, 163, 26, 187, 202, 180, 221, 225, 83, 239, 156, 164, 212, 212, 188, 190],
                 22: [210, 171, 247, 242, 93, 230, 14, 109, 221, 53, 200, 74, 8, 172, 98, 80, 219, 134, 160, 105, 165,
                      231],
                 24: [229, 121, 135, 48, 211, 117, 251, 126, 159, 180, 169, 152, 192, 226, 228, 218, 111, 0, 117, 232,
                      87, 96, 227, 21],
                 26: [173, 125, 158, 2, 103, 182, 118, 17, 145, 201, 111, 28, 165, 53, 161, 21, 245, 142, 13, 102, 48,
                      227, 153, 145, 218, 70],
                 28: [168, 223, 200, 104, 224, 234, 108, 180, 110, 190, 195, 147, 205, 27, 232, 201, 21, 43, 245, 87,
                      42, 195, 212, 119, 242, 37, 9, 123],
                 30: [41, 173, 145, 152, 216, 31, 179, 182, 50, 48, 110, 86, 239, 96, 222, 125, 42, 173, 226, 193, 224,
                      130, 156, 37, 251, 216, 238, 40, 192, 180]}

# поля Галуа (пока из статьи на хабре
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

# полином для нашего случая:
gen_poly = generic_polys[amount_corr_bytes_by_block]
print(f"Генерирующий многочлен ({amount_corr_bytes_by_block}): {gen_poly}")

# считаем корректирующие байты
correction_bytes = get_corr_bytes(data_block_divided, amount_corr_bytes_by_block, gen_poly)
# выводим те самые корректирующие байты по блокам
print(f"\nБайты коррекции:")
for b in correction_bytes:
    print(f"Corr bytes (len = {len(b)}): {b}")
print()
###########################
# Объединение блоков:
###########################
data_flow_bytes = combine_sys_data_corr_bytes(data_block_divided, correction_bytes)
print(f"Поток данных (по байтам. системные, данные, коррекция. len = {len(data_flow_bytes)}): {data_flow_bytes}")

data_flow_bit = combine_flow_bit(data_flow_bytes)
print(f"Поток данных в битах: {divide_by_bytes(data_flow_bit)}")

# вывод байтов коррекции по блокам и данных по блокам
print(f"\n\nCORR:\n{correction_bytes}\nDATA:\n{data_block_divided}")


# поток данных из кода Hello, world!  (с сайта)
# метод кодир-я и сколько данных, строка данных, дальше похоже байты коррекции или еще что-то
#data_flow_bit = "01000000111001001000011001010110110001101100011011110010110000100000011101110110111101110010011011000110010000100001001000000000011111000000001100100011010110000001001000000101000111101011100001111100110101101010011101100100000001000101010111000010101111110100111101101011100010011100101011011000100000011010101001100000001001100110111001000100011110010000000"
#print(f"теперь читаемый код:\nПоток данных в битах: {divide_by_bytes(data_flow_bit)}")
# этот поток данных нормально расшифровался, то есть рисуется нормально
# то есть проблема в байтах коррекции
# мой новый пределанный код для байтов коррекции сделал это:
# НЕ ЧИТАЕТСЯ(((
# data_flow_bit = "0100000011100100100001100101011011000110110001101111001011000010000001110111011011110111001001101100011001000010000100100000000011101000111010100110010110101011110110101001111110011001001001101011011001001001010001001110001111110111010010100100001111011011101011010101101001000101101000010010110110110011101001011110001000101011100001110010110010000110"


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


def draw_qr(matrix, c_modules):
    im_wid_heig = c_modules * 10
    module = im_wid_heig / c_modules  # pixels - ширина длина блока модуля
    image = Image.new("RGB", (im_wid_heig, im_wid_heig))
    draw = ImageDraw.Draw(image)
    # заливаем белый фон
    draw.rectangle((0, 0, im_wid_heig, im_wid_heig), fill=ImageColor.getrgb("white"))
    # рисуем блоки
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i][j] == 1:
                draw.rectangle((j * module, i * module, j * module + module, i * module + module),
                               fill=ImageColor.getrgb("black"))
    image.save("my_qr.png", "PNG")


def add_up(c_x, c_y, matr, data_f, log_file, is_end_f):
    print(f"x,y: {c_x}, {c_y}")
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


def add_down(c_x, c_y, matr, data_f, log_file, is_end_f, c_modules):
    print(f"x,y: {c_x}, {c_y}")
    while c_y != c_modules - 4:
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


def draw_left_up_search(matrix, bl=1, wh=0, not_u=2):
    # внеш черн
    color_empty_rect_matr(matrix, bl, [4, 4, 10, 10])
    # средн бел
    color_empty_rect_matr(matrix, wh, [5, 5, 9, 9])
    # внутр черн
    color_rect_matr(matrix, bl, [6, 6, 8, 8])
    # внешн бел, две стороны
    color_vert_line_matr(matrix, wh, [11, 4, 11, 11])
    color_horiz_line_matr(matrix, wh, [4, 11, 11, 11])


def draw_right_up_searh(matrix, c_modules, ind=4, bl=1, wh=0, not_u=2):
    # внешн бел, две стороны
    t_x = c_modules - 1 - ind - 7
    color_vert_line_matr(matrix, wh, [t_x, 4, t_x, 11])
    color_horiz_line_matr(matrix, wh, [t_x, 11, t_x + 7, 11])
    # внеш черн
    t_x += 1
    color_empty_rect_matr(matrix, bl, [t_x, 4, t_x + 6, 10])
    # средн бел
    t_x += 1
    color_empty_rect_matr(matrix, wh, [t_x, 5, t_x + 4, 9])
    # внутр черн
    t_x += 1
    color_rect_matr(matrix, bl, [t_x, 6, t_x + 2, 8])


def draw_left_down_searh(matrix, c_modules, ind=4, bl=1, wh=0, not_u=2):
    # внешн бел, две стороны
    t_y = c_modules - 1 - ind - 7
    color_horiz_line_matr(matrix, wh, [4, t_y, 11, t_y])
    color_vert_line_matr(matrix, wh, [11, t_y, 11, t_y + 7])
    # внеш черн
    t_y += 1
    color_empty_rect_matr(matrix, bl, [4, t_y, 10, t_y + 6])
    # средн бел
    t_y += 1
    color_empty_rect_matr(matrix, wh, [5, t_y, 9, t_y + 4])
    # внутр черн
    t_y += 1
    color_rect_matr(matrix, bl, [6, t_y, 8, t_y + 2])


def draw_vert_sync(matrix, bl=1, wh=0, not_u=2):
    c_x = 10
    c_y = 12
    is_wh = False
    while matrix[c_y][c_x] == 2:
        if is_wh:
            matrix[c_y][c_x] = wh
            is_wh = False
        else:
            matrix[c_y][c_x] = bl
            is_wh = True
        c_y += 1
    # print(f"cur_x: {cur_x}, cur_y: {cur_y}")


def draw_horiz_sync(matrix, bl=1, wh=0, not_u=2):
    c_x = 12
    c_y = 10
    is_wh = False
    while matrix[c_y][c_x] == 2:
        if is_wh:
            matrix[c_y][c_x] = wh
            is_wh = False
        else:
            matrix[c_y][c_x] = bl
            is_wh = True
        c_x += 1
    # print(f"cur_x: {cur_x}, cur_y: {cur_y}")


def draw_flat_signs(matrix, flat, ver, ind, bl=1, wh=0, not_u=2):
    # если версия больше 6, то
    # чтобы не было наслоения на поисковые, не рисуем точки
    # , (первая, последняя) и (последняя, первая)

    # 16 версия => 6, 26, 50, 74 - места расположения выравнивающих узоров
    # т.е. (6, 6) (6, 26) (6, 50) (6, 74) - центры выравнивающих узоров первых
    # т.е. (26, 6) (26, 26) (26, 50) (26, 74) - центры выравнивающих узоров вторых и тд...
    # чтобы не было наслоения на поисковые, не рисуем точки (6,6) (6,74) и (74,6)
    # составляем координаты выравнивающих узоров (центров их)
    flat_c = []
    for i in range(len(flat)):
        for j in range(len(flat)):
            flat_c.append((flat[i], flat[j]))
    print(f"\nКоординаты выравнив узоров: {flat_c}")
    # удаляем ненужные координаты (если версия > 6)
    if ver > 6:
        # (последняя, первая) - из последнего перебора, первая пара
        del flat_c[len(flat_c) - len(flat)]
        # (первая, последняя) - из первого перебора, последняя пара
        del flat_c[len(flat) - 1]
        # (первая, первая) - вообще самая первая пара
        del flat_c[0]
        # print(f"\nКоординаты выравнив узоров после удаления: {flat_c})
    # рисуем узорчики
    for center in flat_c:
        #print(f"center: {center}")
        # внутр точка
        # не забываем про отступ от начала!!!
        t_x = ind + center[0]
        t_y = ind + center[1]
        matrix[t_y][t_x] = bl
        # бел квадр
        color_empty_rect_matr(used_c_1, wh, [t_x - 1, t_y - 1, t_x + 1, t_y + 1])
        # чер внеш квадр
        color_empty_rect_matr(used_c_1, bl, [t_x - 2, t_y - 2, t_x + 2, t_y + 2])


def draw_ver_code(matrix, ver_c, c_modules, bl=1, wh=0, not_u=2):
    index = 0
    #########
    # Вертикальный:
    for i in range(c_modules - 15, c_modules - 12):
        for j in range(4, 10):
            matrix[j][i] = ver_c[index]
            index += 1
    # Горизонтальный:
    index = 0
    for i in range(c_modules - 15, c_modules - 12):
        for j in range(4, 10):
            matrix[i][j] = ver_c[index]
            index += 1


def draw_masc_cor_code(matrix, masc_c_c, c_modules, bl=1, wh=0, not_u=2):
    index = 0
    # верхн левый (всегда по таким координатам
    for i in range(4, 13):
        if matrix[12][i] == 2:
            matrix[12][i] = masc_c_c[index]
            index += 1
    for i in range(11, 3, -1):
        if matrix[i][12] == 2:
            matrix[i][12] = masc_c_c[index]
            index += 1
    # нижн левый
    index = 0
    for i in range(c_modules - 5, c_modules - 12, -1):
        matrix[i][12] = masc_c_c[index]
        index += 1
    # этот бит всегда черный
    matrix[c_modules - 12][12] = black
    # верхн правый
    for i in range(c_modules - 12, c_modules - 4):
        matrix[12][i] = masc_c_c[index]
        index += 1


def draw_data(matrix, bin_data_f, c_modules):
    # Ура. заполням данные!!!
    # начинаем с нижнего правого пустого угла
    # координаты полосы синхронизации вертикальной, кот пропускаем: cur_x = 10, cur_y = 12
    # маска 0 - (X+Y) % 2
    # считаем маску для каждого модуля (Х - столбец, Y - строка, % — остаток от деления, / — целочисленное деление)
    # если значение = 0, то инвертируем цвет. если = 1 то оставляем как есть
    log_file = open("log.txt", 'w')
    c_x = c_modules - 5
    c_y = c_modules - 5
    # заполняем первые (74) блоки, до полосы синхронизации. т.е. (37) полос по два блока
    # 4 + 4 модуля по бокам, плюс 7 (полоса синхр + 6 после нее) итого 15 модулей не заполняем
    is_end_flow = False
    is_go_up = True
    for i in range(int((c_modules - 15) / 2)):
        if is_go_up:
            bin_data_f, is_end_flow = add_up(c_x, c_y, matrix, bin_data_f, log_file, is_end_flow)
            c_x -= 2
            c_y = 4
            is_go_up = False
        else:
            bin_data_f, is_end_flow = add_down(c_x, c_y, matrix, bin_data_f, log_file, is_end_flow, count_modules)
            c_x -= 2
            c_y = c_modules - 5
            is_go_up = True
        # print(f"cur_x - {cur_x}; cur_y - {cur_y}")
        # print(len(data_flow))

    # после вертикальной полосы синхронизации:
    c_x = 9
    #c_y = c_modules - 5
    for i in range(0, 3):
        if is_go_up:
            bin_data_f, is_end_flow = add_up(c_x, c_y, matrix, bin_data_f, log_file, is_end_flow)
            c_x -= 2
            c_y = 4
            is_go_up = False
        else:
            bin_data_f, is_end_flow = add_down(c_x, c_y, matrix, bin_data_f, log_file, is_end_flow, count_modules)
            c_x -= 2
            c_y = c_modules - 5
            is_go_up = True
        # print(f"cur_x - {cur_x}; cur_y - {cur_y}")
        # print(len(data_flow))
    log_file.close()


# массив, в котором хранятся списки координат выравнивающих узоров (для версий 1, 2, 3, ...)
flat_signs_coords = [None, [18], [22], [26], [30], [34], [6, 22, 38], [6, 24, 42],
                     [6, 26, 46], [6, 28, 50], [6, 30, 54], [6, 32, 58], [6, 34, 62],
                     [6, 26, 46, 66], [6, 26, 48, 70], [6, 26, 50, 74], [6, 30, 54, 78], [6, 30, 56, 82],
                     [6, 30, 58, 86], [6, 34, 62, 90], [6, 28, 50, 72, 94], [6, 26, 50, 74, 98], [6, 30, 54, 78, 102],
                     [6, 28, 54, 80, 106], [6, 32, 58, 84, 110], [6, 30, 58, 86, 114], [6, 34, 62, 90, 118], [6, 26, 50, 74, 98, 122],
                     [6, 30, 54, 78, 102, 126], [6, 26, 52, 78, 104, 130], [6, 30, 56, 82, 108, 134], [6, 34, 60, 86, 112, 138],
                     [6, 30, 58, 86, 114, 142], [6, 34, 62, 90, 118, 146], [6, 30, 54, 78, 102, 126, 150], [6, 24, 50, 76, 102, 128, 154],
                     [6, 28, 54, 80, 106, 132, 158], [6, 32, 58, 84, 110, 136, 162], [6, 26, 54, 82, 110, 138, 166], [6, 30, 58, 86, 114, 142, 170]]
# наши координаты выравнивающих узоров:
flat_coords = flat_signs_coords[version - 1]
print(f"\nКоординаты выравнивающих узоров: {flat_coords}")


# количество модулей всего холста:
# пустые полосы по краям: 4 + 4
# сам холст для рисования: последнее число из массива выравнивающих узоров + 7
count_modules = 8 + 7 + flat_coords[len(flat_coords) - 1]
print(f"Кол-во модулей всего холста: {count_modules}; кол-во без границ: {count_modules - 8}")


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
indents = [0, 1, 2, 3, count_modules - 4, count_modules - 3, count_modules - 2, count_modules - 1]
indent = 4
# верхний и нижний
color_str_matr(used_c_1, white, indents)
# левый и правый
color_col_matr(used_c_1, white, indents)
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# Верхний левый поисковый узор:
#########
draw_left_up_search(used_c_1)
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# Верхний правый поисковый узор:
#########
draw_right_up_searh(used_c_1, count_modules)
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# Нижний левый поисковый узор:
#########
draw_left_down_searh(used_c_1, count_modules)
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# Вертикальная полоса синхронизации:
#########
draw_vert_sync(used_c_1)
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# Горизонтальная полоса синхронизации:
#########
draw_horiz_sync(used_c_1)
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# Выравнивающие узоры:
#########
draw_flat_signs(used_c_1, flat_coords, version, indent)
#########

# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# дальше рисуем код версии
# 16 - 011100 010001 011100
#########
# список со всеми кодами версий (начиниая с 7 версии)
version_codes = [[0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0],
                 [0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0],
                 [1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                 [1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0],
                 [0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0],
                 [1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0],
                 [1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0],
                 [0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0],
                 [0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0],
                 [1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0],
                 [1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0],
                 [0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0],
                 [1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0],
                 [1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0],
                 [0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0],
                 [0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0],
                 [1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0],
                 [1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0],
                 [0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                 [0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0],
                 [1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0],
                 [1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                 [0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0],
                 [1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1],
                 [0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1],
                 [0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
                 [1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1],
                 [1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                 [0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1],
                 [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1],
                 [1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1],
                 [1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1]]
version_code = []
if version > 6:
    version_code = version_codes[version - 7]
    draw_ver_code(used_c_1, version_code, count_modules)
#########


#####################################################
# в генераторах
# 001101 100100 011010 - 12 версия
# код маски и уровня коррекции: 00111001 1100111 - H 2
# МАСКА ДЛЯ СИСТ ИНФОРМАЦИИ ЭТОЙ, ЧТОБЫ xor СДЕЛАТЬ:
# 10101 000 0010010
#####################################################
# ТУТ ВСЕ ХОРОШО ЗАПОЛНЯЕТ
# код маски и уровня коррекции (0 и H пока что)
# на сайте чтения кодов - 10 000 должно быть начало для H 0 (где 0 - (x + y)%2)
# т.е если брать такую маску с сайта генерации кодов, то это будет: 10000001 1001110
# mask_cor_code = [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0]
# H	0	00 101 10 10001001 - ЭТА ПРАВИЛЬНАЯ МАСКА ДЛЯ H 0
mask_cor_code = [0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1]
# H 2   00 111 001 1100111
# mask_cor_code = [0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1]
#########
draw_masc_cor_code(used_c_1, mask_cor_code, count_modules)
#########

# записываем данные в qr код
draw_data(used_c_1, data_flow_bit, count_modules)

# записываем файл + рисуем в картинку
print_matr_file(used_c_1)
draw_qr(used_c_1, count_modules)


#
# # ТЕСТЫ:
# ###########
# # color_empty_rect_matr(used_c_1, 1, [11, 11, 16, 13])
# # color_rect_matr(used_c_1, 1, [11, 11, 16, 13])
# ###########
#

#
#
# ####################
# # ПЕЧАТЬ ПЕРВЫХ ДВУХ СТОЛБЦОВ (по 2 блока) в файл
# ####################
# from_matr = ""
# count = 0
# tfile = open("from_matr.txt", 'w')
# for i in range(84, 12, -1):
#     if count == 8:
#         tfile.write(f" {used_c_1[i][84]}{used_c_1[i][83]}")
#         count = 2
#     else:
#         tfile.write(f"{used_c_1[i][84]}{used_c_1[i][83]}")
#         count += 2
# for i in range(13, 85):
#     if count == 8:
#         tfile.write(f" {used_c_1[i][82]}{used_c_1[i][81]}")
#         count = 2
#     else:
#         tfile.write(f"{used_c_1[i][82]}{used_c_1[i][81]}")
#         count += 2
# tfile.write("\n")
# count = 0
# for i in range(84, 12, -1):
#     if count == 8:
#         if get_mask(84, i) == 0:
#             tfile.write(f" {invert(used_c_1[i][84])}")
#         else:
#             tfile.write(f" {used_c_1[i][84]}")
#         if get_mask(83, i) == 0:
#             tfile.write(f"{invert(used_c_1[i][83])}")
#         else:
#             tfile.write(f"{used_c_1[i][83]}")
#         count = 2
#     else:
#         if get_mask(84, i) == 0:
#             tfile.write(f"{invert(used_c_1[i][84])}")
#         else:
#             tfile.write(f"{used_c_1[i][84]}")
#         if get_mask(83, i) == 0:
#             tfile.write(f"{invert(used_c_1[i][83])}")
#         else:
#             tfile.write(f"{used_c_1[i][83]}")
#         count += 2
#
# for i in range(13, 85):
#     if count == 8:
#         if get_mask(82, i) == 0:
#             tfile.write(f" {invert(used_c_1[i][82])}")
#         else:
#             tfile.write(f" {used_c_1[i][82]}")
#         if get_mask(81, i) == 0:
#             tfile.write(f"{invert(used_c_1[i][81])}")
#         else:
#             tfile.write(f"{used_c_1[i][81]}")
#         count = 2
#     else:
#         if get_mask(82, i) == 0:
#             tfile.write(f"{invert(used_c_1[i][82])}")
#         else:
#             tfile.write(f"{used_c_1[i][82]}")
#         if get_mask(81, i) == 0:
#             tfile.write(f"{invert(used_c_1[i][81])}")
#         else:
#             tfile.write(f"{used_c_1[i][81]}")
#         count += 2
# tfile.close()


# print(used_c_1)
# print(len(used_c_1[0]))
# print(len(used_c_1))
