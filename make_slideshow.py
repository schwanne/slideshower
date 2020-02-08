import argparse
import base64
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape
import csv


def base64image(file_name):
    img = Path(file_name)
    with img.open("rb") as fin:
        img_data = fin.read()

    img_data_base_64 = base64.b64encode(img_data)

    return f"data:image/{img.suffix};base64,{img_data_base_64.decode('utf-8')}"


def make_slides(
    out_file_name="out.html",
    ext_to_find=None,
    caption_file=None,
    template_file="template.html.j2",
    embed=True,
):
    # find all images
    image_exts = [ext_to_find] if ext_to_find is not None else ["png", "jpg", "gif"]

    images = []
    for image_ext in image_exts:
        images.extend(Path.cwd().glob(f"*.{image_ext}"))

    # Process captions
    if caption_file is not None:
        with open(caption_file) as cf:
            captions = [line[0] for line in csv.reader(cf)]
        if len(captions) != len(images):
            print(f"Captions file wrong length: {len(captions)} vs. {len(images)}")
            return
    else:
        captions = ["" for image in images]

    # extract the filenames and create a dictionary
    slides = [
        {
            "number": n + 1,
            "filename": base64image(file.name) if embed else file.name,
            "caption": caption,
        }
        for (n, file), caption in zip(enumerate(sorted(images)), captions)
    ]
    total_slides = len(slides)

    # Process template
    env = Environment(
        loader=PackageLoader("make_slideshow"), autoescape=select_autoescape(["html"])
    )
    template = env.get_template(template_file)

    out_html = template.render(images=slides, total_slides=total_slides)

    with open(out_file_name, "w") as out_file:
        out_file.write(out_html)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Make a web slideshow from a group of images"
    )
    parser.add_argument("--out_file", type=str, help="File to generate", default='out.html')
    parser.add_argument("--embed_images", action="store_true")
    parser.add_argument(
        "--template_file", type=str, help="name of file to use as a template", default='template.html.j2',
    )
    parser.add_argument(
        "--caption_file",
        type=str,
        help="file that contains captions (New line for each slide)",
    )

    parser.add_argument(
        "--ext",
        dest="ext",
        type=str,
        help="extension of images.  default is gif, png, and jpg",
    )
    args = parser.parse_args()
    
    make_slides(out_file_name=args.out_file,
        ext_to_find=args.ext,
        caption_file=args.caption_file,
        template_file=args.template_file,
        embed=args.embed_images,)
