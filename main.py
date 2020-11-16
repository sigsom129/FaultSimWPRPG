#Sig's Branch
import sys
import csv
import itertools

# Class used to store information for a wire
class Node(object):
    def __init__(self, name, value, gatetype, innames, gateinput, fgate, fgateSA):
        self.name = name  # string
        self.value = value  # char: '0', '1', 'U' for unknown
        self.gatetype = gatetype  # string such as "AND", "OR" etc
        self.interms = []  # list of nodes (first as strings, then as nodes), each is a input wire to the gatetype
        self.innames = innames  # helper string to temperarily store the interms' names, useful to find all the interms nodes and link them
        self.is_input = False  # boolean: true if this wire is a primary input of the circuit
        self.is_output = False  # boolean: true if this wire is a primary output of the circuit
        self.gateinput = gateinput # the input for the gates
        self.fgate = ""   # Faulty input into gate
        self.fgateSA = "-1"   # Fault type
        
    def set_value(self, v):
        self.value = v

    def display(self):  # print out the node nicely on one line

        if self.is_input:
            # nodeinfo = f"input:\t{str(self.name[4:]):5} = {self.value:^4}"
            nodeinfo = f"input:\t{str(self.name):5} = {self.value:^4}"
            print(nodeinfo)
            return
        elif self.is_output:
            nodeinfo = f"output:\t{str(self.name):5} = {self.value:^4}"
        else:  # internal nodes
            nodeinfo = f"wire:  \t{str(self.name):5} = {self.value:^4}"

        interm_str = " "
        interm_val_str = " "
        for i in self.interms:
            interm_str += str(i.name) + " "
            interm_val_str += str(i.value) + " "

        nodeinfo += f"as {self.gatetype:>5}"
        nodeinfo += f"  of   {interm_str:20} = {interm_val_str:20}"

        print(nodeinfo)
        return

        # calculates the value of a node based on its gate type and values at interms

    def calculate_value(self):
        count0 = 0
        count1 = 0
        countU = 0

        # for i in self.interms:  # skip calculating unless all interms have specific values 1 or 0
        #     if i.value != "0" and i.value !="1":
        #         return "U"
        
        # - If there is a fault over gate, modifiy calucation to account for failure
        # duplicate interms localy to not effect other calcuations
        input_values = []
        for current_input in self.interms:
            if self.fgate == current_input.name:
                input_values.append(self.fgateSA)
            else:
                input_values.append(current_input.value)
        

        #done
        if self.gatetype == "AND":
            for i in input_values:
                if i == "0":
                    count0 += 1
                if i == "U":
                    countU += 1
                if i == "1":
                    count1 += 1
                if count0 > 0:
                    val = "0"
                if count0 == 0 and count1 == 0:
                    val = "U"
                if count0 == 0 and countU == 0:
                    val = "1"
                if count0 == 0 and count1 > 0 and countU > 0:
                    val = "U"
            self.value = val
            return val
        #done
        elif self.gatetype == "OR":
            for i in input_values:
                if i == "0":
                    count0 += 1
                if i == "U":
                    countU += 1
                if i == "1":
                    count1 += 1
                if count1 > 0:  # 1 ORed with anything is a 1
                    val = "1"
                if count1 == 0 and countU > 0:
                    val = "U"
                if count0 > 0 and count1 == 0 and countU == 0:
                    val = "0"
            self.value = val
            return val
        #done
        elif self.gatetype == "NAND":
            for i in input_values:
                if i == "0":
                    count0 += 1
                if i == "U":
                    countU += 1
                if i == "1":
                    count1 += 1
                if count0 > 0:
                    val = "1"
                if count0 == 0 and count1 == 0:
                    val = "U"
                if count0 == 0 and countU == 0:
                    val = "0"
                if count0 == 0 and count1 > 0 and countU > 0:
                    val = "U"
            self.value = val
            return val
        #done
        elif self.gatetype == "NOT":
            for i in input_values:
                if i == "U":
                    val = "U"
                    return val
                else:
                    val = input_values[0]
                    self.value = str(1-int(val))
                    return val
            self.value = val
            return val
        #done
        elif self.gatetype == "XOR":
            for i in input_values:
                if i == "U":
                    countU += 1
                    val = "U"
                    return val
                elif i == "0":
                    count0 += 1
                    val = count0 % 2
                    val = str(val)
                elif i == "1":
                    count1 += 1
                    val = count1 % 2
                    val = str(val)
            self.value = val
            return val 
        #done
        elif self.gatetype == "XNOR":
            for i in input_values:
                if i == "U":
                    count1 += 1
                    val = "U"
                    return val
                elif i == "0":
                    count0 += 1
                    output = count0 % 2
                    val = str(1-output)   
                elif i == "1":
                    count1 += 1
                    val = count1 % 2
                    val = str(1- val)
            self.value = val
            return val
        #done
        elif self.gatetype == "NOR":
            for i in input_values:
                if i == "0":
                    count0 += 1
                if i == "U":
                    countU += 1
                if i == "1":
                    count1 += 1
                if count1 > 0:  # 1 ORed with anything is a 1
                    val = "0"
                elif count1 == 0 and countU > 0:
                    val = "U"
                elif count0 > 0 and count1 == 0 and countU == 0:
                    val = "1"
            self.value = val
            return val
        #done
        elif self.gatetype == "BUFF":
            val = input_values[0]
            self.value = val
            return val


