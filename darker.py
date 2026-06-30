import re
import argparse
import colorsys

def adjust_lightness(r, g, b, factor, threshold):
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
    
    if l <= threshold:
        l = max(0.0, l - (l * factor))

    r_new, g_new, b_new = colorsys.hls_to_rgb(h, l, s)
    return round(r_new * 255), round(g_new * 255), round(b_new * 255)

def hex_replacer(match, factor, threshold):
    hex_str = match.group(1)
    
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
        
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    
    nr, ng, nb = adjust_lightness(r, g, b, factor, threshold)
    return f"#{nr:02x}{ng:02x}{nb:02x}"

def rgba_replacer(match, factor, threshold):
    prefix = match.group(1)
    r, g, b = int(match.group(2)), int(match.group(3)), int(match.group(4))
    rest = match.group(5)
    
    nr, ng, nb = adjust_lightness(r, g, b, factor, threshold)
    return f"{prefix}({nr}, {ng}, {nb}{rest})"

def main():
    parser = argparse.ArgumentParser(description="Darken Hex and RGB/RGBA colors in a GNOME CSS file.")
    parser.add_argument("input", help="Original CSS file")
    parser.add_argument("-o", "--output", default="darker_theme.css", help="Output CSS file")
    parser.add_argument("-f", "--factor", type=float, default=0.3, help="Darkening factor (0.0 to 1.0). Ex: 0.3 = 30% darker")
    parser.add_argument("-t", "--threshold", type=float, default=0.5, help="Ignore colors lighter than this (0.0 to 1.0). Ex: 0.5 ignores whites and light grays")
    
    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            css = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found.")
        return

    hex_pattern = re.compile(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b')
    rgba_pattern = re.compile(r'(rgba?)\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(.*?)\)')

    css = hex_pattern.sub(lambda m: hex_replacer(m, args.factor, args.threshold), css)
    css = rgba_pattern.sub(lambda m: rgba_replacer(m, args.factor, args.threshold), css)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(css)
        
    print(f"Success! File generated at: {args.output}")
    print(f"Parameters: {args.factor*100}% darker, threshold of {args.threshold*100}%")

if __name__ == "__main__":
    main()