import struct
import sys
import yaml

class Interpreter:
    def __init__(self, binary_file, result_file, memory_size):
        self.binary_file = binary_file
        self.result_file = result_file
        self.memory_size = memory_size
        self.memory = [0] * memory_size

    def interpret(self):
        with open(self.binary_file, 'rb') as file:
            byte = file.read(1)
            while byte:
                instruction = struct.unpack('<B', byte)[0]  # Код инструкции (A)
                #print(f"Instruction code (A): {instruction & 0xF}")

                if instruction & 0xF == 14:  # Загрузка константы
                    value = struct.unpack('<I', file.read(4))[0]
                    A = instruction & 0xF
                    B = (instruction >> 4) & 0xF
                    C = value & 0xFFFFFF
                    print(f"Загрузка константы (Instruction {instruction & 0xF}): A={A}, B={B}, C={C}")
                    if B < self.memory_size:
                        self.memory[B] = C  # Имитация загрузки константы
                    else:
                        print(f"Ошибка: индекс памяти {B} вне допустимого диапазона.")

                elif instruction & 0xF == 10:  # Чтение значения из памяти
                    value_high, value_low = struct.unpack('<H', file.read(2))[0], struct.unpack('<B', file.read(1))[0]
                    value = (value_low << 16) | value_high
                    A = instruction & 0xF
                    B = (instruction >> 4) & 0xF
                    C = value & 0xF
                    D = (value >> 4) & 0x2FFF
                    print(f"Чтение значения из памяти (Instruction {instruction & 0xF}): A={A}, B={B}, C={C}, D={D}")
                    if C < len(self.memory):  # Проверяем, что C в пределах допустимого диапазона
                        base_address = self.memory[C]
                        # Добавляем смещение D
                        read_address = base_address + D
                        # Проверяем, что итоговый адрес находится в пределах памяти
                        if 0 <= read_address < len(self.memory):
                            self.memory[B] = self.memory[read_address]  # Копируем значение в регистр B
                        else:
                            print(f"Ошибка: адрес чтения {read_address} вне допустимого диапазона.")
                    else:
                        print(f"Ошибка: адрес в регистре C {C} вне допустимого диапазона.")

                elif instruction & 0xF == 0:  # Запись значения в память
                    value = struct.unpack('<B', file.read(1))[0]
                    A = instruction & 0xF
                    B = (instruction >> 4) & 0xF
                    C = value & 0xF
                    print(f"Запись значения в память (Instruction {instruction & 0xF}): A={A}, B={B}, C={C}")
                    if C < len(self.memory):
                        value_to_write = self.memory[C]  # Получаем значение из регистра C
                        if B < len(self.memory):  # Проверяем, что индекс B в допустимом диапазоне
                            self.memory[B] = value_to_write  # Записываем в память по адресу B
                            #print(f"Записано значение {value_to_write} в память по адресу {B}")
                        else:
                            print(f"Ошибка: адрес записи {B} вне допустимого диапазона.")
                    else:
                        print(f"Ошибка: регистр {C} вне допустимого диапазона.")

                elif instruction & 0xF == 1:  # Унарная операция: побитовое "не"
                    value_high, value_low = struct.unpack('<H', file.read(2))[0], struct.unpack('<B', file.read(1))[0]
                    value = (value_low << 16) | value_high
                    A = instruction & 0xF
                    B = (instruction >> 4) & 0xF
                    C = value & 0x3FFF
                    D = (value >> 15) & 0xF
                    print(f"Унарная операция (Instruction {instruction & 0xF}): побитовое 'не': A={A}, B={B}, C={C}, D={D}")
                    # Вычисление адреса для чтения
                    read_address = self.memory[B] + C  # Адрес для чтения (регистр[B] + смещение C)
                    # Проверка на валидность адреса
                    if 0 <= read_address < len(self.memory):
                        # Чтение значения из памяти по вычисленному адресу
                        value_to_negate = self.memory[read_address]
                        # Применяем побитовое "не"
                        negated_value = ~value_to_negate & 0xFF  # Побитовое "не" и обрезка до 32 бит
                        # Записываем результат в регистр по адресу D
                        if 0 <= D < len(self.memory):
                            self.memory[D] = negated_value  # Регистр по адресу D получает результат операции
                            #print(f"Унарная операция (побитовое 'не') выполнена: {value_to_negate} -> {negated_value} в регистре {D}")
                        else:
                            print(f"Ошибка: регистр {D} вне допустимого диапазона.")
                    else:
                        print(f"Ошибка: адрес чтения {read_address} вне допустимого диапазона.")

                else:
                    print(f"Unknown instruction code: {instruction & 0xF}")
                    raise ValueError(f"Unknown instruction code: {instruction & 0xF}")

                byte = file.read(1)

        # Запись результатов в файл результата
        result_data = {k: v for k, v in enumerate(self.memory)}
        with open(self.result_file, 'w') as yamlfile:
            yaml.dump(result_data, yamlfile, default_flow_style=False)

if __name__ == "__main__":
    binary_file = sys.argv[1]
    result_file = sys.argv[2]
    memory_size = int(sys.argv[3])
    interpreter = Interpreter(binary_file, result_file, memory_size)
    interpreter.interpret()
