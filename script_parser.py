#!/usr/bin/env python3

import struct

class IntLiteralNode:
    value: int
    def __init__(self, value: int):
        self.value = value
    def __str__(self):
        return hex(self.value)
    def to_bytes(self):
        raise RuntimeError('unimplemented')

class StringLiteralNode:
    value: str
    def __init__(self, value: str):
        self.value = value
    def __str__(self):
        # TODO: escape "s in the middle
        return f'"{self.value}"'

class FunctionNameNode:
    ns: str
    func: str
    def __init__(self, ns: str, func: str):
        self.ns = ns
        self.func = func
    def __str__(self):
        return f"{self.ns}.{self.func}"
class FunctionArgsNode:
    def __init__(self, children):
        self.children = children
    def __str__(self):
        l = len(self.children)
        if l == 0:
            return '()'
        elif l == 1:
            return f'({self.children[0]})'
        else:
            i = iter(self.children)
            result = '(' + str(next(i))
            for s in i:
                result += ', '
                result += str(s)
            result += ')'
            return result
class FunctionCallNode:
    def __init__(self, func, args):
        self.func = func
        self.args = args
    def __str__(self):
        return str(self.func) + str(self.args)

class IntExprNode:
    pass
    
class NegateNode(IntExprNode):
    def __init__(self, expr: IntExprNode):
        super().__init__()
        self.expr = expr
    def __str__(self):
        return f'-({self.expr})'

class BooleanExprNode:
    pass

class LogicalNotNode(BooleanExprNode):
    def __init__(self, expr: BooleanExprNode):
        super().__init__()
        self.expr = expr
    def __str__(self):
        return f"not {self.expr}"

class Cmd0FNode(BooleanExprNode):
    def __init__(self, lhs: BooleanExprNode, rhs: BooleanExprNode):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        # Assuming this is logical and
        return f"({self.lhs} and {self.rhs})"

class Cmd12Node(BooleanExprNode):
    def __init__(self, lhs: BooleanExprNode, rhs: BooleanExprNode):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        # Assuming this is logical or
        return f"({self.lhs} or {self.rhs})"

class Cmd1ANode(BooleanExprNode):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        return f"{self.lhs} == {self.rhs}"

class Cmd1BNode(BooleanExprNode):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        return f"{self.lhs} != {self.rhs}"

class Cmd15Node:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        return f'({self.lhs} + {self.rhs})'

class Cmd20Node:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        return f'{self.lhs} = {self.rhs}'

class StatementNode:
    def is_branch(self):
        return False

class InitStatementNode(StatementNode):
    def __init__(self):
        super().__init__()
    def __str__(self):
        return '{'

class EndStatementNode(StatementNode):
    def __init__(self):
        super().__init__()
    def __str__(self):
        return '}'

class ExprStmtNode(StatementNode):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr
    def __str__(self):
        return f'{self.expr};'

class SpeakerStatement(StatementNode):
    def __init__(self, speaker: str):
        super().__init__()
        self.speaker = speaker
    def __str__(self):
        return f'[{self.speaker}]'

class TextStatement(StatementNode):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
    def __str__(self):
        return f':: "{self.text}";'

class Cmd2BStatement(StatementNode):
    def __init__(self, arg):
        super().__init__()
        self.arg = arg
    def __str__(self):
        return f'cmd2B {hex(self.arg)}'

class Cmd2CStatement(StatementNode):
    def __init__(self, arg):
        super().__init__()
        self.arg = arg
    def __str__(self):
        return f'cmd2C {hex(self.arg)}'

class Cmd30Statement(StatementNode):
    def __init__(self):
        super().__init__()
    def __str__(self):
        # return?
        return f'cmd30;'

class Cmd32Statement(StatementNode):
    def __init__(self, arg):
        super().__init__()
        self.arg = arg
    def __str__(self):
        return f'cmd32 {hex(self.arg)}'

class Cmd33Statement(StatementNode):
    def __init__(self, arg: str):
        super().__init__()
        self.arg = arg
    def __str__(self):
        return f'cmd33 "{self.arg}"'

