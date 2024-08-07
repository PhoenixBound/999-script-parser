#!/usr/bin/env python3

import bisect
import struct
from typing import *

# Classes representing specific script commands in 999's bytecode engine

class IntLiteralNode:
    value: int
    def __init__(self, value: int):
        self.value = value
    def __str__(self):
        v = self.value
        if (v & 0x3FF) != 0:
            return str(v / 0x400)
        else:
            return str(v // 0x400)
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
        return f"{self.lhs} <= {self.rhs}"

class Cmd1DNode(BooleanExprNode):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        return f"{self.lhs} >= {self.rhs}"

class Cmd1ENode(BooleanExprNode):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        # It's either > or <
        return f"{self.lhs} < {self.rhs}"

class Cmd1FNode(BooleanExprNode):
    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self):
        # It's either > or <
        return f"{self.lhs} > {self.rhs}"

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
        return f'bundleStart {hex(self.arg)}'

class Cmd2CStatement(StatementNode):
    def __init__(self, arg):
        super().__init__()
        self.arg = arg
    def __str__(self):
        return f'bundleEnd {hex(self.arg)}'

class Cmd30Statement(StatementNode):
    def __init__(self):
        super().__init__()
    def __str__(self):
        # return?
        return f'return;'

class Cmd32Statement(StatementNode):
    def __init__(self, arg):
        super().__init__()
        self.arg = arg
    def __str__(self):
        return f'page {self.arg:04d}'

class Cmd33Statement(StatementNode):
    def __init__(self, arg: str):
        super().__init__()
        self.arg = arg
    def __str__(self):
        return f'goto "{self.arg}"'

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
    def is_conditional_branch(self):
        return False
    def __str__(self):
        return f'branch 0x{self.branch_offset:X};'

class TrueGotoStatement(GotoStatement):
    def __init__(self, condition: BooleanExprNode, branch_offset: int):
        super().__init__(branch_offset)
        self.condition = condition
    def is_conditional_branch(self):
        return True
    def __str__(self):
        return f'if ({self.condition}) branch 0x{self.branch_offset:X};'

class FalseGotoStatement(GotoStatement):
    def __init__(self, condition: BooleanExprNode, branch_offset: int):
        super().__init__(branch_offset)
        self.condition = condition
    def is_conditional_branch(self):
        return True
    def __str__(self):
        return f'unless ({self.condition}) branch 0x{self.branch_offset:X};'

class EndOfFileStatement(StatementNode):
    def __init__(self):
        super().__init__()
    def __str__(self):
        return '/* EOF */'

# Classes representing higher level control flow stuff

class LoopStatement(StatementNode):
    """
    Represents an infinite loop, like `loop` in Rust
    """
    def __init__(self, loop_body: List[StatementNode]):
        super().__init__()
        self.loop_body = loop_body

    def __str__(self):
        # Especially for higher-level nodes like this, this __str__ method does
        # not have to match the exact syntax that the program will have in the
        # end. It just has to be understandable for debugging.
        s = 'loop { '
        for stmt in loop_body:
            s += str(stmt)
            s += ' '
        s += '}'
        return s

class IfStatement(StatementNode):
    def __init__(self, condition: BooleanExprNode, if_body: List[StatementNode], \
                 else_body: Optional[List[StatementNode]]):
        super().__init__()
        self.condition = condition
        self.if_body = if_body
        # There should be no difference in codegen between "else if" and "elif".
        # But... there are switch statements, which look like ifs that end with
        # a completely empty else block. I'll have to deal with those another
        # time.
        self.else_body = else_body

    def __str__(self):
        s = f'if ({self.condition}) {{ '
        for stmt in if_body:
            s += str(stmt)
            s += ' '
        if else_body is not None:
            s += '} else { '
            for stmt in else_body:
                s += str(stmt)
                s += ' '
        s += '}'
        return s

# Control flow graph

