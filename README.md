clovertier
==========

A simple text-based haggling simulation that demonstrates a couple of API calls from Clover. Based on the Japanese indie game Recettear.

clover_api.py is an API caller utility, which I modified from Chenyang Yuan's original version: https://bitbucket.org/yuanchenyang/clover-example-server

You will need to need to generate an API token for this app to work. Follow these steps to get one:

1. Create an account at https://www.clover.com/developers
2. Sign in to your account at https://www.clover.com/manage
3. Go to Settings > API Tokens
4. Enter a new token name
5. Click on [Generate Token]
6. Enable all read and write permissions on this token

You will also need your merchant ID, which is just a 13-character alphanumeric string. Sign into your Clover account and observe the path parameter after "merchant" in the URL. For example, PTEXTPYDZ6K4C is the merchant ID in the URL https://www.clover.com/manage/merchant/PTEXTPYDZ6K4C/home.

With an API token and a merchant ID in hand, replace the empty strings for TOKEN and MERCHANT_ID in api_token.py.

To make the game as is actually fun, you need to go into the web dashboard and add the following categories with items:

1. drinks
2. equipment
3. toys
4. corgi goodies

Want to change the we do payments? Visit our Clover app developers page: https://www.clover.com/developers
