"""Object oritented programming with Pygame Zero

This module makes pygame zero act more like Scratch and OOP.
Idea: the interaction with objects should always be with methods
The idea comes from
https://www.aposteriori.com.sg/pygame-zero-helper/

This module exports the class Actor and the global objects
stage, mouse and key

TODO: class for mouse
"""

__version__ = "0.1"

import math
import pygame
import pgzero
from pgzero.actor import Actor, POS_TOPLEFT, ANCHOR_CENTER, transform_anchor
from pgzero import game, loaders
from pygame import mouse
from pgzero.keyboard import keyboard
import sys
import time

""" Monkey Patch the mouse object

The mouse object now got some getter and setter methods
"""

def hide_mouse():
    pygame.mouse.set_visible(False)
mouse.hide = hide_mouse

def show_mouse():
    pygame.mouse.set_visible(True)
mouse.show = show_mouse

def mouse_x():
    x, _ = pygame.mouse.get_pos()
    return x
mouse.y_position = mouse_x

def mouse_y():
    _, y = pygame.mouse.get_pos()
    return y
mouse.y_position = mouse_y

def mouse_pos():
    return pygame.mouse.get_pos()
mouse.position = mouse_pos


class Actor(Actor):
    """Helper class for the pygame zero Actor"""

    def __init__(self, image, pos=POS_TOPLEFT, anchor=ANCHOR_CENTER, **kwargs):
        """Create an actor

        Keyword arguments:
        image   -- the image name saved in the images folder
        pos     -- the center position, default topleft at (0,0)
        anchor  -- the anchor position, default is center
        """

        #attributes for the flip_ methods
        self._flip_x = False
        self._flip_y = False

        #scale of the actor in %. 100% = 1
        self._scale = 1

        #mask for a better collide detection
        self._mask = None

        #attribute for the animate method
        self._animate_counter = 0

        super().__init__(image, pos, anchor, **kwargs)

    def position(self):
        return (self.x, self.y)

    def x_position(self):
        return self.x

    def y_position(self):
        return self.y

    def set_anchor(self, x, y):
        self.anchor = (x, y)

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width

    def get_size(self):
        return (self.width, self.height)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, angle):
        self._angle = angle
        self._transform_surf()

    def direction_to(self, actor):
        dx = actor.x - self.x
        dy = self.y - actor.y
        angle = math.degrees(math.atan2(dy, dx))
        if angle > 0:
            return angle
        return 360 + angle

    def move_towards(self, actor, dist):
        angle = math.radians(self.direction_to(actor))
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        self.x += dx
        self.y -= dy

    def point_towards(self, actor):
        self.angle = self.direction_to(actor)

    def move_forward(self, dist):
        angle = math.radians(self.angle)
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        self.x += dx
        self.y -= dy

    def move_left(self, dist):
        self.x -= dist

    def move_right(self, dist):
        self.x += dist

    def move_up(self, dist):
        self.y -= dist

    def move_down(self, dist):
        self.y += dist

    def move_back(self, dist):
        angle = math.radians(self.angle)
        dx = -dist * math.cos(angle)
        dy = -dist * math.sin(angle)
        self.x += dx
        self.y -= dy

    def turn_left(self, degree = 90):
        self.angle += degree

    def turn_right(self, degree = 90):
        self.angle -= degree

    def point_in_direction(self, angle):
        self.angle = angle

    def go_to(self, x, y = 0):
        if type(x) is tuple and len(x) == 2:
            self.pos = x
        else:
            self.pos = (x, y)

    def switch_to_image(self, image):
        self.image = image
        self._transform_surf()

    def switch_to_images(self, images):
        """Set the image of an Actor

        images  -- array of image names, saved in folder images
        """

        self.images = images
        if len(self.images) != 0:
            self.image = self.images[0]
        self._transform_surf()

    def next_image(self):
        if self.image in self.images:
            current = self.images.index(self.image)
            if current == len(self.images) - 1:
                self.image = self.images[0]
            else:
                self.image = self.images[current + 1]
        else:
            self.image = self.images[0]

    def animate(self, fps = 5):
        """Switch automaticaly through the given images.

        Must set Actor.switch_to_images() first.
        """

        now = int(time.time() * fps)
        if now != self._animate_counter:
            self._animate_counter = now
            self.next_image()

    def scale(self, percent):
        self._scale = percent
        self._transform_surf()

    def flip_x(self):
        self._flip_x = not self._flip_x
        self._transform_surf()

    def flip_y(self):
        self._flip_y = not self._flip_y
        self._transform_surf()

    def _transform_surf(self):
        """Transformation of the surface

        Set the surface to the angle, flip, anchor and scale
        """
        self._surf = self._orig_surf
        p = self.pos

        if self._scale != 1:
            size = self._orig_surf.get_size()
            self._surf = pygame.transform.scale(self._surf, (int(size[0] * self._scale), int(size[1] * self._scale)))

        self._surf = pygame.transform.flip(self._surf, self._flip_x, self._flip_y)

        self._surf = pygame.transform.rotate(self._surf, self._angle)

        self.width, self.height = self._surf.get_size()
        w, h = self._orig_surf.get_size()
        ax, ay = self._untransformed_anchor
        anchor = transform_anchor(ax, ay, w, h, self._angle)
        self._anchor = (anchor[0] * self._scale, anchor[1] * self._scale)

        self.pos = p
        self._mask = None

    def collide_with(self, target):
        """target can be a point e.g. (50, 100) or an actor

        If the target is a point,
            then use the method collide_point_pixel
            else use the method overlaps(Actor)
        """
        if type(target) is tuple and len(target) == 2:
            return self.collide_point_pixel(target) #pixel-perfect but could be slow
            #return self.collidepoint(target)       #pygame method (fast)
        else:
            return self.overlaps(target)            #pixel-perfect but could be slow
            #return self.colliderect(target)        #pygame method (fast)

    @property
    def mask(self):
        """An image mask for collision detection."""
        return pygame.mask.from_surface(self._surf)

    def overlaps(self, target):
        """Check for pixel-perfect overlap of two actors."""
        if self.colliderect(target):
            ox = round(self.topleft[0] - target.topleft[0])
            oy = round(self.topleft[1] - target.topleft[1])
            offset = (ox, oy)
            if target.mask.overlap(pygame.mask.from_surface(self._surf), offset) is not None:
                return True
        return False

    def collide_point_pixel(self, point):
        """Check for pixel-perfect oveerlap of position and actor"""
        x, y = point

        self._mask = pygame.mask.from_surface(self._surf)

        xoffset = round(x - self.left)
        yoffset = round(y - self.top)
        if xoffset < 1 or yoffset < 1:
            return False

        width, height = self._mask.get_size()
        if xoffset > width or yoffset > height:
            return False
        elif self._mask.get_at((xoffset - 1, yoffset - 1)) == 0:
            return False
        else:
            return True

    def touching_the_edge(self):
        width, height = pygame.display.get_surface().get_size()
        if self.left <= 0 or self.top <= 0 or self.right >= width or self.bottom >= height:
                return True
        else:
            return False

    def left_the_stage(self):
        width, height = pygame.display.get_surface().get_size()
        if self.right < 0 or self.bottom < 0 or self.left > width or self.top > height:
                return True
        else:
            return False

    def get_rect(self):
        return self._rect

