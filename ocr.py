import pytesseract
import os
import sys
from PIL import Image

async def read_image(img_path, lang='eng'):
    """
    Performs OCR on a single image

    :img_path: str, path to the image file
    :lang: str, language to be used while conversion (optional, default is english)

    Returns
    :text: str, converted text from image
    """
    #return pytesseract.image_to_string(Image.open(img_path), lang=lang)
    try:
        image = Image.open(img_path)
        while True:
            osd_rotated_image = pytesseract.image_to_osd(image)

            # using regex we search for the angle(in string format) of the text
            angle_rotated_image = re.search('(?<=Rotate: )\d+', osd_rotated_image).group(0)

            if (angle_rotated_image == '0'):
                image = image
                # break the loop once we get the correctly deskewed image
                break
            elif (angle_rotated_image == '90'):
                image = rotate(image,90,(255,255,255)) # rotate(image,angle,background_color)
                continue
            elif (angle_rotated_image == '180'):
                image = rotate(image,180,(255,255,255))
                continue
            elif (angle_rotated_image == '270'):
                image = rotate(image,90,(255,255,255))
                continue
        return pytesseract.image_to_string(image, lang=lang)
    except:
        return "[ERROR] Unable to process file: {0}".format(img_path)

async def read_images_from_dir(dir_path, lang='eng', write_to_file=False):
    """
    Performs OCR on all images present in a directory

    :dir_path: str, path to the directory of images
    :lang: str, language to be used while conversion (optional, default is english)

    Returns
    :converted_text: dict, mapping of filename to converted text for each image
    """

    converted_text = {}
    for file_ in os.listdir(dir_path):
        if file_.endswith(('png', 'jpeg', 'jpg')):
            text = await read_image(os.path.join(dir_path, file_), lang=lang)
            converted_text[os.path.join(dir_path, file_)] = text
    if write_to_file:
        for file_path, text in converted_text.items():
            _write_to_file(text, os.path.splitext(file_path)[0] + ".txt")
    return converted_text

def _write_to_file(text, file_path):
    """
    Helper method to write text to a file
    """
    print("[INFO] Writing text to file: {0}".format(file_path))
    with open(file_path, 'w') as fp:
        fp.write(text)
