import unittest
import struct
import tempfile
import os
import yaml
from assembler import Assembler  # Замените на правильный путь к вашему файлу


class TestAssembler(unittest.TestCase):

    def setUp(self):
        # Создадим временные файлы для бинарных данных и логов
        self.source_file = tempfile.NamedTemporaryFile(delete=False)
        self.binary_file = tempfile.NamedTemporaryFile(delete=False)
        self.log_file = tempfile.NamedTemporaryFile(delete=False)

        # Закрываем временные файлы, чтобы они могли быть использованы позже
        self.source_file.close()
        self.binary_file.close()
        self.log_file.close()

    def tearDown(self):
        # Удаляем временные файлы после тестов
        os.remove(self.source_file.name)
        os.remove(self.binary_file.name)
        os.remove(self.log_file.name)

    def test_load_constant(self):
        # Пример строки для загрузки константы (инструкция 14)
        test_code = "14 13 629\n"

        with open(self.source_file.name, 'w') as f:
            f.write(test_code)

        assembler = Assembler(self.source_file.name, self.binary_file.name, self.log_file.name)
        assembler.assemble()

        # Ожидаем, что в бинарном файле будет записано 5 байт
        with open(self.binary_file.name, 'rb') as f:
            binary_data = f.read()

        # Проверяем, что бинарные данные правильные

        expected_value = (14 & 0xF) | ((13 & 0xF) << 4) | ((629 & 0xFFFFF) << 8)
        expected_data = struct.pack('<I', expected_value & 0xFFFFFFFF) + struct.pack('<B',
                                                                                     (expected_value >> 32) & 0xFF)

        self.assertEqual(binary_data, expected_data)

        # Проверяем лог-файл
        with open(self.log_file.name, 'r') as yamlfile:
            log_data = yaml.safe_load(yamlfile)

        expected_log = [{"A": 14, "B": 13, "C": 629}]
        self.assertEqual(log_data, expected_log)

    def test_read_memory(self):
        # Пример строки для чтения значения из памяти (инструкция 10)
        test_code = "10 7 13 333\n"

        with open(self.source_file.name, 'w') as f:
            f.write(test_code)

        assembler = Assembler(self.source_file.name, self.binary_file.name, self.log_file.name)
        assembler.assemble()

        with open(self.binary_file.name, 'rb') as f:
            binary_data = f.read()

        # Ожидаемое значение для инструкции 10 (чтение из памяти)
        expected_value = (10 & 0xF) | ((7 & 0xF) << 4) | ((13 & 0xF) << 8) | ((333 & 0x7FFF) << 12)
        expected_data = struct.pack('<I', expected_value)

        self.assertEqual(binary_data, expected_data)

        # Проверка логов
        with open(self.log_file.name, 'r') as yamlfile:
            log_data = yaml.safe_load(yamlfile)

        expected_log = [{"A": 10, "B": 7, "C": 13, "D": 333}]
        self.assertEqual(log_data, expected_log)

    def test_write_memory(self):
        # Пример строки для записи в память (инструкция 0)
        test_code = "0 6 4\n"

        with open(self.source_file.name, 'w') as f:
            f.write(test_code)

        assembler = Assembler(self.source_file.name, self.binary_file.name, self.log_file.name)
        assembler.assemble()

        with open(self.binary_file.name, 'rb') as f:
            binary_data = f.read()

        # Ожидаемое значение для инструкции 0 (запись в память)
        expected_value = (0 & 0xF) | ((6 & 0xF) << 4) | ((4 & 0xF) << 8)
        expected_data = struct.pack('<H', expected_value)

        self.assertEqual(binary_data, expected_data)

        # Проверка логов
        with open(self.log_file.name, 'r') as yamlfile:
            log_data = yaml.safe_load(yamlfile)

        expected_log = [{"A": 0, "B": 6, "C": 4}]
        self.assertEqual(log_data, expected_log)

    def test_unary_operation_not(self):
        # Пример строки для унарной операции побитового "не" (инструкция 1)
        test_code = "1 6 87 11\n"

        with open(self.source_file.name, 'w') as f:
            f.write(test_code)

        assembler = Assembler(self.source_file.name, self.binary_file.name, self.log_file.name)
        assembler.assemble()

        with open(self.binary_file.name, 'rb') as f:
            binary_data = f.read()

        # Ожидаемое значение для инструкции 1 (побитовое "не")
        expected_value = (1 & 0xF) | ((6 & 0xF) << 4) | ((87 & 0x7F) << 8) | ((87 >> 7) << 15) | ((11 & 0xF) << 23)
        expected_data = struct.pack('<I', expected_value)

        self.assertEqual(binary_data, expected_data)

        # Проверка логов
        with open(self.log_file.name, 'r') as yamlfile:
            log_data = yaml.safe_load(yamlfile)

        expected_log = [{"A": 1, "B": 6, "C": 87, "D": 11}]
        self.assertEqual(log_data, expected_log)


if __name__ == "__main__":
    unittest.main()
