import random


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