# --- Part B2 helper function
# return the correct order list in vector_list_pool
def locate_best_order(main_detected_fault_list, fault_list_pool, vector_list_pool):
    # - Initializing
    best_vector_cover = 0
    best_vector = []
    
    # -- Locate the best current vector
    pos = 0 # iteration counter
    for current_detected_fault_list in main_detected_fault_list:
        parsed_detected_fault_element = current_detected_fault_list.split(",")
        
        # - Remove already coverd faults
        #print(fault_list_pool)
        for remove_fault in fault_list_pool:
            if remove_fault in parsed_detected_fault_element:
                parsed_detected_fault_element.remove(remove_fault)
        
        # - Check for max coverage of a fault
        if (not(parsed_detected_fault_element[0] in vector_list_pool)):
            # - New best match vector located
            # clean the que of TV if new best found and add
            if (best_vector_cover < len(parsed_detected_fault_element)-1):
                best_vector_cover = len(parsed_detected_fault_element)-1
                best_vector = []
                best_vector.append(pos)
            
            # - Identical vector located
            # Add extra equal value TV to check
            elif (best_vector_cover == len(parsed_detected_fault_element)-1) and ((len(parsed_detected_fault_element)-1) != 0):
                best_vector.append(pos)
        
        pos += 1
    
    # If there is no TV to account for then any TV order can be applied for the rest. return this path
    if best_vector_cover == 0:
        # print("I: Path ended here")
        final_vector_pool = vector_list_pool
        return final_vector_pool
    
    # print("I: vectors with most coverage here: {}".format(best_vector))
    # -- Now running though alterantive pathing for coverage
    # Cost here means that how many TVs are need to cover the faults. The smaller the better
    cur_best = 99999999999
    best_vector_path = ""
    i = 0
    
    for current_vector in best_vector:
        # print("I: Loop {} with ID: {}".format(i, len(fault_list_pool)))
        current_vector_content = main_detected_fault_list[current_vector].split(",")
        current_vector_key = current_vector_content[0]
        current_vector_content.pop(0)
        
        # Removed redundent elements 
        for remove_fault in fault_list_pool:
            if remove_fault in current_vector_content:
                current_vector_content.remove(remove_fault)
        
        # Adding faults to covered pool
        next_fault_list_pool = fault_list_pool.copy()
        for new_fault in current_vector_content:
            next_fault_list_pool.append(new_fault)
        
        # Add vector to covered pool
        next_current_vecter_order = vector_list_pool.copy()
        next_current_vecter_order.append(current_vector_key)
        
        
        # print("I: Fault pool at TV {}: {}".format(current_vector,next_fault_list_pool))
        # print("I: base pool at TV {}: {}".format(current_vector,vector_list_pool))
        # print("I: Fault pool length at TV {}: {}".format(current_vector,len(next_fault_list_pool)))
        # print("I: TV pool at TV {}: {}".format(current_vector,next_current_vecter_order))
        # print("")
        current_vector_path = locate_best_order(main_detected_fault_list, next_fault_list_pool, next_current_vecter_order)
        
        # print("I: Path length at TV {}: {}".format(current_vector,len(current_vector_path)))
        if cur_best > len(current_vector_path):
            # print("I: this path is currently elected as best path")
            cur_best = len(current_vector_path)
            best_vector_path = current_vector_path
        i += 1
    
    # print("I: Best path a this point: {}".format(best_vector_path))
    # print("---------------")
    # print("")
    
    return best_vector_path


