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
        if self.ns is not None:
            return f"{self.ns}.{self.func}"
        else:
            return str(self.func)
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

class Cmd1CNode(BooleanExprNode):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        # It's either >= or <=
        return f"{self.lhs} cmpOp1C {self.rhs}"

class Cmd1DNode(BooleanExprNode):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        # It's either >= or <=
        return f"{self.lhs} cmpOp1D {self.rhs}"

class Cmd1FNode(BooleanExprNode):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        # It's either > or <
        return f"{self.lhs} cmpOp1F {self.rhs}"

class Cmd15Node:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        return f'({self.lhs} + {self.rhs})'

class Cmd16Node:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        return f'({self.lhs} - {self.rhs})'

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
        return f'branch 0x{self.branch_offset:X};'

class TrueGotoStatement(GotoStatement):
    def __init__(self, condition: BooleanExprNode, branch_offset: int):
        super().__init__(branch_offset)
        self.condition = condition
    def __str__(self):
        return f'if ({self.condition}) branch 0x{self.branch_offset:X};'

class FalseGotoStatement(GotoStatement):
    def __init__(self, condition: BooleanExprNode, branch_offset: int):
        super().__init__(branch_offset)
        self.condition = condition
    def __str__(self):
        return f'unless ({self.condition}) branch 0x{self.branch_offset:X};'

class EndOfFileStatement(StatementNode):
    def __init__(self):
        super().__init__()
    def __str__(self):
        return '/* EOF */'

