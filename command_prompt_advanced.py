import sys
from getch import getch
import truthcoin_api
import os
import copy
rows, columns = os.popen('stty size', 'r').read().split()
previous_commands=[]
zeroto9=['0','1','2','3','4','5','6','7','8','9']
atoz=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
AtoZ=map(lambda x: x.capitalize(), atoz)
def delete_letter():
    sys.stdout.write('\x08')
    sys.stdout.write(' ')
    sys.stdout.write('\x08')
def delete_to_end_of_line(DB, skip=False):
    sys_print('\033[K')
    if not skip:
        DB['yank']=DB['command'][DB['string_position']:]
        DB['command']=DB['command'][:DB['string_position']]
def yank(DB):
    for l in DB['yank']:
        letter(DB, l)
def move_left(): return sys_print('\033[1D')
def backspace(DB):
    if not DB['string_position']==0:
        c=DB['command']
        s=DB['string_position']
        DB['command']=c[:s-1]+c[s:]
        move_left()
        delete_to_end_of_line(DB, True)
        sys.stdout.write(c[s:])
        DB['string_position']-=1
        set_cursor(DB)
def forward_delete(DB):
    if not DB['string_position']>=len(DB['command']):
        DB['string_position']+=1
        backspace(DB)
def letter(DB, l):
    DB['command']=DB['command'][:DB['string_position']]+l+DB['command'][DB['string_position']:]
    word(DB, 0)
    DB['string_position']+=1
    set_cursor(DB)
def sys_print(txt): return sys.stdout.write(txt)
def set_cursor(DB):
    sys_print('\033['+str(DB['output_lengths']+len(DB['previous_commands'])+1)+';'+str(DB['string_position']+1)+'H')
def word(DB, n):
    for i in range(len(DB['command'])):
        delete_letter()
    if n!=0:
        DB['command_pointer']+=n
        DB['command']=DB['previous_commands'][DB['command_pointer']]
    sys.stdout.write(DB['command'])
    if DB['string_position']>=DB['command']:
        DB['string_position']=len(DB['command'])
def up_arrow(DB):
    if not DB['command_pointer']==0:
        word(DB, -1)
    DB['string_position']=len(DB['command'])
def down_arrow(DB):
    if DB['command_pointer']<len(DB['previous_commands'])-1:
        word(DB, 1)
def right_arrow(DB):
    if not DB['string_position']>=len(DB['command']):
        DB['string_position']+=1
        sys_print('\033[1C')
def left_arrow(DB):
    if not DB['string_position']==0:
        DB['string_position']-=1
        move_left()
def front_of_line(DB):
    DB['string_position']=0
    set_cursor(DB)
def end_of_line(DB):
    DB['string_position']=len(DB['command'])
    set_cursor(DB)
def chunks_of_width(width, s):
    if len(s)<width: return [s]
    else: return [s[:width]]+chunks_of_width(width, s[width:])
def enter(DB):
    print('')
    DB['previous_commands'].append(DB['command'])
    c=copy.deepcopy(DB['command'])
    c=c.split(' ')
    if len(c)>0: 
        DB['command']=c[0]
        DB['args']=c[1:]
        response=truthcoin_api.Do_func(DB)
        if type(response)==str:
            response_chunks=chunks_of_width(100, response)
            for r in response_chunks:
                print(r)
                DB['output_lengths']+=1
    else: 
        error('crazy')

    if len(DB['previous_commands'])>1000:
        DB['previous_commands'].remove(DB['previous_commands'][0])
    DB['command']=''
    DB['command_pointer']=len(DB['previous_commands'])
    DB['string_position']=0
    set_cursor(DB)
def special_keys(DB):
    key = ord(getch())
    #print('special key 1: ' +str(key))
    
    key = ord(getch())
    #print('special key 2: ' +str(key))
    ignore_undefined(key, {'51':forward_delete,
                   '65':up_arrow,
                   '66':down_arrow,
                   '67':right_arrow,
                   '68':left_arrow},
             DB)
letters={
    '1':front_of_line,
    '5':end_of_line,#ctrl+e
    '6':right_arrow,#ctrl+f
    '14':down_arrow,#ctrl+n
    '2':left_arrow,#ctrl+b
    '16':up_arrow,#ctrl+p
    '11':delete_to_end_of_line,#ctrl+k
    '127':backspace,
    '4':forward_delete,#ctrl+d
    '25':yank,#ctrl+y
    '10': enter,
    '27': special_keys,
    '46':lambda DB: letter(DB, '.'),
    '32':lambda DB: letter(DB, ' '),
    '40':lambda DB: letter(DB, '('),
    '41':lambda DB: letter(DB, ')'),
    '44':lambda DB: letter(DB, ','),
    '93':lambda DB: letter(DB, ']'),
    '91':lambda DB: letter(DB, '['),
    '63':lambda DB: letter(DB, '?')}
def ignore_undefined(key, letters, DB): letters.get(str(key), (lambda DB: 42))(DB)
def clear_screen(): 
    sys_print('\033[2J')
    sys_print('\033[H')
def helper(DB, l, i, m): return (lambda DB: letter(DB, l[i-m]))
def main(DB):
    for i in range(48, 58):
        letters[str(i)]=helper(DB, zeroto9, i, 48)
    for i in range(97, 123):
        letters[str(i)]=helper(DB, atoz, i, 97)
    for i in range(65, 91):
        letters[str(i)]=helper(DB, AtoZ, i, 65)
        letters[str(i)]=lambda DB: letter(DB, AtoZ[i-65])
    DB['command']=''
    DB['previous_commands']=[]
    DB['command_pointer']=0
    DB['string_position']=0
    DB['yank']=''
    DB['output_lengths']=0
    DB['args']=[]
    clear_screen()
    while True:
        key = ord(getch())
        #print('key: ' +str(key))
        ignore_undefined(key, letters, DB)
