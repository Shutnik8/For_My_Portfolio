"""
telegram_sender.py
Автор: Вадик (Shutnik8)
Лицензия: См. файл LICENSE.md
"""

import requests
import json
import os
import sys
import logging
from datetime import datetime

# Настройка логирования
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('telegram_sender.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Загрузка конфигурации
def load_config():
    config_file = 'config.json'
    
    if not os.path.exists(config_file):
        logger.error(f"Файл конфигурации {config_file} не найден!")
        logger.info("Создайте файл config.json со следующим содержанием:")
        logger.info('''
{
    "bot_token": "ВАШ_ТОКЕН_БОТА",
    "chat_id": "ВАШ_CHAT_ID"
}
        ''')
        sys.exit(1)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Проверка обязательных полей
        if not config.get('bot_token') or not config.get('chat_id'):
            logger.error("В config.json отсутствуют bot_token или chat_id!")
            sys.exit(1)
        
        return config
    except json.JSONDecodeError:
        logger.error("Ошибка в формате config.json!")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ошибка при загрузке конфигурации: {e}")
        sys.exit(1)

# Чтение файла
def read_text_file(filename):
    try:
        if not os.path.exists(filename):
            logger.error(f"Файл {filename} не найден!")
            return None
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            logger.warning(f"Файл {filename} пуст!")
            return None
        
        logger.info(f"Прочитан файл {filename}, размер: {len(content)} символов")
        return content
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {filename}: {e}")
        return None

# Отправка сообщения в Telegram
def send_to_telegram(text, bot_token, chat_id):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        logger.info(f"Отправляем сообщение в чат {chat_id}...")
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('ok'):
            message_id = result['result']['message_id']
            logger.success(f"Сообщение успешно отправлено! ID сообщения: {message_id}")
            return True
        else:
            logger.error(f"Ошибка Telegram API: {result.get('description', 'Неизвестная ошибка')}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Таймаут при отправке сообщения!")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Ошибка соединения с Telegram!")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return False

# Основная функция
def main():
    # Определяем имя файла
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Введите имя текстового файла (например, message.txt): ").strip()
    
    if not filename:
        logger.error("Не указано имя файла!")
        sys.exit(1)
    
    # Загружаем конфигурацию
    config = load_config()
    bot_token = config['bot_token']
    chat_id = config['chat_id']
    
    # Читаем файл
    text = read_text_file(filename)
    if text is None:
        sys.exit(1)
    
    # Отправляем сообщение
    logger.info("Начинаем отправку сообщения...")
    if send_to_telegram(text, bot_token, chat_id):
        logger.info("="*50)
        logger.info("ОТПРАВКА ЗАВЕРШЕНА УСПЕШНО!")
        logger.info(f"Файл: {filename}")
        logger.info(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*50)
    else:
        logger.error("="*50)
        logger.error("ОТПРАВКА НЕ УДАЛАСЬ!")
        logger.error("="*50)
        sys.exit(1)

if __name__ == "__main__":
    # Добавляем кастомный уровень SUCCESS
    logging.addLevelName(25, "SUCCESS")
    
    def success(self, message, *args, **kwargs):
        if self.isEnabledFor(25):
            self._log(25, message, args, **kwargs)
    
    logging.Logger.success = success
    
    logger = setup_logging()
    main()