import json
from typing import Literal

# Color table for Minecraft color codes
color_table: dict[str, str] = {
    "black": "#000000",
    "dark_blue": "#0000AA",
    "dark_green": "#00AA00",
    "dark_aqua": "#00AAAA",
    "dark_red": "#AA0000",
    "dark_purple": "#AA00AA",
    "gold": "#FFAA00",
    "gray": "#AAAAAA",
    "dark_gray": "#555555",
    "blue": "#5555FF",
    "green": "#55FF55",
    "aqua": "#55FFFF",
    "red": "#FF5555",
    "light_purple": "#FF55FF",
    "yellow": "#FFFF55",
    "white": "#FEFEFE"
}

# Text decoration styles for Minecraft text formatting
style_table_text_decoration: dict[str, str] = {
    "strikethrough": " line-through",
    "underlined": " underline",
    "obfuscated": " overline",
}

style_table_markdown: dict[str, tuple[str, str]] = {
    "underlined": ("<u>", "</u>"),
    "strikethrough": ("~~", "~~"),
    "obfuscated": ("", ""),
    "bold": ("**", "**"),
    "italic": ("*", "*")
}

# Font styles for Minecraft text formatting
style_table_font: dict[str, str] = {
    "bold": "font-weight: bold;",
    "italic": "font-style: italic;"
}


def parse_packet(raw_json_data: str | dict, translation_table: dict[str, str],
                 result_format: Literal["text", "html", "markdown"] = "html") -> str:
    """
    Parse a Minecraft chat packet into a string of the specified format.

    :param raw_json_data: The raw JSON data of the packet, either as a string or a dictionary.
    :param translation_table: The minecraft translation table.
    :param result_format: The format of the parsing result string, which can be HTML with style, Markdown with style, and plain text without style

    :returns: Packet parsing result string in the specified format.
    """
    if not isinstance(raw_json_data, dict):
        if isinstance(raw_json_data, str):
            raw_json_data = json.loads(raw_json_data)
            try:
                return str(int(raw_json_data))
            except:
                pass
        else:
            return str(raw_json_data)
    if "translate" in raw_json_data:
        if "with" in raw_json_data:
            rl = []
            for i in raw_json_data["with"]:
                rl.append(parse_packet(i, translation_table, result_format))
            br = translation_table[raw_json_data["translate"]]
            try:
                return br % tuple(rl)
            except:
                return br
        else:
            if raw_json_data["translate"] in translation_table:
                return translation_table[raw_json_data["translate"]]
            else:
                return raw_json_data["translate"]
    elif "extra" in raw_json_data:
        a, b = raw_json_data.pop("extra"), raw_json_data
        return parse_packet(b, translation_table, result_format) + "".join(
            [parse_packet(i, translation_table, result_format) for i in a])
    else:
        text = raw_json_data.get("text", "Text not found")
        if text in translation_table:
            text = translation_table[text]
        result = ""
        match result_format:
            case "html":
                result = "<font style=\"text-decoration:"
                text_decoration_not_found = True
                for k in style_table_text_decoration.keys():
                    if raw_json_data.get(k, None) == "true":
                        result += style_table_text_decoration[k]
                        text_decoration_not_found = False
                if text_decoration_not_found:
                    result += " none"
                result += ";"
                for k in style_table_font.keys():
                    if raw_json_data.get(k, None) == "true":
                        result += style_table_font[k]
                if "color" in raw_json_data:
                    result += "color: " + color_table.get(raw_json_data["color"], raw_json_data["color"]) + ";"
                result += "\">"
                result += text.replace("<", "&lt;").replace(">", "&gt;").replace("\\n", "<br>").replace("\n", "<br>")

                result += "</font>"
            case "text":
                result += text.replace("\\n", "\n")
            case "markdown":
                suffix = ""
                if "color" in raw_json_data:
                    result = "<font"
                    result += " color=\"" + color_table.get(raw_json_data["color"], raw_json_data["color"]) + "\">"
                    suffix = "</font>" + suffix
                else:
                    result = ""
                for k in style_table_markdown.keys():
                    if raw_json_data.get(k, None) == "true":
                        result += style_table_markdown[k][0]
                        suffix = style_table_markdown[k][1] + suffix
                result += text.replace("<", "&lt;").replace(">", "&gt;").replace("\\n", "<br>").replace("\n", "<br>") + suffix
        return result
