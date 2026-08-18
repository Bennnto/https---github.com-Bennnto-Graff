def format_error(filename: str, code: str, line_no: int, col_no: int, message: str, error_type: str = "RuntimeError") -> str :
    lines = code.splitlines() if code else [] 
    border = "=" * 65
    header = f"[ Gaff {error_type}] in {filename}: Line : {line_no}: Col : {col_no} ]"
    output = []
    output.append(border)
    output.append(header)
    output.append(border)
    output.append("")

    # Check if line no. exists in source code
    if 1 <= line_no <= len(lines):
        if line_no > 1 :
            output.append(f" {line_no-1:04d} | {lines[line_no-2]}")

        target_line = lines[line_no - 1]
        output.append(f" {line_no:04d} | {target_line}")

        # Draw Pointer 
        indent = " " * (8 + max(0, col_no-1))
        pointer_len = max(1, len(target_line.strip()))
        output.append(f"{indent}{'-' * pointer_len}")
    
    else :
        if code:
            output.append(f" Source: {code.strip()[:60]}")

    # Append Error Description
    output.append(f"\n Error : {message}\n")
    return "\n".join(output)
    


