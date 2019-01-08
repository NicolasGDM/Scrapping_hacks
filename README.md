# Scrapping_hacks

This repository aims at presenting some tools and practices for scrapping. Some will find the use cases their were looking for, others simply good practices for scrapping.

The scripts available are as follow :

1) Twitter API too slow ? - scrapping Twitter friends

The Twitter API is unfriendly when it comes to crawling graph friends. It would take around 2 months to crawl the full friends/followers graph of around 100k users. To overcome this limitation, I set up a tool that fetches friend/follower information by simple json requests. For users with a lot of friends, it is slower than using the API. However, the distribution of the number of friends per user is left-skewed/right heavy tailed, and most users have only hundreds of friends, if not less. Querying the API for such users' friends wastes tantamount number of queries and time. A good practice I found is use my code for the vas majority of users (90%) that have less than ~3000 friends, and the API for the rest. With that, depending on the number of IP adresses and API accounts one has, building a 100k nodes/20million edges graph can be done in less than 48h.  For more information, refer to the README_twitter_scrapper.pdf.

2) Crawling Botometer API

Plug and play code to get botometer scores of some accounts.

