import React, { useEffect, useState } from "react";
import { configs } from "./lib/configs";

const fetchTickerData = async (ticker: string) => {
  const r = await fetch(`${configs.BACKEND}/tickers/${ticker}`);

  if (r.status !== 200) {
    return {
      message: "Yikers",
    };
  }

  return await r.json();
};

const TickerPull = (args: { ticker: string }) => {
  const [tickerApiResponse, setTickerApiResponse] = useState({});

  useEffect(() => {
    fetchTickerData(args.ticker).then((a) => {
      console.log(a);
      setTickerApiResponse(a);
    });
  }, [args.ticker]);

  return <pre>{JSON.stringify(tickerApiResponse, null, 4)}</pre>;
};

export default TickerPull;
