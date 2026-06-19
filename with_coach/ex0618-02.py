year = int(input())

if year >= 1955 and year <= 1963 :
    print('베이비붐 세대')
elif year >= 1964 and year <= 1979 :
    print('X 세대')
elif year >= 1980 and year <= 1994 :
    print('밀레니얼 세대')
elif year >= 1995 and year <= 2010 :
    print('Z 세대')
elif year > 2010 :
    print('알파 세대')
else :
    print('연세가..?')