# Take a line from the circuit file which represents a gatetype operation and returns a node that stores the gatetype

def parse_gate(rawline):
    # example rawline is: a' = NAND(b', 256, c')

    # should return: node_name = a',  node_gatetype = NAND,  node_innames = [b', 256, c']

    # get rid of all spaces
    line = rawline.replace(" ", "")
    # now line = a'=NAND(b',256,c')

    name_end_idx = line.find("=")
    node_name = line[0:name_end_idx]
    # now node_name = a'

    gt_start_idx = line.find("=") + 1
    gt_end_idx = line.find("(")
    node_gatetype = line[gt_start_idx:gt_end_idx]
    # now node_gatetype = NAND

    # get the string of interms between ( ) to build tp_list
    interm_start_idx = line.find("(") + 1
    end_position = line.find(")")
    temp_str = line[interm_start_idx:end_position]
    tp_list = temp_str.split(",")
    # now tp_list = [b', 256, c]

    node_innames = [i for i in tp_list]
    # now node_innames = [b', 256, c]

    return node_name, node_gatetype, node_innames


# Create circuit node list from input file
def construct_nodelist():
    o_name_list = []
    gateinput = None
    for line in input_file_values:
        if line == "\n":
            continue

        if line.startswith("#"):
            continue

        # TODO: clean this up (Rao's comment)
        if line.startswith("INPUT"):
            index = line.find(")")
            # intValue = str(line[6:index])
            name = str(line[6:index])
            n = Node(name, "U", "PI", [], gateinput, '', -1)
            n.is_input = True
            node_list.append(n)


        elif line.startswith("OUTPUT"):
            index = line.find(")")
            name = line[7:index]
            o_name_list.append(name)


        else:  # majority of internal gates processed here
            node_name, node_gatetype, node_innames = parse_gate(line)
            n = Node(node_name, "U", node_gatetype, node_innames, gateinput, '', -1)
            node_list.append(n)

    # now mark all the gates that are output as is_output
    for n in node_list:
        if n.name in o_name_list:
            n.is_output = True

    # link the interm nodes from parsing the list of node names (string)
    # example: a = AND (b, c, d)
    # thus a.innames = [b, c, d]
    # node = a, want to search the entire node_list for b, c, d
    for node in node_list:
        for cur_name in node.innames:
            for target_node in node_list:
                if target_node.name == cur_name:
                    node.interms.append(target_node)
                    

    return


# TODO: make a circuit class, containing a nodelist, display function, and simulation method. (Rao)
# Helper Function # My Code Signory Somsavath
def remove_dup(x):
    i = 0 
    while i < len(x):
        j = i +1
        while j < len(x):
            if x[i] == x[j]:
                del x[j]
            else:
                j+=1
        i += 1

def test_vectors():
    numberOfInputs = []
    vecLst = []
    for node in node_list:
       if (node.is_input):
           numberOfInputs.append(node.name)
           remove_dup(numberOfInputs)
    #print(numberOfInputs)
    total = 2**(len(numberOfInputs))
    while (total != -1):
        z = bin(total)[2:].zfill(numInputNodes)
        total += -1
        vecLst.insert(0, z)
    vecLst.pop()
    return vecLst

