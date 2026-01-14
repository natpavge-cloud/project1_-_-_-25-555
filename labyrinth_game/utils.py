"""Модуль для вспомогательных функций игры."""

from player_actions import get_input
import math
from constants import COMMANDS
from constants import ROOMS

def show_help(commands):
    print("\nДоступные команды:")
    for description in commands.values():
        print(f"  - {description}")

def describe_current_room(game_state):
    current_room_key = game_state['current_room']
    room = ROOMS[current_room_key]
    
    # Используем имя комнаты или ключ, если имя не указано
    room_name = room.get('name', current_room_key).replace('_', ' ').upper()
    print(f"\n== {room_name} ==")
    
    description = room.get('description', 'Здесь ничего особенного.')
    print(description)
    
    # Список видимых предметов (если есть)
    items = room.get('items', [])
    if items:
        print("\n📦 Заметные предметы:")
        for item in items:
            if isinstance(item, dict):
                print(f"  • {item.get('name', 'Неизвестный предмет')}")
            else:
                print(f"  • {item}")
    
    # Доступные выходы
    exits = room.get('exits', {})
    if exits:
        exits_list = ", ".join(exits.keys())
        print(f"\n🚪 Выходы: {exits_list}")
    
    # Сообщение о наличии загадки
    if room.get('puzzle'):
        print("\n❓ Кажется, здесь есть загадка (используйте команду 'solve').")

def solve_puzzle(game_state):
    
    # Получаем текущую комнату
    current_room_key = game_state['current_room']
    
    # Если мы в treasure_room, вызываем специальную функцию
    if current_room_key == 'treasure_room':
        return attempt_open_treasure(game_state)
    
    current_room = ROOMS[current_room_key]
    
    # Проверяем, есть ли загадка в комнате
    if 'puzzle' not in current_room or current_room['puzzle'] is None:
        print("❌ Загадок здесь нет.")
        return False
    
    # Получаем информацию о загадке
    puzzle = current_room['puzzle']
    
    # Выводим вопрос загадки
    print(f"\n{'='*40}")
    print("🎯 ЗАГАДКА!")
    print('='*40)
    print(f"Вопрос: {puzzle.get('question', 'Вопрос не указан')}")
    
    # Получаем ответ от пользователя
    answer = get_input("\nВаш ответ: ").strip().lower()
    
    # Получаем правильный ответ (может быть строкой или списком вариантов)
    correct_answer = puzzle.get('answer', '')
    
    # Проверяем ответ (учитываем разные форматы ответов и альтернативные варианты)
    is_correct = False
    
    if isinstance(correct_answer, str):
        # Правильный ответ - строка
        answer_lower = answer.lower()
        correct_lower = correct_answer.lower()
        
        # Проверяем точное совпадение
        is_correct = answer_lower == correct_lower
        
        # Проверка альтернативных вариантов для числовых ответов
        # Для числовых ответов принимаем также текстовое представление
        if not is_correct and correct_lower.isdigit():
            # Пробуем преобразовать ответ пользователя в число
            try:
                user_num = int(answer_lower)
                correct_num = int(correct_lower)
                is_correct = user_num == correct_num
            except ValueError:
                # Если не число, проверяем текстовые представления
                number_words = {
                    '10': ['десять', 'десяти', 'десятью'],
                    '5': ['пять', 'пяти', 'пятью'],
                    # Можно добавить другие числа по необходимости
                }
                if correct_lower in number_words:
                    is_correct = answer_lower in number_words[correct_lower]
          
    elif isinstance(correct_answer, list):
        # Правильный ответ - список возможных вариантов
        is_correct = any(answer == option.lower() for option in correct_answer)

