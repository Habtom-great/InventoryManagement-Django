from num2words import num2words

def amount_in_words(amount):
    return num2words(amount, to='currency', lang='en')

def amount_in_words(amount):
    ones = [
        "", "One", "Two", "Three", "Four", "Five",
        "Six", "Seven", "Eight", "Nine", "Ten",
        "Eleven", "Twelve", "Thirteen", "Fourteen",
        "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"
    ]

    tens = [
        "", "", "Twenty", "Thirty", "Forty",
        "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"
    ]

    def words(n):
        if n < 20:
            return ones[n]
        elif n < 100:
            return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
        elif n < 1000:
            return ones[n // 100] + " Hundred" + (
                " " + words(n % 100) if n % 100 != 0 else ""
            )
        elif n < 1000000:
            return words(n // 1000) + " Thousand" + (
                " " + words(n % 1000) if n % 1000 != 0 else ""
            )
        else:
            return str(n)

    try:
        amount = int(round(amount))
        return words(amount) + " Birr Only"
    except Exception:
        return ""

# transactions/utils.py
from num2words import num2words

def amount_to_words(amount, currency='ETB'):
    words = num2words(amount, to='currency', lang='en')
    return f"{words}".title()
