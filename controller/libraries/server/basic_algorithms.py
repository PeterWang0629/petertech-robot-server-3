import time, json
import controller.libraries.server.configure as configure


def dict_cmp(a: dict | str, b: dict | str) -> bool:
    if isinstance(a, str): a = json.loads(a)
    if b is str: b = json.loads(b)
    if a == b: return True

    for i in a:
        if i not in b:
            return False
        if type(a[i]) is not type(b[i]):
            return False
        if type(a) is dict:
            if type(b) is dict:
                if not dict_cmp(a[i], b[i]):
                    return False
            else:
                return False
    return True


def time_stamp_to_str(timestamp: str | int) -> str:
    time_stamp = int(timestamp)
    time_array = time.localtime(time_stamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", time_array)


def save_data(fileio, data):
    data_path = configure.get_config("data_path")
    fileio.write(data_path, json.dumps(data))


def read_data(fileio):
    data_path = configure.get_config("data_path")
    return json.loads(fileio.read(data_path))


def get_init_data():
    return {"ref": {}, "ban": [], "gpt": {"key": "", "history": [], "conversation": {}, "draw": {}}, "users": {},
            "error": {}, "guijiao": {"history": []}, "config": {}, "timer": {}, "online": {}}


def reset_data(fileio):
    # global init_dat
    init_dat = get_init_data()
    save_data(fileio, init_dat)
    return init_dat


def md_startswith_title(markdown):
    fst_line = markdown.split("\n")[0]
    while fst_line.startswith("#"):
        fst_line = fst_line[1:]
    if fst_line[0] == " ":
        return True
    else:
        return False


def md_endswith_title(markdown):
    lst_line = markdown.split("\n")[-1]
    while lst_line.startswith("#"):
        lst_line = lst_line[1:]
    if lst_line[0] == " ":
        return True
    else:
        return False
