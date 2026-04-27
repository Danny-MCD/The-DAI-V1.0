//+------------------------------------------------------------------+
//|                                              AI_Trader_v2.mq5    |
//|                                      Copyright 2026, Danny-MCD   |
//+------------------------------------------------------------------+
#property copyright "Danny-MCD"
#property link      ""
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>

//--- GLOBAL VARIABLES
CTrade trade;
input int MagicNumber = 123456;
double dailyStartEquity = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    // Check every 3 seconds to avoid file locking with Python
    EventSetTimer(3); 
    
    Print("--- AI BRIDGE: DYNAMIC LOTS & 3s POLLING ACTIVE ---");
    
    trade.SetExpertMagicNumber(MagicNumber);
    dailyStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    EventKillTimer();
}

//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
{
    ExportMarketData();
    CheckForSignal();
}

//+------------------------------------------------------------------+
//| Export 500 candles for Python to analyze                         |
//+------------------------------------------------------------------+
void ExportMarketData()
{
    int handle = FileOpen("live_market_data.csv", FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI, ',');
    if(handle != INVALID_HANDLE)
    {
        FileWrite(handle, "time", "open", "high", "low", "close", "tick_volume");
        
        MqlRates rates[];
        ArraySetAsSeries(rates, true);
        int copied = CopyRates(_Symbol, _Period, 0, 500, rates);
        
        for(int i = copied - 1; i >= 0; i--)
        {
            FileWrite(handle, 
                TimeToString(rates[i].time), 
                rates[i].open, 
                rates[i].high, 
                rates[i].low, 
                rates[i].close, 
                rates[i].tick_volume
            );
        }
        FileClose(handle);
    }
}

//+------------------------------------------------------------------+
//| Read signal from Python and execute trades                       |
//+------------------------------------------------------------------+
void CheckForSignal()
{
    // 1. Safety Check: 25% Drawdown Limit (Protects your remaining 150 EUR)
    if(AccountInfoDouble(ACCOUNT_EQUITY) < (dailyStartEquity * 0.75)) 
    {
        Print("CRITICAL: 25% Drawdown reached. Trading halted.");
        return;
    }

    // 2. Open Signal File (ANSI mode to avoid Asian character bug)
    int handle = FileOpen("ai_signal.txt", FILE_READ|FILE_TXT|FILE_COMMON|FILE_ANSI);
    if(handle == INVALID_HANDLE) return;
    
    string signal = FileReadString(handle);
    FileClose(handle);
    
    StringTrimLeft(signal); 
    StringTrimRight(signal);

    // Skip if file is neutral
    if(signal == "0" || signal == "") return;

    // --- 3. EXIT LOGIC (Check if Python says EXIT or signal reversed)
    if(signal == "EXIT" || signal == "1" || signal == "-1")
    {
        for(int i = PositionsTotal() - 1; i >= 0; i--)
        {
            ulong ticket = PositionGetTicket(i);
            if(PositionSelectByTicket(ticket) && PositionGetInteger(POSITION_MAGIC) == MagicNumber)
            {
                long type = PositionGetInteger(POSITION_TYPE);
                
                // Exit conditions: "EXIT" command OR signal flipped against current position
                if(signal == "EXIT" || 
                  (type == POSITION_TYPE_BUY && signal == "-1") || 
                  (type == POSITION_TYPE_SELL && signal == "1"))
                {
                    Print("AI SIGNAL: ", signal, " - Closing position ticket: ", ticket);
                    trade.PositionClose(ticket);
                }
            }
        }
    }

    // --- 4. ENTRY LOGIC (Only if no positions open)
    if((signal == "1" || signal == "-1") && PositionsTotal() == 0)
    {
        // DYNAMIC LOT CALCULATION: 0.03 lots per 100 EUR
        double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
        // We divide by 100, multiply by 0.03, then normalize to 2 decimal places
        double dynamicLot = MathFloor((currentBalance / 100.0) * 0.03 * 100.0) / 100.0;
        
        // Final safety checks on lot size
        if(dynamicLot < 0.01) dynamicLot = 0.01;
        if(dynamicLot > 0.10) dynamicLot = 0.10; // Extra cap for safety

        double price = (signal == "1") ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
        ENUM_ORDER_TYPE type = (signal == "1") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;

        Print("Signal: ", signal, " | Balance: ", currentBalance, " | Calculating Dynamic Lot: ", dynamicLot);

        if(trade.PositionOpen(_Symbol, type, dynamicLot, price, 0, 0, "AI DYNAMIC"))
        {
            Print("SUCCESS: Market Order Placed at ", dynamicLot, " lots.");
        }
        else
        {
            Print("TRADE FAILED. Error Code: ", GetLastError());
        }
    }

    // 5. Clear Signal File (Prevents duplicate entries)
    int clearHandle = FileOpen("ai_signal.txt", FILE_WRITE|FILE_TXT|FILE_COMMON|FILE_ANSI);
    if(clearHandle != INVALID_HANDLE)
    {
        FileWriteString(clearHandle, "0");
        FileClose(clearHandle);
    }
}