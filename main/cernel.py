import csv
import os

from PIL import Image

__author__ = 'Denis'

BLACK_PIXEL = (0, 0, 0)
WHITE_PIXEL = (255, 255, 255)
FORMATS = ("JPG", "jpg", "png", "bmp")


def measure_text_area_height(pixels, width, r_position):
    """ Measures the height of the text area at the top of the image.

    :param pixels: image view
    :param width: image width
    :param r_position: r - position in pixel representation
    :return: height of the text area
    """
    text_area_height = 0
    num = text_area_height * width + 1
    while pixels[num][r_position: r_position + 3: 1] == BLACK_PIXEL:
        text_area_height += 1
        num = text_area_height * width + 1
    return text_area_height


def find_edges(pixels, r_position, text_area_height, width):
    """ Find two position for text line creation

    :param pixels: image view
    :param r_position: r - position in pixel representation
    :param text_area_height:
    :param width: image width
    :return: left edge and right edge
    """
    line_height = text_area_height // 2

    bias = line_height * width
    num = width // 2
    while pixels[bias + num][r_position: r_position + 3: 1] == BLACK_PIXEL:
        num -= 1
    left_edge = num + 30

    num = width // 2
    while pixels[bias + num][r_position: r_position + 3: 1] == BLACK_PIXEL:
        num += 1
    while sum([sum(pixels[i * width + num][r_position: r_position + 3: 1])
               for i in range(0, line_height)]) > 600:
        num += 1
    right_edge = num
    while pixels[bias + num][r_position: r_position + 3: 1] == BLACK_PIXEL:
        num += 1
    right_edge = (right_edge + num) // 2
    return left_edge, right_edge


def make_text_line(image_file, work_dir):
    """ Make tmp image with text line

    :param image_file: image file path
    :param work_dir: os.getcwd()
    """
    with Image.open(image_file) as image:
        width, height = image.size
        pixels = list(image.getdata())
        r_position = image.mode.find("RGB")
    text_zone_height = measure_text_area_height(pixels, width, r_position)
    if text_zone_height < 10:
        raise ValueError("image {} don't have top text line.".format(image_file))
    edges = find_edges(pixels, r_position, text_zone_height, width)

    length1 = edges[0]
    length2 = width - edges[1] + 1
    length = length1 + length2

    new_pixels = [(0, 0, 0)] * text_zone_height * length

    for y in range(0, text_zone_height):
        for x in range(0, length1):
            old_pixel = y * width + x
            new_pixels[y * length + x] = pixels[old_pixel]
        for x in range(length1, length1 + length2):
            old_pixel = y * width + (edges[1] + x - length1)
            new_pixels[y * length + x] = pixels[old_pixel]

    text_image = Image.new(image.mode, (length, text_zone_height))
    text_image.putdata(new_pixels)
    text_image.save(work_dir + r"\tmp.jpg")


def extract_data(text_file):
    """ Extract data from tesseract text file

    :param text_file: text file path
    :return: data list
    """
    with open(text_file, "r") as input_file:
        text = input_file.readline()
    date = text[0:text.index("M") + 1]

    temperature = text.split(" ")[-1]
    temperature = temperature[::-1]
    tmp = 0
    power = 1
    for char in temperature:
        if char.isdigit():
            tmp += int(char) * power
            power *= 10

    if "F" in temperature or "f" in temperature:
        tmp_c = round((tmp - 32) / 1.8, 2)
    else:
        tmp_c = tmp
        tmp = round((tmp_c * 1.8) + 32, 2)
    return [date, str(tmp_c).replace(".", ","),
            str(tmp).replace(".", ",")]


def collect_data(image_dir):
    """ Run process for all image in directory and extract table

    :param image_dir: image directory
    :return: result table
    """
    work_dir = os.getcwd()
    tmp_file = work_dir + r"\tmp.jpg"
    text_file = work_dir + r"\out.txt"
    all_data = []

    for image_file in os.listdir(image_dir):
        if image_file.split(".")[-1] in FORMATS:
            image_full_path = image_dir + "\\" + image_file
            try:
                make_text_line(image_full_path, work_dir)
            except ValueError as e:
                print(str(e))
                continue
            os.system("".join(["tesseract.exe ", tmp_file, " out"]))
            row = [image_file]
            row += extract_data(text_file)
            all_data.append(row)
            print(image_file)
    try:
        os.remove(tmp_file)
        os.remove(text_file)
    except FileNotFoundError:
        print("Directory with images is empty")
    return all_data


def make_table(image_dir):
    """ Run process and write result to .csv file

    :return:
    """
    table_data = collect_data(image_dir)
    while True and table_data:
        try:
            with open(image_dir + "\\result.csv", "w", newline='') as result_file:
                writer = csv.writer(result_file, delimiter=';')
                writer.writerows([["name", "date", "C", "F"]])
                writer.writerows(table_data)
                break
        except PermissionError:
            print("result.csv file in use by another application.\n"
                  "Please close it and write anything to "
                  "console to rewrite result.csv")
            input()


image_sample_dir = os.getcwd().rpartition("\\")[0]
make_table(image_sample_dir)
