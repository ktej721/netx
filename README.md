# netx

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/github/license/ktej721/netx)

> 🚧 This project is under active development.  
> Built in public to explore networking internals step by step. kinda like v0ish

hey there! netx is a little tool that helps you understand what's going on when you visit a website. you know how you type in a website address and magically a page appears? netx shows you all the secret steps that happen in between. i thought it would come handy in specific cases.

this was supposed to be a weekend-project where i wanted to implement what i had learnt in my CN-1 course at uni, but yeah i also though its kinda helpful if you know what's taking so long for your web requests to open up, easily in your cli, presented in a "human-friendly manner"...this is a very initial prototype of the tool, i am sure i will try to improve this as far as possible.

it's like a friendly guide that explains the journey your computer takes to fetch a webpage. and yeah also point out the errors if needed.

## how to get it

to use netx, you need to install it first. make sure you have python on your computer, and then you can install it right from github with this command:

```
pip install git+https://github.com/ktej721/netx.git
```

this will install the `netx` command on your computer.

## how to use it

it's super simple. you just open your terminal and type:

```
netx explain [the website address]
```

for example:

```
netx explain https://google.com
```

and it will show you everything that's happening, step by step.

## what it shows you

netx will show you a few things:

* **url parsing:** it checks the website address you typed and makes sure it's a real address.
* **dns resolution:** it finds the computer on the internet that has the website you want to visit. it's like looking up a friend's address in your contacts. yeah caching and all that too...
* **tcp connect:** it connects your computer to the website's computer. it's like calling your friend on the phone.
* **tls handshake:** this is a secret handshake to make sure your connection is safe and private. it's like whispering a secret password to your friend.
* **http request:** your computer asks the website's computer for the webpage. it's like saying "hey, can i see your webpage?".

## want to see it in a different way?

if you're a computer expert, you might want to see the results in a different way. you can use the `--json` flag to get the results in a format that computers can understand.

```
netx explain https://google.com --json
```

## Example Output
```bash
$ netx explain https://example.com
▶ Network Explorer — v0.1
▶ Target: https://example.com

✓ URL parsing  0.02 ms
  scheme: https
  host: example.com
  port: 443
  path: /
  query:

✓ DNS resolution  979.01 ms
  IPv6: 2606:4700:90d2:8c7c:3376:429:ccc4:a209
  IPv4: 104.18.26.120
  IPv4: 104.18.27.120

✓ TCP connect  28.89 ms
✓ TLS handshake  98.24 ms
✓ HTTP request  111.81 ms
  Status: 200 OK
  TTFB: 111.73 ms