def print_cmd(file, offset, expr_stack, stmt_list):
    cmd = file[offset]
    # print(f'DEBUG: file[0x{offset:X}] = 0x{cmd:02X}')
    match cmd:
        case 0x01:
            node = NegateNode(expr_stack[-1][1])
            expr_stack[-1] = (expr_stack[-1][0], node)
            return offset + 1
        case 0x07:
            node = LogicalNotNode(expr_stack[-1][1])
            expr_stack[-1] = (expr_stack[-1][0], node)
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
                    expr_stack.append((offset, IntLiteralNode(num)))
                    return offset + 2 + i
                case 0xF1:
                    # TODO: Why would this be used instead of 0xF4? Specifically for `?System` functions?
                    str_id = file[offset+2] | (file[offset+3] << 8)
                    expr_stack.append((offset, FunctionNameNode(None, get_string(str_id))))
                    return offset + 4
                case 0xF4:
                    (str1_id, str2_id) = struct.unpack_from('<HH', buffer=file, offset=offset+2)
                    if str2_id != 0:
                        expr_stack.append((offset, FunctionNameNode(get_string(str1_id), get_string(str2_id))))
                    else:
                        expr_stack.append((offset, StringLiteralNode(get_string(str1_id))))
                    return offset + 6
                case _:
                    raise RuntimeError(f'unimplemented command 0D {subcmd:02X}')
        case 0x0F:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append((lhs[0], Cmd0FNode(lhs[1], rhs[1])))
            return offset + 1
        case 0x12:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append((lhs[0], Cmd12Node(lhs[1], rhs[1])))
            return offset + 1
        case 0x15:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append((lhs[0], Cmd15Node(lhs[1], rhs[1])))
            return offset + 1
        case 0x16:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append((lhs[0], Cmd16Node(lhs[1], rhs[1])))
            return offset + 1
        case 0x1A:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append((lhs[0], Cmd1ANode(lhs[1], rhs[1])))
            return offset + 1
        case 0x1B:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append((lhs[0], Cmd1BNode(lhs[1], rhs[1])))
            return offset + 1
        case 0x1C:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append((lhs[0], Cmd1CNode(lhs[1], rhs[1])))
            return offset + 1
        case 0x1D:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append((lhs[0], Cmd1DNode(lhs[1], rhs[1])))
            return offset + 1
        case 0x1F:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append((lhs[0], Cmd1FNode(lhs[1], rhs[1])))
            return offset + 1
        case 0x20:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append((lhs[0], Cmd20Node(lhs[1], rhs[1])))
            return offset + 1
        case 0x23:
            expr_stack.append((offset, FunctionArgsNode([])))
            return offset + 1
        case 0x24:
            i = len(expr_stack)
            while not isinstance(expr_stack[i - 1][1], FunctionArgsNode):
                i -= 1
            expr_stack[i - 1][1].children = [expr[1] for expr in expr_stack[i:]]
            del expr_stack[i:]
            args = expr_stack.pop()
            func = expr_stack.pop()
            expr_stack.append((func[0], FunctionCallNode(func[1], args[1])))
            return offset + 1
        case 0x25:
            stmt_list.append((offset, InitStatementNode()))
            return offset + 1
        case 0x26:
            stmt_list.append((offset, EndStatementNode()))
            return offset + 1
        case 0x27:
            expr = expr_stack.pop()
            stmt_list.append((expr[0], ExprStmtNode(expr[1])))
            return offset + 1
        case 0x28:
            str_id = file[offset+1] | (file[offset+2] << 8)
            stmt_list.append((offset, SpeakerStatement(get_string(str_id))))
            return offset + 3
        case 0x2B:
            stmt_list.append((offset, Cmd2BStatement(file[offset+1])))
            return offset + 2
        case 0x2C:
            stmt_list.append((offset, Cmd2CStatement(file[offset+1])))
            return offset + 2
        case 0x2F:
            str_id = file[offset+1] | (file[offset+2] << 8)
            stmt_list.append((offset, TextStatement(get_string(str_id))))
            return offset + 3
        case 0x30:
            stmt_list.append((offset, Cmd30Statement()))
            return offset + 1
        case 0x32:
            num = file[offset+1] | (file[offset+2] << 8)
            stmt_list.append((offset, Cmd32Statement(num)))
            return offset + 3
        case 0x33:
            str_id = file[offset+1] | (file[offset+2] << 8)
            stmt_list.append((offset, Cmd33Statement(get_string(str_id))))
            return offset + 3
        case 0x34:
            (str_id,) = struct.unpack_from('<H', buffer=file, offset=offset+1)
            stmt_list.append((offset, LabelMarker(get_string(str_id))))
            return offset + 3
        case 0x35:
            (branch_offset,) = struct.unpack_from('<h', buffer=file, offset=offset+1)
            stmt_list.append((offset, GotoStatement(offset + 3 + branch_offset)))
            return offset + 3
        case 0x36:
            (branch_offset,) = struct.unpack_from('<h', buffer=file, offset=offset+1)
            cond = expr_stack.pop()
            stmt_list.append((cond[0], TrueGotoStatement(cond[1], offset + 3 + branch_offset)))
            return offset + 3
        case 0x37:
            (branch_offset,) = struct.unpack_from('<h', buffer=file, offset=offset+1)
            cond = expr_stack.pop()
            stmt_list.append((cond[0], FalseGotoStatement(cond[1], offset + 3 + branch_offset)))
            return offset + 3
        case 0x45:
            stmt_list.append((offset, EndOfFileStatement()))
            return offset + 1
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
with open('../999_jp_files/root/scr/b12.fsb', 'rb') as f:
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

entrypoints = {}
while True:
    addr, name = struct.unpack_from('<LL', buffer=fsb, offset=entrypoint_dict_offset)
    entrypoint_dict_offset += 8
    if addr == 0 and name == 0:
        break
    name_end = fsb.index(0, name)
    name_str = fsb[name:name_end].decode('mskanji')
    assert addr not in entrypoints
    entrypoints[addr] = name_str
# print(entrypoints)

with open(filename, 'w', encoding='utf-8') as f:
    # Decompile all statements
    addr = 0x10
    statements = []
    expressions = []
    while len(statements) == 0 or not isinstance(statements[-1][1], EndOfFileStatement):
        addr = print_cmd(fsb, addr, expressions, statements)
    assert len(expressions) == 0
    
    for statement in statements:
        func_name = entrypoints.get(statement[0])
        if func_name is not None:
            f.write(f'function {func_name}:\n')
        f.write(f'\t/* 0x{statement[0]:04X} */ {str(statement[1])}\n')
    f.write('// There should be an "EOF" comment immediately before this comment')