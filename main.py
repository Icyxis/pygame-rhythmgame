import pygame
import sys
import math

# 초기화
pygame.init()

# 화면 설정
screen_width = 1400
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("4키 리듬 게임")

# 색상 정의
white = (255, 255, 255)
black = (0, 0, 0)
gray = (169, 169, 169)
yellow = (255, 255, 0)

# 폰트 설정
font = pygame.font.Font(None, 36)

# 키 설정
keys = {'d': pygame.K_d, 'f': pygame.K_f, 'j': pygame.K_j, 'k': pygame.K_k}

# 노트 설정
note_speed = 5
note_radius = 30
notes = []

# 키 UI 설정
key_radius = 30
key_spacing = 70
key_hitboxes = {}  # 각 키의 UI 히트박스 정보를 저장

# Combo 설정
combo = 0

# 눌린 상태를 저장
key_pressed_state = {key: False for key in keys}

# 노트 파일 로드 함수
def load_notes_from_file(file_path):
    notes = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for y, line in enumerate(lines):
            for x, char in enumerate(line.strip()):
                if char == '1':
                    key_to_drop = list(keys.keys())[x]
                    note_x = int((list(keys.keys()).index(key_to_drop) + 0.465) * key_spacing)
                    
                    # 메트로놈 주기에 따라 각 줄의 노트 생성 간격 조절
                    note_y = y * -note_radius * 2 * (60 / metronome_bpm)  
                    
                    notes.append({'x': note_x, 'y': note_y, 'color': gray, 'active': True})
    return notes

# 키별로 노트 파일 경로 지정
note_file_path = '파일이름.txt' #채보 파일 입력

# 메트로놈 BPM 설정
metronome_bpm = 55

# 노트 초기화
notes.extend(load_notes_from_file(note_file_path))

# 음악 파일 경로
music_file_path = '곡 이름.mp3' # 곡 입력

# 음악 초기화
pygame.mixer.init()
pygame.mixer.music.load(music_file_path)

# 키 UI 설정
for key, x_position in zip(keys.keys(), range(0, screen_width, key_spacing)):
    key_hitboxes[key] = {'center': (x_position + key_radius, screen_height - 40), 'color': gray}


# 게임 루프
clock = pygame.time.Clock()

# 대기 시간 설정 (단위: 초)
wait_time_seconds = 0
start_time = pygame.time.get_ticks()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    current_time = pygame.time.get_ticks()

    # 음악 재생 시작 시간 경과 후 음악 재생
    if current_time - start_time > wait_time_seconds * 1000:
        pygame.mixer.music.play()
        start_time = float('inf')  # 음악이 재생된 후에는 더 이상 음악 재생 안되게 함

    # 노트 이동
    for note in notes:
        note['y'] += note_speed

    # 노트가 화면 아래로 벗어나면 Combo 초기화
    for note in notes:
        if note['y'] > screen_height and note['active']:
            combo = 0
            note['active'] = False

    # 화면 지우기
    screen.fill(white)

    # 왼쪽 아래에 키 UI 그리기
    for key, hitbox in key_hitboxes.items():
        is_key_pressed = pygame.key.get_pressed()[keys[key]]

        # 키가 눌린 상태이고, 노트와 키 UI가 50% 이상 겹쳤을 때 노트를 제거하고 Combo 증가
        if is_key_pressed and not key_pressed_state[key]:
            for note in notes[:]:
                distance = math.sqrt((note['x'] - hitbox['center'][0]) ** 2 + (note['y'] - hitbox['center'][1]) ** 2)
                overlap_percentage = 1 - distance / (note_radius + key_radius)
                if overlap_percentage >= 0.5 and note['active']:
                    notes.remove(note)
                    combo += 1
                    break  # 노트 1개만 사라지게 하기 위해 break 추가

        key_pressed_state[key] = is_key_pressed  # 현재 키 상태 저장

        pygame.draw.circle(screen, gray if not is_key_pressed else yellow, hitbox['center'], key_radius)
        pygame.draw.circle(screen, black if not is_key_pressed else yellow, hitbox['center'], key_radius, 2)  # 키 UI 테두리 그리기

        text = font.render(key, True, white)
        screen.blit(text, (hitbox['center'][0] - text.get_width() // 2, hitbox['center'][1] - text.get_height() // 2))

    # Combo 표시
    combo_text = font.render(f'Combo: {combo}', True, black)
    screen.blit(combo_text, (10, 10))

    # 노트 그리기
    for note in notes:
        pygame.draw.circle(screen, note['color'], (note['x'], note['y']), note_radius)

    pygame.display.flip()

    # 초당 프레임 수 제어
    clock.tick(60)
