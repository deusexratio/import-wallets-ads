import os
import shutil

# Указываем путь к основной директории
base_dir = r'E:\.ADSPOWER_GLOBAL\cache'

# Название папки, которую нужно удалить (extension data)
folder_to_delete = 'bfnaelmomeimhlpmgjnjophhpkkoljpa'
#### ВНИМАНИЕ!!!!! Этот скрипт удалит из всех ваших профилей адс локальные закешированные данные указанного расширения


# Перебираем все папки в основной директории
for folder_name in os.listdir(base_dir):
    # Формируем полный путь к целевой папке
    target_folder = os.path.join(base_dir, folder_name, 'Default', 'Local Extension Settings', folder_to_delete)

    # Проверяем, существует ли папка
    if os.path.exists(target_folder):
        try:
            # Удаляем папку и все её содержимое
            shutil.rmtree(target_folder)
            print(f'Папка {target_folder} успешно удалена.')
        except Exception as e:
            print(f'Ошибка при удалении {target_folder}: {e}')
    else:
        print(f'Папка {target_folder} не найдена.')
