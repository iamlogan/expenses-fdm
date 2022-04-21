import random
import os
import math
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files import File


# Generates a random and unique reference string for any model Class with a field called 'reference'
def get_unique_reference(class_obj, prefix):
    length = class_obj._meta.get_field('reference').max_length - 1
    minimum_value = int("1" + (length - 1) * "0")
    maximum_value = int("9" * length)
    first_ref_num = random.randint(minimum_value, maximum_value)
    if not class_obj.objects.filter(reference = prefix + str(first_ref_num)).exists():
        return prefix + str(first_ref_num)
    ref_num = first_ref_num
    ref_num += 1
    while class_obj.objects.filter(reference = prefix + str(ref_num)).exists():
        ref_num += 1
        if ref_num > maximum_value:
            ref_num = minimum_value
        if ref_num == first_ref_num:
            raise Exception("AllPossibleReferencesAlreadyAssigned")
    return prefix + str(ref_num)


# Handles file uploads
def handle_uploaded_file(file, receipt):
    new_file_name = "{}_{}".format(receipt.reference, os.path.splitext(file.name)[0]+".jpeg")
    image = Image.open(file)
    width = image.size[0]
    height = image.size[1]
    pixel_count = width * height
    target_pixel_count = 500000
    if pixel_count > target_pixel_count:
        resize_ratio = math.sqrt(target_pixel_count / pixel_count)
        new_dimensions = (round(width * resize_ratio), round(height * resize_ratio))
        new_image = image.resize(new_dimensions, Image.ANTIALIAS)
        new_image = ImageOps.exif_transpose(new_image)
    else:
        new_image = ImageOps.exif_transpose(image)
    blob = BytesIO()
    new_image.save(blob, "JPEG", quality=95)
    receipt.file.save(new_file_name, File(blob))

