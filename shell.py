import basic

while True:
    text = input('basic > ')
    if text == "exit":
        exit()
    result, error = basic.run('<stdin>', text)

    if error: print(error.as_string())
    else: print(result)
