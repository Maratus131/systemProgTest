import csv

def write_to_csv(filepath, products):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Название товара', 'Цена'])
        writer.writerows(products)
