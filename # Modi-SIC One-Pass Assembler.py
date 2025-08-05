# Modi-SIC One-Pass Assembler

def process_assembly_code(input_file):
    symbol_table = {}
    output=[]
    object_code_buffer = []
    forwardREF = []
    location_counter = 0x0000
    CountPerLine = 0x0000
    counter=0
    flag = 0
    Fflag = 0
    FIRST_LOC = 0
    LAST_LOC = 0
    x = 0
    cutloc=0
    last = 0
    mask_bits = ""
    forwardfound = 0
    with open(input_file, 'r',encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if len(line.split()) == 1:
                 if line.split()[0].startswith('END'):
                    object_code_buffer.append('\n'+'E ')
                    object_code_buffer.append("00"+hex(FIRST_LOC)[2:].upper()+'\n')
                    output.append("END")
                    LAST_LOC=location_counter
                    break
                 elif line.split()[0] in ('FIX', 'FLOAT', 'HIO', 'NORM', 'SIO', 'TIO'):
                        CountPerLine = location_counter+1
                        object_code = hex(get_opcode(line.split()[0]))[2:].upper()
                        object_code_buffer.append(object_code+" ")
                        output.append(hex(location_counter)[2:].upper()+" ")
                        output.append(line.split()[0]+' 0\n')
                        mask_bits+= "0"

                 elif line.split()[0] == 'RSUB':
                        CountPerLine = location_counter+3
                        opcode = get_opcode(line.split()[0])  
                        lable_loc = 0x0000
                        output.append(hex(location_counter)[2:].upper()+" ")
                        output.append(line.split()[0]+' 0\n')
                        mask_bits+= "0"
                       
                        object_code = hex(opcode)[2:].zfill(2).upper() + hex(lable_loc)[2:].upper().zfill(4)
                        object_code_buffer.append(object_code+" ")
                elif len(line.split()) == 2:
                 WORD1 = line.split()[0]
                 WORD2 = line.split()[1]
                 if WORD1 in ('BYTE', 'WORD', 'RESB', 'RESW'):
                    if WORD1 == 'BYTE':
                        if WORD2.startswith('C'):
                            CountPerLine = location_counter+3
                            value = WORD2[2:-1].encode().hex()
                            
                        elif WORD2.startswith('X'):
                            value = WORD2[2:-1]
                            CountPerLine = location_counter+1
                    elif WORD1 == 'WORD':
                        value = str(int(WORD2))
                        CountPerLine = location_counter + 3
                    elif WORD1 == 'RESB':
                        CountPerLine = location_counter + int(WORD2)
                        flag = 1
                    elif WORD1 == 'RESW':
                        CountPerLine = location_counter + int(WORD2) * 3
                    object_code_buffer.append(value)
                    flag = 1
                 else:
                    if WORD2 in ('FIX', 'FLOAT', 'HIO', 'NORM', 'SIO', 'TIO'):
                        CountPerLine = location_counter+1
                        object_code = hex(get_opcode(WORD2))[2:].upper()
                        object_code_buffer.append(object_code)
                        output.append(hex(location_counter)[2:].upper()+" ")
                        output.append(WORD1+" "+WORD2+' 0\n')
                        mask_bits+= "0"


                    elif WORD1 in ('ADD', 'AND', 'COMP', 'DIV', 'J', 'JEQ', 'JGT', 'JLT', 'JSUB', 'LDA', 'LDCH', 'LDL', 'LDX', 'MUL', 'OR', 'RD', 'RSUB', 'STA', 'STCH', 'STL', 'STSW', 'STX', 'SUB', 'TD', 'TIX', 'WD'):
                        CountPerLine = location_counter+3
                        output.append(hex(location_counter)[2:].upper()+" ")
                        opcode = get_opcode(WORD1)  
                        lable_loc = 0x0000
                        flag1 = 0
                        
                        if WORD2.startswith('#'):
                            A=WORD2
                            WORD2=int(WORD2[1:])
                            lable_loc = int(lable_loc)
                            lable_loc = f'{WORD2:04X}'
                            lable_loc = int(lable_loc)
                            flag1 = 1
                        elif WORD2 == 'X':
                            WORD2=WORD2[:-2]
                            for key, value in symbol_table.items():
                             if key == WORD2[:-1]:
                                lable_loc=value | (1 << 15)
                        else:
                         for key, value in symbol_table.items():
                          if key == WORD2:
                            lable_loc = value    
                            Fflag = 0
                            break
                          else :
                            Fflag = 1
                        if Fflag == 1:
                            if WORD2 not in forwardREF:
                             forwardREF.append(WORD2) 
                             forwardREF.append(hex(location_counter+1)[2:].upper())
                                 
                            elif WORD2 in forwardREF:
                               forwardREF.append(hex(location_counter+1)[2:].upper())    

                        if flag1 == 1 :
                         output.append(WORD1+" "+A+' 0\n')
                         mask_bits+= "0"
                        else :
                         output.append(WORD1+" "+WORD2+' 1\n')
                         mask_bits+= "1"
                        object_code = hex(opcode)[2:].zfill(2).upper() + hex(lable_loc)[2:].upper().zfill(4)
                        object_code_buffer.append(object_code+" ")

                       
                elif len(line.split()) == 3:
                 WORD1 = line.split()[0]
                 WORD2 = line.split()[1]
                 WORD3 = line.split()[2]
                 if WORD2.startswith('START'):
                    res=LAST_LOC-FIRST_LOC
                    location_counter = int(line.split()[2],16)
                    start_loc = location_counter
                    object_code_buffer.append('H ')
                    object_code_buffer.append(line.split()[0]+"00 ")
                    object_code_buffer.append("00"+hex(location_counter)[2:]+'\n')
                    object_code_buffer.append("T "+str(hex(location_counter)[2:].upper()).rjust(6,'0')+" ")
                    output.append(WORD3+" "+WORD1+" "+WORD2+" "+WORD3+"\n")
                    FIRST_LOC= location_counter
                

                 elif WORD2 in ('BYTE', 'WORD', 'RESB', 'RESW'):
                    if WORD2 == 'BYTE':
                        if WORD3.startswith('C'):
                            value = WORD3[2:-1].encode().hex().upper()+" "
                            CountPerLine = location_counter+len(WORD3[2:-1])
                            output.append(hex(location_counter)[2:]+" ")
                            output.append(WORD1+" "+WORD2+" "+WORD3+" 0\n")
                            mask_bits+= "0"
                        elif WORD3.startswith('X'):
                            value = WORD3[2:-1]
                            CountPerLine = location_counter+1
                        object_code_buffer.append(value)

                    elif WORD2 == 'WORD':
                        value = WORD3.zfill(6)+" "
                        CountPerLine = location_counter + 3
                        output.append(hex(location_counter)[2:]+" ")
                        output.append(WORD1+" "+WORD2+" "+WORD3+" 0"'\n')
                        mask_bits+= "0"
                        object_code_buffer.append(value)
                    elif WORD2 == 'RESB':
                        CountPerLine = location_counter + int(WORD3)
                        if flag == 0 : 
                            cutloc=location_counter
                        flag = 1
                        output.append(hex(location_counter)[2:].upper()+" ")
                        output.append(WORD1+" "+WORD2+" "+WORD3+'\n')
                    elif WORD2 == 'RESW':
                        
                        CountPerLine = location_counter + int(WORD3) * 3
                        if flag == 0 : 
                            cutloc=location_counter

                        flag = 1
                        output.append(hex(location_counter)[2:].upper()+" ")
                        output.append(WORD1+" "+WORD2+" "+WORD3+'\n')


                 elif WORD2 in ('ADD', 'AND', 'COMP', 'DIV', 'J','JEQ', 'JGT', 'JLT', 'JSUB', 'LDA', 'LDCH', 'LDL', 'LDX', 'MUL', 'OR', 'RD', 'RSUB', 'STA', 'STCH', 'STL', 'STSW', 'STX', 'SUB', 'TD', 'TIX', 'WD'):
                        CountPerLine = location_counter+3
                        immediate_flag = '0'
                        lable_loc = 0x0000
                        opcode = get_opcode(WORD2)  
                        if WORD3.startswith('#'):
                            immediate_flag = '1'
                            WORD2=WORD2[1:]
                        elif WORD3 == 'X':
                            X_flag = '1'
                            opcode+=0x1
                            WORD3=WORD3[:-2]
                        else:
                         for key, value in symbol_table.items():
                          if key == WORD3:
                            lable_loc = value    
                            Fflag = 0
                            break
                          else :
                            Fflag = 1

                        if Fflag == 1 and WORD3 not in forwardREF :
                            forwardREF.append(WORD3)     
                            forwardREF.append(hex(location_counter+1)[2:].upper())   
              
                        object_code = hex(opcode)[2:].zfill(2).upper() + hex(lable_loc)[2:].upper().zfill(4)
                        if flag == 1:
                            object_code_buffer[4] = hex(cutloc-start_loc)[2:].upper().rjust(2,'0')+" "+ object_code_buffer[4]
                            start_loc = hex(cutloc-start_loc)[2:].upper().rjust(2,'0')
                            object_code_buffer.append("\nT ") 
                            last = location_counter
                            flag = 0
                        if WORD1 in forwardREF:
                            for word in range(len(forwardREF) -1):
                               if forwardREF[word] == WORD1:
                                 if forwardREF[word+2].isdigit():
                                  object_code_buffer.append("\nT "+forwardREF[word+1].rjust(6,'0')+" 02 000 "+ str(hex(location_counter)[2:].upper()))  
                                  object_code_buffer.append("\nT "+forwardREF[word+2].rjust(6,'0')+" 02 000 "+ str(hex(location_counter)[2:].upper())+" \nT ")
                                  print(mask_bits)
                                  mask_bits=""

                                 else:
                                  object_code_buffer.append("\nT "+forwardREF[word+1].rjust(6,'0')+" 02 000 "+ str(hex(location_counter)[2:].upper())+" \nT ")
                                  print(mask_bits)
                                  mask_bits=""

                        object_code_buffer.append(str(hex(location_counter)[2:].upper()).rjust(6,'0')+' '+object_code+" ")
                        output.append(hex(location_counter)[2:].upper()+" ")
                        output.append(WORD1+" "+WORD2+" "+WORD3+' 1\n')
                        mask_bits+= "1"
                        
                 elif WORD1 in ('ADD', 'AND', 'COMP', 'DIV', 'J','JEQ', 'JGT', 'JLT', 'JSUB', 'LDA', 'LDCH', 'LDL', 'LDX', 'MUL', 'OR', 'RD', 'RSUB', 'STA', 'STCH', 'STL', 'STSW', 'STX', 'SUB', 'TD', 'TIX', 'WD'):
                        CountPerLine = location_counter+3
                        opcode = get_opcode(WORD1)  
                        lable_loc = 0x0000
                        output.append(hex(location_counter)[2:].upper()+" ")
                        output.append(WORD1+" "+WORD2+" "+WORD3+' 1\n')
                        mask_bits+= "1"
                        if WORD3.startswith('#'):
                            opcode+=0x1
                            WORD1=WORD1[1:]
                        elif WORD3 == 'X':
                            WORD3=WORD3[:-2]
                            for key, value in symbol_table.items():
                             if key == WORD2[:-1]:
                                lable_loc=value | (1 << 15)
                        else:
                         for key, value in symbol_table.items():
                          if key == WORD3:
                            lable_loc = value    
                            Fflag = 0
                            break
                          else :
                            Fflag = 1
                        if Fflag == 1 and WORD3 not in forwardREF :
                            forwardREF.append(WORD3)   
                              
                       
                        object_code = hex(opcode)[2:].zfill(2).upper() + hex(lable_loc)[2:].upper().zfill(4)
                        if flag == 1:
                            object_code_buffer.append("\nT ")
                            flag = 0
                        object_code_buffer.append(object_code+" ")

                print(symbol_table)
                print("line number -->", x)  
                x+=1 

                if line.split()[0] in ('END','RESW','RESB','WORD','BYTE','ADD', 'AND', 'COMP', 'DIV', 'J', 'JEQ', 'JGT', 'JLT', 'JSUB', 'LDA', 'LDCH', 'LDL', 'LDX', 'MUL', 'OR', 'RD', 'RSUB', 'STA', 'STCH', 'STL', 'STSW', 'STX', 'SUB', 'TD', 'TIX', 'WD','FIX', 'FLOAT', 'HIO', 'NORM', 'SIO', 'TIO'):
                    location_counter  = CountPerLine
                # Update symbol table and location counter
                elif line.split()[0] not in ('END','RESW','RESB','WORD','BYTE','ADD', 'AND', 'COMP', 'DIV', 'J', 'JEQ', 'JGT', 'JLT', 'JSUB', 'LDA', 'LDCH', 'LDL', 'LDX', 'MUL', 'OR', 'RD', 'RSUB', 'STA', 'STCH', 'STL', 'STSW', 'STX', 'SUB', 'TD', 'TIX', 'WD','FIX', 'FLOAT', 'HIO', 'NORM', 'SIO', 'TIO','COPY'):
                    symbol = line.split()[0]
                    if symbol not in symbol_table:
                     symbol_table[symbol] = location_counter 
                    location_counter  = CountPerLine
            
               
            # Generate symbol table file
            with open('symbolTable.txt', 'w') as sym_file:
                for symbol, address in symbol_table.items():
                    sym_file.write(symbol + '\t' + hex(address)[2:].upper() + '\n')
            
            # Generate HTE records (objectcode.txt)
            with open('objectcode.txt', 'w') as obj_file:
                for record in object_code_buffer:
                    obj_file.write(str(record))

            with open('output.txt', 'w') as out_file:
                for things in output:
                    out_file.write(str(things))
            
       
            print("FORWARD REF LIST",forwardREF)
            print('Assembly process completed successfully.')


def get_opcode(instruction):
    match instruction:
        case 'ADD': return 0x18
        case 'AND': return 0x40
        case 'COMP': return 0x28
        case 'DIV':return 0x24
        case 'J':return 0x3C
        case 'JEQ':return 0x30
        case 'JGT':return 0x34
        case 'JLT':return 0x38
        case 'JSUB':return 0x48
        case 'LDA':return 0x00
        case 'LDCH':return 0x50
        case 'LDL':return 0x08
        case 'LDX':return 0x04
        case 'MUL':return 0x20
        case 'OR':return 0x44
        case 'RD':return 0xD8
        case 'RSUB':return 0x4C
        case 'STA':return 0x0C
        case 'STCH':return 0x54
        case 'STL':return 0x14
        case 'STSW':return 0xE8
        case 'STX':return 0x10
        case 'SUB':return 0x1C
        case 'TD':return 0xE0
        case 'TIX':return 0x2C
        case 'WD':return 0xDC
        case 'FIX':return 0xC4
        case 'FLOAT':return 0xC0
        case 'HIO':return 0xF4
        case 'NORM':return 0xC8
        case 'SIO':return 0xF0
        case 'TIO':return 0xF8
    return instruction
# Example usage
process_assembly_code('in.txt')