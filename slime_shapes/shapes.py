'''
sLIME shapes generates a dataset of images consisting of geometric shapes on a
background. It serves as a demonstration dataset for sLIME, for which the shapes
and colours provide clearly discerinble features.
'''
from random import randint
from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


class Shape(ABC):
    '''
    Shape is an abstract base class for creating concrete shapes. It implements
    a method for adding shapes to an existing image.
    '''
    def __init__(self, position, colour=np.zeros(3, dtype=np.uint8)):
        self._position = position
        self._colour = colour

    def add_to_image(self, target):
        '''
        Adds this shape to an existing image by recolouring its mask on the target image.
        '''
        target[self._mask(target.shape, (self._position.x_position, self._position.y_position))] = self._colour

    @abstractmethod
    def _mask(self, shape, location):
        '''
        A binary array corresponding to the pixel mask of this shape.
        '''


class Square(Shape):
    '''
    A square.
    '''
    def __init__(self, position, **kwargs):
        super().__init__(position, **kwargs)

    def create_canvas(self):
        '''
        Creates a base image (ie. a coloured square) onto which shapes can be added.
        '''
        canvas = np.zeros((self._position.size, self._position.size, 3), dtype=np.uint8)
        canvas[:, :] = self._colour
        return canvas

    def _mask(self, shape, location):
        base = np.zeros(shape[:2], dtype=bool)
        base[location[0]:location[0]+self._position.size,
             location[1]:location[1]+self._position.size] = True
        return base


class Circle(Shape):
    '''
    A circle.
    '''
    def __init__(self, position, **kwargs):
        super().__init__(position, **kwargs)

    def _mask(self, shape, location):
        radius = self._position.size / 2
        x_x, y_y = np.mgrid[:shape[0], :shape[1]]
        circle = (x_x - (location[0] + radius)) ** 2 + \
            (y_y - (location[1] + radius))**2
        return circle < radius**2


@dataclass
class Position:
    '''
    Position describes the position of a shape in an image.
    '''
    size: int
    x_position: int
    y_position: int

    def intersects(self, other):
        '''
        Returns true if the bounding boxes for the positions intersect.
        '''
        x_intersects = self._1d_intersect(self.x_position, self.size, other.x_position, other.size)
        y_intersects = self._1d_intersect(self.y_position, self.size, other.y_position, other.size)
        return x_intersects and y_intersects

    @staticmethod
    def _1d_intersect(x_1, size_1, x_2, size_2):
        return (x_1 <= x_2 <= x_1 + size_1) or (x_1 <= x_2 + size_2 <= x_1 + size_2)


def get_positions(canvas_size, count):
    '''
    Builds a list of positions for placing shapes onto a canvas. The first
    position is for the canvas, which overlaps with all the other shapes; the
    remaining positions' bounding-boxes do not mutually overlap, but are
    otherwise randomly place. The size of the positions is between 10% and 25%
    of the canvas size to ensure they are visible and multiple fit onto the
    canvas.

    The positions are found by attempting random placement and checking for overlap. This is not efficient for large numbers of shapes, and will result in an infinite loop when no position can be found.
    '''
    positions = [Position(canvas_size, 0, 0)]

    def random_position():
        shape_size = randint(canvas_size/10, canvas_size/4)
        x_position = randint(0, canvas_size - shape_size)
        y_position = randint(0, canvas_size - shape_size)
        return Position(shape_size, x_position, y_position)

    def add():
        while True:
            new_position = random_position()
            intersects = False
            for existing_position in positions[1:]:
                if new_position.intersects(existing_position):
                    intersects = True
            if not intersects:
                positions.append(new_position)
                return

    for _ in range(count):
        add()

    return positions


ORANGE = (255, 166, 0)
PURPLE = (88, 80, 141)
SALMON = (255, 99, 97)
PINK = (188, 87, 144)
BLUE = (0, 66, 92)
