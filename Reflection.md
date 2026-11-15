# What I learned

I split this assignment up into two main parts. First, I chose the football link from
the website and changed the program to fetch information from that link. Then I further
changed the program to include one GET and one POST endpoint.

The POST endpoint takes a JSON dictionary of a certain country and returns only players
from that country. For example, the curl statement below would return only players from Spain. 

curl -X POST http://127.0.0.1:5000/football -H "Content-Type: application/json" -d "{\"country\":\"Spain\"}"

I did not know that POST statements could be used in a way that doesn't alter the data that it is
interacting with. I thought we only used them for updating, deleting, or creating, but this one performs
a read function. Post statements take JSON from the user, but the JSON does not necessarily need to change
anything.
