#!/usr/bin/python

def merge_sort(unsorted):
    sorted = []
    num_of_items = len(unsorted)
    if num_of_items <= 1:
        sorted.append(unsorted[0])
        return sorted 
    elif num_of_items == 2:
        if unsorted[1] < unsorted[0]:
            sorted.extend([unsorted[1], unsorted[0]])
            return sorted
    else:
        half_point = num_of_items/2 + 1
        half_sorted_a = merge_sort(unsorted[0:half_point])
        half_sorted_b = merge_sort(unsorted[half_point:])
        print "a: ", half_sorted_a
        print "b: ", half_sorted_b
        while len(half_sorted_a) > 0 and len(half_sorted_b) > 0:
            if half_sorted_a[0] < half_sorted_b[0]:
                sorted.append(half_sorted_a.pop(0))
            else:
                sorted.append(half_sorted_b.pop(0))
        sorted.extend(half_sorted_a + half_sorted_b)
        return sorted 

mylist = [ 5, 3, 2, 0, 9, -1, 67, 20, 90, 50, 15 ]
mysorted = merge_sort(mylist)
print mysorted


def so_merge_sort1(x):
    if len(x) < 2:return x

    result,mid = [],int(len(x)/2)

    y = merge_sort(x[:mid])
    z = merge_sort(x[mid:])

    while (len(y) > 0) and (len(z) > 0):
        if y[0] > z[0]:result.append(z.pop(0))   
        else:result.append(y.pop(0))

    result.extend(y+z)
    return result


# a more functional approach...
# def so_merge_sort2_merge(l1, l2, out=[]):
#     if l1==[]: return out+l2
#     if l2==[]: return out+l1
#     if l1[0]<l2[0]: return so_merge_sort2_merge(l1[1:], l2, out+l1[0:1])
#     return so_merge_sort2_merge(l1, l2[1:], out+l2[0:1])
# def so_merge_sort_2(l): return (lambda h: l if h<1 else so_merge_sort2_merge(so_merge_sort_2(l[:h]), so_merge_sort_2(l[h:])))(len(l)/2)
# print(so_merge_sort_2([1,4,6,3,2,5,78,4,2,1,4,6,8]))