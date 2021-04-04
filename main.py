import ctypes
import time
import threading
import pyautogui

# Constants for keys
ENTER_KEY = 0x1C
S_KEY = 0x1F
ESC_KEY = 0x01
ARROW_DOWN_KEY = 0xD0
ARROW_UP_KEY = 0xC8
ARROW_LEFT_KEY = 0xCB
ARROW_RIGHT_KEY = 0xCD

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]
    
class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]
    

class KeyPresser:
    @staticmethod
    def press_key(hex_key_code):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, hex_key_code, 0x0008, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    @staticmethod
    def release_key(hex_key_code):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, hex_key_code, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    @staticmethod
    def press_and_release_key(hex_key_code, delay):
        KeyPresser.press_key(hex_key_code)
        time.sleep(1)
        KeyPresser.release_key(hex_key_code)
        time.sleep(1)
        time.sleep(delay)

class AnimationSkipper:
    @staticmethod
    def skip_pack_animation():
        global kill_flag
        while not kill_flag:
            for _ in range(3):
                KeyPresser.press_and_release_key(S_KEY, 1)
            time.sleep(3)

class HalfTimeSkipper:
    @staticmethod
    def skip_half_time():
        global kill_flag
        while not kill_flag:
            for _ in range(4):
                KeyPresser.press_and_release_key(ENTER_KEY, 1)
            time.sleep(25)

class UserSideDetector:
    @staticmethod
    def get_user_side():
        try:
            positions = pyautogui.locateCenterOnScreen('homeTeam.png', confidence=0.8, region=(0, 0, 423, 304))
            return 0 if positions else 1  # 0: Home team, 1: Away team
        except Exception as e:
            print(e)
            return 1 # Default to away team
        
class MenuAutomation:
    @staticmethod
    def is_match_already_played():
        positions = pyautogui.locateCenterOnScreen('alreadyPlayed.png', region=(1494, 226, 427, 408))
        return bool(positions)

    @staticmethod
    def press_key_sequence(key, delay_sequence):
        for delay in delay_sequence:
            KeyPresser.press_and_release_key(key, delay)

    @staticmethod
    def press_attack_mode_sequence():
        attack_mode_sequence = [1, 1, 1]
        MenuAutomation.press_key_sequence(0x50, attack_mode_sequence)

    @staticmethod
    def start_match_sequence():
        global kill_flag
        kill_flag = False
        enter_key_sequence = [2, 3, 2, 2, 4, 2, 4, 2, 10]
        MenuAutomation.press_key_sequence(ENTER_KEY, enter_key_sequence)
        s_key_sequence = [1, 2, 1]
        MenuAutomation.press_key_sequence(S_KEY, s_key_sequence)
        threading.Timer(1, AnimationSkipper.skip_pack_animation).start()
        threading.Timer(5, HalfTimeSkipper.skip_half_time).start()
        time.sleep(2)
        MenuAutomation.press_attack_mode_sequence()

    @staticmethod
    def navigate_menu(key):
        KeyPresser.press_key(key)
        time.sleep(0.2)
        KeyPresser.release_key(key)
        time.sleep(2)

class MatchSelector:
    @staticmethod
    def match_selection_loop():
        while True:
            time.sleep(15)
            if not MenuAutomation.is_match_already_played():
                print("Match is not already played, starting match...")
                MenuAutomation.start_match_sequence()
                break
            else:
                MatchSelector._navigate_and_check(ARROW_RIGHT_KEY)

            if not MenuAutomation.is_match_already_played():
                print("Match is not already played, starting match...")
                MenuAutomation.start_match_sequence()
                break
            else:
                MatchSelector._navigate_and_check(ARROW_DOWN_KEY)

            if not MenuAutomation.is_match_already_played():
                print("Match is not already played, starting match...")
                MenuAutomation.start_match_sequence()
                break
            else:
                MatchSelector._navigate_and_check(ARROW_LEFT_KEY)

            if not MenuAutomation.is_match_already_played():
                print("Match is not already played, starting match...")
                MenuAutomation.start_match_sequence()
                break
            else:
                MatchSelector._navigate_and_check(ARROW_UP_KEY)

    @staticmethod
    def _navigate_and_check(key):
        MenuAutomation.navigate_menu(key)
        if not MenuAutomation.is_match_already_played():
            print("Match is not already played, starting match...")
            MenuAutomation.start_match_sequence()
            return True
        return False

    @staticmethod
    def perform_attack_mode_sequence():
        user_side = UserSideDetector.get_user_side()
        print(f"User side: {user_side}")
        if user_side == 0:
            pyautogui.hotkey('alt', '7')
        elif user_side == 1:
            pyautogui.hotkey('alt', '6')
        MenuAutomation.press_attack_mode_sequence()