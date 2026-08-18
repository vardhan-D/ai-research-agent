from media.tools import generate_image


prompt = """
A futuristic city at dusk with humanoid robots
working alongside people, advanced skyscrapers,
cinematic documentary photography, dramatic lighting,
high detail, realistic, wide 16:9 composition,
no text, no watermark
"""


image_path = generate_image(

    prompt=prompt,

    scene_number=1

)


print(
    f"\nGenerated image: "
    f"{image_path}"
)