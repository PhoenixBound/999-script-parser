#!/usr/bin/env python3

import struct

def print_cmd(file, offset, out):
    cmd = file[offset]
    match cmd:
        case 0x07:
            out.write('not ')
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
                    out.write(hex(num) + ' ')
                    return offset + 2 + i
                case 0xF4:
                    (str1_id, str2_id) = struct.unpack_from('<HH', buffer=file, offset=offset+2)
                    if str2_id != 0:
                        out.write(f'{get_string(str1_id)}.{get_string(str2_id)} ')
                    else:
                        out.write(f'"{get_string(str1_id)}" ')
                    return offset + 6
                case _:
                    raise RuntimeError(f'unimplemented command 0D {subcmd:02X}')
        case 0x0F:
            out.write('cmd0F ')
            return offset + 1
        case 0x12:
            out.write('cmd12 ')
            return offset + 1
        case 0x15:
            out.write('cmd15 ')
            return offset + 1
        case 0x1A:
            out.write('cmd1A ')
            return offset + 1
        case 0x1B:
            out.write('cmd1B ')
            return offset + 1
        case 0x20:
            out.write('cmd20\n')
            return offset + 1
        case 0x23:
            out.write('args ')
            return offset + 1
        case 0x24:
            out.write('callfunc ')
            return offset + 1
        case 0x25:
            out.write('init_stack_stuff\n')
            return offset + 1
        case 0x26:
            out.write('bye\n')
            return offset + 1
        case 0x27:
            out.write('drop\n')
            return offset + 1
        case 0x28:
            str_id = file[offset+1] | (file[offset+2] << 8)
            out.write(f'speaker "{get_string(str_id)}"\n')
            return offset + 3
        case 0x2B:
            out.write(f'cmd2B {file[offset+1]:02X}\n')
            return offset + 2
        case 0x2C:
            out.write(f'cmd2C {file[offset+1]:02X}\n')
            return offset + 2
        case 0x2F:
            str_id = file[offset+1] | (file[offset+2] << 8)
            out.write(f'text "{get_string(str_id)}"\n')
            return offset + 3
        case 0x30:
            out.write(f'cmd30\n')
            return offset + 1
        case 0x32:
            num = file[offset+1] | (file[offset+2] << 8)
            out.write(f'cmd32 {num}\n')
            return offset + 3
        case 0x34:
            (str_id,) = struct.unpack_from('<H', buffer=file, offset=offset+1)
            out.write(f'cmd34 "{get_string(str_id)}"\n')
            return offset + 3
        case 0x35:
            branch_offset = file[offset+1] | (file[offset+2] << 8)
            out.write(f'branch {branch_offset:+d}\n')
            return offset + 3
        case 0x36:
            branch_offset = file[offset+1] | (file[offset+2] << 8)
            out.write(f'branch_if_false {branch_offset:+d}\n')
            return offset + 3
        case 0x37:
            branch_offset = file[offset+1] | (file[offset+2] << 8)
            out.write(f'branch_if_true {branch_offset:+d}\n')
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
with open('../999_files/root/scr/a01.fsb', 'rb') as f:
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
        f.write(f'[[{entrypoint[1]}]]\n')
        
        addr = entrypoint[0]
        while fsb[addr] != 0x26:
            addr = print_cmd(fsb, addr, f)
        
        f.write('bye\n\n')

    f.write('// done')