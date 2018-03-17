# Prerequisites

All event: commands have to be 0 amount to be valid, and sent to self only.
No impact on hyper size or balance.  
Event commands are specified via openfield data.

prototype:  
`event:xxx:event_name:optional_data`

xxx is a 3 letters event command.
event_name is 3 letters long minimum.

# EVENTS COMMANDS

## Main commands

### reg
Register an event.  
`event:reg:Egg`

### msg
Emit an event (can be anything, including binary, z85 encoded).    
`event:msg:Egg:Z85ENCODEDPAYLOAD`  
> Message could be encrypted (with sender privkey or another one)

## Rights management commands

### xfr
Transfer admin rights to someone.  
(only one admin at a time - may add a new command later)
`event:xfr:Egg:edf.......25`

### add
Give source rights to someone.  
`event:add:Egg:edf.......25`

### del
Remove source rights from someone.  
`event:del:Egg:edf.......25`

## Additionnal commands

### dsc
Add or change event description (only text allowed here).  
`event:dsc:Egg:Info and stats about EggPool Mining pool`

### icn
Attach an icon/avatar (size/format to be spec, like 128x128png).    
`event:icn:Egg:Z85bin`

### typ
Add or change event mime-type (default is text/plain).  
`event:typ:Egg:text/html|image/png`  
or custom types:  
bin|graph(description needed, will display live values, like pool stats)  
Client can use widgets to display graphs.





