import React, {useEffect, useState} from "react";
import "./App.css";
import TickerPull from "./TickerPull";
import EMAPull from "./EMAPull";
import { TickerSelectBox } from "./TickerSelectBox";

function App() {
  const [price, setPrice] = useState("0");
  const [emaPrice, setEmaPrice] = useState("0");
  const [selectedTicker, setTicker] = useState("AAPL")

  useEffect(() => {
    console.log(selectedTicker)
  }, [selectedTicker]);
  return (
    <div className="App">
      <header className="App-header">
        <div>
          <p>Select Ticker</p>
          <TickerSelectBox setTicker={setTicker} selectedTicker={selectedTicker} />
        </div>
        <TickerPull ticker={selectedTicker} setPrice={setPrice} />
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
      </header>
    </div>
  );
}

export default App;
