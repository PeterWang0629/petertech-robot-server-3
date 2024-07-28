import json

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

# Font styles for Minecraft text formatting
style_table_font: dict[str, str] = {
    "bold": "font-weight: bold;",
    "italic": "font-style: italic;"
}


def parse_packet(raw_json_data: str | dict, translation_table: dict[str, str], with_style: bool = True) -> str:
    """
    Parses a Minecraft packet and converts it into styled HTML code or plain text.

    :param with_style: Add HTML styling to the result.
    :param translation_table: The minecraft translation table.
    :param raw_json_data: The raw JSON data of the packet, either as a string or a dictionary.

    :returns: The string representation of the packet.
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
                rl.append(parse_packet(i, translation_table, with_style))
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
        return parse_packet(b, translation_table, with_style) + "".join([parse_packet(i, translation_table, with_style) for i in a])
    else:
        if with_style:
            result = "<font style=\"text-decoration:"
            text_decoration_found = True
            for k in style_table_text_decoration.keys():
                if raw_json_data.get(k, None) == "true":
                    result += style_table_text_decoration[k]
                    text_decoration_found = False
            if text_decoration_found:
                result += " none"
            result += ";"
            for k in style_table_font.keys():
                if raw_json_data.get(k, None) == "true":
                    result += style_table_font[k]
            if "color" in raw_json_data:
                result += "color: " + color_table[raw_json_data["color"]] + ";"
            result += "\">"
        else:
            result = ""
        txt = raw_json_data.get("text", "[Unsupported Message]")
        if txt in translation_table: txt = translation_table[txt]
        if with_style:
            result += txt.replace("<", "&lt;").replace(">", "&gt;")
            result += "</font>"
        else:
            result += txt
        return result
