Welcome to TradeBot Python program.

In order to use the program, you must have an Alpaca account.
https://app.alpaca.markets/brokerage/dashboard/overview

You will also need...
1. Alpaca API key
2. Alpaca API secret key

Once you obtain these keys, you will need to set them as environmental variables.

Follow these steps to set them up...

IF MacOS:
1. Open Terminal.
2. Type "nano ~/.zshrc".
3. Anywhere in the file, add the following two lines by pasting...
    export ALPACA_KEY="YOUR ALPACA API KEY"
    export ALPACA_SECRET_KEY="YOUR ALPACA API SECRET KEY"
4. Press CTRL X to exit.
5. Press Y to save changes.
6. Press ENTER (RETURN).
7. Restart your terminal by quitting (CMD Q) then reopening terminal.
8. Then you are free to run the main.py file.

IF Ubuntu:
1. Open Terminal.
2. Type "nano ~/.profile".
3. Anywhere in the file, add the following two lines by pasting...
    export ALPACA_KEY="YOUR ALPACA API KEY"
    export ALPACA_SECRET_KEY="YOUR ALPACA API SECRET KEY"
4. Press CTRL X to exit.
5. Press Y to save changes.
6. Press ENTER (RETURN).
7. Restart your terminal by quitting (CMD Q) then reopening terminal.
8. Then you are free to run the main.py file.