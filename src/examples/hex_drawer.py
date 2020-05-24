
from PIL import Image
from PIL import ImageDraw

from genme import colors
from genme import map_hex


WIDTH = 20
HEIGHT = 10


BLACK = colors.RGBA(0, 0, 0)


cell_size = map_hex.Point(20, 20)

canvas_size = map_hex.Point(WIDTH * cell_size.x * 2,
                            HEIGHT * cell_size.y * 2)

canvas = Image.new('RGBA',
                   canvas_size.xy(),
                   BLACK.ints)

x = map_hex.Cell(0, 0, 0)

layout = map_hex.Layout(orientation=map_hex.layout_flat,
                        size=cell_size,
                        origin=canvas_size / 2)


draw = ImageDraw.Draw(canvas)

for cell in x.neighbours():
    draw.polygon([point.xy() for point in map_hex.cell_corners(layout, cell)],
                 fill=colors.RGBA.random().ints)

print(map_hex.cell_corners(layout, cell))

# @dataclasses.dataclass
# class Sprite:
#     color: colors.Color = BLACK
#     image: Image = dataclasses.field(default=None, init=False, compare=False)

#     def prepair(self, size):
#         self.image = Image.new('RGBA', (size, size), self.color.ints)


            # canvas.paste(biome.sprite.image,
            #              (x * self.cell_size, y * self.cell_size))

canvas.show()