def full_coverage():
    gateList = [] #Gates Inputs for example g-'a'-1 or g-'b'-1
    outputGate = [] # Names of the Gate output 'g'-a-1 
    allInputs = []
    faultLst = []
    i = 0
    j = 0
    k = 0
    for node in node_list:
        allInputs.append(node.name)
        for gateInput in node.innames:
            for target in node_list:
                if target.name == gateInput:
                    gateList.append(node.innames)
                    outputGate.append(node.name)
    while ( j < len(allInputs)):
            a = ("{}-{}".format(allInputs[j],0))
            b = ("{}-{}".format(allInputs[j],1))
            faultLst.append(a),faultLst.append(b)
            j += 1
    while (i < len(outputGate)):
        k = 0
        while (k < len(gateList[i])):
            a = ("{}-{}-0".format(outputGate[i],gateList[i][k]))
            b = ("{}-{}-1".format(outputGate[i],gateList[i][k]))
            faultLst.append(a),faultLst.append(b)
            k += 1
        i +=1    
    remove_dup(faultLst)
    return faultLst

# this function will add a fault into our circuit after being constructed
def addFaultAt(x):
    faultlocation = str(
        input("Where do you want your fault \n"))
    if len(faultlocation != 0):
        return

    if len(faultlocation) != 0:
        faultAt = faultlocation
        if faultAt != x.name:
            print("Node doesn't exist")
            return
        else:
            faultNum = str(
            input("What do you want the fault to be stuck at 1 or 0\n"))
            x.value = faultNum
            return  # print("Fault has been placed")
    else:
        return  # print("No fault")


# using this to clone a list for a fault
def cloneList(nlist):
    fnode_list = nlist[:]
    return fnode_list


def D_Two_A(originalSeed):  # 8-bit LFSRs with no taps (shifter)
    seedChunk = originalSeed
    newSeed = ''

    newSeed += seedChunk[7]
    newSeed += seedChunk[0]
    newSeed += seedChunk[1]
    newSeed += seedChunk[2]
    newSeed += seedChunk[3]
    newSeed += seedChunk[4]
    newSeed += seedChunk[5]
    newSeed += seedChunk[6]
        
    return newSeed


def D_Two_B(originalSeed):  # 8-bit LFSRs with taps at 2, 4, 5
    seedChunk = originalSeed
    newSeed = ''

    newSeed += seedChunk[7]
    newSeed += seedChunk[0]
    newSeed += str(ord(seedChunk[1]) ^ ord(seedChunk[7]))
    newSeed += seedChunk[2]
    newSeed += str(ord(seedChunk[3]) ^ ord(seedChunk[7]))
    newSeed += str(ord(seedChunk[4]) ^ ord(seedChunk[7]))
    newSeed += seedChunk[5]
    newSeed += seedChunk[6]
        
    return newSeed


def D_Two_C(originalSeed):  # 8-bit LFSRs with taps at 2, 3, 4
    seedChunk = originalSeed
    newSeed = ''

    newSeed += seedChunk[7]     
    newSeed += seedChunk[0]
    newSeed += str(ord(seedChunk[1]) ^ ord(seedChunk[7]))
    newSeed += str(ord(seedChunk[2]) ^ ord(seedChunk[7]))
    newSeed += str(ord(seedChunk[3]) ^ ord(seedChunk[7]))
    newSeed += seedChunk[4]
    newSeed += seedChunk[5]
    newSeed += seedChunk[6]

    return newSeed


def D_Two_D(originalSeed):  # 8-bit LFSRs with taps at 3, 5, 7
    seedChunk = originalSeed
    newSeed = ''

    newSeed += seedChunk[7]
    newSeed += seedChunk[0]
    newSeed += seedChunk[1]
    newSeed += str(ord(seedChunk[2]) ^ ord(seedChunk[7]))
    newSeed += seedChunk[3]
    newSeed += str(ord(seedChunk[4]) ^ ord(seedChunk[7]))
    newSeed += seedChunk[5]
    newSeed += str(ord(seedChunk[6]) ^ ord(seedChunk[7]))

    return newSeed



