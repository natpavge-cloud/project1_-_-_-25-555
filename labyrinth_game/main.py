#!/usr/bin/env python3
# остальной код ниже

from constants import ROOMS, COMMANDS
from player_actions import show_inventory, get_input, move_player, take_item, use_item
from utils import describe_current_room, solve_puzzle, attempt_open_treasure, show_help

def process_command(game_state, command_string):
    # Если игра уже завершена, не обрабатываем команды
    if game_state.get('game_over', False):
        return False
    
    # Разделяем строку на части
    parts = command_string.strip().split()
    if not parts:
        print("Вы ничего не ввели.")
        return True
    
    # Первое слово - команда, остальное - аргументы
    cmd = parts[0].lower()
    args = parts[1:]
    
    # Используем match/case для обработки команд
    match cmd:
        # Команда осмотреться
        case "look" | "осмотреться" | "осмотр":
            describe_current_room(game_state)
            return True
        
        # Команда инвентаря
        case "inventory" | "инвентарь" | "инв":
            show_inventory(game_state)
            return True
        
        # Команда перемещения с указанием направления
        case "go" | "идти" | "move":
            if not args:
                print("Укажите направление движения.")
                return True
            
            # Берем последнее слово, если ввели "идти на север"
            direction = args[-1].lower() 
            
            direction_map = {
                'север': 'north', 'north': 'north', 'n': 'north',
                'юг': 'south', 'south': 'south', 's': 'south',
                'запад': 'west', 'west': 'west', 'w': 'west',
                'восток': 'east', 'east': 'east', 'e': 'east',
                'вверх': 'up', 'вниз': 'down' 
            }
            
            if direction in direction_map:
                # Передаем уже стандартизированное английское название
                move_player(game_state, direction_map[direction])
            else:
                # Если направления нет в мапе, пробуем передать как есть (вдруг там кастомный выход)
                move_player(game_state, direction)
            return True
        
        # Команда взять предмет
        case "take" | "взять" | "подобрать":
            if not args:
                print("Укажите, какой предмет вы хотите взять.")
                return True
            
            item_name = " ".join(args)
            take_item(game_state, item_name)
            return True
        
        # Команда использования предмета
        case "use" | "использовать":
            if not args:
                print("Укажите, какой предмет вы хотите использовать.")
                return True
            
            item_name = " ".join(args)
            use_item(game_state, item_name)
            return True
        
        # Команда решения загадки или открытия сундука
        case "solve" | "решить" | "загадка":
            # Проверка на treasure_room 
            if game_state['current_room'] == 'treasure_room':
                # В treasure_room вызываем функцию открытия сундука
                from utils import attempt_open_treasure
                attempt_open_treasure(game_state)
            else:
                # В других комнатах решаем загадки
                solve_puzzle(game_state)
            return True
        
        # Команда открытия сундука (специальная команда)
        case "open" | "открыть":
            if game_state['current_room'] == 'treasure_room':
                from utils import attempt_open_treasure
                attempt_open_treasure(game_state)
            else:
                print("Здесь нечего открывать.")
            return True
        
        # Команды завершения игры
        case "quit" | "exit" | "выход" | "выйти":
            print("Вы покидаете Лабиринт. Игра окончена.")
            game_state['game_over'] = True
            return False
        
        # Команда помощи
        case "help" | "помощь" | "?":
            print(COMMANDS)
            print("nОсобые предметы:")
            print("  torch/факел - освещает комнату")
            print("  sword/меч - придает уверенность")
            print("  bronze box/бронзовая шкатулка - можно открыть")
            print("nЗагадки:")
            print("  Решайте загадки с помощью команды 'solve'")
            print("  Каждая решенная загадка дает очки и награду")
            print("nПОБЕДА:")
            print("  Чтобы победить, найдите ключ от сокровищ и откройте сундук")
            print("  в treasure_room. Или взломайте сундук, решив загадку.")
            return True
                  
        # Команда показа счета 
        case "score" | "очки" | "счет":
            print(f"nВаш текущий счет: {game_state['score']} очков")
            print(f"Решено загадок: {game_state.get('solved_puzzles', 0)}")
            # Гарантируем, что player_inventory существует и это список/словарь
            inv_count = len(game_state.get('player_inventory', []))
            print(f"Собрано предметов: {inv_count}")
            return True
        
        # Односложные команды движения (без слова go)
        case "north" | "n" | "север":
            move_player(game_state, 'north')
            return True
        case "south" | "s" | "юг":
            move_player(game_state, 'south')
            return True
        case "west" | "w" | "запад":
            move_player(game_state, 'west')
            return True
        case "east" | "e" | "восток":
            move_player(game_state, 'east')
            return True
        
        # Неизвестная команда (ОСТАВЛЯЕМ ТОЛЬКО ЭТОТ БЛОК В КОНЦЕ ФУНКЦИИ)
        case _:
            print(f"Неизвестная команда: '{command_string}'")
            print("Введите 'help' для списка доступных команд.")
            return True