class Key:
    """helper class to the keyboard object

    keyboard.w -> key.w_is_pressed()

    Some keys got changed. Fits the german keyboard
    """
    def __init__(self, keyboard):
        self.keyboard = keyboard

    def a_is_pressed(self):
        return self.keyboard.a

    def b_is_pressed(self):
        return self.keyboard.b

    def c_is_pressed(self):
        return self.keyboard.c

    def d_is_pressed(self):
        return self.keyboard.d

    def e_is_pressed(self):
        return self.keyboard.e

    def f_is_pressed(self):
        return self.keyboard.f

    def g_is_pressed(self):
        return self.keyboard.g

    def h_is_pressed(self):
        return self.keyboard.h

    def i_is_pressed(self):
        return self.keyboard.i

    def j_is_pressed(self):
        return self.keyboard.j

    def k_is_pressed(self):
        return self.keyboard.k

    def l_is_pressed(self):
        return self.keyboard.l

    def m_is_pressed(self):
        return self.keyboard.m

    def n_is_pressed(self):
        return self.keyboard.n

    def o_is_pressed(self):
        return self.keyboard.o

    def p_is_pressed(self):
        return self.keyboard.p

    def q_is_pressed(self):
        return self.keyboard.q

    def r_is_pressed(self):
        return self.keyboard.r

    def s_is_pressed(self):
        return self.keyboard.s

    def t_is_pressed(self):
        return self.keyboard.t

    def u_is_pressed(self):
        return self.keyboard.u

    def v_is_pressed(self):
        return self.keyboard.v

    def w_is_pressed(self):
        return self.keyboard.w

    def x_is_pressed(self):
        return self.keyboard.x

    def y_is_pressed(self):
        return self.keyboard.z

    def z_is_pressed(self):
        return self.keyboard.y

    def k_0_is_pressed(self):
        return self.keyboard.k_0

    def k_1_is_pressed(self):
        return self.keyboard.k_1

    def k_2_is_pressed(self):
        return self.keyboard.k_2

    def k_3_is_pressed(self):
        return self.keyboard.k_3

    def k_4_is_pressed(self):
        return self.keyboard.k_4

    def k_5_is_pressed(self):
        return self.keyboard.k_5

    def k_6_is_pressed(self):
        return self.keyboard.k_6

    def k_7_is_pressed(self):
        return self.keyboard.k_7

    def k_8_is_pressed(self):
        return self.keyboard.k_8

    def k_9_is_pressed(self):
        return self.keyboard.k_9

    def kp0_is_pressed(self):
        return self.keyboard.kp0

    def kp1_is_pressed(self):
        return self.keyboard.kp1

    def kp2_is_pressed(self):
        return self.keyboard.kp2

    def kp3_is_pressed(self):
        return self.keyboard.kp3

    def kp4_is_pressed(self):
        return self.keyboard.kp4

    def kp5_is_pressed(self):
        return self.keyboard.kp5

    def kp6_is_pressed(self):
        return self.keyboard.kp6

    def kp7_is_pressed(self):
        return self.keyboard.kp7

    def kp8_is_pressed(self):
        return self.keyboard.kp8

    def kp9_is_pressed(self):
        return self.keyboard.kp9

    def up_is_pressed(self):
        return self.keyboard.up

    def down_is_pressed(self):
        return self.keyboard.down

    def right_is_pressed(self):
        return self.keyboard.right

    def left_is_pressed(self):
        return self.keyboard.left

    def backspace_is_pressed(self):
        return self.keyboard.backspace

    def space_is_pressed(self):
        return self.keyboard.space

    def hash_is_pressed(self):
        return self.keyboard.backslash

    def plus_is_pressed(self):
        return self.keyboard.plus

    def comma_is_pressed(self):
        return self.keyboard.comma

    def minus_is_pressed(self):
        return self.keyboard.slash

    def period_is_pressed(self):
        return self.keyboard.period

    def slash_is_pressed(self):
        return self.keyboard.slash

