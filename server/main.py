import sys
from yahoofinancials import YahooFinancials
import sqlite3
from aiohttp import web

sys.path.insert(1, 'C:\Users\Dev.Juneja\Downloads\Fin-Maestro-Web\Valuations')
sys.path.insert(1, 'C:\Users\Dev.Juneja\Downloads\Fin-Maestro-Web\Sentiment')
sys.path.insert(1, 'C:\Users\Dev.Juneja\Downloads\Fin-Maestro-Web\Sentiment\pcr')
sys.path.insert(1, 'C:\Users\Dev.Juneja\Downloads\Fin-Maestro-Web\SWOT')
import json
import pcr_analyzer
import valuation_determiner
import swot_generator

routes = web.RouteTableDef()

@routes.get('/api/tickers')
async def tickers(request):
    with open("../Prerequisites/Tickers.csv") as f:
        cont = f.read().split()
        cont = cont[1:]
    
    return web.Response(text=json.dumps(cont))

@routes.get("/api/valuation/{ticker}")
async def valu(request):
    ticker = request.match_info["ticker"]
    t = valuation_determiner.valuation_determiner(ticker+".NS")
    t2 = valuation_determiner.financials_extractor(ticker+".NS")
    
    return web.Response(text=json.dumps({"v1":t, "v2": t2}))   

@routes.get("/api/sentiment/{ticker}")
async def valu(request):
    ticker = request.match_info["ticker"]
    t = valuation_determiner.valuation_determiner(ticker+".NS")
    t2 = valuation_determiner.financials_extractor(ticker+".NS")
    
    return web.Response(text=json.dumps({"v1":t, "v2": t2}))    

@routes.get("/api/ohlc/{ticker}/{interval}")
async def valu(request):
    ticker = request.match_info["ticker"]
    interval = request.match_info["interval"]
    yf = YahooFinancials(ticker+".NS")
    ohlc = yf.get_historical_price_data("2022-01-01","2023-03-11", interval)
    return web.Response(text=json.dumps(ohlc))

@routes.get("/api/sentiment/pcrAnalyzer/{ticker}")
async def pcrAnal(request):
    ticker = request.match_info["ticker"]
    if (ticker == "index"):
        data = pcr_analyzer.pcr_stocks_anal(ticker)
    else:
        data = pcr_analyzer.pcr_anal()
    return web.Response(text=json.dumps(data))


@routes.get("/api/swot/{ticker}")
async def swot(request):
    ticker = request.match_info["ticker"]
    data = swot_generator.swot_producer(ticker)
    return web.Response(text=json.dumps(data))

@routes.post("/api/registerTrade")
async def registerTrade(request):
    data = await request.json()
    print(data)
    conn = sqlite3.connect('system.db')
    cursor = conn.cursor()

    # Use parameterized query to avoid SQL injection
    cursor.execute("INSERT INTO TRADES VALUES (?, ?, ?, ?, ?, ?)",
                   (data['id'], data['tickerName'], data['type'], data['enterPrice'], data['exitPrice'], data['isOpen']))

    conn.commit()
    conn.close()
    return web.Response(text=json.dumps({"success": "inserted"}))

@routes.get("/api/closeTrade/{tradeID}/{exitPrice}")
async def valu(request):
    conn = sqlite3.connect('system.db')
    cursor = conn.cursor()

    # Use parameterized query to avoid SQL injection
    exit_price = request.match_info['exitPrice']
    trade_id = request.match_info['tradeID']

    cursor.execute("UPDATE TRADES SET exitPrice=?, isOpen='0' WHERE id=?", (exit_price, trade_id))
    
    conn.commit()
    conn.close()
    return web.Response(text=json.dumps({"success": "inserted"}))

@routes.get("/api/trades/{ticker}")
async def valu(request): 
    conn = sqlite3.connect('system.db') 
    cursor = conn.cursor() 

    # Use parameterized query to avoid SQL injection
    ticker_name = request.match_info['ticker']
    cursor.execute("SELECT * FROM TRADES WHERE tickerName=?", (ticker_name,))
    
    output = cursor.fetchall() 
    di = {"trades": []} 
    for row in output: 
        di["trades"].append(list(row)) 

    conn.commit() 
    conn.close() 
    return web.Response(text=json.dumps(di))
    
    
app = web.Application()
app.add_routes(routes)
web.run_app(app)
