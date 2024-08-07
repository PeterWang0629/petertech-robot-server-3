import uuid

from library.features.chat_parse import parse_packet
from library.minecraft.networking.packets import ChatMessagePacket, ChatPacket, Packet, JoinGamePacket
from library.minecraft.networking.packets.clientbound.play import PlayerListHeaderAndFooterPacket
from library.minecraft.networking.connection import Connection
from library.server.basic_algorithms import *
from library.server.cmd_process import ConsoleCommands
from library.server.fileio import FileIO
from library.server.logger import Logger
from library.features.dingtalk import *
from datetime import datetime
import datetime
import os
import subprocess
import threading
import psutil
import time


class RobotCommandFuncs:
    def __init__(self, req_data: dict, data: dict, fileio: FileIO, logger: Logger):
        self.text_info = req_data['text']['content'].strip()
        self.webhook_url = req_data['sessionWebhook']
        self.senderid = req_data['senderId']
        self.sendernick = req_data["senderNick"]
        self.fileio = fileio
        self.logger = logger
        self.dat = data

    def modify_config(self, Key, Value):
        self.dat["config"][Key] = Value
        save_data(self.fileio, self.dat)
        send_md_msg(self.senderid, "[Robot Message]", "Operation success.", self.webhook_url)

    def add_ref(self, Ref_Type, Ref_Key, Ref_Msg):
        if Ref_Type == "md":
            tmp = {"type": "md", "answer": Ref_Msg.replace("\\n", "\n")}
            self.dat["ref"][Ref_Key] = tmp
            save_data(self.fileio, self.dat)
            send_md_msg(self.senderid, "[Robot Message]", "Operation success.", self.webhook_url)
        elif Ref_Type == "txt":
            tmp = {"type": "txt", "answer": Ref_Msg.replace("\\n", "\n")}
            self.dat["ref"][Ref_Key] = tmp
            save_data(self.fileio, self.dat)
            send_md_msg(self.senderid, "[Robot Message]", "Operation success.", self.webhook_url)
        else:
            pass

    def del_ref(self, Ref_Key):
        if Ref_Key in self.dat["ref"]:
            self.dat["ref"].pop(Ref_Key)
            save_data(self.fileio, self.dat)
            send_md_msg(self.senderid, "[Robot Message]", "Operation success.", self.webhook_url)
        else:
            send_md_msg(self.senderid, "[Robot Message]", "Non-existent autoresponders.", self.webhook_url)

    def list_ref(self):
        if self.dat["ref"] == {}:
            send_md_msg(self.senderid, "[Data]", "**No existing autoresponders.**", self.webhook_url)
            return
        msg = "**All autoresponders:**<br>"
        flag = 0
        for Ref_Key in self.dat["ref"]:
            msg += "**" + self.dat["ref"][Ref_Key]["type"] + "** " + Ref_Key + ":"
            if md_startswith_title(self.dat["ref"][Ref_Key]["answer"]):
                msg += "\n"
            else:
                msg += "<br>"
            msg += self.dat["ref"][Ref_Key]["answer"]
            if md_endswith_title(self.dat["ref"][Ref_Key]["answer"]):
                msg += "\n<br>"
                flag = True
            else:
                msg += "<br><br>"
                flag = False
        if flag:
            send_md_msg(self.senderid, "[Data]", msg[:-3], self.webhook_url)
        else:
            send_md_msg(self.senderid, "[Data]", msg[:-4], self.webhook_url)

    def ban_user(self, Ban_User):
        if not Ban_User in self.dat["ban"]:
            if Ban_User != self.sendernick and Ban_User != self.senderid:

                self.dat["ban"].append(Ban_User)
                save_data(self.fileio, self.dat)
                send_md_msg(self.senderid, "[Robot Message]", "Successfully banned " + Ban_User, self.webhook_url)

            else:
                send_md_msg(self.senderid, "[Robot Message]", "You cannot ban yourself.", self.webhook_url)

    def pardon_user(self, Pardon_User):
        if Pardon_User in self.dat["ban"]:
            self.dat["ban"].remove(Pardon_User)
            save_data(self.fileio, self.dat)
            send_md_msg(self.senderid, "[Robot Message]", "Successfully unbanned " + Pardon_User, self.webhook_url)

        else:
            send_text_msg(self.senderid, 'This user is not banned.', self.webhook_url)

    def ban_list(self):
        send_md_msg(self.senderid, "[Data]", "**封禁列表:**<br>" + str(self.dat["ban"]), self.webhook_url)

    def set_key(self, GPT_Key):
        self.dat["gpt"]["key"] = GPT_Key
        save_data(self.fileio, self.dat)
        send_md_msg(self.senderid, "[Robot Message]", "Operation success.", self.webhook_url)

    def server_status(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        zj = float(mem.total) / 1024 / 1024 / 1024
        ysy = float(mem.used) / 1024 / 1024 / 1024

        text = "CPU Usage:" + str(cpu * 10) + "%\nRAM: Used " + str(ysy)[:4] + "GB/" + str(zj)[
                                                                                       :4] + "GB\nRAM Usage:" + str(
            int(ysy / zj * 100)) + "%"
        send_text_msg(self.senderid, text, self.webhook_url)

    def server_full_status(self):
        mem = psutil.virtual_memory()
        send_text_msg(self.senderid,
                      "RAM used" + str(float(mem.used)) + " KB,\n Total RAM " + str(
                          float(mem.total)) + " KB", self.webhook_url)

    def os_cmd(self, Os_Cmd):
        os.system(Os_Cmd)
        send_md_msg(self.senderid, "[Robot Message]", "Operation success.", self.webhook_url)

    def python_code(self, Py_Code):
        exec(Py_Code)
        send_md_msg(self.senderid, "[Robot Message]", "Operation success.", self.webhook_url)

    def say_text(self, Msg):
        send_text_msg(self.senderid, Msg, self.webhook_url)

    def say_md(self, Msg):
        send_md_msg(self.senderid, "[DEBUG Message]", Msg, self.webhook_url)

    def raise_error(self, Err_Msg):
        raise Exception(Err_Msg)

    def say_text_in(self, Msg, Webhook_Url):
        send_text_msg(self.senderid, Msg, Webhook_Url)
        send_md_msg(self.senderid, "[Robot Message]", "Operation success.", self.webhook_url)

    def say_md_in(self, Msg, Webhook_Url):
        send_md_msg(self.senderid, "[Message]", Msg, Webhook_Url)
        send_md_msg(self.senderid, "[Robot Message]", "Operation success.", self.webhook_url)

    def reset_data(self):
        self.dat = reset_data(self.fileio)
        save_data(self.fileio, self.dat)
        send_md_msg(self.senderid, "[Robot Message]", "Operation success.", self.webhook_url)

    def show_data(self):
        send_md_msg(self.senderid, "[Data]", "**存储的数据:**<br>" + str(self.dat), self.webhook_url)

    def set_data(self, Data):
        self.dat = json.loads(Data)
        save_data(self.fileio, self.dat)
        send_md_msg(self.senderid, "[Robot Message]", "Operation success.", self.webhook_url)

    def set_timer(self, Name, Time):
        if not type(self.dat["timer"]) == dict or "name" in self.dat["timer"] or "time" in self.dat["timer"]:
            self.dat["timer"] = {}
            send_md_msg(self.senderid, "[Data]",
                        f"**Warning**<br>Old data format!",
                        self.webhook_url)
        self.dat["timer"][Name] = Time
        save_data(self.fileio, self.dat)
        send_md_msg(self.senderid, "[Timer Message]",
                    f"**Operation Success**<br>Set countdown {Name} target to {Time}",
                    self.webhook_url)

    def get_timer(self, Name):
        if Name not in self.dat["timer"]:
            send_md_msg(self.senderid, "[Timer Message]",
                        f"**Unknown countdown {Name}**",
                        self.webhook_url)
            return
        start = datetime.now()
        end = self.dat["timer"][Name]
        # Name = self.dat["timer"]["name"]
        start_datetime = start
        end_datetime = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        delta = end_datetime - start_datetime
        date_time = datetime(1, 1, 1) + delta

        years = date_time.year - 1
        months = date_time.month - 1
        days = date_time.day - 1
        hours = date_time.hour
        minutes = date_time.minute
        seconds = date_time.second

        result = f"{years} Years {months} Months {days} Days {hours} Hours {minutes} Minutes {seconds} Seconds"
        send_md_msg(self.senderid, "[Timer Message]",
                    f"**Countdown {Name} Remaining Time**<br>{result}",
                    self.webhook_url)

    def execute_server_console_command(self, Cmd_Dict, Cmd):
        cc = ConsoleCommands(self.fileio, self.logger, True)  # Skip
        cc.cmd = json.loads(Cmd_Dict)
        res = cc.execute_command(Cmd).replace('\n', '<br>')
        send_md_msg(self.senderid, "[CMD Message]",
                    f"**Result**<br>{res}",
                    self.webhook_url)

    def add_online_check(self, Name, Ip_Address):
        self.dat["online"][Name] = {"ip": Ip_Address, "status": "offline", "time": time.time()}
        save_data(self.fileio, self.dat)
        send_md_msg(self.senderid, "[Device Status]",
                    f"**Creation Operation Success**<br>Name: {Name}<br>IP: {Ip_Address}",
                    self.webhook_url)

    def remove_online_check(self, Name):
        if Name in self.dat["online"]:
            self.dat["online"].pop(Name)
            send_md_msg(self.senderid, "[Device Status]",
                        f"**Deletion Operation Success**<br>Name: {Name}",
                        self.webhook_url)
            save_data(self.fileio, self.dat)
        else:
            send_md_msg(self.senderid, "[Device Status]",
                        f"**Non-existent device {Name}",
                        self.webhook_url)

    def query_online_check(self, Name):
        if Name in self.dat["online"]:
            send_md_msg(self.senderid, "[Device Status]",
                        f"**Device Status**<br>Name: {Name}<br>IP: {self.dat['online'][Name]['ip']}<br>Status: {self.dat['online'][Name]['status']}<br>Latest status change: {time_stamp_to_str(self.dat['online'][Name]['time'])}",
                        self.webhook_url)
        else:
            send_md_msg(self.senderid, "[Device Status]",
                        f"**Non-existent device {Name}",
                        self.webhook_url)

    def online_check_task(self):
        webhook = ("https://oapi.dingtalk.com/robot/send?access_token"
                   "=b2b15239cd2204824b594c2b2c5bed7a5f3fe04e5df9461108ea420e03b884b3")
        while True:
            try:
                for device in self.dat["online"]:
                    result = subprocess.run(['ping', '-n', '1', "-w", "2000", self.dat["online"][device]["ip"]],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            text=True)
                    if "TTL=" in result.stdout:
                        current_status = "Online"
                    else:
                        current_status = "Offline"
                    if current_status != self.dat["online"][device]["status"]:
                        self.dat["online"][device]["status"] = current_status
                        self.dat["online"][device]["time"] = time.time()
                        save_data(self.fileio, self.dat)
                time.sleep(3)
            except:
                continue

    def start_online_check(self):
        task = threading.Thread(target=self.online_check_task)
        task.start()
        send_md_msg(self.senderid, "[Device Status]",
                    f"**Task started**<br>Do not start the task again!",
                    self.webhook_url)

    def bomb(self, Times, Msg):
        if Msg == "":
            Msg = "[Brainstorming]" * 20 + "[Lovely]" * 20
        Times = int(Times)
        for i in range(Times):
            send_md_msg(self.senderid, "[Bomb]",
                        Msg.replace("[UUID]", uuid.uuid4().hex),
                        self.webhook_url)

    def query_minecraft_server_status(self, Print_Chat):
        send_md_msg(self.senderid, "[Robot Message]",
                    f"Please wait, querying...",
                    self.webhook_url)
        ts1 = time.time()
        username = "statbot1"
        login_password = "Bot123456#"
        domain = query_srv_record("3c3u.org")
        address, port = domain[0], domain[1]

        def extract_player_count(string):
            match = re.search(r'\b(\d+)\s*\+\s*(\d+)\b', string)
            if match:
                return (int(match.group(1)), int(match.group(2)))
            else:
                return None

        def extract_queue_length(string):
            if "队列中" in string and "前面" in string:
                numbers = re.findall(r'\d+', string)
                if len(numbers) == 2:
                    return tuple(map(int, numbers))
            return None

        class PacketHandler(object):
            def __init__(self, login_password):
                self.joined_game = False
                self.queue_length = None
                self.player_count = None
                self.logged_in = False
                self.login_password = login_password
                self.chat = ""

            def handle_incoming(self, packet=None):
                return

            def handle_outgoing(self, packet=None):
                return

            def handle_join_game(self, join_game_packet):
                self.joined_game = True

                packet = ChatPacket()
                packet.message = f"/login {self.login_password}"
                connection.write_packet(packet)
                self.logged_in = True

            def handle_chat(self, chat_packet: ChatMessagePacket):
                try:
                    # print(parse_packet(chat_packet.json_data, {}, "text"))

                    self.chat += parse_packet(chat_packet.json_data, {}, "markdown") + "<br>"
                    if not self.queue_length and self.logged_in and self.joined_game:
                        self.queue_length = extract_queue_length(
                            parse_packet(chat_packet.json_data, {}, "text"))
                except Exception as e:
                    return

            def handle_player_list_header_and_footer(self, packet: PlayerListHeaderAndFooterPacket):
                txt = parse_packet(packet.header, {}, "text")
                for line in txt.split("\n"):
                    if self.player_count or not self.logged_in or not self.joined_game:
                        break
                    self.player_count = extract_player_count(line)

        connection = Connection(address, port, username=username)
        handler = PacketHandler(login_password)
        connection.register_packet_listener(handler.handle_incoming, Packet, early=True)
        connection.register_packet_listener(handler.handle_outgoing, Packet, outgoing=True)
        connection.register_packet_listener(handler.handle_join_game, JoinGamePacket)
        connection.register_packet_listener(handler.handle_chat, ChatMessagePacket)
        connection.register_packet_listener(handler.handle_player_list_header_and_footer,
                                            PlayerListHeaderAndFooterPacket)
        connection.connect()
        while not handler.queue_length or not handler.player_count:
            pass
        connection.disconnect()
        ts2 = time.time()
        # print(handler.player_count, handler.queue_length)
        if Print_Chat in ['y', 'yes', '1']:
            send_md_msg(self.senderid, "[Chat Log]", handler.chat, self.webhook_url)
        send_md_msg(self.senderid, "[Robot Message]",
                    f"**Minecraft Server Status**<br>**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}<br>**DNS Record:** {address}:{port}<br>**Player Count:** {handler.player_count[0]}+{handler.player_count[1]}<br>**Queue Length:** {handler.queue_length[0] - 1}<br>*Query completed in {round(ts2 - ts1, 2)} sec*",
                    self.webhook_url)


class RobotCommands:
    def __init__(self, req_data: dict, fileio: FileIO, logger: Logger):
        self.req_data = req_data
        self.text_info = req_data['text']['content'].strip()
        self.webhook_url = req_data['sessionWebhook']
        self.senderid = req_data['senderId']
        self.sendernick = req_data["senderNick"]
        self.fileio = fileio
        self.logger = logger
        self.dat = {}
        self.cmd = {}

    def read_file(self):
        init_dat = get_init_data()
        try:
            self.dat = read_data(self.fileio)
        except:
            self.dat = reset_data(self.fileio)
            send_md_msg(self.senderid, "[Error Message]",
                        "**Data Error**<br>Failed while reading data file.<br>Recreated data file.<br>Time:" + datetime.now().strftime(
                            "%c"), self.webhook_url)
            return
        if not dict_cmp(init_dat, self.dat):
            self.dat = reset_data(self.fileio)
            send_md_msg(self.senderid, "[Error Message]",
                        "**Data Error**<br>Failed while reading data file.<br>Recreated data file.<br>Time:" + datetime.now().strftime(
                            "%c"), self.webhook_url)
            return

        try:
            with open("data/cmd.json", 'r') as f:
                self.cmd = json.load(f)
        except Exception as e:
            send_md_msg(self.senderid, "[Error Message]",
                        "**Data Error**<br>Failed while reading command data file.<br>Time:" + datetime.now().strftime(
                            "%c"), self.webhook_url)
            return

    def generate_help(self, cmd_directory: list):
        try:
            fa_cmd = ""
            if len(cmd_directory) == 0:
                fa_cmd = ""
            else:
                for d in cmd_directory:
                    fa_cmd += d + self.dat["config"].get("command_spliter", "$")
            help_str = "Usage of command '**" + fa_cmd + "**':<br>"
            fa_cmd_dict = self.cmd
            for sub in cmd_directory:
                flag = False
                for cmds in fa_cmd_dict["sub_commands"]:
                    if sub in cmds["content"]:
                        fa_cmd_dict = cmds
                        flag = True
                        break
                if not flag:
                    return "Failed to generate help message."

            if fa_cmd_dict["type"] == "sub":
                for sub in fa_cmd_dict["sub_commands"]:
                    if sub["type"] == "sub":
                        help_str += "**" + sub["content"][0] + "**<br>"
                    elif sub["type"] == "cmd":
                        help_str += "**" + sub["content"][0] + "** "
                        for arg in sub["arg"]:
                            help_str += "\\<" + arg["type"] + " " + arg["content"] + "\\> "
                        help_str += "<br>"

            elif fa_cmd_dict["type"] == "cmd":
                help_str += "**" + fa_cmd_dict["content"][0] + "** "
                for arg in fa_cmd_dict["arg"]:
                    help_str += "\\<" + arg["type"] + " " + arg["content"] + "\\>"
                help_str += "<br>"

            return help_str[:-2]
        except Exception as e:
            return "Failed to generate help message."

    def run(self, cmd: str):
        self.read_file()
        cmd_spl = self.dat["config"].get("command_spliter", "$")
        cmd = cmd.split(cmd_spl)
        cur_dict = self.cmd
        cmd_directory = []
        for sub in cmd:
            flag = False
            if cur_dict["type"] == "cmd":
                break
            for cmds in cur_dict["sub_commands"]:
                if sub in cmds["content"]:
                    cur_dict = cmds
                    cmd_directory.append(cmds["content"][0])
                    flag = True
                    break
            if not flag:
                flag = False
                for cmds in cur_dict["sub_commands"]:
                    if cmds["content"][0] == "__DEFAULT__":
                        cur_dict = cmds
                        flag = True
                        break
                if not flag:
                    fa_cmd = ""
                    if len(cmd_directory) == 0:
                        send_md_msg(self.senderid, "[Error Message]",
                                    "**Incorrect command usage:**<br>Unknown prefix '" + sub + "'!", self.webhook_url)
                        return
                    for d in cmd_directory:
                        fa_cmd += d + self.dat["config"].get("command_spliter", "$")
                    send_md_msg(self.senderid, "[Error Message]",
                                "**Incorrect command usage:**<br>Command" + fa_cmd + " does not have a subcommand:<br>" + sub + "<br>" + self.generate_help(
                                    cmd_directory), self.webhook_url)
                    return
        fa_cmd = ""
        for d in cmd_directory:
            fa_cmd += d + cmd_spl
        if cur_dict["type"] == "sub":
            flag = False
            for cmds in cur_dict["sub_commands"]:
                if cmds["content"][0] == "__DEFAULT__":
                    cur_dict = cmds
                    flag = True
                    break

            if not flag:
                send_md_msg(self.senderid, "[Error Message]",
                            "**Incorrect command usage:**<br>" + fa_cmd + " requires a subcommand.<br>" + self.generate_help(
                                cmd_directory), self.webhook_url)
                return
        have_spec_arg = False
        for arg in cur_dict["arg"]:
            if arg["type"] == "spec":
                have_spec_arg = True
                break
        if ((not have_spec_arg) and len(cmd) != len(cmd_directory) + len(cur_dict["arg"])) or (
                have_spec_arg and len(cmd) < len(cmd_directory) + len(cur_dict["arg"])):
            send_md_msg(self.senderid, "[Error Message]",
                        "**Incorrect command usage:**<br>" + fa_cmd + " requires " + str(
                            len(cur_dict["arg"])) + " arguments.<br>" + self.generate_help(
                            cmd_directory), self.webhook_url)
            return
        else:
            arg_inx = len(cmd_directory)
            arg_dict = {}
            for arg in cur_dict["arg"]:
                if arg["type"] == "str":
                    arg_dict[arg["content"]] = cmd[arg_inx]
                elif arg["type"] == "choice":
                    if not cmd[arg_inx] in arg["choice"]:
                        send_md_msg(self.senderid, "[Error Message]",
                                    "**Incorrect command usage:**<br>" + fa_cmd + " required an literal argument '" +
                                    arg[
                                        "content"] + "' ,with choices: " + str(
                                        arg["choice"]) + "<br>But the given argument value is not a valid choice: '" +
                                    cmd[
                                        arg_inx] + "'<br>" + self.generate_help(
                                        cmd_directory), self.webhook_url)
                        return
                    arg_dict[arg["content"]] = cmd[arg_inx]
                elif arg["type"] == "int":
                    if not cmd[arg_inx].isdigit():
                        send_md_msg(self.senderid, "[Error Message]",
                                    "**Incorrect command usage:**<br>" + fa_cmd + " required an integer argument '" +
                                    arg["content"] + "<br>But the given argument value is not an integer: '" +
                                    cmd[arg_inx] + "'<br>" + self.generate_help(
                                        cmd_directory), self.webhook_url)
                        return
                    arg_dict[arg["content"]] = cmd[arg_inx]
                elif arg["type"] == "spec":
                    tmp = ""
                    for a in cmd[arg_inx:]:
                        tmp += a + cmd_spl
                        cmd.remove(a)
                    tmp = tmp[:-1]
                    cmd.append(tmp)
                    arg_dict[arg["content"]] = cmd[arg_inx]
                arg_inx += 1
            command_funcs = RobotCommandFuncs(self.req_data, self.dat, self.fileio, self.logger)
            getattr(command_funcs, cur_dict["func"].split("(")[0])(**arg_dict)
