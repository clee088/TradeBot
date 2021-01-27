helpText = '''
        ========================================
        /           TradeBot Commands          /
        ========================================
        /                System                /
        ----------------------------------------
        STOP ------------> Stops TradeBot.
        START -----------> Returns date when TradeBot started.
        UPTIME ----------> Returns the time TradeBot has been running.
        PREV/LAST -------> Executes last command.
        CLEAR -----------> Clears previous messages/text.
        ----------------------------------------
        /                Alpaca                /
        ----------------------------------------
        ACCOUNT ---------> Returns account info.
        ORDERS ----------> Returns any open Alpaca orders.
        CREATE ORDER ----> Creates market order (qty=1) for TradeBot's symbol.
        CANCEL ALL ------> Cancels all open Alpaca orders.
        POSITIONS -------> Returns current Alpaca positions.
        CLOSE POSITION --> Closes position for any given symbol if owned.
        CONN STREAMS ----> (Re)connects to trade/data stream.
        ----------------------------------------
        /                 SQL                  /
        ----------------------------------------
        LIST DATABASES --> Lists all SQL database table names.
        VIEW LAST DATA --> Returns last two data entries for TradeBot's symbol.
        COUNT DATABASE --> Returns number of rows in any given symbol's SQL database.
        CHECK TABLE -----> Checks SQL database if a table with any given symbol exists.
        DROP TABLE ------> Drops any given symbol's SQL database.
        ----------------------------------------
        /                 Data                 /
        ----------------------------------------
        GET MARKET DATA -> Gets historical data from inputted symbol, month, and year.
                           Then populates SQL database with market data.
        CALCULATE HOUR --> Calculates current hour data for TradeBot's symbol.
        TEST INDICATOR --> Calculates and analyzes indicators for TradeBot's symbol.
        ----------------------------------------
        /                Charts                /
        ----------------------------------------
        PLOT HOUR -------> Plots hourly chart of TradeBot's symbol including
                           price and indicators (hull moving average and macd histogram).
        =======================================
        '''
