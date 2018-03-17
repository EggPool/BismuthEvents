# What is Event Sourcing?

It's an object/data model that stores the *events* leading to the current state of objects, rather than the *current state* itself.

## Advantages

* Complete log of every state change ever  
* Unmatched traceability and debugability
* Very good performance characteristics
* Allows after-the-fact data analysis of Event Streams
* Full metadata: Who did that? when?
* Easy temporal queries

## Very Good overview (not blockchain related)

* Slides [Event sourcing in practive](http://ookami86.github.io/event-sourcing-in-practice/)  
  By Benjamin Reitzammer and Johannes Seitz
  
## In a blockchain context

Perfect fit, since  
* the blockchain ensures the immutability of the events  
* storing the current state of evolving objects would waste enormous amount of (immutable) data  

## Event sourcing with ETH

[Event sourcing on blockchain](https://softwaremill.com/event-sourcing-on-blockchain/)

Way too complex and eth-related to be of use for Bismuth, but some info to understand the context.

## Some more pointers

https://dzone.com/articles/5-great-points-why-you-use-event-sourcing-1
http://microservices.io/patterns/data/event-sourcing.html
http://microservices.io/patterns/data/cqrs.html
https://msdn.microsoft.com/en-us/library/jj591559.aspx
http://cqrs.nu/Faq/event-sourcing
https://news.ycombinator.com/item?id=12627944
https://dapp.transmute.industries/

## Related Projects or tools

WIP
https://eventstore.org/