key = Key(keyboard)

class PGZA_meta(type):
    """Metaclass for the Pygame Zero Attributes

    https://stackoverflow.com/questions/128573/using-property-on-classmethods
    """
    main_mod = None

    @property
    def screen(cls):
        return cls.get_main_mod().screen

    @property
    def WIDTH(cls):
        return cls.get_main_mod().WIDTH

    @property
    def HEIGHT(cls):
        return cls.get_main_mod().HEIGHT

    @property
    def TITLE(cls):
        return cls.get_main_mod().TITLE


class PGZA(metaclass = PGZA_meta):
    """Pygame Zero Attributes

    usage: PGZA.screen

    class to get the attributes of Pygame Zero
    """

    @classmethod
    def get_main_mod(cls):
        if cls.main_mod is None:
            if getattr(sys, '_pgzrun', None):
                module_name = "pgzero.builtins"
                for key, value in sys.modules.items():
                    if value.__name__ == "pgzero.builtins" \
                            and key != "pgzero.builtins":
                        module_name = key
                        break
                cls.main_mod = sys.modules[module_name]
            else:
                cls.main_mod = sys.modules['__main__']
        return cls.main_mod

class Stage:
    """helper class for the screen object"""

    def __init__(self):
        self.is_image = False
        self.image = None
        self.color = (0, 0, 0)

    def draw(self):
        if self.is_image:
            PGZA.screen.clear()
            PGZA.screen.blit(self.image, (0,0))
        else:
            PGZA.screen.fill(self.color)

    def switch_to_image(self, image):
        self.is_image = True
        self.image = image

    def switch_to_color(self, color):
        self.is_image = False
        self.color = color

    def write_text(self, text, pos, **kwargs):
        PGZA.screen.draw.text(text, pos, **kwargs)

    def get_size(self):
        return pygame.display.get_surface().get_size()

    def height(self):
        return PGZA.HEIGHT

    def width(self):
        return PGZA.WIDTH

    def title(self):
        return PGZA.TITLE


stage = Stage()