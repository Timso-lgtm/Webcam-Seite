import pygame
import random
import sys
from pygame.locals import *

# ------------------- 1. SPIEL-LOGIK -------------------
class RockPaperScissors:
    def __init__(self):
        self.gesture_map = {
            0: {"name": "STEIN", "symbol": "✊", "beats": 2},  # Stein schlägt Schere
            1: {"name": "PAPIER", "symbol": "✋", "beats": 0},  # Papier schlägt Stein
            2: {"name": "SCHERE", "symbol": "✌️", "beats": 1}   # Schere schlägt Papier
        }
        self.results = ["DU GEWINNST! 🎉", "ROBOTER GEWINNT! 🤖", "UNENTSCHIEDEN! 🤝"]
    
    def robot_choice(self, strategy="random"):
        """Roboter wählt eine Geste"""
        return random.randint(0, 2)
    
    def determine_winner(self, human, robot):
        """Bestimme Gewinner (0=Mensch, 1=Roboter, 2=Unentschieden)"""
        if human == robot:
            return 2
        return 0 if self.gesture_map[human]["beats"] == robot else 1

# ------------------- 2. FAKE GESTURE DETECTION (für PC) -------------------
class FakeGestureDetector:
    """Simuliert die Gestenerkennung für PC-Tests"""
    def __init__(self):
        self.gestures = ["rock", "paper", "scissors", "none"]
        self.current_gesture = "none"
    
    def update_from_keyboard(self):
        """Tastatur-Steuerung für Gesten (S=Stein, P=Papier, C=Schere)"""
        keys = pygame.key.get_pressed()
        if keys[K_s]:
            self.current_gesture = "rock"
        elif keys[K_p]:
            self.current_gesture = "paper"
        elif keys[K_c]:
            self.current_gesture = "scissors"
        else:
            self.current_gesture = "none"
        return self.current_gesture
    
    def get_gesture_id(self, gesture_name):
        """Wandelt Gesten-Namen in ID um"""
        map_dict = {"rock": 0, "paper": 1, "scissors": 2, "none": -1}
        return map_dict.get(gesture_name, -1)