# Проверка числовых вариантов в списке
        if not is_correct:
            for option in correct_answer:
                # Добавлена проверка, что option — строка, чтобы .isdigit() не падал
                if isinstance(option, str) and option.isdigit() and answer.isdigit():
                    if int(answer) == int(option):
                        is_correct = True
                        break
        
    else:
        # Неизвестный формат ответа
        print("❌ Ошибка: неправильный формат загадки.")
        return False
    
    # Обрабатываем результат
    if is_correct:
        print("\n✅ Верно! Загадка решена!")
        print("🎉 Вы получаете награду!")
        
        # Убираем загадку из комнаты
        current_room['puzzle'] = None
        print("✨ Загадка исчезает.")
        
        # Добавляем награду игроку
        reward = puzzle.get('reward', None)

        if not reward:
            # Если награда не указана в загадке, используем комнатную награду
            room_items = current_room.get('items', [])
            if room_items and current_room_key == 'trap_room':
                reward = 'особый ключ'  # Пример комнатной награды
            elif current_room_key == 'hall':
                reward = 'серебряная медаль'
            elif current_room_key == 'library':
                reward = 'древний свиток'
            elif current_room_key == 'treasure_room':
                reward = 'сокровище'

        if reward:
            if isinstance(reward, list):
                # Если награда - список предметов
                for item in reward:
                    game_state['player_inventory'].append(item)
                    print(f"🎁 Вы получаете: {item}")
            elif isinstance(reward, dict):
                # Если награда - словарь с описанием
                game_state['player_inventory'].append(reward)
                print(f"🎁 Вы получаете: {reward.get('name', 'награда')}")
            else:
                # Если награда - строка
                game_state['player_inventory'].append(reward)
                print(f"🎁 Вы получаете: {reward}")
        
        # Добавляем очки за решение
        points = puzzle.get('points', 10)
        game_state['score'] = game_state.get('score', 0) + points
        
        # Увеличиваем счетчик решенных загадок
        game_state['solved_puzzles'] = game_state.get('solved_puzzles', 0) + 1
        
        print(f"⭐ Вы заработали {points} очков!")
        print(f"💰 Текущий счет: {game_state['score']} очков")
        
        return True
    else:
        print("\n❌ Неверно. Попробуйте снова.")
        
        # В trap_room неверный ответ активирует ловушку
        if current_room_key == 'trap_room':
            print("Неверный ответ активирует ловушку!")
            trigger_trap(game_state)
            return False

def attempt_open_treasure(game_state):
       
    # Получаем текущую комнату
    current_room_key = game_state['current_room']
    current_room = ROOMS[current_room_key]
    
    # Проверяем, что мы в treasure_room
    if current_room_key != 'treasure_room':
        print("Здесь нет сундука с сокровищами.")
        return False
    
    # Проверяем, есть ли сундук в комнате
    if 'treasure_chest' not in current_room.get('items', []):
        print("Сундук уже открыт.")
        return True  # Возвращаем True, так как сундук уже открыт (игра может быть завершена)
    
    # Проверяем, есть ли у игрока ключ
    inventory = game_state.get('player_inventory', [])
    
    # Проверяем наличие treasure_key в инвентаре
    has_treasure_key = False
    for item in inventory:
        if isinstance(item, str):
            if item.lower() == 'treasure_key' or item.lower() == 'ключ от сокровищ':
                has_treasure_key = True
                break
    
    # Вариант 1: У игрока есть ключ
    if has_treasure_key:
        print("\nВы применяете ключ, и замок щёлкает. Сундук открыт!")
        
        # Удаляем сундук из комнаты
        current_room['items'] = [item for item in current_room.get('items', []) 
                                 if isinstance(item, str) and item.lower() != 'treasure_chest']
        
        print("🎉 В сундуке сокровище! Вы победили!")
        
        # Устанавливаем флаг победы
        game_state['victory'] = True
        game_state['game_over'] = True
        
        # Добавляем бонусные очки за победу
        game_state['score'] = game_state.get('score', 0) + 100
        
        return True
    
    # Вариант 2: Ключа нет, предлагаем ввести код
    print("\nСундук заперт. У вас нет подходящего ключа.")
    
    # Спрашиваем, хочет ли игрок ввести код
    response = get_input("Попробовать ввести код? (да/нет): ").strip().lower()
    
    if response in ('да', 'yes', 'y', 'д'):
        # Получаем код от пользователя
        code = get_input("Введите код: ").strip()
        
        # Получаем правильный ответ из загадки ДО того, как её удалим
        puzzle_data = current_room.get('puzzle')
        correct_code = puzzle_data.get('answer', '') if puzzle_data else None
        
        # Проверяем код
        if code == correct_code:
            print("\n✅ Код принят! Сундук открывается!")
            
            # Удаляем сундук из комнаты
            current_room['items'] = [item for item in current_room.get('items', []) 
                                     if isinstance(item, str) and item.lower() != 'treasure_chest']
            
            print("🎉 В сундуке сокровище! Вы победили!")
            
            # Устанавливаем флаг победы
            game_state['victory'] = True
            game_state['game_over'] = True
            
            # Добавляем бонусные очки за победу
            game_state['score'] = game_state.get('score', 0) + 100
            
            # Добавляем очки за решение загадки
            if puzzle_data:
                points = puzzle_data.get('points', 25)
                game_state['score'] += points
            
            # ВАЖНО: Удаляем загадку только после начисления очков
            current_room['puzzle'] = None
            
            return True
        else:
            print("❌ Неверный код. Сундук остается запертым.")
            return False
    else:
        print("Вы отступаете от сундука.")
        return False

