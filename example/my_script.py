from oopz import *                      # importiere die oopz-Datei

TITLE = "Beispiel"                      # Titel, Höhe und Breite festlegen
HEIGHT = 100
WIDTH = 400

alien = Actor("alien")                  # Ein Objekt mit dem Namen alien wird erzeugt
alien.go_to(50, 50)                     # alien wird auf die Position (50,50) gesetzt

stage.switch_to_color("white")          # Wechsel zu Hintergrundfarbe white

def draw():                             # In draw() wird gezeichnet
    stage.draw()                        # zeichne die Buehne
    alien.draw()                        # zeichne den alien

def update():                           # In update() werden Objekte manipuliert
    alien.move_forward(2)               # alien geht zwei Pixel vor
    if alien.x_position() > 500:        # Wenn x vom alien größer als 500 ist,
        alien.go_to(-50, 50)            # dann setze alien auf (-50,50)

    if key.r_is_pressed():              # Wenn die Taste r gedrückt wird,
        alien.switch_to_image("alien")  # dann ändere das Bild auf "alien"

def on_mouse_down(pos):                 # Aufruf bei Maus klick
    if alien.collide_with(pos):         # Wenn alien mit der Mausposition kollidiert
        alien.switch_to_image("hurt")   # dann ändere das Bild zu "hurt"
        print("got me :( ")             # und gib Text aus
    else:                               # sonst:
        print("you missed me :P")       # gib Text aus