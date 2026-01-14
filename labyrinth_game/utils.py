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

def solve_puzzle(game_state, rooms_data):
    """
    Решение загадки в текущей комнате.
    rooms_data — передаем словарь комнат как аргумент, чтобы не зависеть от глобальных переменных.
    """
    current_room_key = game_state.get('current_room')
    
    # Если мы в treasure_room, вызываем специальную функцию
    if current_room_key == 'treasure_room':
        return attempt_open_treasure(game_state)

    current_room = rooms_data.get(current_room_key)
    if not current_room:
        print("❌ Ошибка: комната не найдена.")
        return False

    # Проверяем, есть ли загадка в комнате
    puzzle = current_room.get('puzzle')
    if puzzle is None:
        print("❌ Загадок здесь нет.")
        return False

    # Вывод интерфейса загадки
    print(f"\n{'=' * 40}")
    print("🎯 ЗАГАДКА!")
    print('=' * 40)
    print(f"Вопрос: {puzzle.get('question', 'Вопрос не указан')}")

    # Получаем ответ (используем input, если get_input не определена)
    answer_raw = input("\nВаш ответ: ")
    answer = answer_raw.strip().lower()

    correct_answer = puzzle.get('answer', '')
    is_correct = False

    # --- ЛОГИКА ПРОВЕРКИ ОТВЕТА ---
    if isinstance(correct_answer, (str, int)):
        correct_str = str(correct_answer).lower()
        if answer == correct_str:
            is_correct = True
        elif correct_str.isdigit():
            # Проверка текстовых представлений чисел
            number_words = {
                '10': ['десять', 'десяти', 'десятью'],
                '5': ['пять', 'пяти', 'пятью'],
                '3': ['три', 'трех', 'тремя']
            }
            is_correct = answer in number_words.get(correct_str, [])

    elif isinstance(correct_answer, list):
        normalized_options = [str(opt).lower() for opt in correct_answer]
        is_correct = answer in normalized_options
        
        if not is_correct and answer.isdigit():
            # Сравнение числовых значений в списке
            is_correct = any(int(answer) == int(opt) for opt in normalized_options if opt.isdigit())

    # --- ОБРАБОТКА РЕЗУЛЬТАТА ---
    if is_correct:
        print("\n✅ Верно! Загадка решена!")
        
        # Очищаем загадку в текущей сессии
        current_room['puzzle'] = None
        
        # Определение награды
        reward = puzzle.get('reward')
        if not reward:
            # Дефолтные награды по комнатам
            rewards_map = {
                'trap_room': 'особый ключ',
                'hall': 'серебряная медаль',
                'library': 'древний свиток',
                'treasure_room': 'сокровище'
            }
            reward = rewards_map.get(current_room_key)

        # Выдача награды
        if reward:
            inventory = game_state.setdefault('player_inventory', [])
            if isinstance(reward, list):
                for item in reward:
                    inventory.append(item)
                    print(f"🎁 Вы получаете: {item}")
            elif isinstance(reward, dict):
                inventory.append(reward)
                print(f"🎁 Вы получаете: {reward.get('name', 'награда')}")
            else:
                inventory.append(reward)
                print(f"🎁 Вы получаете: {reward}")

        # Обновление прогресса
        points = puzzle.get('points', 10)
        game_state['score'] = game_state.get('score', 0) + points
        game_state['solved_puzzles'] = game_state.get('solved_puzzles', 0) + 1
        
        print(f"⭐️ +{points} очков! Всего: {game_state['score']}")
        return True

    else:
        print("\n❌ Неверно.")
        if current_room_key == 'trap_room':
            print("⚠️ Ошибка активирует ловушку!")
            if 'trigger_trap' in globals():
                trigger_trap(game_state)
        return False

# Заглушки функций для работы кода
def attempt_open_treasure(gs): print("💰 Вы у сокровищницы!"); return True
def trigger_trap(gs): print("💥 БАБАХ! Ловушка сработала!"); gs['score'] = max(0, gs.get('score', 0) - 5)

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
        return True  # Считаем, что условие победы уже было достигнуто
    
    # Проверяем, есть ли у игрока ключ
    inventory = game_state.get('player_inventory', [])
    
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
        current_room['items'] = [
            item for item in current_room.get('items', [])
            if not (isinstance(item, str) and item.lower() == 'treasure_chest')
        ]
        
        # Отмечаем победу
        game_state['game_over'] = True
        game_state['win'] = True
        
        print("🎉 В сундуке сокровище! Вы победили!")
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