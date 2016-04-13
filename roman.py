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

def get_roman_digit(number, power_of_ten):
    if power_of_ten < 1: return 
    (quotient, remainder) = divmod(number, power_of_ten)

    if quotient >= 5:
        # do something including the half power_of_ten
        if quotient == 9:
            sys.stdout.write('%s%s' % (ROMAN_PREFIX[(power_of_ten*10)], ROMAN_DIGIT[(power_of_ten*10)])) 
        else:
            sys.stdout.write('%s' % ROMAN_DIGIT[(power_of_ten*5)])
            remaining = quotient - 5
            sys.stdout.write('%s' % ROMAN_DIGIT[power_of_ten] * remaining)
    else:
        if quotient == 4:
            if power_of_ten == 1000:
                sys.stdout.write('%s' % ROMAN_DIGIT[power_of_ten] * quotient)
            else:
                sys.stdout.write('%s%s' % (ROMAN_PREFIX[(power_of_ten*10)], ROMAN_DIGIT[(power_of_ten*5)] )) 
        else:
            sys.stdout.write('%s' % ROMAN_DIGIT[power_of_ten] * quotient)

    get_roman_digit(remainder, power_of_ten/10)    

def get_largest_power_of_ten(number):
    if number < 10:
        return 0
    for i in range(4,0,-1):
        if (0 < number / (10**i) < 10):
            return 10**i 

def main(argv): 
    number_to_convert = int(argv[0])
    if number_to_convert >= 5000:
        print "Can't convert number bigger than 5000 - Romans are kinda limited"
        return     
    power_of_ten = get_largest_power_of_ten(number_to_convert)
    print "power of then is {}".format(power_of_ten)
    get_roman_digit(number_to_convert, power_of_ten)
    print ""

if __name__ == "__main__":
   main(sys.argv[1:])

