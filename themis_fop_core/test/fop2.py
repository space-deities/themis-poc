from fops.internal.args import AND, Action, Operator
from fops.lang.send import Send
from fops.lang.verify_tm import VerifyTM

res1 = VerifyTM(["TM1", "eq", 100], Retries=3)
#print(res1)

expr = AND(["TM1", "eq", 10], ["TM2", "lt", 5])
res2 = VerifyTM(expr, Tolerance=0.1, ValueFormat="RAW")
#print(res2)

send1 = Send("COMMAND_A", Delay=2)
#print(send1)

send1 = Send("COMMAND_B")

send2 = Send("COMMAND_C", Confirm=True)
#print(send2)
    
Send( command = "COMMAND_D")

Send(command = 'COMMAND_E',
     args = [ [ 'ARG1', 1.0 ],
              [ 'ARG2', 0xFF, {'Radix':'HEX'} ] ],
    
     verify= [ ['TM1', Operator.EQ, 10.0, {'Tolerance' :0.1} ],
               ['TM2', Operator.GT ,0, {'Timeout' :20} ] ],

     Delay = 10,
     Tolerance = 0.5,
     OnFailure = {Action.CANCEL},
     PromptUser = False
)

Send("COMMAND_F", PromptUser=3)

Send("COMMAND_EX")
