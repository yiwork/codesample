#!/usr/local/bin/python

import sys 

ROMAN_PREFIX = { 
    10000: 'M',
    5000: 'M',
    1000: 'C',
    500: 'C', 
    100: 'X', 
    50: 'X', 
    10: 'I', 
    5: 'I',
    1: 'I',
}

ROMAN_DIGIT = {
    10000: '??',
    5000: '?',
    1000: 'M', 
    500: 'D', 
    100: 'C', 
    50: 'L', 
    10: 'X', 
    5: 'V',
    1: 'I',
}

def get_roman_digit(number, base):
    if base < 1: return 
    (quotient, remainder) = divmod(number, base)

    if quotient >= 5:
        # do something including the half base
        if quotient == 9:
            sys.stdout.write('%s%s' % (ROMAN_PREFIX[(base*10)], ROMAN_DIGIT[(base*10)])) 
        else:
            sys.stdout.write('%s' % ROMAN_DIGIT[(base*5)])
            remaining = quotient - 5
            sys.stdout.write('%s' % ROMAN_DIGIT[base] * remaining)
    else:
        if quotient == 4:
            if base == 1000:
                sys.stdout.write('%s' % ROMAN_DIGIT[base] * quotient)
            else:
                sys.stdout.write('%s%s' % (ROMAN_PREFIX[(base*10)], ROMAN_DIGIT[(base*5)] )) 
        else:
            sys.stdout.write('%s' % ROMAN_DIGIT[base] * quotient)

    get_ROMAN_DIGIT(remainder, base/10)    

def get_largest_base(number):
    for i in range(4,0,-1):
        if (0 < number / (10**i) < 10):
            return 10**i 

def main(argv): 
    number_to_convert = int(argv[0])
    if number_to_convert >= 5000:
        print "Can't convert number bigger than 5000 - Romans are kinda limited"
        return     
    base = get_largest_base(number_to_convert)
    get_ROMAN_DIGIT(number_to_convert, base)
    print ""

if __name__ == "__main__":
   main(sys.argv[1:])

