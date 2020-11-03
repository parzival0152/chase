import random
prompt = "ready"
options = ['a','b','c','d']

mix = [0,1,2,3]
random.shuffle(mix)
correct = mix[0]
print(options)
options[mix[0]],options[mix[1]],options[mix[2]],options[mix[3]] = options
print(options)
print(mix)
print(correct)
msg = f'{prompt}#'+'#'.join(options)
prompt, *options = msg.split('#')
print(prompt,options)