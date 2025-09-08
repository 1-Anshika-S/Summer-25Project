import React, { useEffect, useState } from "react";
import "./App.css";
import TickerPull from "./TickerPull";
import EMAPull from "./EMAPull";
import { TickerSelectBox } from "./TickerSelectBox";
import { TickerSelect } from "./tickerSelect/TickerSelect";
import { TopBar } from "./TopBar";

function App() {
  const [price, setPrice] = useState("0");
  const [emaPrice, setEmaPrice] = useState("0");
  const [activeTicker, setActiveTicker] = useState<{
    name: string;
    ticker: string;
  }>({
    name: "Apple Inc.",
    ticker: "AAPL",
  });

  return (
    <div className="App">
      <div className="left">
        <TopBar activeTicker={activeTicker} />
        <div className="content">
          <TickerPull ticker={activeTicker.ticker} setPrice={setPrice} />
          {
            //  <EMAPull ticker={selectedTicker} setPrice={setEmaPrice} />
          }

          <main>
            <section id="closingPrice" className="enhanced-section">
              <h2>Closing Price</h2>
              <p>
                <span id="ticker-pull">{price}</span>
              </p>
            </section>
            {/*
          <section id="ema" className="enhanced-section">
            <h2>Exponential Moving Average(EMA)</h2>
            <p>
              <span id="ema">{emaPrice}</span>
            </p>
          </section>
          */}
          </main>
        </div>
      </div>
      <div className="right">
        <TickerSelect setActiveTicker={setActiveTicker} />
      </div>
    </div>
  );
}

export default App;