# ------------------- 3. VOLLSTÄNDIGE PyGame UI -------------------
class GameUI:
    def __init__(self, width=1024, height=768):
        pygame.init()
        pygame.display.set_caption("Schere-Stein-Papier vs Roboter 🤖")
        
        # Für PC: Fenstermodus statt Fullscreen
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont('Arial', 72, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 36)
        self.font_small = pygame.font.SysFont('Arial', 24)
        
        # Farbpalette
        self.colors = {
            'bg': (25, 25, 35),
            'panel': (40, 44, 52),
            'human': (65, 150, 200),    # Blau für Mensch
            'robot': (200, 100, 200),   # Lila für Roboter
            'text': (220, 220, 220),
            'highlight': (255, 215, 0),  # Gold
            'btn': (70, 130, 180)
        }
        
        # Spielzustand
        self.game_state = "waiting"  # waiting, counting, showing, result
        self.countdown_value = 3
        self.last_countdown_update = 0
        
        # Symbole zeichnen (als Surface)
        self.symbols = self.create_symbols()

    def create_symbols(self):
        """Erstellt die Symbol-Surfaces"""
        symbols = {}
        for i, data in game_logic.gesture_map.items():
            # Symbol als Text rendern
            symbol_surf = self.font_large.render(data["symbol"], True, (255, 255, 255))
            symbols[i] = symbol_surf
        return symbols

    def draw_text(self, text, position, size="medium", color=None, center=True):
        """Text zeichnen Hilfsfunktion"""
        if color is None:
            color = self.colors['text']
        
        if size == "large":
            font = self.font_large
        elif size == "small":
            font = self.font_small
        else:
            font = self.font_medium
            
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = position
        else:
            text_rect.topleft = position
        self.screen.blit(text_surface, text_rect)
        return text_rect

    def draw_button(self, text, rect, color=None):
        """Button zeichnen"""
        if color is None:
            color = self.colors['btn']
        
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=12)
        self.draw_text(text, rect.center, "medium", (255, 255, 255))
        return rect

    def draw_gesture_panel(self, gesture_id, title, position, color):
        """Zeichnet ein Panel mit einer Geste"""
        x, y = position
        panel_rect = pygame.Rect(x - 150, y - 150, 300, 350)
        
        # Panel Hintergrund
        pygame.draw.rect(self.screen, color, panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, 3, border_radius=20)
        
        # Symbol
        if gesture_id != -1:
            symbol = self.symbols[gesture_id]
            symbol_rect = symbol.get_rect(center=(x, y))
            self.screen.blit(symbol, symbol_rect)
        
        # Titel
        self.draw_text(title, (x, y + 180), "medium", (255, 255, 255))
        
        # Geste Name
        if gesture_id != -1:
            gesture_name = game_logic.gesture_map[gesture_id]["name"]
            self.draw_text(gesture_name, (x, y + 220), "small", (255, 255, 255))

    def show_waiting_screen(self, current_gesture):
        """Startbildschirm - wartet auf Geste"""
        self.screen.fill(self.colors['bg'])
        
        # Titel
        self.draw_text("SCHERE - STEIN - PAPIER", (512, 80), "large", self.colors['highlight'])
        self.draw_text("vs ROBOTER", (512, 140), "medium", (200, 200, 255))
        
        # Aktuelle Geste anzeigen (wenn erkannt)
        if current_gesture != "none":
            gesture_id = gesture_detector.get_gesture_id(current_gesture)
            self.draw_gesture_panel(gesture_id, "DEINE GESTE", (512, 350), self.colors['human'])
            
            # Start Button
            start_btn = pygame.Rect(412, 500, 200, 60)
            if self.draw_button("SPIELEN! (LEERTASTE)", start_btn):
                pass
        else:
            # Instruktionen
            self.draw_text("Drücke eine Taste für deine Geste:", (512, 300), "medium")
            self.draw_text("S = ✊ STEIN", (512, 360), "medium", (150, 200, 255))
            self.draw_text("P = ✋ PAPIER", (512, 400), "medium", (150, 200, 255))
            self.draw_text("C = ✌️ SCHERE", (512, 440), "medium", (150, 200, 255))
            self.draw_text("Dann drücke LEERTASTE zum Spielen", (512, 520), "small", (200, 200, 150))
        
        # Score Anzeige
        score_text = f"Spieler: {scores['human']} | Roboter: {scores['robot']} | Unentschieden: {scores['draw']}"
        self.draw_text(score_text, (512, 650), "small")
        
        # Debug Info
        self.draw_text(f"Erkannte Geste: {current_gesture}", (512, 700), "small", (150, 150, 150))
        self.draw_text("ESC zum Beenden", (80, 30), "small", (150, 150, 150))

    def show_countdown(self):
        """Countdown Animation"""
        self.screen.fill(self.colors['bg'])
        
        # Großer Countdown in der Mitte
        countdown_text = str(self.countdown_value) if self.countdown_value > 0 else "LOS!"
        color = (255, 100, 100) if self.countdown_value > 0 else (100, 255, 100)
        self.draw_text(countdown_text, (512, 384), "large", color)
        
        # Instruktion
        self.draw_text("Halte deine Hand bereit!", (512, 500), "medium")

    def show_results(self, human_choice, robot_choice, result):
        """Zeigt beide Entscheidungen und das Ergebnis"""
        self.screen.fill(self.colors['bg'])
        
        # Spieler Panel (links)
        self.draw_gesture_panel(human_choice, "DEINE WAHL", (300, 350), self.colors['human'])
        
        # VS in der Mitte
        self.draw_text("VS", (512, 350), "large", self.colors['highlight'])
        
        # Roboter Panel (rechts)
        self.draw_gesture_panel(robot_choice, "ROBOTER", (724, 350), self.colors['robot'])
        
        # Ergebnis Banner oben
        pygame.draw.rect(self.screen, (30, 30, 40), (262, 50, 500, 80), border_radius=15)
        result_color = (100, 255, 100) if result == 0 else (255, 100, 100) if result == 1 else (255, 255, 150)
        self.draw_text(game_logic.results[result], (512, 90), "large", result_color)
        
        # Wer schlägt wen?
        if result != 2:
            winner = "Spieler" if result == 0 else "Roboter"
            loser = "Roboter" if result == 0 else "Spieler"
            action = "schlägt"
            self.draw_text(f"{winner} {action} {loser}", (512, 150), "medium", (200, 200, 255))
        
        # Weiter Button
        continue_btn = pygame.Rect(412, 550, 200, 60)
        self.draw_button("WEITER (LEERTASTE)", continue_btn)
        
        # Score Update
        score_text = f"Spieler: {scores['human']} | Roboter: {scores['robot']} | Unentschieden: {scores['draw']}"
        self.draw_text(score_text, (512, 650), "medium")

    def update_countdown(self):
        """Aktualisiert den Countdown-Timer"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_countdown_update > 1000:  # 1 Sekunde
            self.countdown_value -= 1
            self.last_countdown_update = current_time
            if self.countdown_value <= 0:
                self.game_state = "showing"
                return True
        return False

    def handle_click(self, pos):
        """Verarbeitet Mausklicks (für Buttons)"""
        # Start Button im Wartezustand
        if self.game_state == "waiting":
            start_btn = pygame.Rect(412, 500, 200, 60)
            if start_btn.collidepoint(pos):
                self.start_game()
        
        # Continue Button im Ergebniszustand
        elif self.game_state == "result":
            continue_btn = pygame.Rect(412, 550, 200, 60)
            if continue_btn.collidepoint(pos):
                self.reset_game()

    def start_game(self):
        """Startet ein neues Spiel"""
        self.game_state = "counting"
        self.countdown_value = 3
        self.last_countdown_update = pygame.time.get_ticks()

    def reset_game(self):
        """Setzt das Spiel zurück"""
        self.game_state = "waiting"
        self.countdown_value = 3

# ------------------- 4. SPIEL-STEUERUNG -------------------
def update_scores(result, scores):
    """Aktualisiert die Punktestände"""
    if result == 0:
        scores["human"] += 1
    elif result == 1:
        scores["robot"] += 1
    else:
        scores["draw"] += 1
    return scores

# ------------------- 5. HAUPTLOOP -------------------
if __name__ == "__main__":
    # Initialisierung
    game_logic = RockPaperScissors()
    gesture_detector = FakeGestureDetector()
    ui = GameUI()
    
    # Spielzustände
    scores = {"human": 0, "robot": 0, "draw": 0}
    current_human_gesture = "none"
    stored_human_choice = -1
    robot_choice = -1
    game_result = -1
    
    # Hauptloop
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_SPACE:
                    if ui.game_state == "waiting" and current_human_gesture != "none":
                        ui.start_game()
                    elif ui.game_state == "result":
                        ui.reset_game()
                elif event.key == K_r:  # Reset Scores
                    scores = {"human": 0, "robot": 0, "draw": 0}
            elif event.type == MOUSEBUTTONDOWN:
                ui.handle_click(event.pos)
        
        # --- Tastatur-Gesten-Update ---
        current_human_gesture = gesture_detector.update_from_keyboard()
        
        # --- Spiel-Logik je nach State ---
        if ui.game_state == "waiting":
            # Speichere die aktuelle Geste für den Spielstart
            stored_human_choice = gesture_detector.get_gesture_id(current_human_gesture)
        
        elif ui.game_state == "counting":
            # Countdown laufen lassen
            if ui.update_countdown():
                # Countdown fertig -> Roboter wählt und Ergebnis berechnen
                robot_choice = game_logic.robot_choice()
                game_result = game_logic.determine_winner(stored_human_choice, robot_choice)
                scores = update_scores(game_result, scores)
                ui.game_state = "result"
        
        # --- UI Zeichnen ---
        if ui.game_state == "waiting":
            ui.show_waiting_screen(current_human_gesture)
        elif ui.game_state == "counting":
            ui.show_countdown()
        elif ui.game_state == "result":
            ui.show_results(stored_human_choice, robot_choice, game_result)
        
        # --- Update Display ---
        pygame.display.flip()
        ui.clock.tick(60)  # 60 FPS
    
    pygame.quit()
    sys.exit()