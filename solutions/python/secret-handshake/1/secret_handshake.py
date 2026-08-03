ACTIONS = [
    "Reverse the order of the operations in the secret handshake",
    "wink", 
    "double blink", 
    "close your eyes", 
    "jump"
]

def commands(binary_str):
    reverse = 1
    if binary_str[0] == '1':
        reverse = -1

    actions = []
    for i in range(1, 5):
        if binary_str[-i * reverse] == '1':
            actions.append(ACTIONS[i * reverse])

    return actions
            
    
