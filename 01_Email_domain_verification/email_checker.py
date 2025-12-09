"""
email_checker.py - Проверка MX-записей доменов
Автор: Вадик (Shutnik8)
Лицензия: См. файл LICENSE.md
Версия: 1.0 (январь 2025)
"""

import dns.resolver
import os
import sys

def check_mx_records(domain):
    """
    Проверяет наличие MX-записей для домена
    """
    try:
        # Пытаемся получить MX-записи
        mx_records = dns.resolver.resolve(domain, 'MX')
        
        # Если MX-записи найдены, проверяем их валидность
        if mx_records:
            # Проверяем, что есть хотя бы одна валидная MX-запись
            for record in mx_records:
                # Проверяем, что exchange не пустой и не является корневым доменом
                exchange = str(record.exchange).rstrip('.')
                if exchange and exchange != '.':
                    return "домен валиден"
            return "MX-записи отсутствуют или некорректны"
        else:
            return "MX-записи отсутствуют или некорректны"
            
    except dns.resolver.NoAnswer:
        # Нет ответа на MX-запрос
        return "MX-записи отсутствуют или некорректны"
    except dns.resolver.NXDOMAIN:
        # Домен не существует
        return "домен отсутствует"
    except dns.resolver.Timeout:
        # Таймаут при запросе
        return "MX-записи отсутствуют или некорректны"
    except Exception as e:
        # Другие ошибки DNS
        return "MX-записи отсутствуют или некорректны"

def extract_domain(email):
    """
    Извлекает домен из email-адреса
    """
    try:
        # Проверяем, что email содержит символ @
        if '@' in email:
            domain = email.split('@')[1].strip()
            if domain:
                return domain
        return None
    except:
        return None

def main():
    # Путь к файлам (в той же директории, где находится скрипт)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "in_email.txt")
    output_file = os.path.join(script_dir, "out_email.txt")
    
    # Проверяем существование входного файла
    if not os.path.exists(input_file):
        print(f"Ошибка: файл {input_file} не найден!")
        print(f"Пожалуйста, создайте файл in_email.txt в директории: {script_dir}")
        sys.exit(1)
    
    # Читаем email-адреса из файла
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            emails = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)
    
    if not emails:
        print("Файл in_email.txt пуст или не содержит email-адресов")
        sys.exit(0)
    
    print(f"Найдено {len(emails)} email-адресов для проверки")
    print("-" * 50)
    
    results = []
    
    # Проверяем каждый email-адрес
    for i, email in enumerate(emails, 1):
        domain = extract_domain(email)
        
        if not domain:
            status = "некорректный email-адрес"
            result_line = f"{email}: {status}"
        else:
            status = check_mx_records(domain)
            result_line = f"{email}: {status}"
        
        # Выводим в консоль
        print(f"{i}. {result_line}")
        
        # Сохраняем для записи в файл
        results.append(result_line)
    
    print("-" * 50)
    
    # Записываем результаты в файл
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Результаты проверки MX-записей:\n")
            f.write("=" * 50 + "\n")
            for result in results:
                f.write(result + "\n")
        print(f"Результаты сохранены в файл: {output_file}")
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")

if __name__ == "__main__":
    main()
