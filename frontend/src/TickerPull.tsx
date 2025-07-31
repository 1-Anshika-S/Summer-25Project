import React, { useEffect, useState } from "react";
import { configs } from "./lib/configs";

const fetchTickerData = async (ticker: string) => {
  const r = await fetch(`${configs.BACKEND}/tickers/AAPL`);

  if (r.status !== 200) {
    return {
      message: "Yikers",
    };
  }

  const body = await r.json();
  return body;
};

const TickerPull = () => {
  const [tickerApiResponse, setTickerApiResponse] = useState({});

  useEffect(() => {
    fetchTickerData("APPL").then((a) => {
      console.log(a);
      setTickerApiResponse(a);
    });
  }, []);

  return <pre>{JSON.stringify(tickerApiResponse, null, 4)}</pre>;
};

export default TickerPull;
