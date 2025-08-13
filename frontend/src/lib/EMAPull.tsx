import React, { useEffect, useState } from "react";
import { configs } from "./lib/configs";

const fetchTickerData = async (ticker: string) => {
  const r = await fetch(`${configs.BACKEND}/tickers/${ticker}`);

  if (r.status !== 200) {
    return { message: "Yikers" };
  }

  return await r.json();
};

interface EMAPullProps {
  ticker: string;
  setPrice: React.Dispatch<React.SetStateAction<string>>;
}

const EMAPull = ({ ticker, setPrice }: TickerPullProps) => {
  const [tickerApiResponse, setTickerApiResponse] = useState<any>({});

  useEffect(() => {
    fetchTickerData(ticker).then((a) => {
      console.log("Raw API data:", a);
      setTickerApiResponse(a);

      // Try most likely paths for closing price
      let closeVal: any =
        a?.closingPrices?.[a?.closingPrices.length - 1]?.close ??
        a?.data?.closingPrices?.[a?.closingPrices.length - 1]?.close ??
        a?.results?.closingPrices?.[a?.closingPrices.length - 1]?.close ??
        a?.price; // fallback if your API just has `price`

      console.log("Extracted ema:", emaVal);
      if (emaVal !== undefined) {
        setPrice(String(emaVal));
      } else {
        setPrice("N/A");
      }
    });
  }, [ticker, setPrice]);

  // Still show the debug of just the closing price
  return <span></span>
};

export default EMAPull;
