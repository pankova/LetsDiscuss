def get_element(arr, index):
    if index >= 0 and index < len(arr):
        return arr[index]
    else:
        return None
    

def get_subscript(dict, subscript):
    if dict is not None:
        return dict.get(subscript, None)
    else:
        return None