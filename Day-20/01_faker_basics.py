"""Task 1: Faker library basics (run: python 01_faker_basics.py)"""
from faker import Faker

fake = Faker()
Faker.seed(1)

print("--- Basic providers ---")
print(fake.name(), "|", fake.email(), "|", fake.phone_number())
print(fake.address().replace("\n", ", "))

print("\n--- Dates and numbers ---")
print(fake.date_between(start_date="-2y", end_date="today"))
print(fake.date_time_this_year())
print(fake.random_int(min=1, max=100), fake.pyfloat(left_digits=3, right_digits=2, positive=True))

print("\n--- Company and internet ---")
print(fake.company(), "|", fake.job(), "|", fake.catch_phrase())
print(fake.url(), "|", fake.ipv4(), "|", fake.user_name())

print("\n--- Localization ---")
for locale in ["en_IN", "en_US", "de_DE", "fr_FR", "ja_JP"]:
    f = Faker(locale)
    print(locale, "->", f.name(), "|", f.city())
