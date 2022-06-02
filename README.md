# priceScraper

__Compares given product's prices in given K-Ruoka stores.__

Takes short names of K-Ruoka stores and link to or a search term for K-Ruoka product as input.

Seperate store names with `,`. <br />
Adding `*` to store name, searches 10 nearest stores aswell. <br />

Usually does not work with VPN or on known server IPs because of undetected_chromedriver being deteced.

Current version works as discord bot.

### Commands
`!vertaile [product name] [store name]`
Use `""` when adding spaces to arguments.


### Requirements
- python3
- beautifulsoup4
- selenium
- undetected_chromedriver
- webdriver_manager