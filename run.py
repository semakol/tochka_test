from datetime import datetime as dt
import json

def check_capacity(max_capacity: int, guests: list) -> bool:
    guests_event = []
    min_day = min(dt.fromisoformat(i['check-in']) for i in guests)
    for item in guests:
        guests_event.append(((dt.fromisoformat(item['check-in']) - min_day).days, True))
        guests_event.append(((dt.fromisoformat(item['check-out']) - min_day).days, False))
    room_taken = 0
    guests_event.sort(key=lambda x: (x[0], x[1]))
    for event in guests_event:
        if event[1]:
            room_taken += 1
        else:
            room_taken -= 1
        if room_taken > max_capacity:
            return False
    return True

if __name__ == "__main__":
    # Чтение входных данных
    max_capacity = int(input())
    n = int(input())


    guests = []
    for _ in range(n):
        guest_json = input()
        guest_data = json.loads(guest_json)
        guests.append(guest_data)


    result = check_capacity(max_capacity, guests)
    print(result)