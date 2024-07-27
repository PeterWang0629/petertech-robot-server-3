import controller.libraries.server.configure as configure
from controller.libraries.server.fileio import FileIO
from controller.libraries.server.logger import Logger


class ConsoleCommands:
    def __init__(self, fileio: FileIO, logger: Logger, skip_refresh_file_data: bool = False) -> None:
        self.fileio = fileio
        self.logger = logger
        self.cmd = []
        if not skip_refresh_file_data:
            self.refresh_file_data()

    def refresh_file_data(self) -> None:
        cmd_dict_file = configure.get_config("cmd_dict_file", "data/cmd.json")
        self.fileio.register_file([cmd_dict_file])
        self.cmd = self.fileio.read(cmd_dict_file)

    def __split_cmd(self, cmd: str) -> list:
        result = []
        split_cmd = cmd.split(" ")
        in_string = False
        string = ""
        for part in split_cmd:
            if in_string:
                if part.endswith("\"") and not part.endswith("\\\""):
                    in_string = False
                    string += " " + part[:-1]
                    string = string.replace("\\n", "\n").replace("\\\"", "\"")
                    result.append({"type": "argument", "argument_type": "str", "value": string})
                    string = ""
                else:
                    string += " " + part[:-1]
            else:
                if part.startswith("\""):
                    if part.endswith("\""):
                        result.append({"type": "argument", "argument_type": "str", "value": part[1:-1]})
                    else:
                        in_string = True
                        string += part[1:]

                elif part.startswith("-"):
                    result.append({"type": "option", "value": part[1:]})

                else:
                    if part.isnumeric():
                        result.append({"type": "argument", "argument_type": "int", "value": int(part)})
                    elif part == "true":
                        result.append({"type": "argument", "argument_type": "bool", "value": True})
                    elif part == "false":
                        result.append({"type": "argument", "argument_type": "bool", "value": False})
                    else:
                        result.append({"type": "command", "value": part})
        if in_string:
            result = None
        return result

    def __find_command(self, cmd_list: list, cmd: str) -> dict | None:
        for cmd_ in cmd_list:
            if cmd in cmd_["content"]:
                return cmd_
        return None

    def __find_option(self, cmd_dict: dict, option: str) -> dict | None:
        for option_ in cmd_dict["option"]:
            if option in option_["content"]:
                return option_
        return None

    def __parse_single_command(self, split_cmd: list, cmd_json: list) -> dict | None:
        print(split_cmd)
        result_json = {"success": True, "command": [], "arguments": {}, "options": {}}
        if split_cmd[0]["type"] != "command":
            return {"success": False, "error": "SYNTAX_ERROR",
                    "message": f"Unexpected command after option(s) or argument(s)."}
        cmd_json = self.__find_command(cmd_json, split_cmd[0]["value"])
        if not cmd_json:
            return {"success": False, "error": "COMMAND_NOT_FOUND",
                    "message": f"{split_cmd[0]['value']} is not a valid command or sub-command."}

        result_json["command"].append(split_cmd[0]["value"])

        in_option = None
        in_option_completed = None
        for part_id in range(len(split_cmd[1:])):
            part = split_cmd[1:][part_id]
            if in_option:
                if len(result_json["options"][in_option["content"][0]]) >= len(in_option["arg"]):
                    in_option = None
                    in_option_completed = True

                if part["type"] == "argument":
                    cur_option_argument = in_option["arg"][len(result_json["options"][in_option["content"][0]])]
                    if cur_option_argument["type"] != part["argument_type"]:
                        return {"success": False, "error": "OPTION_ARGUMENT_TYPE_ERROR",
                                "message": f"Option {split_cmd[0]['value']} for this command requires a(n) {cur_option_argument['type']} argument \"{cur_option_argument['name']}\""
                                           f", but a(n) {part['argument_type']} argument were given."}
                    result_json["options"][in_option["content"][0]][cur_option_argument["name"]] = part["value"]

                else:
                    return {"success": False, "error": "TOO_FEW_OPTION_ARGUMENTS",
                            "message": f"Option {in_option['content'][0]} for this command requires at least {len(cmd_json['arg'])}"
                                       f"argument(s), but {len(result_json['arguments'])} argument(s) were given."}

                if len(result_json["options"][in_option["content"][0]]) >= len(in_option["arg"]):
                    in_option_completed = True

            if not in_option:
                if part["type"] == "command":
                    if part_id != 0:
                        return {"success": False, "error": "SYNTAX_ERROR",
                                "message": f"Unexpected command after option(s) or argument(s)."}
                    if cmd_json["type"] == "cmd":
                        return {"success": False, "error": "COMMAND_NOT_FOUND",
                                "message": f"Command or sub-command {split_cmd[0]['value']} has no sub-command, but an sub-command were given"}
                    else:
                        parse_result = self.__parse_single_command(split_cmd[part_id + 1:], cmd_json["sub_commands"])
                        if parse_result["success"]:
                            for cmd in parse_result["command"]:
                                result_json["command"].append(cmd)
                            result_json["arguments"] = parse_result["arguments"]
                            result_json["options"] = parse_result["options"]
                            return result_json
                        else:
                            return parse_result

                elif part["type"] == "argument":
                    if cmd_json["type"] == "sub":
                        return {"success": False, "error": "NOT_ACCEPTED",
                                "message": f"No option required for command or sub-command {split_cmd[0]['value']}, it requires sub-command."}
                    if len(result_json["arguments"]) >= len(cmd_json["arg"]):
                        return {"success": False, "error": "TOO_MANY_ARGUMENTS",
                                "message": f"Command or sub-command {split_cmd[0]['value']} requires at most {len(cmd_json['arg'])} "
                                           f"argument(s), but {len(result_json['arguments'])} argument(s) were given."}
                    cur_argument = cmd_json["arg"][len(result_json["arguments"])]
                    if cur_argument["type"] != part["argument_type"]:
                        return {"success": False, "error": "ARGUMENT_TYPE_ERROR",
                                "message": f"Command or sub-command {split_cmd[0]['value']} requires a(n) {cur_argument['type']} argument \"{cur_argument['name']}\""
                                           f", but a(n) {part['argument_type']} argument were given."}
                    result_json["arguments"][cur_argument['name']] = part["value"]
                elif part["type"] == "option":
                    if cmd_json["type"] == "sub":
                        return {"success": False, "error": "NOT_ACCEPTED",
                                "message": f"No option required for command or sub-command {split_cmd[0]['value']}, it requires sub-command."}
                    found_option = self.__find_option(cmd_json, part["value"])
                    if not found_option:
                        return {"success": False, "error": "OPTION_NOT_FOUND",
                                "message": f"-{part['value']} is not a valid option for command or sub-command {split_cmd[0]['value']}"}
                    if len(found_option["arg"]):
                        result_json["options"][found_option["content"][0]] = {}
                        in_option = found_option
                        in_option_completed = False
                        continue
                    else:
                        result_json["options"][found_option["content"][0]] = {}
        if cmd_json["type"] == "sub":
            return {"success": False, "error": "SUB_COMMAND_REQUIRED",
                    "message": f"Command or sub-command {split_cmd[0]['value']} requires sub-command, but no sub-command were given"}
        if len(result_json["arguments"]) < len(cmd_json["arg"]):
            return {"success": False, "error": "TOO_FEW_ARGUMENTS",
                    "message": f"Command or sub-command {split_cmd[0]['value']} requires at least {len(cmd_json['arg'])} "
                               f"argument(s), but {len(result_json['arguments'])} argument(s) were given."}
        if in_option_completed == False:
            return {"success": False, "error": "TOO_FEW_OPTION_ARGUMENTS",
                    "message": f"Option {in_option['content'][0]} requires at least {len(cmd_json['arg'])} "
                               f"argument(s), but {len(result_json['options'][in_option['content'][0]])} argument(s) were given."}
        return result_json

    def __parse_command(self, cmd: str) -> dict:
        cmd_json = self.cmd
        split_cmd = self.__split_cmd(cmd)
        if not split_cmd:
            return {"success": False, "error": "SYNTAX_ERROR",
                    "message": f"Quotes unpair."}
        return self.__parse_single_command(split_cmd, self.cmd)

    def generate_help(self, cmd_directory: list) -> str | None:
        help_string = "Command Help for command " + " ".join(cmd_directory) + f":\nUsage: \n"
        cmd_json = {"sub_commands": self.cmd}
        for cmd in cmd_directory:
            cmd_json = cmd_json["sub_commands"]
            cmd_json = self.__find_command(cmd_json, cmd)
        if cmd_json["type"] == "cmd":
            # Generate Usage
            help_string += f"{' '.join(cmd_directory)} "
            if len(cmd_json["arg"]):
                for arg in cmd_json["arg"]:
                    help_string += f"<{arg['type']} {arg['name']}> "
            if len(cmd_json["option"]):
                help_string += "[options]"
            help_string += "\n"
            # Generate Options
            if len(cmd_json["option"]):
                help_string += "Options: \n"
                for option in cmd_json["option"]:
                    for name in option["content"]:
                        help_string += f"-{name}, "
                    help_string = help_string[:-2] + " "
                    for option_arg in option["arg"]:
                        help_string += f"<{option_arg['type']} {option_arg['name']}> "
                    help_string += "\n"
            return help_string
        elif cmd_json["type"] == "sub":
            # Generate Usage
            help_string += f"{' '.join(cmd_directory)} \n"
            # Generate Commands
            help_string += "Commands: \n"
            for sub_command in cmd_json["sub_commands"]:
                for name in sub_command["content"]:
                    help_string += f"{name}, "
                help_string = help_string[:-2] + "\n"
            return help_string
        elif cmd_json["type"] == "mixed":
            # Generate Usage
            help_string += f"[1] {' '.join(cmd_directory)} "
            if len(cmd_json["arg"]):
                for arg in cmd_json["arg"]:
                    help_string += f"<{arg['type']} {arg['name']}> "
            if len(cmd_json["option"]):
                help_string += "[options]"
            help_string += "\n"
            # Generate Options
            if len(cmd_json["option"]):
                help_string += "Options: \n"
                for option in cmd_json["option"]:
                    for name in option["content"]:
                        help_string += f"-{name}, "
                    help_string = help_string[:-2] + " "
                    for option_arg in option["arg"]:
                        help_string += f"<{option_arg['type']} {option_arg['name']}> "
                    help_string += "\n"
            # Generate Usage
            help_string += "\n"
            help_string += f"[2] {' '.join(cmd_directory)} "
            # Generate Commands
            help_string += "Commands: \n"
            for sub_command in cmd_json["sub_commands"]:
                for name in sub_command["content"]:
                    help_string += f"{name}, "
                help_string = help_string[:-2] + "\n"
            return help_string

    def execute_command(self, cmd: str) -> str:
        parsed_command = self.__parse_command(cmd)
        if not parsed_command["success"]:
            return f"Command Parse Failed (Error {parsed_command['error']}):\n{parsed_command['message']}"
        return f"Do you know? About how to execute, i don't know either.\nBut I parsed your command: {parsed_command}\nHelp:\n{self.generate_help(parsed_command['command'])}"