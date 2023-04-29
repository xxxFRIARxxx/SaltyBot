from datetime import date, datetime



mylist = [None, 2, 1]
fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
newlist = [x+" test" for x in fruits if "a" in x]
now = datetime.time(datetime.now())

date_from_datetime = str(date.today())
split_date = date_from_datetime.split("-")
final_date = f"{split_date[0]}{split_date[1]}{split_date[2]}"
intdate = int(final_date)

tstring = f"{intdate +1}"
# print(tstring)
# time_from_datetime = time.isoformat()
print(datetime.date(datetime.now()))
print(datetime.now())

split_date = int(str(datetime.date(datetime.now())).replace("-",""))
split_time = int(str(datetime.time(datetime.now())).replace(":","").replace(".",""))

print(split_date, split_time)
# newlist = [expression for item in iterable if condition == True]

# if not all(mylist):
#     print("at least 1 is false")
# else:
#     print("All are true")

# if not any(mylist):
#     print("All are false")
# else:
#     print("At least 1 is true")

# print(newlist)