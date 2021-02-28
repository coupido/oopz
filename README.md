# OOPZ
Object oriented programming based on Pygame Zero and Mu. 

## Idea
Students know Scratch and have to learn OOP. This module makes Pygame Zero act more like [Scratch](https://scratch.mit.edu/) and OOP.

The idea comes from
https://www.aposteriori.com.sg/pygame-zero-helper/

## Example
You can find a list of all methods in the [OOPZ Cheat Sheet](OOPZ%20Cheat%20Sheet_en.docx)
```
from oopz import *

TITLE = "example"
HEIGHT = 100
WIDTH = 400

alien = Actor("alien")
alien.go_to(50, 50) 

stage.switch_to_color("white")

def draw():
    stage.draw()
    alien.draw()

def update():
    alien.move_forward(2) 
    if alien.x_position() > 500: 
        alien.go_to(-50, 50)

    if key.r_is_pressed(): 
        alien.switch_to_image("alien")

def on_mouse_down(pos):
    if alien.collide_with(pos): 
        alien.switch_to_image("hurt")
        print("got me :( ") 
    else:
        print("you missed me :P")

```