def pseudo_random(seed, modulo):
    if modulo <= 0:
        return 0 
    
def pseudo_random(seed, modulo):
    # Если modulo <= 0, возвращаем 0, чтобы избежать ошибки деления на ноль
    if modulo <= 0:
        return 0
        
    # Вычисляем псевдослучайное значение по формуле
    x = math.sin(seed * 12.9898) * 43758.5453
    fractional_part = x - math.floor(x)
    
    # Преобразуем в нужный диапазон
    result = int(fractional_part * modulo)
    
    return result

def trigger_trap(game_state):
    print("\n⚠️ Ловушка активирована! Пол стал дрожать...")
    
    inventory = game_state.get('player_inventory', [])
    
    # Считаем шаги для "рандома", если ключа нет, используем 0
    steps = game_state.get('steps_taken', 0)
    
    if inventory:
        # Выбираем случайный предмет для удаления
        item_index = pseudo_random(steps, len(inventory))
        lost_item = inventory.pop(item_index)
        
        if isinstance(lost_item, dict):
            print(f"📉 Вы потеряли предмет: {lost_item.get('name', 'предмет')}")
        else:
            print(f"📉 Вы потеряли предмет: {lost_item}")
    else:
        # Игрок получает "урон"
        damage_chance = pseudo_random(steps, 10)
        
        if damage_chance < 3:  # 30% шанс поражения
            print("☠️ Вас настигла ловушка! Игра окончена.")
            game_state['game_over'] = True
        else:
            print("🏃 Вам удалось увернуться от ловушки. Вы уцелели!")

def random_event(game_state):
    # Проверяем, произойдет ли событие (10% шанс)
    event_roll = pseudo_random(game_state.get('steps_taken', 0), 10)
    
    if event_roll == 0:  # Событие происходит
        # Выбираем тип события
        event_type = pseudo_random(game_state.get('steps_taken', 0) + 1, 3)
        
        # Импорт лучше держать в начале файла, но если нужно здесь — ок
        from constants import ROOMS
        current_room_key = game_state['current_room']
        current_room = ROOMS[current_room_key]
        inventory = game_state.get('player_inventory', [])
        
        if event_type == 0:  # Сценарий 1: Находка
            print("\n✨ На полу вы замечаете блестящую монетку!")
            # Инициализируем список предметов, если его нет
            if 'items' not in current_room:
                current_room['items'] = []
            
            if 'coin' not in current_room['items']:
                current_room['items'].append('coin')
                print("🪙 Монета добавлена в комнату.")
        
        elif event_type == 1:  # Сценарий 2: Испуг
            print("\n👣 Вы слышите странный шорох в темноте...")
            # Проверяем, есть ли у игрока меч
            has_sword = any(
                (isinstance(item, str) and item.lower() in ['sword', 'меч']) or 
                (isinstance(item, dict) and item.get('name', '').lower() in ['sword', 'меч'])
                for item in inventory
            )
            
            if has_sword:
                print("⚔️ Вы достаете меч, и шорох тут же затихает.")
            else:
                print("😨 Шорох продолжается. Вам становится не по себе.")
        
        elif event_type == 2:  # Сценарий 3: Ловушка
            # Проверяем, есть ли у игрока факел
            has_torch = any(
                (isinstance(item, str) and item.lower() in ['torch', 'факел']) or 
                (isinstance(item, dict) and item.get('name', '').lower() in ['torch', 'факел'])
                for item in inventory
            )
            
            if current_room_key == 'trap_room' and not has_torch:
                print("\n⚠️ Вы не заметили ловушку в темноте!")
                trigger_trap(game_state)