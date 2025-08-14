import React, { useEffect, useState } from "react";

import { configs } from "./lib/configs";

const fetchEMAData = async (ticker: string, period: number, signal?: AbortSignal) => {
  const r = await fetch(`${configs.BACKEND}/ema/${encodeURIComponent(ticker)}?period=${period}`, { signal });

  if (r.status !== 200) {
    return { message: "Yikers" };
  }

  return await r.json();
};

interface EMAPullProps {
  ticker: string;
  setPrice: React.Dispatch<React.SetStateAction<string>>;
  period?: number; //optional; defaults to 50
}

const EMAPull = ({ ticker, setPrice, period = 50 }: EMAPullProps) => {
  const [tickerApiResponse, setTickerApiResponse] = useState<any>({});
  useEffect(() => {
    fetchEMAData(ticker, period)
        .then((data) => {
      console.log("Raw EMA API data:", data);
      setTickerApiResponse(data);

      // Try most likely paths for EMA value
      const emaArr =
        data?.emaValue ??
        data?.data?.emaValue ??
        data?.results?.emaValue ??
        [];

      let emaVal: any;

      if (Array.isArray(emaArr) && emaArr.length > 0) {
        emaVal = emaArr[emaArr.length - 1]?.ema;
      }

      console.log("Extracted EMA:", emaVal);

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
