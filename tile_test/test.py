from PIL import Image

img = Image.open("image/tourne.png").resize((128,128))

for angle in [0, 90, 180, 270]:
    rotated = img.rotate(-angle)
    rotated.save(f"test_T_{angle}.png")
