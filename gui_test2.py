from guizero import App, Combo,Text, CheckBox, ButtonGroup, PushButton, info
from classes.pid import PID

def do_booking():
    info("Booking", "Thank you for booking")

PI = PID()

app = App(title="My second GUI app", width=300, height=200, layout="grid")

film_choice = Combo(app, options=["Star Wars", "Frozen", "Lion King"], grid=[1,0], align="left")
film_description = Text(app, text="Which film?", grid=[0,0], align="left")
vip_seat = CheckBox(app, text="VIP seat?", grid=[1,1], align="left")
Text(app,text="Seat Type", grid=[0,1],align="left")

row_choice = ButtonGroup(app, options=[ ["Front", "F"], ["Middle", "M"],["Back", "B"] ],
selected="M", horizontal=True, grid=[1,2], align="left")
Text(app,text="Seat Location", grid=[0,2],align="left")

PushButton(app,command=do_booking,text="Book seats",grid=[1,3],align="left")


app.display()

print( film_choice.value )
print( vip_seat.value )
print( row_choice.value )

print(PI.ki)