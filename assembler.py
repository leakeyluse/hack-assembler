import os
import sys

#c1 c2 c3 c4 c5 c6
validCompPatterns = {
    '0':'0101010', 
    '1':'0111111',
    '-1':'0111010',
    'D':'0001100',
    'A':'0110000',
    '!D':'0001101',
    '!A':'0110001',
    '-D':'0001111',
    '-A':'0110011',
    'D+1':'0011111',
    'A+1':'0110111',
    'D-1':'0001110',
    'A-1':'0110010',
    'D+A':'0000010',
    'D-A':'0010011',
    'A-D':'0000111',
    'D&A':'0000000',
    'D|A':'0010101',
    'M':'1110000',
    '!M':'1110001',
    '-M':'1110011',
    'M+1':'1110111',
    'M-1':'1110010',
    'D+M':'1000010',
    'M+D':'1000010',
    'D-M':'1010011',
    'M-D':'1000111',
    'D&M':'1000000',
    'D|M':'1010101'
}

#d1 d2 d3
validDestPatterns = {
    'null':'000',
    'M':'001',
    'D':'010',
    'MD':'011',
    'A':'100',
    'AM':'101',
    'AD':'110',
    'AMD':'111'
}

#j1 j2 j3
validJmpPatterns =  {
    'null':'000',
    'JGT':'001',
    'JEQ':'010',
    'JGE':'011',
    'JLT':'100',
    'JNE':'101',
    'JLE':'110',
    'JMP':'111'
}

#predefined symbols and RAM locations
symbolTable = {
    'SP':0,
    'LCL':1,
    'ARG':2,
    'THIS':3,
    'THAT':4,
    'R0':0,
    'R1':1,
    'R2':2,
    'R3':3,
    'R4':4,
    'R5':5,
    'R6':6,
    'R7':7,
    'R8':8,
    'R9':9,
    'R10':10,
    'R11':11,
    'R12':12,
    'R13':13,
    'R14':14,
    'R15':15,
    'SCREEN':16384,
    'KBD':24576
} 

#user defined symbols
userVars = {}

def parse(command):  
    #strip all whitespace
    command = ''.join(command.split())

    #return None for empty line
    if not command:
        return None

    #return None for comment
    if command[0:2] == "//":
        return None

    #remove trailing comment
    command = command.rsplit('//',1)[0]
    
    #Data structure to hold the parsed fields for the command
    s = {}

    s['instructionType'] = ''
    s['value'] = ''
    s['dest'] = ''
    s['comp'] = ''
    s['jmp'] = ''  

    #Extract tokens from command
    for char in command:        
        if char == "@":
            s['instructionType'] = "A"
            s['value'] = command.rsplit('@',1)[1]
        if char == ";" or char == "=":
            s['instructionType'] = "C"
            if command.find('=') > -1:
                s['dest'] =  command.rsplit('=',1)[0]
                s['comp'] =  command.rsplit('=',1)[1]
            else:
                s['value'] =  command.rsplit(';',1)[0]
                s['jmp'] =  command.rsplit(';',1)[1]        
        if char == '(':
            if not command[1].isdigit() and command.endswith(')'):
                s['instructionType'] = "L"
                s['value'] =  command[1:-1]
    return s    

def runAssembler(fileName):
    global symbolTable
    global userVars
    global validJmpPatterns
    global validDestPatterns
    global validCompPatterns

    ir = []
    programAddress = 0
    ramAddress = 16
    #Pass 1 of the assembler to generate the intermediate data structure
    with open(fileName, 'r') as f:
        for command in f:  
            s = parse(command)
            if s is not None:
                #Add to user defined symbols
                if s['instructionType'] == "L":
                    userVars[s['value']] = programAddress
                else:                    
                    programAddress += 1
                ir.append(s.copy())
     
    #Pass 2 of assembler to generate the machine code from the intermediate data structure
    machineCode = []
    for s in ir:
        if s['instructionType'] == "A":
            if s['value'].isdigit():
                machineCode.append('0' + format(int(s['value']), '015b'))
            if s['value'] in symbolTable:
                machineCode.append('0' + format(symbolTable[s['value']], '015b'))
            if s['value'] in userVars:
                machineCode.append('0' + format(userVars[s['value']], '015b'))
            else:
                if not s['value'].isdigit() and not s['value'] in symbolTable:
                    userVars[s['value']] = ramAddress
                    machineCode.append('0' + format(userVars[s['value']], '015b'))
                    ramAddress += 1
        elif s['instructionType'] == "C":
            if s['dest'] != "":
                machineCode.append('111'+ validCompPatterns[s['comp']] + validDestPatterns[s['dest']] + '000')
            else:
                machineCode.append('111' + validCompPatterns[s['value']] + '000' + validJmpPatterns[s['jmp']])
        elif s['instructionType'] == "L":
            pass
        else:
            return
    return machineCode
 
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Python assembler.py file-name.asm")
    else:
        print("Assembling file:", sys.argv[1])
        fileNameMinusExtension, _ = os.path.splitext(sys.argv[1])
        outputFile = fileNameMinusExtension + '.hack'
        machineCode = runAssembler(sys.argv[1])
        if machineCode:
            print('Machine code generated successfully')
            print('Writing output to file:', outputFile)
            f = open(outputFile, 'w')
            for s in machineCode:
                f.write('%s\n' %s)
            f.close()
        else:
            print('Error generating machine code')  