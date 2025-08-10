from primitives.directives import SendTC, VerifyTM

a = SendTC(1); print(a)
b = VerifyTM(2); print(b)

# Doing a stupid loop and python stuff. All these stuff is not "traced" (so, no track of lines in runtime)
# But of course, you can debug this using VSCode or whatever!


c = SendTC(3); print(c)
d = SendTC(2); print(d)
