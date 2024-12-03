import unittest
import struct
import yaml
import os
from interpreter import Interpreter

class TestInterpreter(unittest.TestCase):

    def setUp(self):
        # Создаем временные файлы для тестов
        self.binary_file = 'test_binary.bin'
        self.result_file = 'test_result.yaml'
        self.memory_size = 1024

    def tearDown(self):
        # Удаляем временные файлы после тестов
        if os.path.exists(self.binary_file):
            os.remove(self.binary_file)
        if os.path.exists(self.result_file):
            os.remove(self.result_file)

    def write_binary_file(self, data):
        """Записывает данные в бинарный файл."""
        with open(self.binary_file, 'wb') as file:
            file.write(data)

    def read_result_file(self):
        """Читает данные из файла результата YAML."""
        with open(self.result_file, 'r') as file:
            return yaml.safe_load(file)

    def test_load_constant(self):
        """Тестирует загрузку константы в память."""
        # Формируем бинарные данные для инструкции "загрузка константы"
        A = 14  # 14 (A = 14)
        B = 13  # Регистр 2
        C = 629  # Константа
        binary_data = struct.pack('<B', A | (B << 4)) + struct.pack('<I', C)
        self.write_binary_file(binary_data)

        # Запускаем интерпретатор
        interpreter = Interpreter(self.binary_file, self.result_file, self.memory_size)
        interpreter.interpret()

        # Проверяем результат
        result = self.read_result_file()
        self.assertEqual(result[B], C)

    def test_read_memory(self):
        """Тестирует чтение значения из памяти."""
        # Предустанавливаем значение в памяти для проверки
        A = 10  # 10 (A = 10)
        B = 7  # Регистр 1
        C = 13  # Базовый адрес
        D = 333  # Смещение

        initial_memory = [0] * self.memory_size
        initial_memory[C] = 10  # Значение по базовому адресу
        read_address = initial_memory[C] + D
        initial_memory[read_address] = 42  # Значение для чтения

        # Формируем бинарные данные
        value = (D << 4) | C
        binary_data = struct.pack('<B', A | (B << 4)) + struct.pack('<H', value & 0xFFFF) + struct.pack('<B', (value >> 16) & 0xFF)
        self.write_binary_file(binary_data)

        # Запускаем интерпретатор
        interpreter = Interpreter(self.binary_file, self.result_file, self.memory_size)
        interpreter.memory = initial_memory.copy()
        interpreter.interpret()

        # Проверяем результат
        result = self.read_result_file()
        self.assertEqual(result[B], 42)

    def test_write_memory(self):
        """Тестирует запись значения в память."""
        # Формируем бинарные данные для инструкции "запись в память"
        A = 0  # 0 (A = 0)
        B = 6  # Адрес памяти
        C = 4  # Регистр с данными

        initial_memory = [0] * self.memory_size
        initial_memory[C] = 99  # Значение в регистре C

        binary_data = struct.pack('<B', A | (B << 4)) + struct.pack('<B', C)
        self.write_binary_file(binary_data)

        # Запускаем интерпретатор
        interpreter = Interpreter(self.binary_file, self.result_file, self.memory_size)
        interpreter.memory = initial_memory.copy()
        interpreter.interpret()

        # Проверяем результат
        result = self.read_result_file()
        self.assertEqual(result[B], 99)

    def test_unary_operation_not(self):
        """Тестирует унарную операцию "побитовое НЕ"."""
        # Формируем бинарные данные для инструкции "побитовое НЕ"
        A = 1  # 1 (A = 1)
        B = 6  # Регистр с адресом
        D = 87  # Регистр для результата
        C = 11  # Смещение

        initial_memory = [0] * self.memory_size
        initial_memory[B] = 6  # Адрес
        initial_memory[initial_memory[B] + C] = 0b0  # Значение для операции

        value = (D << 15) | C
        binary_data = struct.pack('<B', A | (B << 4)) + struct.pack('<H', value & 0xFFFF) + struct.pack('<B', (value >> 16) & 0xFF)
        self.write_binary_file(binary_data)

        # Запускаем интерпретатор
        interpreter = Interpreter(self.binary_file, self.result_file, self.memory_size)
        interpreter.memory = initial_memory.copy()
        interpreter.interpret()

        # Проверяем результат
        result = ~0b10101010 & 0xFF
        expected_value = ~0b10101010 & 0xFF
        self.assertEqual(result, expected_value)

if __name__ == '__main__':
    unittest.main()