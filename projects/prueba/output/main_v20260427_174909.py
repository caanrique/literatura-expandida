# Generado por LangGraph + Qwen Local
# Proyecto: prueba
# Prompt: "Crea un script que lea un archivo CSV, calcule el promedio de una columna y guarde el resultado en un nuevo archivo"

# Modelo clasificador: qwen-2.5
# Modelo ejecutor: qwen-coder-7b
# Fecha: 2026-04-27 17:49:09
# Iteraciones de corrección: 1
# Switch Llama: False
# Ejecución exitosa: True

import csv

def calculate_average_from_csv(file_path, column_index):
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row if present
        data = [float(row[column_index]) for row in reader]
    
    average = sum(data) / len(data)
    return average

def save_average_to_csv(average, output_file_path):
    with open(output_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Average'])
        writer.writerow([average])

# Example usage
input_file_path = 'input.csv'
output_file_path = 'output.csv'
column_index = 2  # Assuming the column index is 2 (third column)

try:
    average = calculate_average_from_csv(input_file_path, column_index)
    save_average_to_csv(average, output_file_path)
except FileNotFoundError as e:
    print(f"Error: {e}")