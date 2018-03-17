# Bismuth as a Dapp framework

[Bismuth](https://github.com/hclivess/Bismuth) is way more than "just" another cryptocurrency.

Its open architecture allows for smooth dapps (distributed apps) development, and its Python codebase eases the adoption and comprehension of its internals.

I read about Event sourcing a while ago, and Bismuth seems to be the perfect fit.  
It provides a stable and secure blockchain implementation, with arbitrary data embedding in its open field.

## The trigger

Lately, the Bismuth node evolved with API commands allowing to easily interact with the chain.

Then, it suddenly became obvious to add some [event sourcing](What_is_event_sourcing.md) functionality on top of Bismuth, and try how easy it would be to design and code such features from scratch.

## Two days of light work

Yep, about 2 small days to design [some protocol](events.md), test it, and have the documented code to [test run](../event_cli/readme.md).

## Lessons learned and proofs

* The "data" open field of Bismuth is incredibly flexible and allows for an insane amount of future features.
* You can design non trivial protocols on top of Bismuth (this one includes register, auth, source management, delegation, filtering, signing, encrypting...)
* You don't need to learn a new language or wait for a PR to Bismuth core: a few lines of Python and you're the master of your own Distributed App! 

## Built upon!  

This code is released under a GNU GPL v3 Licence.  
You can use it as a starting point, or built upon. Reuse the event protocol and extend it, built upon the auth/delegation mecanism...

The client I made for this POC is quite basic, but I plan to built more, see the [roadmap](Roadmap.md).


Wanna help? Got an idea for something alike or built upon? Need a coder for a real use case application? Tell me!