class Block:
    def __init__(self):
        self.statements = []
        self.fallthrough_target = None
        self.branch_target = None
    
    def append(self, stmt):
        self.statements.append(stmt)
        
    def __str__(self):
        s = f"Block(fallthrough_target={self.fallthrough_target}, branch_target={self.branch_target}, code='"
        for stmt in self.statements:
            t = str(stmt)
            # Do any escaping here that seems appropriate
            s += t
            s += "\\n"
        s += "')"
        return s

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
                    i = 0
                    num = 0
                    while (file[offset+2+i] & 0x80) != 0 and i < 4:
                        num |= (file[offset+2+i] & 0x7F) << (7 * i)
                        i += 1
                    num |= file[offset+2+i] << (7 * i)
                    i += 1
                    
                    sign = num & 1
                    num >>= 1
                    if sign != 0:
                        raise RuntimeError(f"Negative integer literal commands *do* exist! At offset {offset:04X}")
                        num = -num - 1
                    # These are only errors because they'll make matching recompilation more difficult.
                    # And I just want Python to shout at me loudly and excitedly when this happens.
                    if num < -0x80000000 or num > 0x7FFFFFFF:
                        raise RuntimeError(f"The padding bits on the integer literal at {offset:04X} aren't 0?!?!")
                    if (num & 0x3FF) != 0:
                        raise RuntimeError(f"Fractional number found at {offset:04X}?!?!")
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
                    raise RuntimeError(f'unimplemented command 0D {subcmd:02X} at offset {offset:04X}')
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
        case 0x1E:
            rhs = expr_stack.pop()
            lhs = expr_stack.pop()
            expr_stack.append((lhs[0], Cmd1ENode(lhs[1], rhs[1])))
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
        # Haven't seen this get used yet
        # case 0x36:
        #     (branch_offset,) = struct.unpack_from('<h', buffer=file, offset=offset+1)
        #     cond = expr_stack.pop()
        #     stmt_list.append((cond[0], TrueGotoStatement(cond[1], offset + 3 + branch_offset)))
        #     return offset + 3
        case 0x37:
            (branch_offset,) = struct.unpack_from('<h', buffer=file, offset=offset+1)
            cond = expr_stack.pop()
            stmt_list.append((cond[0], FalseGotoStatement(cond[1], offset + 3 + branch_offset)))
            return offset + 3
        case 0x45:
            stmt_list.append((offset, EndOfFileStatement()))
            return offset + 1
        case _:
            raise RuntimeError(f'unimplemented command {cmd:02X} at offset {offset:04X}')
    raise RuntimeError('I forgot a return statement somewhere')

def get_string(id):
    assert id < str_count
    (string_addr,) = struct.unpack_from('<L', buffer=fsb, offset=str_table_offset + ptr_size*id)
    string_end_addr = fsb.index(0, string_addr)
    # Characters like ⑲ don't exist in the 'shift_jis' encoding, so the distinction is important
    return fsb[string_addr:string_end_addr].decode('mskanji')

fsb = None
with open('../999_files/root/scr/b32.fsb', 'rb') as f:
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
    label_table_offset, variable_table_offset) \
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
    
    
    # Get the list of all the places where a node of the CFG starts
    leaders = set(entrypoints)
    for (i, (addr, stmt)) in enumerate(statements):
        if stmt.is_branch():
            leaders.add(stmt.branch_offset)
            # The fallthrough to the next statement after a conditional branch also begins a node
            if stmt.is_conditional_branch():
                leaders.add(statements[i + 1][0])
    leaders = list(leaders)
    leaders.sort()
    
    # print(leaders)
    # raise RuntimeError("that's all the leaders")

    statements = dict(statements)
    
    # Create and populate blocks (control flow graph nodes) with statements
    blocks = []
    i = 0
    statements_iter = iter(statements.items())
    addr, stmt = next(statements_iter)
    for i in range(len(leaders)):
        block = Block()
        assert addr == leaders[i]
        while (i != len(leaders) - 1 and addr < leaders[i + 1]) or \
              (i == len(leaders) - 1 and not isinstance(stmt, EndOfFileStatement)):
            block.append(stmt)
            addr, stmt = next(statements_iter)
        # Add references to other blocks
        last_stmt = block.statements[-1]
        # Add fallthrough reference for blocks that end with normal statements and conditional branches
        if (last_stmt.is_branch() and last_stmt.is_conditional_branch()) or \
           (not last_stmt.is_branch() and not isinstance(last_stmt, EndStatementNode)):
            block.fallthrough_target = i + 1
            assert 0 <= block.fallthrough_target < len(leaders)
        if last_stmt.is_branch():
            block.branch_target = bisect.bisect_left(leaders, last_stmt.branch_offset)
            assert leaders[block.branch_target] == last_stmt.branch_offset
        blocks.append(block)
        
        # DEBUG
        # print(f'BLOCK {i} (from addr {addr:04X})')
        # print(block)
        # input()
        # END DEBUG
    del addr
    del stmt
    del statements_iter
    del i
    
    # for (i, block) in enumerate(blocks):
    #     print('BLOCK', i)
    #     print(block)
    
    # raise RuntimeError("We got this far")
    
    for (addr, statement) in statements.items():
        func_name = entrypoints.get(addr)
        if func_name is not None:
            f.write(f'function {func_name}:\n')
        f.write(f'\t/* 0x{addr:04X} */ {str(statement)}\n')
    f.write('// There should be an "EOF" comment immediately before this comment')