# Main function starts

# Step 1: get circuit file name from command line
print('****************************************************')
print('                  ECE464 Project 2')
print('****************************************************\n')

wantToInputCircuitFile = str(
    input("Provide a benchfile name (return to accept circuit.bench by default):\n"))

if len(wantToInputCircuitFile) != 0:
    circuitFile = wantToInputCircuitFile
    try:
        f = open(circuitFile)
        f.close()
    except FileNotFoundError:
        print('File does not exist, setting circuit file to default')
        circuitFile = "circuit.bench"
else:
    circuitFile = "circuit.bench"

# Constructing the circuit netlist
file1 = open(circuitFile, "r")
input_file_values = file1.readlines()
file1.close()
node_list = []
construct_nodelist()
# printing list of constructed nodes
display_choice = input("\nShow node list? ('yes' or 'no') ")
if (display_choice.lower() == 'y') and (display_choice.lower() == 'yes'):
    for n in node_list:
        n.display()

print("---------------\n")

# Bookeeping
total_fault_list_pool = []
run_extend = 0
show_content_choice = 1

# Bookeep the number of inputs
numInputNodes = 0
for node in node_list:
    if node.is_input:
        numInputNodes += 1

# Produce full fault list for the ciruit 
fault_list = full_coverage()

while True:

    # --- Circuit input handling 
    # -- More than 6 inputs
    if(numInputNodes > 6) and not(run_extend):
        operation_choice = input("Which LFSR would you like to run?\n\t(a)8-bit LFSRs with no taps (shifter) " + 
            "\n\t(b)8-bit LFSRs with taps at 2, 4, 5\n\t(c)8-bit LFSRs with taps at 2, 3, 4 " +
            "\n\t(d)8-bit LFSRs with taps at 3, 5, 7\n\t(e)n-bit Counter\n\n\t")
  
        hexNum = input("\nEnter a hex seed number (start with 0x...): ")

        vector_list_main = []
        
        binString = ''
        hexNumLen = len(hexNum) - 2
        binNum = bin(int(hexNum, 16))
        binNum = binNum[2:]

        if len(binNum) < numInputNodes:
            while(len(binNum) < numInputNodes):
                binNum += binNum
        if len(binNum) > numInputNodes:
            binNum = binNum[0:numInputNodes]
        print("The binary TV generated from seed is: {}".format(binNum))

        loops = min(100, 2**numInputNodes)


        

        
        # --- LFSR calcuations
        # - Now using input test vector to generate next vectors with select LFSR
        x = int(binNum, 2)

        # -- 8-bit LFSRs with no taps (shifter)
        if(operation_choice.lower() == 'a'.lower()):
            # - Initial TV
            prior_test_vector = bin(x)[2:].zfill(numInputNodes)
            vector_list_main.append(prior_test_vector)

            # Create full batch of test vectors
            for i in range(0,loops-1): 
                new_test_vector = ""
                
                # - Generate full string of vector
                for j in range(int(len(prior_test_vector)/8)):
                    new_test_vector = new_test_vector + D_Two_A(prior_test_vector[j*8:(j+1)*8])
                
                # - If length does not match evenly with 8 input, last one uses less inputs
                if len(prior_test_vector)%8 != 0:
                    # Run LFSR with extra zeros to compenstate for lack of input
                    full_content = D_Two_A(prior_test_vector[(len(prior_test_vector) - len(prior_test_vector)%8):(len(prior_test_vector))].zfill(8))
                    
                    # pinch off what is not needed for TV
                    new_test_vector = new_test_vector + full_content[0:len(prior_test_vector)%8]

                prior_test_vector = new_test_vector
                vector_list_main.append(new_test_vector)
        
        # -- 8-bit LFSRs with taps at 2, 4, 5 
        elif(operation_choice.lower() == 'b'.lower()):
            # - Initial TV
            prior_test_vector = bin(x)[2:].zfill(numInputNodes)
            vector_list_main.append(prior_test_vector)

            # Create full batch of test vectors
            for i in range(0,loops-1):  
                new_test_vector = ""
                
                # - Generate full string of vector
                for j in range(int(len(prior_test_vector)/8)):
                    new_test_vector = new_test_vector + D_Two_B(prior_test_vector[j*8:(j+1)*8])
                
                # - If length does not match evenly with 8 input, last one uses less inputs
                if len(prior_test_vector)%8 != 0:
                    # Run LFSR with extra zeros to compenstate for lack of input
                    full_content = D_Two_B(prior_test_vector[(len(prior_test_vector) - len(prior_test_vector)%8):(len(prior_test_vector))].zfill(8))
                    
                    # pinch off what is not needed for TV
                    new_test_vector = new_test_vector + full_content[0:len(prior_test_vector)%8]

                prior_test_vector = new_test_vector
                vector_list_main.append(new_test_vector)

        # -- 8-bit LFSRs with taps at 2, 3, 4
        elif(operation_choice.lower() == 'c'.lower()):
            # - Initial TV
            prior_test_vector = bin(x)[2:].zfill(numInputNodes)
            vector_list_main.append(prior_test_vector)

            # Create full batch of test vectors
            for i in range(0,loops-1): 
                new_test_vector = ""
                
                # - Generate full string of vector
                for j in range(int(len(prior_test_vector)/8)):
                    new_test_vector = new_test_vector + D_Two_C(prior_test_vector[j*8:(j+1)*8])
                
                # - If length does not match evenly with 8 input, last one uses less inputs
                if len(prior_test_vector)%8 != 0:
                    # Run LFSR with extra zeros to compenstate for lack of input
                    full_content = D_Two_C(prior_test_vector[(len(prior_test_vector) - len(prior_test_vector)%8):(len(prior_test_vector))].zfill(8))
                    
                    # pinch off what is not needed for TV
                    new_test_vector = new_test_vector + full_content[0:len(prior_test_vector)%8]

                prior_test_vector = new_test_vector
                vector_list_main.append(new_test_vector)

        # -- 8-bit LFSRs with taps at 3, 5, 7 
        elif(operation_choice.lower() == 'd'.lower()):
            # - Initial TV
            prior_test_vector = bin(x)[2:].zfill(numInputNodes)
            vector_list_main.append(prior_test_vector)

            # Create full batch of test vectors
            for i in range(0,loops-1): 
                new_test_vector = ""
                
                # - Generate full string of vector
                for j in range(int(len(prior_test_vector)/8)):
                    new_test_vector = new_test_vector + D_Two_D(prior_test_vector[j*8:(j+1)*8])
                
                # - If length does not match evenly with 8 input, last one uses less inputs
                if len(prior_test_vector)%8 != 0:
                    # Run LFSR with extra zeros to compenstate for lack of input
                    full_content = D_Two_D(prior_test_vector[(len(prior_test_vector) - len(prior_test_vector)%8):(len(prior_test_vector))].zfill(8))
                    
                    # pinch off what is not needed for TV
                    new_test_vector = new_test_vector + full_content[0:len(prior_test_vector)%8]

                prior_test_vector = new_test_vector
                vector_list_main.append(new_test_vector)

        # -- N-bit counter
        else: 
            # Create full batch of test vectors
            for i in range(loops):
                # To account for overflow, reset TV back to zero
                if(x == 2**hexNumLen):
                    x = 0
                # Generate test vector and add to list
                binString = bin(x)[2:].zfill(numInputNodes)
                vector_list_main.append(binString)

                # Increment TV by 1
                x += 1


        # - Option for less clutered output when getting accumulative fault coverage
        content_choice = input("\nPrint test vector content and coverage? ('yes' or 'no') ")
        if (content_choice.lower() == 'y'.lower()) and (content_choice.lower() == 'yes'.lower()):
            show_content_choice = 1
        else:
            show_content_choice = 0
        

        # - First loop run setup
        vector_list = vector_list_main[0 : 9]

        # Bookeeping
        History_per = []
        run_extend = 1
        proc = 10
        cur_runs = 1

    # -- Run follow up from more than 6 input
    # This part creates the next 10 TV or less depending on remaining vectors to run with
    elif run_extend:
        print("Current runs completed for LFSR option {} is: {}".format(operation_choice, cur_runs))
        cur_runs += 1
        # If there no more TV left to do 10 batch, run with remaining 
        if proc+10 > 2**numInputNodes:
            input("\nHit enter for final {} test vectors".format(2**numInputNodes - proc))
            vector_list = vector_list_main[proc : proc + (2**numInputNodes - proc)]
            run_extend = 0
        
        # Run with next 10 TV 
        else:
            input("\nHit enter for next 10 test vectors")
            vector_list = vector_list_main[proc : proc + 10]
            proc += 10

            # Reaching zero means this run follow up is done
            if(proc == 100):
                run_extend = 0


    # -- less than 7 input 
    # Will run all TV and and show information related to TV 
    else:
        input("\nHit enter to start operation")
        show_content_choice = 1
        vector_list = test_vectors()

    # --- Calc and printing output ---
    print("Now running operation...")
    if show_content_choice:
        # --- PART A content
        print("PART A content:")
        print("Circuit full fault list with {} faults: {}".format(len(fault_list),fault_list))
        print(vector_list)
        print("---------------\n")

        # --- PART B content
        print("PART B content:")
    
    # -- Creating list of test vector with associated fault list
    main_detected_fault_list = []
    for current_vector in vector_list:
        loop = 0
        curr_vec = []
        vec_faults = []
        # --- Good circuit run
        # - Clear all nodes values to U in between simulation runs
        for node in node_list:
            node.set_value("U")
            node.fgate = ''
            node.fgateSA = -1

        strindex = 0
        # - Set value of input node
        for node in node_list:
            if node.is_input:
                if strindex > len(current_vector)-1:
                    break
                node.set_value(current_vector[strindex])
                strindex = strindex + 1

        # --- Simulate by calculating each node's values
        # - Initialize updated_count to 1 to enter while loop at least once
        updated_count = 1
        iteration = 0
        while updated_count > 0:
            updated_count = 0
            iteration += 1
            for n in node_list:
                if n.value == "U":
                    n.calculate_value()
                    if n.value == "0" or n.value == "1":
                        updated_count +=1

        good_output_val = [i.value for i in node_list if i.is_output]


        # --- Bad circuits
        # - Running through each fault to see if issue detected
        current_vector_fault_list = []
        for current_fault in fault_list:
            # Clean nodes before start sim
            for node in node_list:
                node.set_value("U")
                node.fgate = ''
                node.fgateSA = -1

            # - Detemine fault info
            in_out_wire_list = current_fault.split("-")
            
            # Fault on gate output
            if len(in_out_wire_list) == 2:
                faulty_out_wire = in_out_wire_list[0]
                faulty_type = in_out_wire_list[1]
            # Fault around gate
            if len(in_out_wire_list) == 3:
                faulty_out_wire = in_out_wire_list[0]
                faulty_in_wire = in_out_wire_list[1]
                faulty_type = in_out_wire_list[2]

            strindex = 0
            # - Set value of input node
            for node in node_list:
                if node.name == faulty_out_wire:
                    # Fault on gate output, only need to set to fault value
                    if len(in_out_wire_list) == 2:
                        node.set_value(faulty_type)
                    # Fault around gate, set interal values to fault values
                    else:
                        node.fgate = faulty_in_wire
                        node.fgateSA = faulty_type

                    if node.is_input:
                        strindex = strindex + 1
                
                elif node.is_input:
                    node.set_value(current_vector[strindex])
                    strindex = strindex + 1
            
            # --- Simulate by calculating each node's values
            # - Initialize updated_count to 1 to enter while loop at least once
            updated_count = 1
            iteration = 0
            while updated_count > 0:
                updated_count = 0
                iteration += 1
                for n in node_list:
                    if n.value == "U":
                        n.calculate_value()
                        if n.value == "0" or n.value == "1":
                            updated_count +=1

            bad_output_val = [i.value for i in node_list if i.is_output]


            # --- Simulation results
            # - Locating if there is delta on output
            faulty_nodes = 0
            for i in range(len(good_output_val)):
                # Recording outputs that show faulty event
                if(good_output_val[i] != bad_output_val[i]):
                    faulty_nodes = 1
            
            # - Determining if fault is detected
            if not(faulty_nodes == 0):
                current_vector_fault_list.append(current_fault)

        print_detected_fault = "{}".format(current_vector)
        for cur_fault in current_vector_fault_list:
            print_detected_fault = print_detected_fault + ",{}".format(cur_fault)

    # --- Test vector Results
    # - Parsing out vector and associated faults
        print_detected_fault = "{}".format(current_vector)
        for cur_fault in current_vector_fault_list:
            print_detected_fault = print_detected_fault + ",{}".format(cur_fault)
        # - Store result in to csv file
        main_detected_fault_list.append(print_detected_fault)

    if show_content_choice:
        print ("--- Printing out faults detected per test vector ---")
        print ("Test vector, associated faults captured with test vector...\n")

        # - Printing out result for test vector
        for current_detected_fault in main_detected_fault_list:
            print(current_detected_fault)

    # Storing data in csv
    f = open('circuit_all.csv', 'w')
    length = len(vector_list)
    j = 0  
    while(j < length):
        f.write(main_detected_fault_list[j])
        f.write('\n')
        j += 1
    f.close()


    # --- PART B2 --- (originally PART C in first part of report)
    # --- Find best order to cover all faults with given test vectors
    best_vector_order = locate_best_order(main_detected_fault_list, [], [])
    
    # - Adding non order important test vectors
    if(numInputNodes > 6):
        for vector in vector_list:
            if not(vector in best_vector_order):
                best_vector_order.append(vector)
    
    fault_list_pool = []
    # --- Creating output strings
    main_optimal_cover_list = []
    for vector in best_vector_order:
        for cur_content in main_detected_fault_list:
            current_data = cur_content.split(",")
            if vector == current_data[0]:
                break
        current_data.pop(0)
        
        print_optimal_vector = str(vector)
        for cur_fault in current_data:
            if not(cur_fault in fault_list_pool):
                print_optimal_vector = print_optimal_vector + ",{}".format(cur_fault)
                fault_list_pool.append(cur_fault)
                
        main_optimal_cover_list.append(print_optimal_vector)
    
    if show_content_choice:
        print ("\nPART B2 content:")
        print ("--- Printing optimal ordering of fault coverage ---")
        print ("Test vector, associated faults covered with test vector...\n")

    f = open('circuit_list.csv', 'w')
    for vector in main_optimal_cover_list:
        if show_content_choice:
            print(vector)
        f.write(vector)
        f.write('\n')
    f.close()

    print("---------------\n")

    # --- Part C of code --- 
    # - Less than 7 inputs should use all test vectors
    if(numInputNodes < 7):
        print("Fault coverage percent of all test vectors: {}".format((len(fault_list_pool)/len(fault_list))*100))
    
    # - More than 6 inputs should do a accumulative total with each batch of 1 to 10 TV
    else:
        # Add new faults found into the total faults covered with created TV
        for new_fault in fault_list_pool:
            if not(new_fault in total_fault_list_pool):
                total_fault_list_pool.append(new_fault)
        
        # - Output and update of  accumulative content
        print("Current accumulative fault coverage percent: {}".format((len(total_fault_list_pool)/len(fault_list))*100))
        
        # List that stores the historical percentages in order of runs
        History_per.append((len(total_fault_list_pool)/len(fault_list))*100)
        print("Accumulative fault coverage percent: {}".format(History_per))

    # - Clean looping
    print("---------------\n")
