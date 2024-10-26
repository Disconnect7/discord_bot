import re


token = None
users_list = []
text_channels = []


def print_asd():
    print("asd")


def get_attributes():
    return token, users_list, text_channels


def distribute_data(data_type, content):
    global token

    if data_type == "TOKEN":
        token = str(content)

    elif data_type == "USER_ID":
        try:
            users_list.append(int(content))
        except ValueError:
            print(f"USER_ID should be integer, instead of = {content}")

    elif data_type == "TEXT_CHANNEL_ID":
        try:
            text_channels.append(int(content))
        except ValueError:
            print(f"TEXT_CHANNEL_ID should be integer, instead of = {content}")


def parse_settings_file(debug=False):
    f = open("settings.txt", encoding="utf-8", mode="r")

    for line in f:

        # берём начала строк, до \n или комментария #
        s = re.split("\s*\n|\s*#", line)[0]

        # осталось много пустых строк, пропускаем их
        if len(s) == 0:
            continue

        # разделяем строки по знаку равно, получаем списки со строками
        my_list = re.split('\s*=\s*', s)

        # выкиываем пустые строки из списка
        try:
            my_list.remove("")
        except ValueError:
            # если пустой строки нет:
            pass

        # пропускаем пустые записи-заглушки "USER_ID =            "
        if len(my_list) == 1:
            continue

        if debug:
            print(my_list)

        distribute_data(data_type=my_list[0],
                        content=my_list[1])
    f.close()


if __name__ == '__main__':
    parse_settings_file(debug=True)
