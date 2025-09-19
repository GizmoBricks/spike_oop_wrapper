"""Constants for the oop module"""

class Port:
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    F = 5

    __dict = {A: "Port.A",
              B: "Port.B",
              C: "Port.C",
              D: "Port.D",
              E: "Port.E",
              F: "Port.F"}


class Direction:
    CLOCKWISE = 0
    COUNTERCLOCKWISE = 1
    SHORTEST_PATH = 2
    LONGEST_PATH = 3

    __dict = {CLOCKWISE: "CLOCKWISE",
              COUNTERCLOCKWISE: "COUNTERCLOCKWISE",
              SHORTEST_PATH: "SHORTEST_PATH",
              LONGEST_PATH: "LONGEST_PATH"}


class Stop:
    CONTINUE = 0
    COAST = 1
    BRAKE = 2
    HOLD = 3
    SMART_COAST = 4
    SMART_BRAKE = 5

    __dict = {CONTINUE: "CONTINUE",
              COAST: "COAST",
              BRAKE: "BRAKE",
              HOLD: "HOLD",
              SMART_COAST: "SMART_COAST",
              SMART_BRAKE: "SMART_BRAKE"}
    

class Color:
    NONE = -1
    BLACK = 0
    MAGENTA = 1
    PURPLE = 2
    BLUE = 3
    AZURE = 4
    TURQUOISE = 5
    GREEN = 6
    YELLOW = 7
    ORANGE = 8
    RED = 9
    WHITE = 10
    
    __dict = {NONE: "NONE",
              BLACK: "BLACK",
              MAGENTA: "MAGENTA",
              PURPLE: "PURPLE",
              BLUE: "BLUE",
              AZURE: "AZURE",
              TURQUOISE: "TURQUOISE",
              GREEN: "GREEN",
              YELLOW: "YELLOW",
              ORANGE: "ORANGE",
              RED: "RED",
              WHITE: "WHITE"}


class Orientation:
    """
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    """
    TOP = 0
    FRONT = 1
    RIGHT = 2
    BOTTOM = 3
    BACK = 4
    LEFT = 5
    """
    __dict = {UP: "UP",
              RIGHT: "RIGHT",
              DOWN: "DOWN",
              LEFT: "LEFT"}
    """
    

class Buttons:
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    BT = 3
    
    __dict = {LEFT: "LEFT",
              CENTER: "CENTER",
              RIGHT: "RIGHT",
              BT: "BT"}
    
class Icon:
    HEART = 1
    HEART_SMALL = 2
    HAPPY = 3
    SMILE = 4
    SAD = 5
    CONFUSED = 6
    ANGRY = 7
    ASLEEP = 8
    SURPRISED = 9
    SILLY = 10
    FABULOUS = 11
    MEH = 12
    YES = 13
    NO = 14
    CLOCK12 = 15
    CLOCK1 = 16
    CLOCK2 = 17
    CLOCK3 = 18
    CLOCK4 = 19
    CLOCK5 = 20
    CLOCK6 = 21
    CLOCK7 = 22
    CLOCK8 = 23
    CLOCK9 = 24
    CLOCK10 = 25
    CLOCK11 = 26
    ARROW_N = 27
    ARROW_NE = 28
    ARROW_E = 29
    ARROW_SE = 30
    ARROW_S = 31
    ARROW_SW = 32
    ARROW_W = 33
    ARROW_NW = 34
    GO_RIGHT = 35
    GO_LEFT = 36
    GO_UP = 37
    GO_DOWN = 38
    TRIANGLE = 39
    TRIANGLE_LEFT = 40
    CHESSBOARD = 41
    DIAMOND = 42
    DIAMOND_SMALL = 43
    SQUARE = 44
    SQUARE_SMALL = 45
    RABBIT = 46
    COW = 47
    MUSIC_CROTCHET = 48
    MUSIC_QUAVER = 49
    MUSIC_QUAVERS = 50
    PITCHFORK = 51
    XMAS = 52
    PACMAN = 53
    TARGET = 54
    TSHIRT = 55
    ROLLERSKATE = 56
    DUCK = 57
    HOUSE = 58
    TORTOISE = 59
    BUTTERFLY = 60
    STICKFIGURE = 61
    GHOST = 62
    SWORD = 63
    GIRAFFE = 64
    SKULL = 65
    UMBRELLA = 66
    SNAKE = 67
 
class Gesture:
    UNKNOWN = -1
    TAPPED = 0
    DOUBLE_TAPPED = 1
    SHAKEN = 2
    FALLING = 3
    
    __dict = {UNKNOWN: "UNKNOWN",
              TAPPED: "TAPPED",
              DOUBLE_TAPPED: "DOUBLE_TAPPED",
              SHAKEN: "SHAKEN",
              FALLING: "FALLING"}
    

    
if __name__ == "__main__":
    pass