def main():
    # Глобальное состояние игры
    game_state = {
        'player_inventory': [],      # Инвентарь игрока
        'current_room': 'entrance',  # Текущая комната
        'game_over': False,          # Флаг окончания игры
        'steps_taken': 0,            # Количество шагов
        'score': 0,                  # Счет игрока
        'solved_puzzles': 0,         # Количество решенных загадок
        'victory': False             # Флаг победы
    }

    # Приветственное сообщение
    print("=" * 40)
    print("Добро пожаловать в Лабиринт сокровищ!")
    print("=" * 40)
    print("nВаша цель - исследовать лабиринт, собирать предметы,")
    print("решать загадки и находить сокровища.")
    print("nКЛЮЧ К ПОБЕДЕ:")
    print("1. Найдите ключ от сокровищ (treasure_key)")
    print("2. Или взломайте сундук кодом")
    print("3. Откройте сундук в treasure_room")
    print("nВведите 'help' для списка команд, 'score' для просмотра счета.")
    print("-" * 50)

    # Описание стартовой комнаты
    describe_current_room(game_state)

    # Основной игровой цикл
    while not game_state['game_over']:
        command = get_input("n> ").strip()
        if not command:
            print("Введите команду. Для справки введите 'помощь'.")
            continue
        process_command(game_state, command)

    # Завершение игры
    print("n" + "=" * 50)
    if game_state.get('victory', False):
        print("🎉🎉🎉 ПОЗДРАВЛЯЕМ С ПОБЕДОЙ! 🎉🎉🎉")
        print("Вы нашли сокровище и победили в игре!")
    else:
        print("ИГРА ЗАВЕРШЕНА")
    print("=" * 50)

    print(f"nВаши результаты:")
    print(f"• Количество сделанных шагов: {game_state['steps_taken']}")
    print(f"• Ваш счет: {game_state['score']} очков")
    print(f"• Решено загадок: {game_state.get('solved_puzzles', 0)}")
    print(f"• Предметов собрано: {len(game_state['player_inventory'])}")
    
    # Определяем уровень по очкам
    score = game_state['score']
    if game_state.get('victory', False):
        if score >= 200:
            rating = "Легендарный герой! 🏆🏆🏆"
        elif score >= 150:
            rating = "Великий победитель! 🏆🏆"
        else:
            rating = "Победитель лабиринта! 🏆"
    else:
        if score >= 100:
            rating = "Было близко! ⭐️⭐️⭐️"
        elif score >= 50:
            rating = "Хорошая попытка! ⭐️⭐️"
        else:
            rating = "Попробуйте еще раз! ⭐️"
    print(f"• Рейтинг: {rating}")
    print("\nСпасибо за игру! До новых приключений")


# Точка входа
if __name__ == "__main__":
    main()