class LabelMarker(StatementNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    def __str__(self):
        return f'{self.name}:'

class GotoStatement(StatementNode):
    def __init__(self, branch_offset: int):
        super().__init__()
        self.branch_offset = branch_offset
    def is_branch(self):
        return True
    def __str__(self):
        return f'goto {self.branch_offset:+d};'

class TrueGotoStatement(GotoStatement):
    def __init__(self, condition: BooleanExprNode, branch_offset: int):
        super().__init__(branch_offset)
        self.condition = condition
    def __str__(self):
        return f'if ({self.condition}) goto {self.branch_offset:+d};'

class FalseGotoStatement(GotoStatement):
    def __init__(self, condition: BooleanExprNode, branch_offset: int):
        super().__init__(branch_offset)
        self.condition = condition
    def __str__(self):
        return f'unless ({self.condition}) goto {self.branch_offset:+d};'

def print_cmd(file, offset, expr_stack, stmt_list):
    cmd = file[offset]
    match cmd:
        case 0x01:
            node = NegateNode(expr_stack[-1])
            expr_stack[-1] = node
            return offset + 1
        case 0x07:
            node = LogicalNotNode(expr_stack[-1])
            expr_stack[-1] = node
            return offset + 1
        case 0x0D:
            subcmd = file[offset+1]
            match subcmd:
                case 0xF0:
                    # TODO: limits for i exist
                    i = 0
                    num = 0
                    while (file[offset+2+i] & 0x80) != 0:
                        num |= (file[offset+2+i] & 0x7F) << (7 * i)
                        i += 1
                    num |= file[offset+2+i] << (7 * i)
                    i += 1
                    expr_stack.append(IntLiteralNode(num))
                    return offset + 2 + i
                case 0xF4:
                    (str1_id, str2_id) = struct.unpack_from('<HH', buffer=file, offset=offset+2)
                    if str2_id != 0:
                        expr_stack.append(FunctionNameNode(get_string(str1_id), get_string(str2_id)))
                    else:
                        expr_stack.append(StringLiteralNode(get_string(str1_id)))
                    return offset + 6
                case _:
                    raise RuntimeError(f'unimplemented command 0D {subcmd:02X}')
        case 0x0F:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append(Cmd0FNode(lhs, rhs))
            return offset + 1
        case 0x12:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append(Cmd12Node(lhs, rhs))
            return offset + 1
        case 0x15:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append(Cmd15Node(lhs, rhs))
            return offset + 1
        case 0x1A:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append(Cmd1ANode(lhs, rhs))
            return offset + 1
        case 0x1B:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append(Cmd1BNode(lhs, rhs))
            return offset + 1
        case 0x20:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append(Cmd20Node(lhs, rhs))
            return offset + 1
        case 0x23:
            expr_stack.append(FunctionArgsNode([]))
            return offset + 1
        case 0x24:
            i = len(expr_stack)
            while not isinstance(expr_stack[i - 1], FunctionArgsNode):
                i -= 1
            expr_stack[i - 1].children = expr_stack[i:]
            del expr_stack[i:]
            args = expr_stack.pop()
            func = expr_stack.pop()
            expr_stack.append(FunctionCallNode(func, args))
            return offset + 1
        case 0x25:
            stmt_list.append(InitStatementNode())
            return offset + 1
        case 0x26:
            stmt_list.append(EndStatementNode())
            return offset + 1
        case 0x27:
            stmt_list.append(ExprStmtNode(expr_stack.pop()))
            return offset + 1
        case 0x28:
            str_id = file[offset+1] | (file[offset+2] << 8)
            stmt_list.append(SpeakerStatement(get_string(str_id)))
            return offset + 3
        case 0x2B:
            stmt_list.append(Cmd2BStatement(file[offset+1]))
            return offset + 2
        case 0x2C:
            stmt_list.append(Cmd2CStatement(file[offset+1]))
            return offset + 2
        case 0x2F:
            str_id = file[offset+1] | (file[offset+2] << 8)
            stmt_list.append(TextStatement(get_string(str_id)))
            return offset + 3
        case 0x30:
            stmt_list.append(Cmd30Statement())
            return offset + 1
        case 0x32:
            num = file[offset+1] | (file[offset+2] << 8)
            stmt_list.append(Cmd32Statement(num))
            return offset + 3
        case 0x33:
            str_id = file[offset+1] | (file[offset+2] << 8)
            stmt_list.append(Cmd33Statement(get_string(str_id)))
            return offset + 3
        case 0x34:
            (str_id,) = struct.unpack_from('<H', buffer=file, offset=offset+1)
            stmt_list.append(LabelMarker(get_string(str_id)))
            return offset + 3
        case 0x35:
            (branch_offset,) = struct.unpack_from('<h', buffer=file, offset=offset+1)
            stmt_list.append(GotoStatement(branch_offset))
            return offset + 3
        case 0x36:
            (branch_offset,) = struct.unpack_from('<h', buffer=file, offset=offset+1)
            cond = expr_stack.pop()
            stmt_list.append(TrueGotoStatement(cond, branch_offset))
            return offset + 3
        case 0x37:
            (branch_offset,) = struct.unpack_from('<h', buffer=file, offset=offset+1)
            cond = expr_stack.pop()
            stmt_list.append(FalseGotoStatement(cond, branch_offset))
            return offset + 3
        case _:
            raise RuntimeError(f'unimplemented command {cmd:02X}')
    raise RuntimeError('I forgot a return statement somewhere')

def get_string(id):
    assert id < str_count
    (string_addr,) = struct.unpack_from('<L', buffer=fsb, offset=str_table_offset + ptr_size*id)
    string_end_addr = fsb.index(0, string_addr)
    # Characters like ⑲ don't exist in the 'shift_jis' encoding, so the distinction is important
    return fsb[string_addr:string_end_addr].decode('mskanji')

fsb = None
with open('../999_jp_files/root/scr/a12d.fsb', 'rb') as f:
    fsb = f.read()

assert fsb[0:3] == b'SIR'

if fsb[3] == ord('0'):
    ptr_size = 4
elif fsb[3] == ord('1'):
    ptr_size = 8
    raise RuntimeError("SIR1 scripts are unsupported for now")

# We could verify the pointer metadata... or we could just ignore it because we
# know what the pointers are anyway
script_header_offset = int.from_bytes(fsb[4:4+ptr_size], byteorder='little')
# ptr_metadata_offset = int.from_bytes(fsb[4+ptr_size:4+ptr_size*2], byteorder='little')

(filename_offset, entrypoint_dict_offset, str_count, str_table_offset, \
    label_table_offset, unk_offset) \
    = struct.unpack_from('<LLLLLL', buffer=fsb, offset=script_header_offset)

# The filename is null-terminated
filename_end_offset = fsb.index(0, filename_offset)
filename = fsb[filename_offset:filename_end_offset].decode('ascii')
# Add a .txt extension
filename = filename + '.txt'
print('Output file name:', filename)

entrypoints = []
while True:
    addr, name = struct.unpack_from('<LL', buffer=fsb, offset=entrypoint_dict_offset)
    entrypoint_dict_offset += 8
    if addr == 0 and name == 0:
        break
    name_end = fsb.index(0, name)
    name_str = fsb[name:name_end].decode('mskanji')
    entrypoints.append((addr, name_str))
# print(entrypoints)

with open(filename, 'w', encoding='utf-8') as f:
    for entrypoint in entrypoints:
        expr_stack = []
        f.write(f'function {entrypoint[1]}\n')
        
        addr = entrypoint[0]
        statements = []
        expressions = []
        while len(statements) == 0 or not isinstance(statements[-1], EndStatementNode):
            addr = print_cmd(fsb, addr, expressions, statements)
        
        for statement in statements:
            f.write('\t')
            f.write(str(statement))
            f.write('\n')
        f.write('\n')

    f.write('// done')