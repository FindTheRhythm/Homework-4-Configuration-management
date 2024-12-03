import struct
import sys
import yaml


class Assembler:
    def __init__(self, source_file, binary_file, log_file):
        self.source_file = source_file
        self.binary_file = binary_file
        self.log_file = log_file

    def assemble(self):
        binary_data = []
        log_data = []

        with open(self.source_file, 'r') as file:
            for line in file:
                parts = line.strip().split()
                instruction = int(parts[0])
                if instruction == 14:
                    # Загрузка константы
                    A, B, C = int(parts[0]), int(parts[1]), int(parts[2])
                    value = (A & 0xF) | ((B & 0xF) << 4) | ((C & 0xFFFFF) << 8)
                    binary_data.append(struct.pack('<I', value & 0xFFFFFFFF) + struct.pack('<B', (value >> 32) & 0xFF))
                    log_data.append({"A": A, "B": B, "C": C})

                elif instruction == 10:
                    # Чтение значения из памяти
                    A, B, C, D = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                    value = (A & 0xF) | ((B & 0xF) << 4) | ((C & 0xF) << 8) | ((D & 0x7FFF) << 12)
                    binary_data.append(struct.pack('<I', value))
                    log_data.append({"A": A, "B": B, "C": C, "D": D})

                elif instruction == 0:
                    # Запись значения в память
                    A, B, C = int(parts[0]), int(parts[1]), int(parts[2])
                    value = (A & 0xF) | ((B & 0xF) << 4) | ((C & 0xF) << 8)
                    binary_data.append(struct.pack('<H', value))
                    log_data.append({"A": A, "B": B, "C": C})


                elif instruction == 1:
                    # Унарная операция: побитовое "не"
                    A, B, C, D = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                    # Формируем значение с правильными сдвигами
                    value = (A & 0xF) | ((B & 0xF) << 4) | ((C & 0x7F) << 8) | ((C >> 7) << 15) | ((D & 0xF) << 23)
                    binary_data.append(struct.pack('<I', value))
                    log_data.append({"A": A, "B": B, "C": C, "D": D})

        # Запись в бинарный файл
        with open(self.binary_file, 'wb') as file:
            for data in binary_data:
                file.write(data)

        # Запись в лог-файл
        with open(self.log_file, 'w') as yamlfile:
            yaml.dump(log_data, yamlfile, default_flow_style=False)




if __name__ == "__main__":
    source_file = sys.argv[1]
    binary_file = sys.argv[2]
    log_file = sys.argv[3]
    assembler = Assembler(source_file, binary_file, log_file)
    assembler.assemble()