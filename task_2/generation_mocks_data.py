import os
import random

DIR_NAME = "test_files"

def generate():
    if not os.path.exists(DIR_NAME):
        os.makedirs(DIR_NAME)

    print(f"Генерируем 1000 файлов в папке {DIR_NAME}...")

    for i in range(1000):
        lines_count = random.randint(100, 500)
        content = "\n".join([f"Строка данных номер {x}" for x in range(lines_count)])

        with open(f"{DIR_NAME}/file_{i}.txt", "w", encoding='utf-8') as f:
            f.write(content)

    print("Готово!")


if __name__ == "__main__":
    generate()