"""Модуль для функций, связанных с действиями игрока."""

from constants import ROOMS

def get_input(prompt="> "):
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nВыход из игры.")
        return "quit"

def describe_current_room(game_state):
    current_room_key = game_state.get('current_room')
    room = ROOMS.get(current_room_key)
    
    if not room:
        print("Вы находитесь в неизвестном месте.")
        return

    name = room.get('name', current_room_key).upper()
    print(f"\n== {name} ==")

    description = room.get('description', 'Здесь ничего особенного.')
    print(description)

    # Список видимых предметов (исправлен отступ)
    items = room.get('items', [])
    if items:
        print("\nЗаметные предметы:")
        for item in items:
            if isinstance(item, dict):
                print(f"  • {item.get('name', 'Неизвестный предмет')}")
            else:
                print(f"  • {item}")
    
    # Доступные выходы
    exits = room.get('exits', {})
    if exits:
        exits_list = ", ".join(exits.keys())
        print(f"\nВыходы: {exits_list}")
    
    # Сообщение о наличии загадки
    if room.get('puzzle'):
        print("\n🧩 Кажется, здесь есть загадка (используйте команду 'solve').")

def show_inventory(game_state):
    
    inventory = game_state.get('player_inventory') or []

    if not inventory:
        print("Инвентарь пуст.")
        return

    print("\n=== ИНВЕНТАРЬ ===\n")

    def print_item(index, name, desc=None):
        print(f"{index}. {name}")
        if desc:
            print(f"   {desc}")

    if isinstance(inventory, list):
        for index, item in enumerate(inventory, 1):
            if isinstance(item, str):
                print_item(index, item)
            elif isinstance(item, dict):
                print_item(
                    index,
                    item.get('name', 'Неизвестный предмет'),
                    item.get('description')
                )
            else:
                print_item(index, f"[неизвестный формат] {item}")

    elif isinstance(inventory, dict):
        for index, item in enumerate(inventory.values(), 1):
            if isinstance(item, str):
                print_item(index, item)
            elif isinstance(item, dict):
                # Добавил сюда desc, чтобы было как в списке
                print_item(index, item.get('name', 'Неизвестный предмет'), item.get('description'))
            else:
                print_item(index, f"[неизвестный формат] {item}")

    else:
        print(f"Содержимое инвентаря: {inventory}")

def move_player(game_state, direction):
    current_room_key = game_state['current_room']
    current_room = ROOMS[current_room_key]
    
    exits = current_room.get('exits', {})
    
    if direction in exits:
        # Проверка для перехода в treasure_room
        if exits.get(direction) == 'treasure_room':
            inventory = game_state.get('player_inventory', [])
            has_rusty_key = False
            
            # Твоя логика поиска ключа
            for item in inventory:
                if isinstance(item, str) and item.lower() in ['rusty_key', 'rusty key', 'ржавый ключ']:
                    has_rusty_key = True
                    break
                elif isinstance(item, dict):
                    item_name = item.get('name', '').lower()
                    if item_name in ['rusty_key', 'rusty key', 'ржавый ключ']:
                        has_rusty_key = True
                        break
            
            if not has_rusty_key:
                print("\n🔒 Дверь заперта. Нужен ключ, чтобы пройти дальше.")
                print("Похоже, нужен ржавый ключ...")
                return False
            else:
                print("\n🗝️ Вы используете найденный ключ, чтобы открыть путь в комнату сокровищ.")
               
        # Перемещаем игрока
        game_state['current_room'] = exits[direction]
        game_state['steps_taken'] = game_state.get('steps_taken', 0) + 1
        
        describe_current_room(game_state)
        
        # Случайное событие (импорт внутри функции — ок для скриптов)
        try:
            from utils import random_event
            random_event(game_state)
        except ImportError:
            pass # Если файла еще нет, игра не упадет
        
        return True
    else:
        print("🚫 Нельзя пойти в этом направлении.")
        return False
    
def take_item(game_state, item_name):
    # Получаем текущую комнату
    current_room_key = game_state['current_room']
    current_room = ROOMS[current_room_key]
    
    # Получаем список предметов в комнате
    room_items = current_room.get('items', [])
    
    # Если предметов нет
    if not room_items:
        print("Здесь нет предметов.")
        return False
    
    # Ищем предмет в комнате (без учета регистра)
    found_item = None
    found_index = -1
    
    for i, item in enumerate(room_items):
        # Проверяем разные форматы предметов
        if isinstance(item, str):
            if item.lower() == item_name.lower():
                found_item = item
                found_index = i
                break
        elif isinstance(item, dict):
            # Если предмет - словарь, ищем по ключу 'name'
            item_name_in_dict = item.get('name', '')
            if item_name_in_dict.lower() == item_name.lower():
                found_item = item
                found_index = i
                break
    
    # Если предмет найден
    if found_item is not None:
        # Добавляем предмет в инвентарь игрока
        game_state['player_inventory'].append(found_item)
        
        # Удаляем предмет из комнаты
        room_items.pop(found_index)
        
        # Выводим сообщение об успешном взятии
        if isinstance(found_item, dict):
            print(f"🛍️ Вы подняли: {found_item.get('name', 'предмет')}")
        else:
            print(f"🛍️ Вы подняли: {found_item}")
        
        return True
    else:
        # Предмет не найден (исправлен return)
        print("Такого предмета здесь нет.")
        return
    
def use_item(game_state, item_name):
    # Получаем инвентарь игрока
    inventory = game_state.get('player_inventory', [])
    
    # Ищем предмет в инвентаре
    found_item = None
    item_index = -1
    
    for i, item in enumerate(inventory):
        if isinstance(item, str):
            if item.lower() == item_name.lower():
                found_item = item
                item_index = i
                break
        elif isinstance(item, dict):
            item_name_in_dict = item.get('name', '')
            if item_name_in_dict.lower() == item_name.lower():
                found_item = item
                item_index = i
                break
    
    # Если предмет не найден
    if found_item is None:
        print("У вас нет такого предмета.")
        return False
    
    # Определяем фактическое название предмета
    actual_name = found_item if isinstance(found_item, str) else found_item.get('name', 'предмет')
    item_name_lower = actual_name.lower()
    
    if item_name_lower in ["torch", "факел"]:
        print("\n🔥 Вы зажгли факел. Стало значительно светлее!")
        print("Теперь вы можете разглядеть скрытые детали в комнатах.")
        return True
    
    elif item_name_lower in ["sword", "меч"]:
        print("\n⚔️ Вы достали меч и почувствовали уверенность в себе.")
        print("Теперь вы готовы к опасностям!")
        return True
    
    elif item_name_lower in ["bronze box", "бронзовая шкатулка"]:
        print("\n📦 Вы открываете бронзовую шкатулку...")
        print("Внутри вы находите старый ржавый ключ!")
        
        # Проверка дубликата ключа
        has_key = any(
            (isinstance(it, str) and it.lower() in ["rusty key", "ржавый ключ"]) or
            (isinstance(it, dict) and it.get('name', '').lower() in ["rusty key", "ржавый ключ"])
            for it in inventory
        )
        
        if not has_key:
            game_state['player_inventory'].append("ржавый ключ")
            print("🎁 Вы получили: ржавый ключ")
        else:
            print("Но у вас уже есть такой ключ.")
        
        # УДАЛЕНИЕ ШКАТУЛКИ (чтобы не открывать бесконечно)
        inventory.pop(item_index)
        print(f"(Предмет {actual_name} исчез из инвентаря)")
        
        return True
    
    else:
        print(f"Вы не знаете, как использовать {actual_name}.")
        return False