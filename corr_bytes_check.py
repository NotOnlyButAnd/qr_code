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


def divide_by_bytes(d_string):
    my_list = []
    while d_string != "":
        t_byte = d_string[:8:]
        # print(f"t_byte {t_byte}")
        my_list.append(t_byte)
        d_string = d_string[8::]
        # print(f"d_string {d_string}\n")
    return my_list


#def get_bin_from_dec(num):


my_string = "Hello, world! "

# получаем байтовое представление UTF-8
bytes_encoded = my_string.encode(encoding='ascii', errors='replace')

# получаем бинарное представление UTF-8
binary_encoded = binaryEncodingUTF(bytes_encoded)

print(f"Двоично раскодированная строка (дина - {len(binary_encoded)}б = {len(binary_encoded)/8}Б):{binary_encoded}")

binary_encoded = "010000001110" + binary_encoded + "0000"   # частный случай
print(f"Двоично раскодированная строка (дина - {len(binary_encoded)}б = {len(binary_encoded)/8}Б):{binary_encoded}")

binary_bytes = divide_by_bytes(binary_encoded)
print(f"По байтам разбитое (count={len(binary_bytes)}): {binary_bytes}")

# 28 байт коррекции нужно для этого кода. один блок будет, вот этот
generic_poly = [168, 223, 200, 104, 224, 234, 108, 180, 110, 190, 195, 147, 205, 27, 232, 201, 21, 43, 245, 87, 42, 195,
                212, 119, 242, 37, 9, 123]
generic_poly_copy = generic_poly.copy()

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

# максимум из кол-ва блоков коррекции и кол-ва байтов в текщем блоке
# max(28, 16) = 28
arr = [0] * 28
print(arr)

# заполняем масив данными, если закончились, то в конце нули
for i in range(len(arr)):
    if i < len(binary_bytes):
        arr[i] = binary_bytes[i]
    else:
        arr[i] = "0" * 8

print(f"До начала создания {len(arr)} - {arr}")

dec_arr = []

for num in arr:
    dec_arr.append(int(num, 2))

# в десятичной форме - верно
print(f"До начала создания (dec) {len(dec_arr)} - {dec_arr}")

# такое повторяем для каждого блока данных. одинаковое число байтов коррекции
# этот цикл повторяется столько раз, сколько байтов данных находится в данном блоке
count_bytes_in_block = len(binary_bytes)

corr_log = open("correction_log.txt", 'w')

for i in range(count_bytes_in_block):
    corr_log.write(f"|||||||||||||||||||||||\n|||||||| {i} итерация в блоке||||||\n|||||||||||||||||||||||\n")
    # берём первый эл-т массива и сохраняем его в переменной А
    dec_A = dec_arr[0]
    bin_A = arr[0]
    corr_log.write(f"Первый эл-т А = {dec_A} = {bin_A}\n")
    if dec_A != 0:
        # ищем соответствующее А число в обратном поле Галуа
        dec_B = inverse_galoi_256[dec_A]
        corr_log.write(f"А != 0 => B из обратного поля гауа = {dec_B}\n\n")
        # прибавляем B к каждому числу генерирующего многочлена по модулю 255
        for j in range(len(generic_poly_copy)):
            t_sum = dec_B + generic_poly_copy[j]
            corr_log.write(f"Dec_b {dec_B} + gen_poly[{j}] {generic_poly_copy[j]} = {t_sum}\n")
            # если B > 254 то записываем остаток от деления на 255 (т.е. складываем оп модулю 255)
            if dec_B > 254:
                t_sum = t_sum % 255
                corr_log.write(f"B > 254 => складываем по модулю 255, сумма =  {t_sum}\n")
            generic_poly_copy[j] = t_sum
            corr_log.write(f"Итого, gen_poly[{j}] =  {generic_poly_copy[j]}\n")
        corr_log.write(f"\n")
        # для каждого полученного эл-та полинома ищем соответствие в поле галуа
        for j in range(len(generic_poly_copy)):
            corr_log.write(f"Находим соответсвие {generic_poly_copy[j]} в поле Галуа,")
            generic_poly_copy[j] = galoi_256[generic_poly_copy[j]]
            corr_log.write(f"тогда новый эл-т  =  {generic_poly_copy[j]}\n")
        # почленно проводим операцию побитового сложения по модулю два с подготовленным массивом
        corr_log.write(f"\n")
        
    corr_log.write(f"|||||||||||||||||||||||\n|||||||| КОНЕЦ {i} итерации в блоке||||||\n|||||||||||||||||||||||\n")

corr_log.close()
